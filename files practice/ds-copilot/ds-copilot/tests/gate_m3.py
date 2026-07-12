import sys, os, json
sys.path.insert(0, "src")
from pathlib import Path as _P; os.environ.setdefault("DSCOPILOT_DB", str(_P(__file__).resolve().parents[1] / "out" / "copilot.db"))
from planner import ask
from pathlib import Path

r = ask("Why did North-zone Rajnigandha volumes drop in early 2025?", "ops")
tools = [t[0] for t in r["trace"]]
checks = [
    ("SQL tool used with visible trace", "run_sql" in tools),
    ("doc tool used with visible trace", "search_docs" in tools),
    ("price circular cited", "[sales-price-revision-circular-2025]" in r["citations"]),
    ("numeric data in answer", "[governed-db]" in r["answer"] and "%" in r["answer"]),
    ("chart rendered for numeric answer", r["chart"] and Path(r["chart"]).exists()),
]
ok = all(c[1] for c in checks)
for n, p in checks: print(("✅" if p else "❌"), n)
json.dump({"answer": r["answer"], "citations": r["citations"], "tools": tools,
           "chart": r["chart"]}, open("out/m3_gate.json", "w"), indent=1)
print("M3 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
