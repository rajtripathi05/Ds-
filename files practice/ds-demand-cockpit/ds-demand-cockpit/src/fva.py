"""Forecast Value Add: champion vs sales_targets plan vs seasonal-naive, zone x category x month."""
import numpy as np, pandas as pd

def fva_table(series, Y, weeks, folds, targets):
    rows = []
    for f in folds:
        o = f["origin"]
        for name in ("champion", "snaive"):
            P = f["preds"][name]
            for h in range(P.shape[1]):
                t = o + 1 + h
                y = Y[:, t]; m = ~np.isnan(y)
                rows.append(pd.DataFrame({
                    "month": pd.Timestamp(weeks[t]).strftime("%Y-%m"),
                    "zone": series["zone"].values[m],
                    "category": series["category"].values[m],
                    "model": name, "y": y[m], "p": P[m, h]}))
    df = pd.concat(rows)
    g = df.groupby(["month", "zone", "category", "model"], as_index=False)[["y", "p"]].sum()
    t = targets.rename(columns={"target_qty": "p"}).copy()
    t["model"] = "plan_target"
    act = g[g["model"] == "champion"][["month", "zone", "category", "y"]].drop_duplicates()
    t = t.merge(act, on=["month", "zone", "category"], how="inner")
    both = pd.concat([g, t[["month", "zone", "category", "model", "y", "p"]]])
    out = []
    for model, gg in both.groupby("model"):
        out.append(dict(model=model,
                        wmape=float(np.abs(gg.y - gg.p).sum() / gg.y.sum()),
                        bias=float((gg.p - gg.y).sum() / gg.y.sum()),
                        n_cells=len(gg)))
    res = pd.DataFrame(out).set_index("model")
    res["fva_vs_plan_pp"] = (res.loc["plan_target", "wmape"] - res["wmape"]) * 100
    return res, both
