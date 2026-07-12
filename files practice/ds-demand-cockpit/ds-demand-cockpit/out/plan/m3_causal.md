# M3 — causal promo uplift (measured)

| category       |   n_obs |   el_true |   el_recovered |   rel_err_pct |
|:---------------|--------:|----------:|---------------:|--------------:|
| Beverages      |     168 |     1.327 |          1.237 |           6.8 |
| Confectionery  |     267 |     0.632 |          0.53  |          16   |
| Dairy          |     179 |     1.173 |          1.373 |          17   |
| MouthFreshener |     259 |     0.856 |          0.909 |           6.3 |
| Snacks         |     190 |     1.322 |          1.478 |          11.8 |
| Spices         |     159 |     1.135 |          1.231 |           8.4 |

Tolerance: |recovered−true|/true ≤ 20.0% per category → GREEN (worst: Dairy 17.0%)

Method: matched non-promo/non-festival controls within ±6 weeks, seasonality-adjusted, median across ≥2 controls; 1222 promo-week cells; distributor-scoped promos analysed in their zone; ROI in ₹ from sku_costs (promo funding = 0.4×depth price cut per data contract).

Promo ROI: median 1.31, 75/118 promos ROI>1 — full table in m3_promo_roi.csv
