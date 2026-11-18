#!/usr/bin/env python3
"""Serves the site with caching turned off, so an edited page is never
hidden behind the browser's copy of the old one, and serves 404.html for
missing addresses the way Vercel will.

    python3 serve.py            # port 8230
    python3 serve.py 8200       # any other port
"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT") or (sys.argv[1] if len(sys.argv) > 1 else 8230))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        page = os.path.join(ROOT, "404.html")
        if code == 404 and os.path.exists(page):
            body = open(page, "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
