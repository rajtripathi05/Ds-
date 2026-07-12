"""End-to-end: load -> normalize (structured | txt | pdf) -> rules -> decision + audit.
The ONLY writer of out/decisions_*.json and out/audit_log.jsonl."""
import json, time, hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from loaders import load_set, all_sets
from extract import extract_set
from match import run_checks, decide

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "out" / "config.json"

def config():
    if CFG.exists():
        return json.load(open(CFG))
    return {"conf_threshold": 0.90}

def normalize_structured(inv):
    gst = inv.get("gst")
    if isinstance(gst, dict):
        gst = round(sum(v for v in gst.values() if isinstance(v, (int, float))), 2)
    return dict(invoice_no=inv.get("invoice_no"), invoice_date=inv.get("invoice_date"),
                po_no=inv.get("po_no"), lines=inv.get("lines", []), subtotal=inv.get("subtotal"),
                gst=gst, grand_total=inv.get("grand_total"), coa=inv.get("coa"),
                _doc_conf=1.0, _conf={})

_CAL = None
def _cal():
    global _CAL
    if _CAL is None:
        f = ROOT / "out/calibrator.json"
        try:
            import math
            d = json.load(open(f))
            a, b = float(d["a"]), float(d["b"])
            _CAL = lambda c: 1 / (1 + math.exp(-(a * c + b)))
        except Exception:
            _CAL = lambda c: c          # missing/corrupt calibrator -> identity (never fatal)
    return _CAL

def run_all(source="structured", threshold=None, audit=True, degrade=None):
    th = threshold if threshold is not None else config()["conf_threshold"]
    seen = {}
    out = []
    for sid in all_sets():
        st = load_set(sid)
        if source == "structured":
            inv = normalize_structured(st["invoice"])
        else:
            if degrade and st.get("txt"):
                st = dict(st, txt=degrade(st["txt"]))
            inv = extract_set(st, source)
        if inv.get("_unreadable"):
            rec = dict(set_id=sid, outcome="route_to_human",
                       reason=["unreadable", "route_to_human", "document unreadable -> human queue (LAW 4)"],
                       checks=[], confidence=0.0)
        else:
            checks = run_checks(inv, st["po"], st["grn"], seen)
            # gate on CALIBRATED confidence for extracted sources; structured is exact (1.0)
            gate_conf = inv["_doc_conf"] if source == "structured" else _cal()(inv["_doc_conf"])
            outcome, reason, fails = decide(checks, gate_conf, th)
            rec = dict(set_id=sid, outcome=outcome, reason=list(reason),
                       checks=[list(c) for c in checks], confidence=inv["_doc_conf"],
                       conf_gate=round(gate_conf, 3), invoice_no=inv.get("invoice_no"))
            ino = inv.get("invoice_no")
            if ino and ino not in seen:
                seen[ino] = sid
        out.append(rec)
        if audit:
            log_audit(rec, source, th)
    (ROOT / "out").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / f"out/decisions_{source}.json", "w"), indent=1)
    return out

def log_audit(rec, source, th, actor="system"):
    entry = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S"), source=source, actor=actor,
                 threshold=th, **{k: rec[k] for k in ("set_id", "outcome", "reason", "confidence")})
    entry["checks_fired"] = [c[0] for c in rec.get("checks", []) if c[1] != "pass"]
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:16]
    with open(ROOT / "out/audit_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "structured"
    res = run_all(src)
    from collections import Counter
    print(src, Counter(r["outcome"] for r in res))
