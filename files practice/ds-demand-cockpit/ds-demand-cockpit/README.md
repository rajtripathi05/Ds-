# ds-demand-cockpit — Demand-to-Shelf Brain
*A working FMCG planning cockpit: hierarchical forecasting + causal trade-promo measurement + a
constrained S&OP optimizer + a live what-if cockpit — built overnight, fully offline, every claim
below measured by a test in this repo.* **Synthetic DS-themed data; no DS Group internal data.**

## The problem
A ₹10,000-crore-scale FMCG network sells through thousands of distributor-week-SKU cells. Promos,
festivals, price moves and launches bend history exactly where naive statistical forecasts fail;
planners can't safely ask "what if"; and nobody can prove which promo rupee was incremental. The
result is stockouts on winners, working capital on losers, and trade spend justified by
correlation.

## Architecture (laws enforced in code)
```
data/ (FROZEN spine: 297,610 secondary rows · 151 SKUs · 60 distributors · 105 wks)
   │  loaders.py — NEVER STOPS: warn+fallback+completeness badges (5/5 planted defects caught)
   ▼
features.py ─ SKU×zone weekly panel · price ratios · promo exposure · festival weeks
   ▼
models.py ──► backtest.py       ETS-lite + global ridge + Croston/TSB vs seasonal-naive
   │             (rolling-origin, 5 folds, h=4 — champion per series, chosen inside train)
   ▼
hierarchy.py  bottom-up + MinT(OLS): SKU→brand→category→zone→total, ties asserted EXACT
   ▼
causal.py     matched-control promo uplift → recovered elasticities → promo ROI (₹)
   ▼
optimizer.py  exact greedy allocation: WC budget · category capacity · A-class service floor
   │             names THE binding constraint + shadow price
   ▼
pipeline.py   ═ the ONLY writer of out/plan/* (ONE-WAY STATE) ═ snapshot.json + whatif_state.npz
   ▼
server.py     stdlib HTTP · role gate (ops = zero financial keys, enforced server-side)
cockpit/      vanilla-JS cockpit: levers → INTENT → reconcile (tie assert) → optimize → display
tests/        run_tests.py = canonical CI (9 gates) · ui_walk.mjs · make_screenshots.py
```

## VERIFIED results (measured by `python tests/run_tests.py`; see out/plan/CI_RESULTS.md)
| Gate | Measured result |
|---|---|
| Data resilience | messy set loads never-fatally; **5/5 planted defect classes caught with exact keys**; 297,610/297,610 fact rows recovered |
| Forecast vs naive | champion WMAPE **8.98% vs 18.27%** (SKU) and **6.55% vs 15.89%** (category) — 5-fold rolling origin, h=4; bias −1.0% vs −13.5% |
| Hierarchy | BU and MinT-OLS reconciliation tie gaps **0.0** (asserted) across all horizons |
| FVA | champion **+54.2pp** more accurate than the stretch plan targets and **+8.9pp** vs seasonal-naive at zone×category×month |
| Causal promos | recovered elasticity within **≤17.0%** of generative truth in **all 6 categories** (tolerance 20%); v1 estimator was RED at 49.6% and is kept in-repo for the audit trail |
| Promo ROI | measured per promo in ₹; median ROI 1.31, 75/118 promos > 1 — trade-type shallow-depth promos dominate the top (full table: out/plan/m3_promo_roi.csv) |
| Optimizer | baseline plan is demand-bound (budget util 73.5%); stressed budget names **working-capital budget binding at 100.0% util, shadow price ₹0.215 margin/₹**; near-stockout detector matches data flags **exactly** |
| Launch physics | canonical pipeline-fill **3.13×** detected (doc: 3.13×; threshold >1.3); golden thread reproduces on all 105 verifiable weeks; inventory identity holds on **377,442/377,442** rows |
| Cockpit | what-if → reconcile → optimize round trip **≤31 ms** wall (gate <2,000 ms); role gate leaks **zero** financial keys (recursive scan); scenarios save/compare; role-scoped xlsx export; headless UI walk 8/8 against the live API |

*(Promo-ROI median re-measured from m3_promo_roi.csv at close-out.)*

## Run it
```bash
python3 src/pipeline.py     # build the frozen plan snapshot (~25 s)
python3 src/server.py       # cockpit on http://localhost:8765
python3 tests/run_tests.py  # canonical CI — all 9 gates
```
Stack: pandas + numpy + matplotlib + openpyxl + stdlib only (offline; substitutions in
ASSUMPTIONS.md B1). Git history in `ds-cockpit.gitbundle` (mount-safe, `git clone` it).

## What production scale would add
Real DMS/ERP feeds behind the same loader contract; o9/planning-platform integration as the
system of record with this cockpit as the causal + what-if layer; per-distributor grain and
promo-calendar write-back; MLOps (drift monitors, challengers, model cards) per the governance
framework in the companion blueprint; and planner FVA reviews replacing the synthetic targets.

## Honesty
Synthetic data, deterministic seed; gates were never weakened (BLOCKERS.md lists the four spec
items the offline sandbox forced around — with what was done instead); every number above was
printed by a test in this session (PROGRESS.md is the timestamped log; ASSUMPTIONS.md B1–B11 the
judgment calls).
