"""M6: degrade text at increasing intensity -> field accuracy + decision agreement curves.
Scoring only (invoice.json + structured reference); decision path untouched."""
import sys, json
sys.path.insert(0, "src")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from loaders import load_set, all_sets
from extract import parse_invoice_text
from degrade import degrade
from pipeline import run_all

LEVELS = [0.0, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25]
base = {r["set_id"]: r["outcome"] for r in run_all("structured", audit=False)}

acc_curve, agree_curve = [], []
for lv in LEVELS:
    ok = n = 0
    res = run_all("txt", audit=False, degrade=(lambda t, l=lv: degrade(t, l)))
    agree = sum(1 for r in res if r["outcome"] == base[r["set_id"]]) / len(res)
    for sid in all_sets():
        st = load_set(sid)
        f = parse_invoice_text(degrade(st["txt"], lv))
        inv = st["invoice"]
        gt = inv.get("gst"); gt = round(sum(gt.values()), 2) if isinstance(gt, dict) else gt
        for k, tv in (("subtotal", inv["subtotal"]), ("gst", gt), ("grand_total", inv["grand_total"])):
            n += 1
            ev = f.get(k)
            ok += ev is not None and abs(float(ev) - float(tv)) <= 0.01
    acc_curve.append(ok / n); agree_curve.append(agree)
    print(f"noise {lv:.2f}: amount accuracy {ok/n:.2%} · decision agreement {agree:.2%}")

fig, ax = plt.subplots(figsize=(7.5, 4), dpi=115)
ax.plot([l*100 for l in LEVELS], [a*100 for a in acc_curve], "o-", color="#b3282d", label="amount-field accuracy")
ax.plot([l*100 for l in LEVELS], [a*100 for a in agree_curve], "s--", color="#1c1917", label="decision agreement vs structured")
ax.set_xlabel("text corruption intensity (%)"); ax.set_ylabel("%")
ax.set_title("Robustness: accuracy vs corruption (D3 text-domain degradation)", fontsize=10, loc="left", fontweight="bold")
ax.grid(alpha=.3); ax.legend(frameon=False, fontsize=8); fig.tight_layout()
fig.savefig("robustness.png")
json.dump(dict(levels=LEVELS, amount_acc=acc_curve, agreement=agree_curve),
          open("out/m6_robustness.json", "w"), indent=1)
ok = acc_curve[0] >= 0.995 and agree_curve[0] == 1.0 and acc_curve[-1] < acc_curve[0]
print("M6 ROBUSTNESS GATE:", "GREEN" if ok else "RED",
      "(clean=100%, curve degrades measurably -> honest sensitivity shown)")
sys.exit(0 if ok else 1)
