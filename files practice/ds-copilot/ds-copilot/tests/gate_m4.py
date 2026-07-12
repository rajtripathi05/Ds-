import sys, os, json
sys.path.insert(0, "src")
from pathlib import Path as _P; os.environ.setdefault("DSCOPILOT_DB", str(_P(__file__).resolve().parents[1] / "out" / "copilot.db"))
from planner import ask
from retrieve import Index
from sqlgen import run_sql
import re

FIN_PAT = re.compile(r"margin|₹2[01]\.|unit_cogs|roi|18-24|10-21|dist_price|price_realized", re.I)
q = "What is the distributor margin on Confectionery?"
re_exec = ask(q, "exec")
re_ops = ask(q, "ops")
checks = [
    ("exec gets the margin answer (10% of MRP)", "10%" in re_exec["answer"] and not re_exec["refused"]),
    ("exec cites the exec-only memo", "[fin-margin-structure-memo]" in re_exec["citations"]),
    ("ops is refused with a reason", re_ops["refused"] or "can't find" in re_ops["answer"]),
    ("ops answer contains zero financial specifics", not FIN_PAT.search(re_ops["answer"]) or "REFUSE" in re_ops["answer"]),
]
# layer 1: retrieval index for ops must not contain exec docs at all
idx = Index("ops")
checks.append(("retrieval layer: exec docs absent from ops index",
               "fin-margin-structure-memo" not in idx.docs and "fin-distributor-roi-note" not in idx.docs))
# layer 2: SQL column policy
_, e = run_sql("SELECT mfr_gross_margin_pct FROM sku_costs", "ops")
checks.append(("SQL layer: exec column denied for ops", e is not None))
r_ok, e_ok = run_sql("SELECT mfr_gross_margin_pct FROM sku_costs LIMIT 3", "exec")
checks.append(("SQL layer: same column fine for exec", e_ok is None and len(r_ok["rows"]) == 3))
ok = all(c[1] for c in checks)
for n, p in checks: print(("✅" if p else "❌"), n)
json.dump({"exec_answer": re_exec["answer"][:200], "ops_answer": re_ops["answer"][:200],
           "checks": [(n, bool(p)) for n, p in checks]}, open("out/m4_gate.json", "w"), indent=1)
print("M4 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
