#!/usr/bin/env python3
import http.server, os, re, json
import stripe

# ── CONFIG ──────────────────────────────────────────────
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51TCtPkPRIGtl6B50lWnUdYXcthv9SRv7rmFI1lmgSqmB5oPbINdHkvCC698glnSQdNcnAAfdmZvkJmQ3sIraAb7T00RIMhfIJi')
STRIPE_PRICE      = 1999                        # $19.99 in cents
PORT              = int(os.environ.get('PORT', 3000))
DOMAIN            = os.environ.get('DOMAIN', f'http://localhost:{PORT}')
# ────────────────────────────────────────────────────────

stripe.api_key = STRIPE_SECRET_KEY

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/upload':
            self._handle_upload()
        elif self.path == '/create-checkout-session':
            self._handle_checkout()
        else:
            self.send_response(404); self.end_headers()

    def _handle_checkout(self):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': STRIPE_PRICE,
                        'product_data': {
                            'name': 'Chad Light',
                            'description': 'Foldable COB LED Gym Light — Dual COB, Type-C, Tripod Stand',
                            'images': [DOMAIN + '/images/product1.png'],
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=DOMAIN + '/success.html',
                cancel_url=DOMAIN + '/',
            )
            self.respond(200, json.dumps({'url': session.url}).encode())
        except Exception as e:
            self.respond(500, json.dumps({'error': str(e)}).encode())

    def _handle_upload(self):
        length = int(self.headers['Content-Length'])
        ct = self.headers['Content-Type']
        boundary = ct.split('boundary=')[1].encode()
        data = self.rfile.read(length)
        name_match = re.search(rb'filename="([^"]+)"', data)
        if not name_match:
            self.respond(400, b'No filename'); return
        filename = name_match.group(1).decode()
        header_end = data.find(b'\r\n\r\n') + 4
        file_end = data.rfind(b'\r\n--' + boundary)
        file_bytes = data[header_end:file_end]
        os.makedirs('images', exist_ok=True)
        with open(os.path.join('images', filename), 'wb') as f:
            f.write(file_bytes)
        self.respond(200, f'Saved as {filename}'.encode())

    def respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'Server running at {DOMAIN}')
http.server.HTTPServer(('', PORT), Handler).serve_forever()
