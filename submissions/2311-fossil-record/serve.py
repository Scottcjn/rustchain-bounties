#!/usr/bin/env python3
"""CORS proxy for RustChain API — serves fossil-record locally."""
import http.server
import json
import urllib.request
import os

PORT = 8765
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://rustchain.org"


class FossilHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy_api()
        else:
            super().do_GET()

    def _proxy_api(self):
        url = f"{API_BASE}{self.path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FossilRecord/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


if __name__ == "__main__":
    with http.server.HTTPServer(("", PORT), FossilHandler) as httpd:
        print(f"Fossil Record server: http://localhost:{PORT}")
        httpd.serve_forever()
