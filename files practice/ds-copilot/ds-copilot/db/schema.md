# Copilot database — schema & governance
Tables (CSV; load into DuckDB/SQLite read-only):
- sales_secondary(date, sku→product_master.sku_code, distributor→location_master.distributor_code,
  qty, price_realized[EXEC], promo_id→promo_calendar.promo_id) — weekly fact, 297,610 rows
- product_master(sku_code PK, category, brand, variant, pack_size, mrp[EXEC], dist_price[EXEC],
  launch_date, abc_class, is_intermittent, …)
- location_master(distributor_code PK, super_stockist, territory, city, state, zone, channel,
  urban_rural, golive)
- calendar(date PK, week, month, is_festival, festival_name, season)
- promo_calendar(promo_id PK, sku, location_scope, type, start, end, depth_pct[EXEC], mechanic)
- price_history(sku, effective_from, mrp[EXEC], dist_price[EXEC], reason)
- sku_costs(sku_code, unit_cogs[EXEC], mfr_gross_margin_pct[EXEC]) — ENTIRE TABLE EXEC-ONLY
GOVERNANCE: columns tagged [EXEC] and the sku_costs table must be blocked for the Operations
role at the SQL policy layer, in addition to exec_only doc filtering at retrieval.
