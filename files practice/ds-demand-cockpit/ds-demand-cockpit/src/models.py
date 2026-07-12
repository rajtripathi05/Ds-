"""Forecast models — offline, numpy-only (ASSUMPTIONS B1).
All fit on train slices only; recursive multi-step; never see test."""
import numpy as np, pandas as pd

def snaive_forecast(y, origin, h):
    """y: 1D array indexed by week (NaN = inactive). Seasonal lag 52; fallback trailing-4 mean."""
    out = np.empty(h)
    hist = y[:origin + 1]
    valid = hist[~np.isnan(hist)]
    fb = valid[-4:].mean() if len(valid) else 0.0
    for i in range(1, h + 1):
        t = origin + i
        v = y[t - 52] if t - 52 >= 0 else np.nan
        out[i - 1] = v if not np.isnan(v) else fb
    return np.maximum(out, 0)

def month_seasonal_index(y, months, shrink=6.0):
    """Per-series monthly index with shrinkage toward 1."""
    idx = np.ones(13)
    m = ~np.isnan(y)
    if m.sum() < 8 or np.nansum(y) <= 0:
        return idx
    overall = np.nanmean(y[m])
    if overall <= 0:
        return idx
    for mo in range(1, 13):
        sel = m & (months == mo)
        n = sel.sum()
        if n:
            idx[mo] = (np.nanmean(y[sel]) / overall * n + shrink) / (n + shrink)
    return idx

def ets_lite_forecast(y, months, origin, h, alpha=0.35, beta=0.08, phi=0.98):
    """Damped-trend EWMA on deseasonalised series; multiplicative monthly seasonality."""
    hist = y[:origin + 1].copy()
    mh = months[:origin + 1]
    sidx = month_seasonal_index(hist, mh)
    ds = hist / np.maximum(sidx[mh], 1e-6)
    lvl, tr = np.nan, 0.0
    for t in range(len(ds)):
        v = ds[t]
        if np.isnan(v):
            continue
        if np.isnan(lvl):
            lvl, tr = v, 0.0
            continue
        prev = lvl
        lvl = alpha * v + (1 - alpha) * (lvl + phi * tr)
        tr = beta * (lvl - prev) + (1 - beta) * phi * tr
    if np.isnan(lvl):
        return np.zeros(h)
    out = np.empty(h)
    for i in range(1, h + 1):
        mo = months[min(origin + i, len(months) - 1)]
        damp = sum(phi ** k for k in range(1, i + 1))
        out[i - 1] = max((lvl + damp * tr) * sidx[mo], 0)
    return out

def croston_forecast(y, origin, h, alpha=0.1, variant="croston"):
    hist = y[:origin + 1]
    hist = hist[~np.isnan(hist)]
    if len(hist) == 0:
        return np.zeros(h)
    if variant == "tsb":
        p, z = 0.3, max(hist[hist > 0].mean() if (hist > 0).any() else 0.0, 0.0)
        for v in hist:
            occ = 1.0 if v > 0 else 0.0
            p = p + alpha * (occ - p)
            if v > 0:
                z = z + alpha * (v - z)
        f = p * z
    else:
        nz = np.flatnonzero(hist > 0)
        if len(nz) == 0:
            return np.zeros(h)
        sizes = hist[nz]
        intervals = np.diff(np.concatenate([[-1], nz]))
        zh, ph = sizes[0], max(intervals[0], 1)
        for s, iv in zip(sizes[1:], intervals[1:]):
            zh = zh + alpha * (s - zh)
            ph = ph + alpha * (iv - ph)
        f = zh / max(ph, 1e-6)
    return np.full(h, max(f, 0.0))

# ---------- global ridge challenger ----------
RIDGE_L2 = 3.0

def _design(mat, months, seas_cat, price, promx, fest, catd, zoned, inter, t):
    """Feature rows for predicting week t from history <= t-1 (mat may contain preds)."""
    l1 = np.log1p(np.maximum(mat[:, t - 1], 0))
    l2 = np.log1p(np.maximum(mat[:, t - 2], 0)) if t >= 2 else l1
    l52 = np.full(mat.shape[0], np.nan)
    if t >= 52:
        l52 = np.log1p(np.maximum(mat[:, t - 52], 0))
    has52 = (~np.isnan(l52)).astype(float)
    l52 = np.nan_to_num(l52)
    mo = months[t]
    l4win = mat[:, max(t - 4, 0):t]
    cnt = (~np.isnan(l4win)).sum(1)
    l4 = np.log1p(np.maximum(np.nansum(np.nan_to_num(l4win), 1) / np.maximum(cnt, 1), 0))
    X = np.column_stack([
        np.nan_to_num(l1), np.nan_to_num(l2), np.nan_to_num(l4), l52, has52,
        seas_cat[:, mo], np.log(np.maximum(price[:, t], 1e-6)), promx[:, t],
        np.full(mat.shape[0], fest[t]),
        np.full(mat.shape[0], np.sin(2 * np.pi * mo / 12)),
        np.full(mat.shape[0], np.cos(2 * np.pi * mo / 12)),
        inter.astype(float), catd, zoned,
    ])
    return X

class Ridge:
    def fit(self, X, y):
        mu, sd = X.mean(0), X.std(0) + 1e-9
        Xs = (X - mu) / sd
        Xs = np.column_stack([np.ones(len(Xs)), Xs])
        A = Xs.T @ Xs + RIDGE_L2 * np.eye(Xs.shape[1])
        self.w = np.linalg.solve(A, Xs.T @ y)
        self.mu, self.sd = mu, sd
        return self
    def predict(self, X):
        Xs = (X - self.mu) / self.sd
        Xs = np.column_stack([np.ones(len(Xs)), Xs])
        return Xs @ self.w
