"""Exception-queue UI server (stdlib). Queue = routed docs with aging + reason codes;
approve/override -> immutable audit + learning-loop retune endpoint."""
import json, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from pipeline import run_all, log_audit, config, CFG
from learning import load_calibrator, retune
import llm

STATE = {"overrides": [], "history": []}

def build_queue():
    th = config()["conf_threshold"]
    res = run_all("txt", threshold=th, audit=False)
    cal = load_calibrator()
    q = []
    today = date.today()
    for r in res:
        if r["outcome"] == "route_to_human":
            inv_date = None
            for c in r.get("checks", []):
                pass
            age = None
            item = dict(set_id=r["set_id"], reason_code=r["reason"][0],
                        reason=r["reason"][2], confidence=r["confidence"],
                        conf_calibrated=r.get("conf_gate", round(cal(r["confidence"]), 3)),
                        aging_days=(int(r["set_id"][-2:]) * 3) % 17 + 1)
            if llm.available():
                txt, meta = llm.complete(
                    "You explain, in ONE short plain-English sentence for an AP clerk, why an invoice "
                    "was routed to a human. Use only the given rule reason. No new facts.",
                    f"Rule reason: {r['reason'][0]} - {r['reason'][2]}",
                    cache_key="expl::" + r["reason"][0])
                if txt: item["plain"] = txt
            q.append(item)  # demo aging
    stats = {"total": len(res),
             "auto": sum(1 for r in res if r["outcome"] == "auto_approve"),
             "rejected": sum(1 for r in res if r["outcome"] == "reject"),
             "queued": len(q), "threshold": th}
    stats["stp"] = round(stats["auto"] / stats["total"], 3)
    return q, stats, res

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
        elif u.path == "/queue":
            q, stats, _ = build_queue()
            self._send(200, json.dumps(dict(queue=q, stats=stats, history=STATE["history"])).encode())
        elif u.path == "/llm_status":
            self._send(200, json.dumps(llm.status()).encode())
        elif u.path == "/audit":
            f = ROOT / "out/audit_log.jsonl"
            lines = f.read_text().strip().splitlines()[-25:] if f.exists() else []
            self._send(200, json.dumps([json.loads(l) for l in lines]).encode())
        else:
            self._send(404, b"{}")
    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if u.path == "/review":
            cal = load_calibrator()
            rec = dict(set_id=body["set_id"], outcome="approved" if body["action"] == "approve"
                       else "override_reject", reason=["human_review", body["action"],
                       body.get("note", "")], confidence=body.get("confidence", 0))
            log_audit(rec, "queue-ui", config()["conf_threshold"], actor="human")
            STATE["overrides"].append((cal(body.get("confidence", 0)),
                                       1 if body["action"] == "approve" else 0))
            self._send(200, b'{"ok": true}')
        elif u.path == "/retune":
            th0 = config()["conf_threshold"]
            th1 = retune(STATE["overrides"], th0, floor=0.30)
            json.dump({"conf_threshold": th1}, open(CFG, "w"))
            q, stats, _ = build_queue()
            STATE["history"].append(dict(ts=time.strftime("%H:%M:%S"), from_th=th0, to_th=th1,
                                         stp=stats["stp"]))
            self._send(200, json.dumps(dict(threshold=th1, stp=stats["stp"])).encode())
        else:
            self._send(404, b"{}")

if __name__ == "__main__":
    json.dump({"conf_threshold": 0.92}, open(CFG, "w"))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8780
    print(f"exception queue on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
