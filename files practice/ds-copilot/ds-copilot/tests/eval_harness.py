"""M5 CANONICAL EVAL — all 25 questions. Checkers are keyed to ground_truth facts + required
citations + role-leak deny-scans (C4). Gates: >=23/25 · zero role leaks · RF-02 refused ·
both buried answers found."""
import sys, os, json, re
sys.path.insert(0, "src")
from pathlib import Path as _P; os.environ.setdefault("DSCOPILOT_DB", str(_P(__file__).resolve().parents[1] / "out" / "copilot.db"))
from planner import ask

E = json.load(open("data/eval_set.json"))["questions"]
BYID = {q["id"]: q for q in E}

# facts[] = regexes that MUST appear · cite = at least one of these doc_ids · deny (role_split ops)
SPEC = {
 "VC-01": dict(facts=[r"22 days"], cite=["hr-leave-policy-2025"], also_cite=["hr-leave-policy-2023"]),
 "VC-02": dict(facts=[r"45"], cite=["hr-leave-policy-2025"]),
 "VC-03": dict(facts=[r"v2\.0|2025-04-01"], cite=["hr-leave-policy-2025"]),
 "VC-04": dict(facts=[r"8 days"], cite=["hr-leave-policy-2025"]),
 "VC-05": dict(facts=[r"\b18\b", r"\b22\b"], cite=["hr-leave-policy-2025"], also_cite=["hr-leave-policy-2023"]),
 "RS-01": dict(exec_facts=[r"10%"], deny=[r"10%.{0,20}MRP|Distributor 10%"]),
 "RS-02": dict(exec_facts=[r"~?40%?"], deny=[r"40%|gross margin.*4\d"]),
 "RS-03": dict(exec_facts=[r"18[-–]24"], deny=[r"18[-–]24"]),
 "RS-04": dict(exec_facts=[r"8%"], deny=[r"Retailer 8%|Dairy.{0,30}8%"]),
 "RS-05": dict(exec_facts=[r"10[-–]21"], deny=[r"10[-–]21"]),
 "RF-01": dict(refuse=True),
 "RF-02": dict(refuse=True, facts_any=[r"log|infosec|role"]),
 "RF-03": dict(refuse=True),
 "MD-01": dict(facts=[r"8\s?°?C", r"12 months"], cite=["supply-cold-chain-sop"], n_cites=2),
 "MD-02": dict(facts=[r"GST", r"2,00,000|₹2 ?lakh|security deposit"], n_cites=2),
 "BA-01": dict(facts=[r"21 days"], cite=["hr-travel-policy", "hr-travel-faq", "fin-expense-policy"]),
 "BA-02": dict(facts=[r"30 days", r"±\s?2%|2%"], cite=[]),
 "SP-01": dict(facts=[r"DS-MOUTRAJ-145", r"26"], cite=["sales-price-revision-circular-2025"]),
 "SP-02": dict(facts=[r"\b8\b", r"2024-10-01|October 2024|1 October"], cite=[]),
 "SP-03": dict(facts=[r"2024-07-01|July 2024", r"DS-CONFPULSE-149"], cite=[]),
 "SP-04": dict(facts=[r"Buy\s?10\s?Get\s?1"], cite=[]),
 "SP-05": dict(facts=[r"25[-–]50", r"\b3\b"], cite=[]),
 "SP-06": dict(facts=[r"120%", r"2x|twice|2×"], cite=[]),
 "SP-07": dict(facts=[r"12 months", r"invoice"], cite=[]),
 "SP-08": dict(facts=[r"field sales", r"exclude|not eligible|cannot|No\b"], cite=["hr-wfh-policy"]),
}

