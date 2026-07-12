"""Causal promo uplift via matched controls. Method (after honest iteration, see PROGRESS/M3):
 - controls: same SKU x zone, +/-8 non-promo non-festival weeks, PRICE-STABLE (same price_ratio),
   seasonality-adjusted with a promo/festival-EXCLUDED monthly index, median of >=2;
 - estimator: per-cell el_hat=(lift-1)/(2*depth*type_mult), category estimate = weighted median,
   weights = signal x sqrt(volume);
 - truth (B9): product_master.base_elasticity of the PROMOTED SKUs, observation-weighted.
v1 (plain median, contaminated seasonality) kept in causal_v1_median_baseline.py — it was RED.
"""
import numpy as np, pandas as pd
TYPE_MULT = {"consumer": 1.0, "trade": 0.7, "display": 0.5}

def promo_windows(promo, weeks):
    out = []
    for _, p in promo.iterrows():
        w = weeks[(weeks >= p["start"].to_datetime64()) & (weeks <= p["end"].to_datetime64())]
        out.append((p["promo_id"], p["sku"], p["location_scope"], p["type"],
                    float(p["depth_pct"]), set(w)))
    return out

def wmedian(v, w):
    o = np.argsort(v); v, w = np.asarray(v, float)[o], np.asarray(w, float)[o]
    c = np.cumsum(w)
    return float(v[np.searchsorted(c, c[-1] / 2)])

def uplift_study(panel, promo, product, costs):
    weeks = np.sort(panel["date"].unique())
    widx = {w: i for i, w in enumerate(weeks)}
    fest = panel.groupby("date")["festival"].max()
    pr_map = panel.drop_duplicates(["sku", "date"]).set_index(["sku", "date"])["price_ratio"]
    pw = promo_windows(promo, weeks)
    sku_pw = {}
    for pid, sku, scope, ptype, depth, ws in pw:
        sku_pw.setdefault(sku, set()).update(ws)
    prod = product.set_index("sku_code")
    cost = costs.set_index("sku_code")["unit_cogs"]
    recs, roi_rows = [], []
    for pid, sku, scope, ptype, depth, ws in pw:
        if sku not in prod.index or not ws:
            continue
        g = panel[panel["sku"] == sku]
        if scope != "ALL":
            g = g[g["zone"] == scope]
        if g.empty:
            continue
        clean = g[~g["date"].isin(sku_pw.get(sku, set())) & (g["festival"] == 0)]
        seas_m = clean.groupby(clean["date"].dt.month)["qty"].mean()
        if seas_m.empty:
            continue
        piv = g.pivot_table(index="zone", columns="date", values="qty", aggfunc="sum")
        inc_units = base_units = 0.0
        for z, row in piv.iterrows():
            for w in sorted(ws):
                if w not in widx or w not in row.index or pd.isna(row[w]) or fest.get(w, 0):
                    continue
                pr_w = pr_map.get((sku, pd.Timestamp(w)), 1.0)
                i = widx[w]; ctrl = []
                for d in range(1, 9):
                    for j in (i - d, i + d):
                        if 0 <= j < len(weeks):
                            wj = weeks[j]
                            if wj in sku_pw.get(sku, ()) or fest.get(wj, 0):
                                continue
                            if abs(pr_map.get((sku, pd.Timestamp(wj)), 1.0) - pr_w) > 1e-9:
                                continue
                            v = row.get(wj, np.nan)
                            if not pd.isna(v) and v > 0:
                                sw = seas_m.get(pd.Timestamp(w).month, seas_m.mean())
                                sj = seas_m.get(pd.Timestamp(wj).month, seas_m.mean())
                                ctrl.append(v * sw / max(sj, 1e-9))
                    if len(ctrl) >= 4:
                        break
                if len(ctrl) >= 2:
                    cf = float(np.median(ctrl))
                    if cf > 0:
                        x = 2.0 * depth * TYPE_MULT[ptype]
                        recs.append(dict(promo_id=pid, sku=sku, zone=z,
                                         category=prod.loc[sku, "category"], type=ptype,
                                         depth=depth, week=w, y=float(row[w]), cf=cf,
                                         lift=float(row[w]) / cf, x=x,
                                         el_hat=(float(row[w]) / cf - 1) / x,
                                         el_true=abs(float(prod.loc[sku, "base_elasticity"]))))
                        inc_units += float(row[w]) - cf
                        base_units += cf
        if base_units > 0:
            dp = float(prod.loc[sku, "dist_price"])
            promo_price = dp * (1 - 0.4 * depth)
            cogs = float(cost.get(sku, dp * 0.6))
            inc_margin = inc_units * (promo_price - cogs)
            promo_cost = (dp - promo_price) * (base_units + inc_units)
            roi_rows.append(dict(promo_id=pid, sku=sku, category=prod.loc[sku, "category"],
                                 type=ptype, depth=depth, inc_units=round(inc_units),
                                 inc_margin=round(inc_margin), promo_cost=round(promo_cost),
                                 roi=round(inc_margin / promo_cost, 2) if promo_cost > 0 else np.nan))
    return pd.DataFrame(recs), pd.DataFrame(roi_rows)

def category_recovery(df, product=None):
    rows = []
    for cat, g in df.groupby("category"):
        e = wmedian(g["el_hat"].values, (g["x"] * np.sqrt(g["cf"])).values)
        t = float(g["el_true"].mean())
        rows.append(dict(category=cat, n_obs=len(g), el_true=round(t, 3),
                         el_recovered=round(e, 3), rel_err_pct=round(abs(e - t) / t * 100, 1)))
    return pd.DataFrame(rows).sort_values("category")
