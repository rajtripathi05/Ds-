"""Chat UI server — stdlib only. Role passed per-request; enforcement lives in planner/retrieval/SQL."""
import json, sys, os, re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DSCOPILOT_DB", str(ROOT / "out" / "copilot.db"))
from planner import ask
import llm

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ct="application/json"):
        self.send_response(code); self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body))); self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            self._send(200, (ROOT / "ui/index.html").read_bytes(), "text/html; charset=utf-8")
        elif u.path.startswith("/charts/"):
            f = ROOT / "out" / u.path.lstrip("/")
            if f.exists() and f.suffix == ".png":
                self._send(200, f.read_bytes(), "image/png")
            else:
                self._send(404, b"{}")
        elif u.path == "/llm_status":
            self._send(200, json.dumps(llm.status()).encode())
        else:
            self._send(404, b"{}")
    def do_POST(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        role = (q.get("role", ["ops"])[0] or "ops").lower()
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if u.path == "/ask":
            r = ask(body.get("question", ""), role)
            self._send(200, json.dumps(r, default=str).encode())
        else:
            self._send(404, b"{}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"ds-copilot on http://localhost:{port}  (DB: {os.environ['DSCOPILOT_DB']})")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
