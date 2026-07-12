# KICKOFF — ds-demand-cockpit (GOAT 1: Demand-to-Shelf Brain)

You are my senior ML + platform engineer. We are building a GOAT-tier FMCG planning cockpit
(FMCG theme: Pulse, Catch, Rajnigandha, Ksheer): hierarchical demand forecasting + causal
trade-promo uplift + a constrained S&OP optimizer + a live what-if cockpit.

KEEP-ALIVE + PROGRESS (mandatory, non-negotiable): my screen turns off after 5
minutes without visible activity (system sleep is already set to Never — this is display-off
only). Never go more than 3 minutes without a visible action: append a timestamped heartbeat
line to PROGRESS.md — current step, % done, next step — or open and close a file. Maintain
PROGRESS.md for the entire session; it doubles as the progress log I review.

OPERATING DISCIPLINE (from ./reference — my proven IGL rules): PLAN before
execution (objective / approach / affected files / risks) and WAIT for my approval; PROTECT
existing work (show diffs; never overwrite without explicit OK; new versions get -v2 suffix);
deliverable files named YYYY-MM-DD-descriptive-name.ext; END EVERY TASK with a File Change
Report (Created / Modified / Deleted + summary); ask instead of assuming.

FIRST ACTION: read ./data (start with DATASET_DOCS.md and 2026-07-12-dataset-docs-v2-extensions.md
— they are the DATA CONTRACT), then give me the PLAN + a repo CLAUDE.md and WAIT for approval.

DATA (all synthetic, spine seed=42, 2024-01→2025-12 weekly, 151 SKUs, 60 distributors):
- sales_secondary.csv (297,610 rows — THE fact table, FROZEN truth) + *_messy.csv variants
- product_master / location_master / calendar / promo_calendar / price_history / new_launch_analogs
- v2 extensions: primary_sales.csv (269,948 rows, order-up-to + case multiples + launch pipeline
  fill 3.13x on DS-CONFPULSE-149), distributor_inventory.csv (377,442 rows, exact identity
  closing=opening+in−out, never negative, near_stockout flags), sku_costs.csv (COGS/margin),
  sales_targets.csv (zone×category monthly)
- canonical tests: golden_thread_trace.csv (factor product == stored qty) and
  golden_inventory_walk.csv; planted_data_quality_issues.csv lists every defect in the messy set
- generate_ds.py / extend_ds.py regenerate everything deterministically

ARCHITECTURE LAWS (encode in CLAUDE.md; never break):
1. FROZEN FORECAST CORE — forecasting + reconciliation engine outputs are truth; layers READ them.
2. ONE-WAY STATE — one read-only plan snapshot; only the pipeline writes it.
3. RECONCILIATION IS TRUTH — every what-if is an INTENT validated by the deterministic
   reconcile+optimize step before it applies; nothing bypasses it.
4. NEVER STOPS — bad/missing data → warn + fallback + completeness badge, never fatal.
   Prove it against the *_messy.csv files (catch every planted issue; list caught vs planted).

BUILD ORDER (each milestone gated by tests; update PROGRESS.md throughout):
M0 Plan + CLAUDE.md + data-contract loader with the resilience layer (messy files pass).
M1 Forecast engine: statsforecast AutoETS baseline + LightGBM challenger (price/promo/festival/
   season features); Croston/TSB for is_intermittent SKUs; rolling-origin backtest harness
   (WMAPE, bias) — must beat naive seasonal at SKU and category level.
M2 Hierarchical reconciliation SKU→brand→category→zone (bottom-up + MinT); totals tie exactly.
   Forecast-Value-Add view vs sales_targets.csv and vs the stat baseline.
M3 Causal promo uplift: true incrementality per promo (not correlation — use the promo calendar
   as the design; control = matched non-promo weeks/distributors) + promo ROI in ₹ using
   sku_costs. Validate: recovered lift within tolerance of the documented generative elasticities.
M4 Constrained optimizer: service level vs working capital (distributor_inventory) vs trade
   spend; outputs plan + THE BINDING CONSTRAINT named. Stockout-risk list from near_stockout.
M5 COCKPIT (browser): what-if levers (promo depth/dates, launch date, price) → forecast,
   inventory, margin re-solve live <2s; scenario manager (save/compare side-by-side); primary-vs-
   secondary pipeline-fill view; drift alerts; export a one-click S&OP pack (xlsx + PDF).
   Role gate: Operations sees no margin/cost anywhere; Executive sees the financial layer.
M6 Canonical tests as CI: golden thread reproduces; inventory identity holds; pipeline-fill
   ratio >1.3 detected; messy-set catch-rate 100%. Verify UI flows headlessly (Playwright).

Do not invent data fields; if something is missing, ask. Start now with the PLAN.
