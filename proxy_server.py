#!/usr/bin/env python3
"""
SmartQC CORS Proxy Server
Forwards requests to the DocAPI and adds CORS headers.

Usage:
    python3 proxy_server.py

Then open smartqc_verifier.html in your browser.
The widget will call http://localhost:8080/getdocument?ref_id=...
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, parse_qs
import json
import sys
import os

DOC_API_BASE = "http://10.10.116.174:8000/uidgetdocument"
PROXY_PORT   = 8080
STATIC_DIR   = os.path.dirname(os.path.abspath(__file__))


class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} → {fmt % args}")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")

        # ── Proxy endpoint ──────────────────────────────────────────────
        if path == "/getdocument":
            params = parse_qs(parsed.query)
            ref_id = (params.get("ref_id") or params.get("Payload Ref ID") or [""])[0].strip()

            if not ref_id:
                self._json_error(400, "Missing ref_id query parameter")
                return

            target = f"{DOC_API_BASE}?ref_id={ref_id}"
            print(f"\n[PROXY] GET {target}")
            try:
                req  = Request(target, headers={"User-Agent": "SmartQC-Proxy/1.0"})
                resp = urlopen(req, timeout=20)
                body = resp.read()
                ct   = resp.headers.get("Content-Type", "application/octet-stream")
                print(f"[PROXY] ← {resp.status}  content-type={ct}  bytes={len(body)}")

                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(body)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(body)

            except HTTPError as e:
                body = e.read()
                print(f"[PROXY] ← HTTP {e.code}")
                self._json_error(e.code, f"Upstream error {e.code}: {body[:200].decode(errors='replace')}")

            except URLError as e:
                print(f"[PROXY] ← URLError: {e.reason}")
                self._json_error(502, f"Cannot reach DocAPI: {e.reason}")

            except Exception as e:
                print(f"[PROXY] ← Exception: {e}")
                self._json_error(500, str(e))

        # ── Serve static files (the HTML widget) ────────────────────────
        elif path == "/" or path == "":
            self._serve_file("smartqc_verifier.html", "text/html; charset=utf-8")

        elif path.endswith(".html"):
            fname = os.path.basename(path)
            self._serve_file(fname, "text/html; charset=utf-8")

        elif path.endswith(".js"):
            fname = os.path.basename(path)
            self._serve_file(fname, "application/javascript")

        else:
            self._json_error(404, f"Not found: {self.path}")

    def _serve_file(self, filename, content_type):
        fpath = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(fpath):
            self._json_error(404, f"File not found: {filename}")
            return
        with open(fpath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _json_error(self, code, message):
        body = json.dumps({"error": message}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PROXY_PORT
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)
    print("=" * 56)
    print("  SmartQC CORS Proxy Server")
    print("=" * 56)
    print(f"  Proxy  →  http://localhost:{port}")
    print(f"  Widget →  http://localhost:{port}/smartqc_verifier.html")
    print(f"  DocAPI →  {DOC_API_BASE}")
    print("=" * 56)
    print("  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped.")
