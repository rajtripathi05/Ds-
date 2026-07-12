# M0 gate — caught vs planted (messy set)

| planted issue | caught? | evidence |
|---|---|---|
| missing dist_price (3 SKUs) | ✅ | ['DS-BEVECAT-098', 'DS-CONFFRU-026', 'DS-SPICKEW-009'] |
| #N/A literal in mrp (DS-BEVECAT-006) | ✅ | ['DS-BEVECAT-006'] |
| unit mismatch g-as-kg (3 SKUs) | ✅ | ['DS-CONFPULSE-001', 'DS-DAIRKSH-004', 'DS-SPICCAT-003'] |
| duplicate distributor_code (DIST-NO-001) | ✅ | ['DIST-NO-001'] |
| mixed date format 2,976 rows | ✅ | [2976] |
| messy fact rows fully recovered | ✅ | [297610] |

Catch rate: 5/5 planted classes + never-fatal check · badges: {'product_master': 0.9934, 'location_master': 1.0, 'sales_secondary': 1.0, 'calendar': 1.0, 'promo_calendar': 1.0, 'price_history': 1.0, 'sku_costs': 1.0, 'sales_targets': 1.0, 'primary_sales': 1.0, 'distributor_inventory': 1.0, 'new_launch_analogs': 1.0}

Raw report:
```json
{
 "issues": [
  {
   "table": "product_master",
   "issue": "non-numeric literal in mrp",
   "keys": "DS-BEVECAT-006",
   "action": "coerced to NaN + row quarantined",
   "n": 1
  },
  {
   "table": "product_master",
   "issue": "missing dist_price",
   "keys": "DS-SPICKEW-009; DS-CONFFRU-026; DS-BEVECAT-098",
   "action": "imputed category-median dist_price/mrp ratio",
   "n": 3
  },
  {
   "table": "product_master",
   "issue": "unit mismatch g-labelled-kg",
   "keys": "DS-CONFPULSE-001; DS-SPICCAT-003; DS-DAIRKSH-004",
   "action": "normalised kg->g (/1000 on aggregation base)",
   "n": 3
  },
  {
   "table": "product_master",
   "issue": "quarantined rows (unusable numerics)",
   "keys": "DS-BEVECAT-006",
   "action": "excluded from analytics, listed here",
   "n": 1
  },
  {
   "table": "location_master",
   "issue": "duplicate distributor_code (PK collision)",
   "keys": "DIST-NO-001",
   "action": "dedup keep-first, conflict flagged",
   "n": 1
  },
  {
   "table": "sales_secondary",
   "issue": "mixed date format (DD-MM-YYYY)",
   "keys": "2976 rows re-parsed",
   "action": "format-tolerant parse (ISO first, day-first fallback)",
   "n": 2976
  }
 ],
 "badges": {
  "product_master": 0.9934,
  "location_master": 1.0,
  "sales_secondary": 1.0,
  "calendar": 1.0,
  "promo_calendar": 1.0,
  "price_history": 1.0,
  "sku_costs": 1.0,
  "sales_targets": 1.0,
  "primary_sales": 1.0,
  "distributor_inventory": 1.0,
  "new_launch_analogs": 1.0
 }
}
```