import sys, json
sys.path.insert(0, "src")
import numpy as np, pandas as pd
from features import build_panel
from backtest import assemble, choose_champions, forecast_all
from optimizer import prepare, solve, risk_lists

panel, fr, _ = build_panel()
series, weeks, months, fest, Y, PR, PX, catd, zoned = assemble(panel)
H = 4
# extend exogenous arrays 4 weeks beyond history (Jan-2026: months known; festivals unknown->0;
# price carried forward; no promos scheduled -> 0; honest defaults, what-if levers change them)
ext_w = [pd.Timestamp(weeks[-1]) + pd.Timedelta(weeks=k) for k in range(1, H + 1)]
months_x = np.concatenate([months, [w.month for w in ext_w]])
fest_x = np.concatenate([fest, np.zeros(H)])
Y_x = np.concatenate([Y, np.full((len(series), H), np.nan)], 1)
PR_x = np.concatenate([PR, np.repeat(PR[:, -1:], H, 1)], 1)
PX_x = np.concatenate([PX, np.zeros((len(series), H))], 1)
origin = len(weeks) - 1
champ = choose_champions(series, Y_x, months_x, fest_x, PR_x, PX_x, catd, zoned, origin)
fc = forecast_all(series, Y_x, months_x, fest_x, PR_x, PX_x, catd, zoned, origin, H, champ=champ)["champion"]

prod = fr["product"]
prim = fr["primary"].merge(prod[["sku_code", "category"]], left_on="sku", right_on="sku_code")
last8 = sorted(prim["date"].unique())[-8:]
cap_by_cat = (prim[prim["date"].isin(last8)].groupby("category")["qty"].sum() / 8 * 1.15 * 4).to_dict()
dpmap = prod.set_index("sku_code")["dist_price"]
prim["val"] = prim["qty"] * prim["sku"].map(dpmap)
budget = float(prim[prim["date"].isin(sorted(prim["date"].unique())[-4:])]["val"].sum())

P = prepare(series, fc, fr["inventory"], fr["location"], prod, fr["costs"], fr["primary"])
sol = solve(series, P, budget, cap_by_cat)
sol_plus = solve(series, P, budget * 1.01, cap_by_cat)
shadow = (sol_plus["objective"] - sol["objective"]) / (budget * 0.01)
fwd_risk, rec = risk_lists(series, P, sol, fr["inventory"], fr["location"])

plan = pd.DataFrame({"sku": series["sku"], "zone": series["zone"],
                     "category": series["category"], "ship_units": sol["ship"].astype(int),
                     "cases": sol["cases"], "ship_value": (sol["ship"] * P["dp"]).round(0),
                     "proj_cover_wk": sol["proj_cover"].round(2)})
plan.to_csv("out/plan/m4_plan.csv", index=False)
fwd_risk.to_csv("out/plan/m4_forward_risk.csv", index=False)
summary = {
    "horizon_weeks": H, "plan_lines": int((plan.ship_units > 0).sum()),
    "total_ship_units": int(plan.ship_units.sum()),
    "total_ship_value_inr": float(plan.ship_value.sum()),
    "objective_margin_inr": round(sol["objective"], 0),
    "budget_inr": round(budget, 0), "budget_utilisation": round(sol["util_budget"], 4),
    "capacity_utilisation": {k: round(v, 3) for k, v in sol["cap_util"].items()},
    "BINDING_CONSTRAINT": sol["binding"],
    "shadow_price_margin_per_budget_rupee": round(shadow, 3),
    "forward_risk_lines(cover<1wk)": int(len(fwd_risk)),
    "near_stockout_reconciliation": rec,
}
# STRESS SCENARIO: prove binding detection + shadow price on a constrained budget
need_value = float((np.maximum(P["d4"] + P["davg"] - P["opening"], 0) * P["dp"]).sum())
budget_s = need_value * 0.85
sol_s = solve(series, P, budget_s, cap_by_cat)
sol_s2 = solve(series, P, budget_s * 1.01, cap_by_cat)
shadow_s = (sol_s2["objective"] - sol_s["objective"]) / (budget_s * 0.01)
fwd_risk_s, _ = risk_lists(series, P, sol_s, fr["inventory"], fr["location"])
summary["stress_scenario"] = {
    "budget_inr": round(budget_s, 0),
    "budget_utilisation": round(sol_s["util_budget"], 4),
    "BINDING_CONSTRAINT": sol_s["binding"],
    "shadow_price_margin_per_budget_rupee": round(shadow_s, 3),
    "forward_risk_lines(cover<1wk)": int(len(fwd_risk_s)),
}
fwd_risk_s.to_csv("out/plan/m4_forward_risk_stressed.csv", index=False)
json.dump(summary, open("out/plan/m4_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
ok = (plan.ship_units.sum() > 0
      and rec["exact_agreement"]                                   # reconciliation exact
      and sol_s["binding"].startswith("working-capital budget")    # stressed: real cap named
      and sol_s["util_budget"] >= 0.995                            # cap actually exhausted
      and shadow_s > 0                                             # relaxing it buys margin
      and len(fwd_risk_s) > 0)                                     # risk list responds
print("M4 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
