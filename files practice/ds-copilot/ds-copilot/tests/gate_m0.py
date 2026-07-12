import sys, json, os
sys.path.insert(0, "src")
from pathlib import Path as _P; os.environ.setdefault("DSCOPILOT_DB", str(_P(__file__).resolve().parents[1] / "out" / "copilot.db"))
from corpus import load_corpus
from db import build, TABLES

docs, chunks, vm = load_corpus()
checks = []
checks.append(("24 docs parsed", len(docs) == 24))
tags = {d["access"] for d in docs.values()}
checks.append(("access tags parsed (all/exec_only)", tags == {"all", "exec_only"}))
exec_ids = sorted(d["doc_id"] for d in docs.values() if d["access"] == "exec_only")
checks.append(("2 exec-only docs (margin memo + ROI note)",
               exec_ids == ["fin-distributor-roi-note", "fin-margin-structure-memo"]))
checks.append(("leave-policy version family detected",
               any(v["newest"] == "hr-leave-policy-2025" for v in vm.values())))
c = build()
checks.append(("db built: 7 tables", len(c) == 7))
checks.append(("sales_secondary = 297,610 rows", c["sales_secondary"] == 297610))
ok = all(x[1] for x in checks)
for n, p in checks: print(("✅" if p else "❌"), n)
json.dump({"checks": [(n, bool(p)) for n, p in checks], "table_counts": c},
          open("out/m0_manifest_gate.json", "w"), indent=1)
print("M0 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
