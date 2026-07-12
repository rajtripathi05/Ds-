"""M3 SCORING (the only place ground truth is read — no-peek gate protects src/).
(a) structured path: 40/40 vs ground truth + 13/13 planted caught; (b) PDF path delta, honest."""
import sys, json, csv
sys.path.insert(0, "src")
from pipeline import run_all
from collections import Counter

_rows = list(csv.DictReader(open("data/ground_truth_labels.csv")))
_labcol = next(c for c in _rows[0] if c != "set_id" and "reason" not in c.lower())
gt = {r["set_id"]: r[_labcol] for r in _rows}
planted = list(csv.DictReader(open("data/planted_discrepancies.csv")))

res_s = {r["set_id"]: r for r in run_all("structured", audit=False)}
match = sum(1 for s, lab in gt.items() if res_s[s]["outcome"] == lab)
mism = [(s, lab, res_s[s]["outcome"], res_s[s]["reason"]) for s, lab in gt.items()
        if res_s[s]["outcome"] != lab]

# planted catch: each planted row names a set + issue; caught if that set's non-pass checks
# include the matching rule family (or outcome matches expected severity)
fam = {"qty": "R2", "price": "R3", "grn": "R1", "coa": "R5", "cert": "R5", "duplicate": "R6",
       "arithmetic": "R7", "math": "R7", "date": "R4"}
caught, missed = 0, []
for p in planted:
    sid = p.get("set_id") or p.get("set") or p.get("keys", "")
    issue = (p.get("discrepancy_type") or p.get("issue") or p.get("type") or "").lower()
    rule = next((v for k, v in fam.items() if k in issue), None)
    rec = res_s.get(sid)
    if rec is None:
        missed.append((sid, issue, "set not found")); continue
    fired = [c[0] for c in rec["checks"] if c[1] != "pass"] + [rec["reason"][0]]
    ok = any(f.startswith(rule) for f in fired) if rule else rec["outcome"] != "auto_approve"
    caught += ok
    if not ok: missed.append((sid, issue, fired))

res_p = {r["set_id"]: r for r in run_all("pdf", audit=False)}
match_p = sum(1 for s, lab in gt.items() if res_p[s]["outcome"] == lab)
delta = [(s, lab, res_p[s]["outcome"]) for s, lab in gt.items() if res_p[s]["outcome"] != lab]

lines = ["# DECISIONS.md — scored runs (measured)", "",
         f"## (a) Structured-JSON path: **{match}/40** vs ground truth · planted caught: **{caught}/{len(planted)}**",
         ""]
if mism:
    lines += ["Mismatches:"] + [f"- {s}: truth={t} got={o} reason={r}" for s, t, o, r in mism]
if missed:
    lines += ["Planted missed:"] + [f"- {m}" for m in missed]
lines += ["", f"## (b) End-to-end PDF path: **{match_p}/40** (delta vs structured: {match - match_p})", ""]
if delta:
    lines += ["PDF-path differences:"] + [f"- {s}: truth={t} got={o}" for s, t, o in delta]
else:
    lines += ["No differences — extraction quality carried the full decision set."]
lines += ["", f"Outcome mix (structured): {dict(Counter(r['outcome'] for r in res_s.values()))}"]
open("DECISIONS.md", "w").write("\n".join(lines))
print("\n".join(lines[:14]))
ok = (match == 40 and caught == len(planted))
print("M3 GATE:", "GREEN" if ok else "RED", f"(structured {match}/40, planted {caught}/{len(planted)}, pdf {match_p}/40)")
sys.exit(0 if ok else 1)
