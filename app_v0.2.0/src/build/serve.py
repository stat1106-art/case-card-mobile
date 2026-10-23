import sys, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
class H(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.webmanifest': 'application/manifest+json', '.woff2': 'font/woff2', '.json': 'application/json', '.js': 'text/javascript', '.svg': 'image/svg+xml'}
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache'); super().end_headers()
d = sys.argv[2]
ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), functools.partial(H, directory=d)).serve_forever()
