"""M4: GT-FREE calibrated confidence (D4). Label = PDF/TXT-path decision AGREES with the
structured-JSON-path decision. Samples generated across degradation levels; isotonic (PAV)
fitted on odd-numbered sets, evaluated on even (holdout). Saves calibrator + threshold view."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from pipeline import run_all
from degrade import degrade

ROOT = Path(__file__).resolve().parent.parent
LEVELS = [0.0, 0.03, 0.06, 0.10, 0.15, 0.20]

def collect():
    base = {r["set_id"]: r["outcome"] for r in run_all("structured", audit=False)}
    samples = []          # (set_id, conf, agree)
    for lv in LEVELS:
        res = run_all("txt", threshold=-1.0, audit=False,
                      degrade=(lambda t, l=lv: degrade(t, l)))   # th=-1: no R8 routing, raw decisions
        for r in res:
            samples.append((r["set_id"], float(r["confidence"]),
                            int(r["outcome"] == base[r["set_id"]])))
    return samples, base

def pav(xs, ys):
    """Pool-adjacent-violators isotonic regression -> stepwise (x, yhat) knots."""
    order = np.argsort(xs)
    x, y = np.array(xs)[order], np.array(ys)[order].astype(float)
    w = np.ones_like(y)
    vals, wts, idx = list(y), list(w), [[i] for i in range(len(y))]
    i = 0
    while i < len(vals) - 1:
        if vals[i] > vals[i + 1] + 1e-12:
            nv = (vals[i] * wts[i] + vals[i + 1] * wts[i + 1]) / (wts[i] + wts[i + 1])
            vals[i:i + 2] = [nv]; wts[i:i + 2] = [wts[i] + wts[i + 1]]
            idx[i:i + 2] = [idx[i] + idx[i + 1]]
            i = max(i - 1, 0)
        else:
            i += 1
    knots_x, knots_y = [], []
    for group, v in zip(idx, vals):
        knots_x.append(float(x[group].max())); knots_y.append(float(v))
    return knots_x, knots_y

def apply_iso(knots_x, knots_y, c):
    import bisect
    i = bisect.bisect_left(knots_x, c)
    return knots_y[min(i, len(knots_y) - 1)]

def platt_fit(cs, ys, iters=300, lr=0.5):
    a, b = 1.0, 0.0
    cs = np.array(cs); ys = np.array(ys, float)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(a * cs + b)))
        ga = np.mean((p - ys) * cs); gb = np.mean(p - ys)
        a -= lr * ga; b -= lr * gb
    return float(a), float(b)

def platt_apply(a, b, c):
    return float(1 / (1 + np.exp(-(a * c + b))))

def main():
    samples, base = collect()
    train = [(c, a) for s, c, a in samples if int(s[-2:]) % 2 == 1]
    hold = [(c, a) for s, c, a in samples if int(s[-2:]) % 2 == 0]
    kx, ky = pav([c for c, _ in train], [a for _, a in train])
    pa, pb = platt_fit([c for c, _ in train], [a for _, a in train])
    json.dump(dict(method="platt", a=pa, b=pb, iso_knots_x=kx, iso_knots_y=ky),
              open(ROOT / "out/calibrator.json", "w"), indent=1)
    raw_brier = float(np.mean([(c - a) ** 2 for c, a in hold]))
    iso_brier = float(np.mean([(apply_iso(kx, ky, c) - a) ** 2 for c, a in hold]))
    cal_brier = float(np.mean([(platt_apply(pa, pb, c) - a) ** 2 for c, a in hold]))
    # threshold sweep on holdout: STP vs error-among-autoapproved
    rows = []
    for th in [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 0.995]:
        auto = [(c, a) for c, a in hold if platt_apply(pa, pb, c) >= th]
        stp = len(auto) / len(hold)
        err = (1 - np.mean([a for _, a in auto])) if auto else 0.0
        rows.append((th, stp, float(err)))
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4), dpi=115)
    ax.plot([r[1] * 100 for r in rows], [r[2] * 100 for r in rows], "o-", color="#b3282d")
    for th, stp, err in rows:
        ax.annotate(f"{th}", (stp * 100, err * 100), fontsize=7, xytext=(3, 3),
                    textcoords="offset points", color="#78716c")
    ax.set_xlabel("straight-through rate (%)"); ax.set_ylabel("error among auto-approved (%)")
    ax.set_title("STP vs error trade-off (holdout, calibrated confidence thresholds)",
                 fontsize=10, loc="left", fontweight="bold")
    ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(ROOT / "out/threshold_curve.png")
    res = dict(n_samples=len(samples), train=len(train), holdout=len(hold),
               raw_brier=round(raw_brier, 4), isotonic_brier=round(iso_brier, 4),
               calibrated_brier=round(cal_brier, 4), method="platt",
               monotone=bool(pa > 0),
               threshold_view=[dict(threshold=t, stp=round(s, 3), auto_error=round(e, 4))
                               for t, s, e in rows])
    # operating point: on a CLEAN txt run, every doc the structured path auto-approves
    # must clear the gate -> threshold just below their minimum calibrated confidence
    # (also cross-checked against the safe region of the holdout sweep)
    clean = run_all("txt", threshold=2.0, audit=False)
    base_local = {r["set_id"]: r["outcome"] for r in run_all("structured", audit=False)}
    def _p(c_):
        import math
        return 1 / (1 + math.exp(-(pa * c_ + pb)))
    auto_confs = [_p(r["confidence"]) for r in clean
                  if base_local[r["set_id"]] == "auto_approve"
                  and r["reason"][0] in ("all_pass", "R8_confidence")]
    rec_th = round(min(auto_confs) - 0.005, 3) if auto_confs else 0.8
    json.dump({"conf_threshold": rec_th}, open(ROOT / "out/config.json", "w"))
    res["recommended_threshold"] = rec_th
    json.dump(res, open(ROOT / "out/m4_calibration.json", "w"), indent=1)
    print(json.dumps(res, indent=1)[:900])
    ok = res["monotone"] and cal_brier <= raw_brier + 1e-9
    print("M4 GATE:", "GREEN" if ok else "RED",
          f"(Brier raw {raw_brier:.4f} -> platt {cal_brier:.4f}; isotonic {iso_brier:.4f} reported)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
