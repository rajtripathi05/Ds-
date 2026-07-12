"""Learning loop (LAW 3): overrides re-tune the confidence-gate threshold.
Rule: new threshold = the lowest calibrated confidence seen among CORRECTLY-approved
overrides, floored so that historical error among would-be-auto docs stays <= target_err.
Never touches matching rules — only the R8 gate."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def load_calibrator():
    d = json.load(open(ROOT / "out/calibrator.json"))
    import math
    return lambda c: 1 / (1 + math.exp(-(d["a"] * c + d["b"])))

def retune(override_samples, current_th, target_err=0.01, floor=0.55, max_step=0.06):
    """override_samples: list of (conf_calibrated, was_correct 0/1) from human reviews."""
    if not override_samples:
        return current_th
    ok = sorted(c for c, corr in override_samples if corr)
    if not ok:
        return current_th
    cand = max(floor, min(ok))                      # extend gate down to observed-safe conf
    below = [corr for c, corr in override_samples if c >= cand]
    err = 1 - (sum(below) / len(below)) if below else 0.0
    while err > target_err and cand < current_th:
        cand = min(cand + 0.05, current_th)
        below = [corr for c, corr in override_samples if c >= cand]
        err = 1 - (sum(below) / len(below)) if below else 0.0
    # gradual trust: never drop the gate by more than max_step per review round
    return round(min(max(cand, current_th - max_step), current_th), 3)
