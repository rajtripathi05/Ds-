"""Weekly SKU x zone panel + engineered features (see ASSUMPTIONS B2, B9)."""
import numpy as np, pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from loaders import load_all

TYPE_MULT = {"consumer": 1.0, "trade": 0.7, "display": 0.5}   # B9: documented recipe

def build_panel(messy=False):
    fr, rep = load_all(messy=messy)
    sec = fr["secondary"].merge(fr["location"][["distributor_code", "zone"]],
                                left_on="distributor", right_on="distributor_code", how="left")
    panel = (sec.groupby(["sku", "zone", "date"], as_index=False)
                .agg(qty=("qty", "sum"), rev=("price_realized", lambda s: np.nan)))
    panel = panel.sort_values(["sku", "zone", "date"]).reset_index(drop=True)

    prod = fr["product"].set_index("sku_code")
    panel["category"] = panel["sku"].map(prod["category"])
    panel["elast"] = panel["sku"].map(prod["base_elasticity"]).astype(float)
    panel["intermittent"] = panel["sku"].map(prod["is_intermittent"]).fillna(False)

    # price ratio per sku-week from price_history
    ph = fr["price_history"].sort_values(["sku", "effective_from"])
    base_mrp = ph.groupby("sku")["mrp"].first()
    weeks = np.sort(panel["date"].unique())
    pr_rows = []
    for sku, g in ph.groupby("sku"):
        eff = g["effective_from"].values; mrp = g["mrp"].values
        idx = np.searchsorted(eff, weeks, side="right") - 1
        idx = np.clip(idx, 0, len(mrp) - 1)
        pr_rows.append(pd.DataFrame({"sku": sku, "date": weeks,
                                     "price_ratio": mrp[idx] / base_mrp[sku]}))
    price_panel = pd.concat(pr_rows, ignore_index=True)
    panel = panel.merge(price_panel, on=["sku", "date"], how="left")
    panel["price_ratio"] = panel["price_ratio"].fillna(1.0)

    # promo feature: engineered lift exposure for sku-week-zone
    promo = fr["promo"]
    pf = []
    for _, p in promo.iterrows():
        w = weeks[(weeks >= p["start"].to_datetime64()) & (weeks <= p["end"].to_datetime64())]
        for wk in w:
            pf.append((p["sku"], wk, p["location_scope"],
                       p["depth_pct"] * TYPE_MULT.get(p["type"], 1.0), p["type"], p["promo_id"]))
    pf = pd.DataFrame(pf, columns=["sku", "date", "scope", "depth_eff", "ptype", "promo_id"])
    panel = panel.merge(pf[pf["scope"] == "ALL"][["sku", "date", "depth_eff"]],
                        on=["sku", "date"], how="left")
    zs = pf[pf["scope"] != "ALL"].rename(columns={"scope": "zone", "depth_eff": "depth_zone"})
    panel = panel.merge(zs[["sku", "date", "zone", "depth_zone"]],
                        on=["sku", "date", "zone"], how="left")
    panel["depth_eff"] = panel["depth_eff"].fillna(0) + panel.pop("depth_zone").fillna(0)
    panel["promo_x"] = panel["depth_eff"] * panel["elast"].abs() * 2.0

    # festival week flag (calendar is daily)
    cal = fr["calendar"]
    cal["wk"] = cal["date"] - pd.to_timedelta(cal["date"].dt.weekday, unit="D")
    fest_w = cal.groupby("wk")["is_festival"].apply(
        lambda s: s.astype(str).str.lower().eq("true").any())
    panel["festival"] = panel["date"].map(fest_w).fillna(False).astype(int)
    panel["month"] = panel["date"].dt.month
    return panel, fr, rep

if __name__ == "__main__":
    p, fr, rep = build_panel()
    print("panel rows:", len(p), "| series:", p.groupby(["sku","zone"]).ngroups,
          "| weeks:", p["date"].nunique())
    print(p.head(3).to_string())
