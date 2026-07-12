"""Rolling-origin backtest. Gate: champion beats seasonal-naive WMAPE at SKU AND category level."""
import numpy as np, pandas as pd, json, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from features import build_panel
from models import snaive_forecast, ets_lite_forecast, croston_forecast, Ridge, _design, month_seasonal_index

H = 4
ORIGINS = [76, 82, 88, 94, 100]      # week indices (0-based of 105); train <= origin
VAL_WIN = 8                          # champion-selection window (train tail)

def assemble(panel):
    weeks = np.sort(panel["date"].unique())
    widx = {w: i for i, w in enumerate(weeks)}
    series = panel[["sku", "zone", "category", "elast", "intermittent"]].drop_duplicates(["sku", "zone"]).reset_index(drop=True)
    sidx = {(r.sku, r.zone): i for i, r in enumerate(series.itertuples())}
    n, T = len(series), len(weeks)
    Y = np.full((n, T), np.nan)
    PR = np.ones((n, T)); PX = np.zeros((n, T))
    for row in panel.itertuples():
        i, j = sidx[(row.sku, row.zone)], widx[row.date]
        Y[i, j] = row.qty; PR[i, j] = row.price_ratio; PX[i, j] = row.promo_x
    months = pd.Series(weeks).dt.month.values
    fest = panel.groupby("date")["festival"].max().reindex(weeks).fillna(0).values
    cats = sorted(series["category"].unique()); zones = sorted(series["zone"].unique())
    catd = np.stack([(series["category"] == c).astype(float).values for c in cats[1:]], 1)
    zoned = np.stack([(series["zone"] == z).astype(float).values for z in zones[1:]], 1)
    return series, weeks, months, fest, Y, PR, PX, catd, zoned

def cat_month_seasonality(series, Y, months, upto):
    """Category-level monthly index from train."""
    out = np.ones((len(series), 13))
    for c in series["category"].unique():
        rows = np.flatnonzero((series["category"] == c).values)
        agg = np.nansum(np.where(np.isnan(Y[rows, :upto + 1]), 0, Y[rows, :upto + 1]), axis=0)
        idx = month_seasonal_index(agg.astype(float), months[:upto + 1])
        out[rows, :] = idx
    return out

def ridge_recursive(Y, months, fest, PR, PX, seas, catd, zoned, inter, origin, h):
    """Fit on rows t in [max(4, origin-90), origin], predict origin+1..origin+h recursively."""
    Xs, ys = [], []
    t0 = max(4, origin - 90)
    for t in range(t0, origin + 1):
        X = _design(Y, months, seas, PR, PX, fest, catd, zoned, inter, t)
        y = Y[:, t]
        m = ~np.isnan(y) & ~np.isnan(Y[:, t - 1])
        Xs.append(X[m]); ys.append(np.log1p(np.maximum(y[m], 0)))
    model = Ridge().fit(np.vstack(Xs), np.concatenate(ys))
    Yw = Y.copy()
    preds = np.zeros((Y.shape[0], h))
    for i in range(1, h + 1):
        t = origin + i
        X = _design(Yw, months, seas, PR, PX, fest, catd, zoned, inter, t)
        p = np.expm1(model.predict(X)).clip(0)
        preds[:, i - 1] = p
        Yw[:, t] = np.where(np.isnan(Y[:, t]), np.nan, p)   # recursive with own preds
    return preds

def forecast_all(series, Y, months, fest, PR, PX, catd, zoned, origin, h, champ=None):
    n = len(series)
    inter = series["intermittent"].values.astype(bool)
    seas = cat_month_seasonality(series, Y, months, origin)
    out = {}
    out["snaive"] = np.stack([snaive_forecast(Y[i], origin, h) for i in range(n)])
    out["ets"] = np.stack([ets_lite_forecast(Y[i], months, origin, h) for i in range(n)])
    out["ridge"] = ridge_recursive(Y, months, fest, PR, PX, seas, catd, zoned, inter, origin, h)
    cro = np.stack([croston_forecast(Y[i], origin, h) for i in range(n)])
    tsb = np.stack([croston_forecast(Y[i], origin, h, variant="tsb") for i in range(n)])
    out["croston"] = np.where(inter[:, None], cro, out["ets"])
    out["tsb"] = np.where(inter[:, None], tsb, out["ets"])
    if champ is not None:
        pick = np.zeros((n, h))
        for name in set(champ):
            rows = np.flatnonzero(np.array(champ) == name)
            pick[rows] = out[name][rows]
        out["champion"] = pick
    return out

