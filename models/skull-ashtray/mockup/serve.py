"""Local server for the mockup renderer: serves the skull-ashtray folder and saves POSTed PNGs to mockup/renders/.
Run: python3 models/skull-ashtray/mockup/serve.py, then open http://localhost:8765/mockup/index.html?view=hero"""
import http.server
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "mockup", "renders")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = re.sub(r"[^a-z0-9_-]", "", q.get("name", ["render"])[0].lower()) or "render"
        data = self.rfile.read(int(self.headers["Content-Length"]))
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "skull-ashtray-mockup-%s.png" % name), "wb") as f:
            f.write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


http.server.ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
