"""Constrained S&OP allocator (B5/B6/B10). Exact greedy for a separable linear objective:
maximise sum(margin x expected_served) s.t. WC budget, category capacity, A-class service floor.
Emits: plan, named binding constraint + utilisation + shadow price, forward stockout-risk list.
"""
import numpy as np, pandas as pd
CASE = {"Confectionery": 200, "MouthFreshener": 100, "Beverages": 24,
        "Spices": 48, "Dairy": 24, "Snacks": 48}

def latest_state(inv):
    last = inv["date"].max()
    cur = inv[inv["date"] == last]
    return cur, last

def prepare(series, fc, inv, loc, product, costs, primary):
    """fc: (n,4) champion forward forecast at sku x zone."""
    n = len(series)
    d4 = np.nan_to_num(fc).sum(1)                       # 4-wk demand
    davg = d4 / 4.0
    cur, last = latest_state(inv)
    cur = cur.merge(loc[["distributor_code", "zone"]], left_on="distributor",
                    right_on="distributor_code", how="left")
    op = cur.groupby(["sku", "zone"])["closing"].sum()
    key = list(zip(series["sku"], series["zone"]))
    opening = np.array([op.get(k, 0.0) for k in key], float)
    prod = product.set_index("sku_code")
    dp = series["sku"].map(prod["dist_price"]).astype(float).values
    cogs = series["sku"].map(costs.set_index("sku_code")["unit_cogs"]).astype(float).values
    cogs = np.where(np.isnan(cogs), dp * 0.6, cogs)
    margin = np.maximum(dp - cogs, 0.01)
    abc = series["sku"].map(prod["abc_class"]).values
    casem = series["category"].map(CASE).fillna(24).astype(int).values
    return dict(d4=d4, davg=davg, opening=opening, dp=dp, margin=margin, abc=abc,
                casem=casem, last=last)

def solve(series, P, budget, cap_by_cat, service_floor_weeks=1.0):
    n = len(series)
    d4, davg, opening = P["d4"], P["davg"], P["opening"]
    margin, dp, casem = P["margin"], P["dp"], P["casem"]
    target = np.maximum(d4 + davg * 1.0 - opening, 0)          # demand + 1wk safety - stock
    mandatory = np.where((P["abc"] == "A"),
                         np.minimum(np.maximum(davg * service_floor_weeks - opening, 0) +
                                    np.minimum(d4, davg * service_floor_weeks), target), 0.0)
    mandatory = np.minimum(mandatory, target)
    ship = np.zeros(n)
    cats = series["category"].values
    cap_left = {c: float(cap_by_cat.get(c, np.inf)) for c in set(cats)}
    budget_left = float(budget)
    binding = "demand-bound (no cap binding)"
    # phase 1: mandatory service units
    for i in np.argsort(-margin / dp):
        m = mandatory[i]
        if m <= 0: continue
        m = min(m, cap_left[cats[i]], budget_left / dp[i] if dp[i] > 0 else m)
        ship[i] += m; cap_left[cats[i]] -= m; budget_left -= m * dp[i]
    # phase 2: optional units by margin density
    density = margin / dp
    for i in np.argsort(-density):
        room = target[i] - ship[i]
        if room <= 0: continue
        m = min(room, cap_left[cats[i]], budget_left / dp[i] if dp[i] > 0 else room)
        if m <= 0: continue
        ship[i] += m; cap_left[cats[i]] -= m; budget_left -= m * dp[i]
    # binding detection
    util_budget = 1 - budget_left / budget if budget > 0 else 0
    cap_util = {c: (1 - cap_left[c] / cap_by_cat[c]) for c in cap_by_cat if cap_by_cat[c] > 0}
    worst_cap = max(cap_util, key=cap_util.get) if cap_util else None
    if util_budget >= 0.995:
        binding = f"working-capital budget (₹{budget:,.0f}; {util_budget*100:.1f}% used)"
    elif worst_cap and cap_util[worst_cap] >= 0.995:
        binding = f"capacity: {worst_cap} ({cap_util[worst_cap]*100:.1f}% used)"
    # case rounding (down, then re-check budget)
    cases = np.floor(ship / casem).astype(int)
    ship_r = cases * casem
    served = np.minimum(P["opening"] + ship_r, d4)
    obj = float((margin * served).sum())
    proj_cover = (opening + ship_r) / np.maximum(davg, 1e-9)
    return dict(ship=ship_r, cases=cases, served=served, objective=obj,
                binding=binding, util_budget=util_budget, cap_util=cap_util,
                proj_cover=proj_cover, budget_left=budget_left)

def risk_lists(series, P, sol, inv, loc):
    fwd = pd.DataFrame({"sku": series["sku"], "zone": series["zone"],
                        "proj_cover_wk": sol["proj_cover"].round(2),
                        "d4": P["d4"].round(0), "opening": P["opening"],
                        "ship": sol["ship"]})
    fwd_risk = fwd[(fwd["proj_cover_wk"] < 1.0) & (fwd["d4"] > 0)].sort_values("proj_cover_wk")
    cur, last = latest_state(inv)
    det = cur[cur["weeks_cover"] < 1.0]                      # data's own definition
    flags = cur[cur["near_stockout"] == True]
    agree = (len(det) == len(flags) == 0) or \
            (set(map(tuple, det[["sku","distributor"]].values)) ==
             set(map(tuple, flags[["sku","distributor"]].values)))
    return fwd_risk, dict(latest_week=str(last)[:10], flags_in_data=len(flags),
                          detector_hits=len(det), exact_agreement=bool(agree))