def choose_champions(series, Y, months, fest, PR, PX, catd, zoned, origin):
    """Champion per series from an internal validation window entirely inside train."""
    vo = origin - VAL_WIN
    fc = forecast_all(series, Y, months, fest, PR, PX, catd, zoned, vo, VAL_WIN)
    names = ["ets", "ridge", "snaive", "croston", "tsb"]
    champ = []
    inter = series["intermittent"].values.astype(bool)
    for i in range(len(series)):
        y = Y[i, vo + 1: vo + 1 + VAL_WIN]
        m = ~np.isnan(y)
        cand = ["croston", "tsb", "snaive", "ets"] if inter[i] else names
        if m.sum() == 0:
            champ.append("ets"); continue
        errs = {nm: np.abs(fc[nm][i, m] - y[m]).sum() for nm in cand}
        best = min(errs, key=errs.get)
        # v2 (red-team): sticky default — a challenger must beat ETS-lite by >=3% relative
        # on validation to displace it (selection noise was costing accuracy; see BACKTEST.md)
        if best != "ets" and "ets" in errs and errs[best] > 0.97 * errs["ets"]:
            best = "ets"
        champ.append(best)
    return champ

def wmape_tables(series, Y, folds_pred, level_key):
    """level_key: 'sku' or 'category'. Aggregate preds+actuals to level, then WMAPE."""
    err = {}; den = 0.0
    keys = series[level_key if level_key != "sku" else "sku"].values
    for name in folds_pred[0]["preds"]:
        num = 0.0; den_n = 0.0; bias = 0.0
        for f in folds_pred:
            o = f["origin"]; P = f["preds"][name]
            for i_h in range(P.shape[1]):
                t = o + 1 + i_h
                y = Y[:, t]; m = ~np.isnan(y)
                dfa = pd.DataFrame({"k": keys[m], "y": y[m], "p": P[m, i_h]})
                g = dfa.groupby("k").sum()
                num += np.abs(g["y"] - g["p"]).sum(); den_n += g["y"].sum()
                bias += (g["p"] - g["y"]).sum()
        err[name] = dict(wmape=num / den_n, bias=bias / den_n)
    return err

def run():
    t0 = time.time()
    panel, fr, rep = build_panel()
    series, weeks, months, fest, Y, PR, PX, catd, zoned = assemble(panel)
    folds = []
    champs_used = {}
    for o in ORIGINS:
        champ = choose_champions(series, Y, months, fest, PR, PX, catd, zoned, o)
        fc = forecast_all(series, Y, months, fest, PR, PX, catd, zoned, o, H, champ=champ)
        folds.append(dict(origin=o, preds=fc))
        for c in champ: champs_used[c] = champs_used.get(c, 0) + 1
    sku = wmape_tables(series, Y, folds, "sku")
    cat = wmape_tables(series, Y, folds, "category")
    res = dict(sku=sku, category=cat, champions=champs_used,
               folds=[f["origin"] for f in folds], horizon=H,
               runtime_s=round(time.time() - t0, 1))
    Path("out/plan").mkdir(parents=True, exist_ok=True)
    json.dump(res, open("out/cache/backtest_results.json", "w"), indent=1, default=float)
    return res, series, Y, folds

if __name__ == "__main__":
    res, *_ = run()
    print(json.dumps({k: res[k] for k in ("sku", "category", "champions", "runtime_s")},
                     indent=1, default=float))
    gate = (res["sku"]["champion"]["wmape"] < res["sku"]["snaive"]["wmape"] and
            res["category"]["champion"]["wmape"] < res["category"]["snaive"]["wmape"])
    print("M1 GATE:", "GREEN" if gate else "RED")
