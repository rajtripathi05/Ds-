# Demand drivers — planted ground truth (sales_secondary.csv)

`units` (the TARGET) is generated as a product of these drivers. A good demand
model should recover each direction and rough strength:

| Driver (column) | Effect on units | Planted form |
|---|---|---|
| `unit_price` / `promo_depth` | price down -> units up | price elasticity per category (see promo_true_elasticities.csv); promo uplift = 1 + elasticity x depth x 3 |
| `promo_flag` / `promo_type` | promo weeks lift demand | trade/consumer/festival mechanic active |
| `num_outlets` (distribution) | more outlets -> more units | multiplier (num_outlets / baseline)^0.6, and baseline outlets scale with SKU popularity x distributor size |
| `shelf_facings` | more facings -> more units | multiplier (facings / baseline)^0.30 |
| `ad_spend` | more spend -> more units (diminishing) | multiplier 1 + 0.12 x ln(1 + ad_spend/8000) |
| `seasonal_index` | 1.0 = average; >1 peak | category seasonal profile (summer/winter/festive) |
| trend | mild per-SKU growth/decline | 1 + N(0.04, 0.10) x week/52 |

Product hierarchy = sku -> brand -> category; time = weekly `week_start`.
Use these only to validate a model — never as features beyond the columns themselves.
