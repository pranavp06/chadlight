import os, json
import stripe
from http.server import BaseHTTPRequestHandler

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
DOMAIN = os.environ.get('DOMAIN', 'https://chadlight.store')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 1999,
                        'product_data': {
                            'name': 'Chad Light',
                            'description': 'Foldable COB LED Gym Light — Dual COB, Type-C, Tripod Stand',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=DOMAIN + '/success.html',
                cancel_url=DOMAIN + '/',
            )
            self._respond(200, {'url': session.url})
        except Exception as e:
            self._respond(500, {'error': str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
