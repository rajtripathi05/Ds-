"""M5 learning-loop gate: STP rises across >=3 override rounds with ZERO auto-approve errors
(reference = structured-path outcomes; GT files untouched). Measured, deterministic."""
import sys, json
sys.path.insert(0, "src")
from pipeline import run_all
from degrade import degrade
from learning import load_calibrator, retune

# Realistic stream: 70% of documents arrive clean, 30% with OCR-grade corruption (D3).
# Clean docs pass checks with high extraction confidence; the loop must LEARN that those
# confidences are trustworthy and extend the auto gate — that is the kickoff's STP climb.
cal = load_calibrator()
base = {r["set_id"]: r["outcome"] for r in run_all("structured", audit=False)}

def mixed_degrade(rnd):
    def f(text):
        import zlib as _z
        clean = (_z.crc32(text[:40].encode()) % 10) < 7        # deterministic 70/30 split
        return text if clean else degrade(text, 0.05, seed=rnd)
    return f

th = 0.92                      # conservative start (D5, on calibrated prob)
overrides = []                 # accumulated (conf_cal, was_correct)
history = []
for rnd in range(4):
    res = run_all("txt", threshold=2.0, audit=False,       # th=2 -> nothing auto: get raw checks
                  degrade=mixed_degrade(rnd))
    auto = routed = errors = 0
    for r in res:
        c = r.get("conf_gate", cal(r["confidence"]))
        checks_pass = r["reason"][0] in ("all_pass", "R8_confidence")
        if checks_pass and c >= th:
            auto += 1
            if r["outcome" ] != "auto_approve" and base[r["set_id"]] != "auto_approve":
                pass
            if base[r["set_id"]] != "auto_approve":
                errors += 1                                   # auto'd something rules should catch
        elif checks_pass:
            routed += 1                                       # queue -> human reviews
            correct = 1 if base[r["set_id"]] == "auto_approve" else 0
            overrides.append((c, correct))
        # non-pass outcomes (route/reject on real checks) are not STP candidates
    stp = auto / len(res)
    history.append(dict(round=rnd, threshold=th, auto=auto, routed_for_conf=routed,
                        stp=round(stp, 3), auto_errors=errors, n_overrides=len(overrides)))
    th = retune(overrides, th, floor=0.30)
json.dump(history, open("out/m5_loop.json", "w"), indent=1)
for h in history:
    print(h)
stps = [h["stp"] for h in history]
ok = (stps[-1] >= stps[0] + 0.25                 # climb >= 25pp (strengthened: a real climb)
      and stps[-1] >= 0.40                       # meaningful final STP
      and all(b >= a - 1e-9 for a, b in zip(stps, stps[1:]))
      and sum(h["auto_errors"] for h in history) == 0)
print("M5 LOOP GATE:", "GREEN" if ok else "RED",
      f"(STP {stps[0]:.0%} -> {stps[-1]:.0%} over {len(history)} rounds, 0 auto-errors: {sum(h['auto_errors'] for h in history)==0})")
sys.exit(0 if ok else 1)
