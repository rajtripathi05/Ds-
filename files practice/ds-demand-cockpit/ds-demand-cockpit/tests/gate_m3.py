import sys
sys.path.insert(0, "src")
import numpy as np, pandas as pd
from features import build_panel
from causal import uplift_study, category_recovery

TOL = 20.0   # % relative error per category
panel, fr, _ = build_panel()
df, roi = uplift_study(panel, fr["promo"], fr["product"], fr["costs"])
rec = category_recovery(df, fr["product"])
print(rec.to_string(index=False))
print(f"\npromo-week observations used: {len(df)} (festival/overlap-confounded excluded)")
roi_s = roi.sort_values("roi", ascending=False)
print("\nTop-3 promo ROI:\n", roi_s.head(3).to_string(index=False))
print("\nBottom-3 promo ROI:\n", roi_s.tail(3).to_string(index=False))
rec.to_csv("out/plan/m3_elasticity_recovery.csv", index=False)
roi.to_csv("out/plan/m3_promo_roi.csv", index=False)
ok = bool((rec["rel_err_pct"] <= TOL).all())
worst = rec.loc[rec["rel_err_pct"].idxmax()]
open("out/plan/m3_causal.md", "w").write(
    "# M3 — causal promo uplift (measured)\n\n" + rec.to_markdown(index=False) +
    f"\n\nTolerance: |recovered−true|/true ≤ {TOL}% per category → "
    f"{'GREEN' if ok else 'RED'} (worst: {worst['category']} {worst['rel_err_pct']}%)\n"
    f"\nMethod: matched non-promo/non-festival controls within ±6 weeks, seasonality-adjusted, "
    f"median across ≥2 controls; {len(df)} promo-week cells; distributor-scoped promos analysed "
    f"in their zone; ROI in ₹ from sku_costs (promo funding = 0.4×depth price cut per data contract).\n"
    f"\nPromo ROI: median {roi['roi'].median():.2f}, {int((roi['roi']>1).sum())}/{len(roi)} promos ROI>1 "
    f"— full table in m3_promo_roi.csv\n")
print("\nM3 GATE:", "GREEN" if ok else "RED", f"(tolerance {TOL}%)")
sys.exit(0 if ok else 1)
