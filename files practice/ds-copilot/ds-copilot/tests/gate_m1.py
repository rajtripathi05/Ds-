import sys, json
sys.path.insert(0, "src")
from answer import answer

r = answer("How many Earned Leave days do employees get per year now (mid-2025)?", "ops")
checks = [
    ("answers 22 days", "22 days" in r["answer"]),
    ("resolves to 2025 policy", "[hr-leave-policy-2025]" in r["citations"]),
    ("cites the superseded 2023 version too", "[hr-leave-policy-2023]" in r["citations"]),
    ("supersede note present", "supersede" in r["answer"].lower()),
    ("visible retrieval trace", r["trace"][0][0] == "search_docs"),
]
r2 = answer("What is the moon made of?", "ops")
checks.append(("out-of-corpus → honest no-citation reply",
               "can't find" in r2["answer"] and not r2["citations"]))
ok = all(c[1] for c in checks)
for n, p in checks: print(("✅" if p else "❌"), n)
json.dump({"answer": r["answer"], "citations": r["citations"]},
          open("out/m1_version_conflict.json", "w"), indent=1)
print("M1 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