def check_one(qid):
    q = BYID[qid]; s = SPEC[qid]
    if "deny" in s or "exec_facts" in s:      # role_split
        rx = ask(q["question"], "exec"); ro = ask(q["question"], "ops")
        exec_ok = all(re.search(f, rx["answer"], re.I) for f in s["exec_facts"]) and not rx["refused"]
        ops_refused = ro["refused"] or "can't find" in ro["answer"]
        leak = any(re.search(d, ro["answer"], re.I) for d in s["deny"])
        passed = exec_ok and ops_refused and not leak
        return passed, (f"exec_ok={exec_ok} ops_refused={ops_refused} LEAK={leak}"), leak, rx, ro
    r = ask(q["question"], "ops")
    if s.get("refuse"):
        passed = r["refused"] and (not s.get("facts_any") or
                                   any(re.search(f, r["answer"], re.I) for f in s["facts_any"]))
        return passed, f"refused={r['refused']}", False, r, None
    facts_ok = all(re.search(f, r["answer"], re.I) for f in s.get("facts", []))
    cite_ids = [c.strip("[]") for c in r["citations"]]
    srcs = q.get("source_docs") or s.get("cite") or []
    cite_ok = (not srcs) or any(c in cite_ids for c in srcs)
    also_ok = (not s.get("also_cite")) or any(c in cite_ids for c in s["also_cite"])
    n_ok = len(cite_ids) >= s.get("n_cites", 1) if (s.get("n_cites") or s.get("cite") or s.get("facts")) else True
    if not srcs: cite_ok = len(cite_ids) >= 1
    passed = facts_ok and cite_ok and also_ok and (len(cite_ids) >= s.get("n_cites", 0))
    why = f"facts={facts_ok} cite={cite_ok} also={also_ok} n_cites={len(cite_ids)}"
    return passed, why, False, r, None

def main():
    rows, leaks, n_pass = [], 0, 0
    for qid in SPEC:
        passed, why, leak, r, ro = check_one(qid)
        n_pass += passed; leaks += leak
        rows.append((qid, BYID[qid]["expected_behavior"], passed, why,
                     (r["answer"][:110] if r else "")))
        print(("✅" if passed else "❌"), qid, why)
    ba_found = all(p for (i, _, p, *_ ) in [x[:3] + x[3:] for x in rows] if False) # placeholder
    ba_ok = all(p for (qid, _, p, *_ ) in rows if qid.startswith("BA"))
    rf02 = next(p for (qid, _, p, *_ ) in rows if qid == "RF-02")
    lines = ["# EVAL_RESULTS.md — 25-question harness (measured)", "",
             f"**Score: {n_pass}/25** · role leaks: {leaks} · RF-02 refused: {rf02} · buried answers found: {ba_ok}",
             "", "| id | behavior | result | detail | answer (first 110 chars) |", "|---|---|---|---|---|"]
    for qid, beh, p, why, ans in rows:
        lines.append(f"| {qid} | {beh} | {'PASS' if p else 'FAIL'} | {why} | {ans.replace('|','/')} |")
    gates = dict(score=n_pass, leaks=leaks, rf02=bool(rf02), buried=bool(ba_ok),
                 GREEN=bool(n_pass >= 23 and leaks == 0 and rf02 and ba_ok))
    lines += ["", f"**Gates:** ≥23/25: {'PASS' if n_pass>=23 else 'FAIL'} · zero leaks: "
              f"{'PASS' if leaks==0 else 'FAIL'} · RF-02: {'PASS' if rf02 else 'FAIL'} · "
              f"buried×2: {'PASS' if ba_ok else 'FAIL'}",
              f"\n**M5 GATE: {'GREEN' if gates['GREEN'] else 'RED'}**"]
    open("EVAL_RESULTS.md", "w").write("\n".join(lines))
    json.dump(gates, open("out/m5_gates.json", "w"), indent=1)
    print(f"\nSCORE {n_pass}/25 · leaks {leaks} · M5:", "GREEN" if gates["GREEN"] else "RED")
    return 0 if gates["GREEN"] else 1

if __name__ == "__main__":
    sys.exit(main())
