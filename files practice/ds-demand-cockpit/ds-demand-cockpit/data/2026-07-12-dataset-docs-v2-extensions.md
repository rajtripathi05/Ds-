# Dataset v2 Extensions (addendum to DATASET_DOCS.md)
New derived layers on the FROZEN v1 spine (v1 facts untouched; extend_ds.py, seed 4242):
- **primary_sales.csv** (269,948 rows): company→distributor orders. Weekly order-up-to policy —
  safety = trailing-4wk avg secondary; orders ceil to case multiples (Confectionery 200,
  MouthFreshener 100, Beverages 24, Spices 48, Dairy 24, Snacks 48); NEW-SKU first 2 orders ×1.5
  → verified pipeline-fill: first-4wk primary/secondary = **3.13×** on DS-CONFPULSE-149.
- **distributor_inventory.csv** (377,442 rows): exact identity closing = opening + primary_in −
  secondary_out (verified all rows), never negative, weeks_cover + near_stockout flags.
- **sku_costs.csv**: unit COGS + manufacturer GM% (ESTIMATE: category bands ±5% on dist_price:
  Conf 45 / MF 55 / Bev 40 / Spice 42 / Dairy 28 / Snack 38).
- **sales_targets.csv** (864 rows): monthly zone×category. 2024 = actual×U(0.92,1.12);
  2025 = 2024 actual×(1+10–18%).
- **golden_inventory_walk.csv**: first 8 weeks of DS-CONFPULSE-001 @ DIST-NO-001 — identity
  verifiable by hand.
All v2 verification: PASS (identity, non-negativity, primary≥secondary per pair, case multiples,
pipeline-fill >1.3×, cost coverage, 24 months × 6 zones of targets).
