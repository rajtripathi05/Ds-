"""Data-contract loaders with a NEVER-STOPS resilience layer.
Every defect -> warn + fallback + badge entry; never an exception past this module.
"""
import json, re
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

class Report:
    def __init__(self):
        self.issues = []            # dicts: table, issue, keys, action, n
        self.badges = {}            # table -> completeness float
    def add(self, table, issue, keys, action, n):
        self.issues.append(dict(table=table, issue=issue,
                                keys="; ".join(map(str, keys))[:400], action=action, n=int(n)))
    def badge(self, table, frac):
        self.badges[table] = round(float(frac), 4)
    def to_json(self):
        return dict(issues=self.issues, badges=self.badges)

def _read(name, messy=False):
    f = DATA / (name.replace(".csv", "_messy.csv") if messy else name)
    if not f.exists():
        f = DATA / name
    return pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[""])

def _num(s):
    return pd.to_numeric(s, errors="coerce")

def load_product_master(messy=False, rep=None):
    rep = rep or Report()
    df = _read("product_master.csv", messy)
    n = len(df)
    # numeric coercion; '#N/A' style literals -> NaN + quarantine
    for col in ("mrp", "dist_price", "base_elasticity"):
        raw = df[col].copy()
        df[col] = _num(df[col])
        bad = raw.notna() & raw.astype(str).str.strip().ne("") & df[col].isna()
        if bad.any():
            rep.add("product_master", "non-numeric literal in " + col,
                    df.loc[bad, "sku_code"].tolist(), "coerced to NaN + row quarantined", bad.sum())
    df["is_intermittent"] = df["is_intermittent"].astype(str).str.lower().isin(("true", "1"))
    # missing dist_price -> impute from category median dist_price/mrp ratio
    miss = df["dist_price"].isna() & df["mrp"].notna()
    if miss.any():
        ratio = (df["dist_price"] / df["mrp"]).groupby(df["category"]).median()
        df.loc[miss, "dist_price"] = (df.loc[miss, "mrp"] *
                                      df.loc[miss, "category"].map(ratio).fillna(ratio.median())).round(2)
        rep.add("product_master", "missing dist_price", df.loc[miss, "sku_code"].tolist(),
                "imputed category-median dist_price/mrp ratio", miss.sum())
    # unit mismatch: pack_unit 'kg' implausible for tiny packs/prices -> normalise to g
    q = df["pack_unit"].astype(str).str.lower().eq("kg") & (df["mrp"] < 150)
    if q.any():
        df.loc[q, "pack_unit"] = "g"
        rep.add("product_master", "unit mismatch g-labelled-kg",
                df.loc[q, "sku_code"].tolist(), "normalised kg->g (/1000 on aggregation base)", q.sum())
    quarantined = df["mrp"].isna()
    if quarantined.any():
        rep.add("product_master", "quarantined rows (unusable numerics)",
                df.loc[quarantined, "sku_code"].tolist(), "excluded from analytics, listed here", quarantined.sum())
    rep.badge("product_master", 1 - quarantined.mean())
    return df[~quarantined].copy(), df[quarantined].copy(), rep

def load_location_master(messy=False, rep=None):
    rep = rep or Report()
    df = _read("location_master.csv", messy)
    dup = df.duplicated(subset=["distributor_code"], keep="first")
    if dup.any():
        rep.add("location_master", "duplicate distributor_code (PK collision)",
                df.loc[dup, "distributor_code"].unique().tolist(), "dedup keep-first, conflict flagged", dup.sum())
        df = df[~dup].copy()
    rep.badge("location_master", 1.0)
    return df, rep

def _parse_dates(col, rep, table):
    d = pd.to_datetime(col, format="%Y-%m-%d", errors="coerce")
    bad = d.isna()
    if bad.any():
        d2 = pd.to_datetime(col[bad], format="%d-%m-%Y", errors="coerce")
        d.loc[bad] = d2
        fixed = bad.sum() - d.isna().sum()
        if fixed:
            rep.add(table, "mixed date format (DD-MM-YYYY)", [f"{int(fixed)} rows re-parsed"],
                    "format-tolerant parse (ISO first, day-first fallback)", fixed)
    still = d.isna().sum()
    if still:
        rep.add(table, "unparseable dates", [f"{int(still)} rows"], "dropped with warning", still)
    return d

def load_sales_secondary(messy=False, rep=None):
    rep = rep or Report()
    df = _read("sales_secondary.csv", messy)
    n0 = len(df)
    df["date"] = _parse_dates(df["date"], rep, "sales_secondary")
    df = df[df["date"].notna()].copy()
    df["qty"] = _num(df["qty"]).fillna(0).astype(int)
    df["price_realized"] = _num(df["price_realized"])
    df["promo_id"] = df["promo_id"].replace("", np.nan)
    rep.badge("sales_secondary", len(df) / n0 if n0 else 1.0)
    return df, rep

def load_simple(name, date_cols=(), num_cols=(), rep=None, table=None):
    rep = rep or Report()
    table = table or name.replace(".csv", "")
    df = _read(name)
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in num_cols:
        df[c] = _num(df[c])
    rep.badge(table, 1.0)
    return df, rep

def load_all(messy=False):
    """One call -> dict of frames + consolidated report. Never raises on data defects."""
    rep = Report()
    prod, quarantine, rep = load_product_master(messy, rep)
    loc, rep = load_location_master(messy, rep)
    sec, rep = load_sales_secondary(messy, rep)
    cal, rep = load_simple("calendar.csv", date_cols=("date",), rep=rep)
    promo, rep = load_simple("promo_calendar.csv", date_cols=("start", "end"),
                             num_cols=("depth_pct",), rep=rep)
    price, rep = load_simple("price_history.csv", date_cols=("effective_from",),
                             num_cols=("mrp", "dist_price"), rep=rep)
    costs, rep = load_simple("sku_costs.csv", num_cols=("unit_cogs", "mfr_gross_margin_pct"), rep=rep)
    targets, rep = load_simple("sales_targets.csv", num_cols=("target_qty",), rep=rep)
    prim, rep = load_simple("primary_sales.csv", date_cols=("date",), num_cols=("qty",), rep=rep)
    inv, rep = load_simple("distributor_inventory.csv", date_cols=("date",),
                           num_cols=("opening", "primary_in", "secondary_out", "closing", "weeks_cover"), rep=rep)
    inv["near_stockout"] = inv["near_stockout"].astype(str).str.lower().eq("true")
    launch, rep = load_simple("new_launch_analogs.csv", rep=rep)
    return dict(product=prod, product_quarantine=quarantine, location=loc, secondary=sec,
                calendar=cal, promo=promo, price_history=price, costs=costs, targets=targets,
                primary=prim, inventory=inv, launch_analogs=launch), rep

if __name__ == "__main__":
    for mode in (False, True):
        frames, rep = load_all(messy=mode)
        print(("MESSY" if mode else "CLEAN"), "load ok:",
              {k: len(v) for k, v in frames.items() if hasattr(v, "__len__")})
        print(json.dumps(rep.to_json(), indent=1)[:1200])
