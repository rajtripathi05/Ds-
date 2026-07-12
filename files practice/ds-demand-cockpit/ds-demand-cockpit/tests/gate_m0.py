"""M0 gate: clean AND messy loads succeed; every planted issue class caught with matching keys."""
import sys, json
sys.path.insert(0, "src")
from loaders import load_all
import pandas as pd

frames_c, rep_c = load_all(messy=False)
assert len(frames_c["secondary"]) == 297610, f"clean fact rows {len(frames_c['secondary'])}"
frames_m, rep_m = load_all(messy=True)

planted = pd.read_csv("data/planted_data_quality_issues.csv")
caught = rep_m.issues
def caught_for(substr):
    return [c for c in caught if substr in c["issue"]]

checks = []
# 1 missing dist_price keys
want = set("DS-BEVECAT-098 DS-SPICKEW-009 DS-CONFFRU-026".split())
got = set(); [got.update(c["keys"].split("; ")) for c in caught_for("missing dist_price")]
checks.append(("missing dist_price (3 SKUs)", want <= got, sorted(got)))
# 2 #N/A literal
got2 = set(); [got2.update(c["keys"].split("; ")) for c in caught_for("non-numeric literal")]
checks.append(("#N/A literal in mrp (DS-BEVECAT-006)", "DS-BEVECAT-006" in got2, sorted(got2)))
# 3 unit mismatch
want3 = set("DS-CONFPULSE-001 DS-SPICCAT-003 DS-DAIRKSH-004".split())
got3 = set(); [got3.update(c["keys"].split("; ")) for c in caught_for("unit mismatch")]
checks.append(("unit mismatch g-as-kg (3 SKUs)", want3 <= got3, sorted(got3)))
# 4 duplicate PK
got4 = set(); [got4.update(c["keys"].split("; ")) for c in caught_for("duplicate distributor_code")]
checks.append(("duplicate distributor_code (DIST-NO-001)", "DIST-NO-001" in got4, sorted(got4)))
# 5 mixed dates: 2976 rows
n5 = sum(c["n"] for c in caught_for("mixed date format"))
checks.append(("mixed date format 2,976 rows", n5 == 2976, [n5]))
# never-fatal: messy fact table loads to same row count (all rows recovered)
checks.append(("messy fact rows fully recovered", len(frames_m["secondary"]) == 297610,
               [len(frames_m["secondary"])]))

ok = all(c[1] for c in checks)
lines = ["# M0 gate — caught vs planted (messy set)", "",
         "| planted issue | caught? | evidence |", "|---|---|---|"]
for name, passed, ev in checks:
    lines.append(f"| {name} | {'✅' if passed else '❌'} | {ev} |")
lines += ["", f"Catch rate: {sum(c[1] for c in checks)-1}/5 planted classes"
          f" + never-fatal check · badges: {rep_m.badges}",
          "", "Raw report:", "```json", json.dumps(rep_m.to_json(), indent=1), "```"]
open("out/plan/m0_caught_vs_planted.md", "w").write("\n".join(lines))
print("\n".join(lines[:12]))
print("M0 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
