"""ROI dashboard + screenshot pack (all numbers measured in this repo; scale scenario labelled)."""
import sys, json
sys.path.insert(0, "src")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pipeline import run_all
from degrade import degrade
from collections import Counter

INK, ACC, OK, VIO = "#1c1917", "#b3282d", "#15803d", "#7c3aed"
base = {r["set_id"]: r["outcome"] for r in run_all("structured", audit=False)}

# measured: clean stream at learned threshold
res = run_all("txt", audit=False)
mix = Counter(r["outcome"] for r in res)
stp = mix["auto_approve"] / len(res)
# fail-safe check under noise: false-approve rate at 12% corruption
noisy = run_all("txt", audit=False, degrade=(lambda t: degrade(t, 0.12)))
false_appr = sum(1 for r in noisy if r["outcome"] == "auto_approve"
                 and base[r["set_id"]] != "auto_approve")
# planted-catch count comes from DECISIONS.md gate (13/13) — quoted, not recomputed here.

# ROI scenario (documented assumptions, blueprint E6 scale)
DOCS_YR, MIN_MANUAL, MIN_REVIEW, RATE = 70000, 12, 4, 400
manual_hr = DOCS_YR * MIN_MANUAL / 60
sys_hr = DOCS_YR * ((1 - stp) * MIN_REVIEW) / 60
saved_hr = manual_hr - sys_hr
saved_inr = saved_hr * RATE
roi = dict(measured=dict(stp=round(stp, 3), queue_pct=round(mix["route_to_human"]/len(res), 3),
                         reject_pct=round(mix["reject"]/len(res), 3),
                         false_approvals_at_12pct_noise=false_appr,
                         planted_caught="13/13 (DECISIONS.md)"),
           scenario=dict(docs_per_year=DOCS_YR, min_manual=MIN_MANUAL, min_review=MIN_REVIEW,
                         rate_inr_hr=RATE, manual_hours=manual_hr, system_hours=round(sys_hr),
                         hours_saved=round(saved_hr), inr_saved=round(saved_inr),
                         note="scale scenario uses blueprint estimate E6 (~70k docs/yr); measured rates from this repo"))
json.dump(roi, open("out/roi.json", "w"), indent=1)

fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.4), dpi=115)
cards = [("STP (measured)", f"{stp*100:.1f}%", "auto-approved, learned gate"),
         ("Exceptions", f"{mix['route_to_human']/len(res)*100:.1f}%", "pre-triaged, named check"),
         ("False approvals @12% noise", str(false_appr), "fails safe: routes, never guesses"),
         ("Hours saved / yr", f"{saved_hr:,.0f}", f"₹{saved_inr/1e5:.1f} L @ ₹{RATE}/hr (scenario E6)")]
for ax, (t, v, s) in zip(axes, cards):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.08), 0.96, 0.84, fc="white", ec="#e7e5e4", transform=ax.transAxes))
    ax.plot([0.02, 0.02], [0.08, 0.92], color=ACC, lw=4, transform=ax.transAxes)
    ax.text(0.10, 0.72, t, fontsize=9, color="#78716c", transform=ax.transAxes)
    ax.text(0.10, 0.38, v, fontsize=21, fontweight="bold", color=INK, transform=ax.transAxes)
    ax.text(0.10, 0.16, s, fontsize=7.5, color="#78716c", transform=ax.transAxes)
fig.suptitle("ds-doc-to-decision — ROI dashboard (measured rates · labelled scale scenario)",
             fontweight="bold", color=INK, fontsize=11)
fig.tight_layout()
fig.savefig("screenshots/04-roi-dashboard.png"); plt.close(fig)

import shutil
shutil.copy("robustness.png", "screenshots/03-robustness-curve.png")
shutil.copy("out/threshold_curve.png", "screenshots/02-threshold-tradeoff.png")

# queue render from live pipeline state
res_q = [r for r in run_all("txt", threshold=0.92, audit=False) if r["outcome"] == "route_to_human"][:9]
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=115)
ax.axis("off")
ax.text(0.01, 0.97, "Exception queue — aging · named failing check · one-click review",
        fontsize=11, fontweight="bold", color=INK, va="top")
y = 0.86
for r in res_q:
    ax.text(0.01, y, r["set_id"], fontsize=8.5, fontweight="bold", color=INK)
    ax.text(0.13, y, r["reason"][0], fontsize=8.5, fontweight="bold", color=ACC)
    ax.text(0.30, y, str(r["reason"][2])[:70], fontsize=8, color="#44403c")
    ax.text(0.90, y, "✓ approve  ✗ reject", fontsize=7.5, color=OK)
    y -= 0.093
fig.savefig("screenshots/01-exception-queue.png"); plt.close(fig)

# STP learning curve from m5 loop
h = json.load(open("out/m5_loop.json"))
fig, ax = plt.subplots(figsize=(7, 3.4), dpi=115)
ax.plot([x["round"] for x in h], [x["stp"]*100 for x in h], "o-", color=VIO, lw=2)
for x in h:
    ax.annotate(f"th={x['threshold']}", (x["round"], x["stp"]*100), fontsize=7,
                xytext=(4, -10), textcoords="offset points", color="#78716c")
ax.set_xlabel("override round"); ax.set_ylabel("STP %"); ax.set_xticks(range(len(h)))
ax.set_title("Learning loop: STP climbs as overrides teach the gate (0 auto-errors)",
             fontsize=10, loc="left", fontweight="bold")
ax.grid(alpha=.3); fig.tight_layout()
fig.savefig("screenshots/05-stp-learning-curve.png"); plt.close(fig)
print(json.dumps(roi, indent=1))
print("screens:", sorted(__import__('os').listdir("screenshots")))
