"""Causal promo uplift via matched non-promo controls (design-based, not correlational).
Recovery target (B9): lift = 1 + depth * |elasticity| * 2.0 * type_mult,
type_mult = consumer 1.0 / trade 0.7 / display 0.5. Truth per SKU: product_master.base_elasticity.
"""
import numpy as np, pandas as pd
TYPE_MULT = {"consumer": 1.0, "trade": 0.7, "display": 0.5}
CTRL_SPAN = 6   # weeks each side

def promo_windows(promo, weeks):
    out = []
    for _, p in promo.iterrows():
        w = weeks[(weeks >= p["start"].to_datetime64()) & (weeks <= p["end"].to_datetime64())]
        out.append((p["promo_id"], p["sku"], p["location_scope"], p["type"],
                    float(p["depth_pct"]), set(w)))
    return out

def uplift_study(panel, promo, product, costs):
    weeks = np.sort(panel["date"].unique())
    widx = {w: i for i, w in enumerate(weeks)}
    fest_by_week = panel.groupby("date")["festival"].max()
    # promo-week map per sku (any promo) to keep controls clean
    pw = promo_windows(promo, weeks)
    sku_promo_weeks = {}
    for pid, sku, scope, ptype, depth, ws in pw:
        sku_promo_weeks.setdefault(sku, set()).update(ws)

    prod = product.set_index("sku_code")
    cost = costs.set_index("sku_code")["unit_cogs"]
    recs, roi_rows = [], []
    for pid, sku, scope, ptype, depth, ws in pw:
        if sku not in prod.index or not ws:
            continue
        el_true = abs(float(prod.loc[sku, "base_elasticity"]))
        g = panel[panel["sku"] == sku]
        if scope != "ALL":
            g = g[g["zone"] == scope]
        if g.empty:
            continue
        piv = g.pivot_table(index="zone", columns="date", values="qty", aggfunc="sum")
        seas_m = g.groupby(g["date"].dt.month)["qty"].mean()
        seas = lambda w: seas_m.get(pd.Timestamp(w).month, seas_m.mean())
        inc_units = 0.0; base_units = 0.0
        for z, row in piv.iterrows():
            for w in sorted(ws):
                if w not in widx or w not in row.index or pd.isna(row[w]):
                    continue
                if fest_by_week.get(w, 0):      # festival-confounded promo week -> exclude
                    continue
                i = widx[w]
                ctrl = []
                for d in range(1, CTRL_SPAN + 1):
                    for j in (i - d, i + d):
                        if 0 <= j < len(weeks):
                            wj = weeks[j]
                            if wj in sku_promo_weeks.get(sku, ()) or fest_by_week.get(wj, 0):
                                continue
                            v = row.get(wj, np.nan)
                            if not pd.isna(v) and v > 0:
                                ctrl.append(v * seas(w) / max(seas(wj), 1e-9))
                    if len(ctrl) >= 4:
                        break
                if len(ctrl) >= 2:
                    cf = float(np.median(ctrl))
                    if cf > 0:
                        recs.append(dict(promo_id=pid, sku=sku, zone=z,
                                         category=prod.loc[sku, "category"], type=ptype,
                                         depth=depth, week=w, y=float(row[w]), cf=cf,
                                         lift=float(row[w]) / cf, el_true=el_true))
                        inc_units += float(row[w]) - cf
                        base_units += cf
        if base_units > 0:
            dp = float(prod.loc[sku, "dist_price"])
            promo_price = dp * (1 - 0.4 * depth)
            cogs = float(cost.get(sku, dp * 0.6))
            inc_margin = inc_units * (promo_price - cogs)
            promo_cost = (dp - promo_price) * (base_units + inc_units)
            roi_rows.append(dict(promo_id=pid, sku=sku, category=prod.loc[sku, "category"],
                                 type=ptype, depth=depth,
                                 inc_units=round(inc_units), inc_margin=round(inc_margin),
                                 promo_cost=round(promo_cost),
                                 roi=round(inc_margin / promo_cost, 2) if promo_cost > 0 else np.nan))
    df = pd.DataFrame(recs)
    # recovered elasticity per observation
    df["tmult"] = df["type"].map(TYPE_MULT)
    df["el_hat"] = (df["lift"] - 1) / (df["depth"] * 2.0 * df["tmult"])
    return df, pd.DataFrame(roi_rows)

def category_recovery(df, product):
    truth = product.groupby("category")["base_elasticity"].apply(lambda s: float(np.abs(s).mean()))
    rows = []
    for cat, g in df.groupby("category"):
        # weight by depth (deeper promos = stronger signal-to-noise on lift-1)
        e = float(np.median(g["el_hat"]))
        t = truth[cat]
        rows.append(dict(category=cat, n_obs=len(g), el_true=round(t, 3),
                         el_recovered=round(e, 3), rel_err_pct=round(abs(e - t) / t * 100, 1)))
    return pd.DataFrame(rows).sort_values("category")
