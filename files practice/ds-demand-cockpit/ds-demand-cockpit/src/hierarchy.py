"""Hierarchical reconciliation: bottom = SKU x zone; aggregates = SKU, brand, category, zone,
category x zone, TOTAL. Bottom-up and MinT(OLS); ties asserted exactly."""
import numpy as np, pandas as pd

def build_S(series, product):
    """Returns (S, node_index list) where S @ bottom = all-node values."""
    n = len(series)
    brand = series["sku"].map(product.set_index("sku_code")["brand"])
    keys = {
        "sku": series["sku"].values,
        "brand": brand.values,
        "category": series["category"].values,
        "zone": series["zone"].values,
        "catzone": (series["category"] + "|" + series["zone"]).values,
    }
    rows, names = [np.eye(n)], [("bottom", f"{s}|{z}") for s, z in zip(series["sku"], series["zone"])]
    for lvl, k in keys.items():
        for v in pd.unique(k):
            rows.append((k == v).astype(float)[None, :])
            names.append((lvl, str(v)))
    rows.append(np.ones((1, n)))
    names.append(("total", "TOTAL"))
    S = np.vstack(rows)
    return S, names

def bottom_up(S, yhat_bottom):
    return S @ yhat_bottom

def mint_ols(S, yhat_all):
    """MinT with identity covariance (OLS): reconciled_bottom = (S'S)^-1 S' yhat_all."""
    StS = S.T @ S
    beta = np.linalg.solve(StS, S.T @ yhat_all)
    return S @ beta, beta          # (all-node reconciled, bottom reconciled)

def assert_ties(S, all_vals, bottom_vals, tol=1e-8):
    recon = S @ bottom_vals
    denom = np.maximum(np.abs(all_vals), 1.0)
    gap = np.max(np.abs(recon - all_vals) / denom)
    assert gap < tol, f"hierarchy tie violated: max rel gap {gap:.2e}"
    return gap
