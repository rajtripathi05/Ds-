# DS Group FMCG Synthetic Dataset — Documentation

**Prompt B deliverable** of the DS Group AI-portfolio synthetic-data suite (GOAT 1: demand
forecasting + S&OP + trade-promotion cockpit). Regenerate any time with `generate_ds.py`.

> **Not DS Group internal data.** Brand/category/price/geography/seasonality *structure* is grounded
> in public facts (annual coverage, company site, trade press — see the grounding pack). Every actual
> value is synthetic. Provenance is tagged per field in `data_dictionary.csv`.

## Spine (shared across Prompts B/C/D/E so datasets cross-join)
`seed=42` · `2024-01-01 → 2025-12-31` · weekly grain · **151 SKUs** · **60 distributors** ·
**297,610 fact rows** · SKU key `DS-<CAT><BRD>-<NNN>` · distributor key `DIST-<ZONE>-<NNN>`.

## Tables (7 clean + 3 messy + docs)
| File | Grain / PK | What |
|---|---|---|
| `product_master.csv` | sku_code | 151 SKUs: category, brand, variant, pack, MRP, dist price, ABC, elasticity, intermittent flag |
| `location_master.csv` | distributor_code | 60 distributors: super-stockist → territory → city → state → zone, channel, urban/rural |
| `calendar.csv` | date | daily spine with ISO week, season, real 2024–25 festival flags |
| `promo_calendar.csv` | promo_id | 120 promos: consumer/trade/display, depth, mechanic, scope |
| `sales_secondary.csv` | (date, sku, distributor) | **the fact table** — weekly secondary off-take + realized price + promo FK |
| `price_history.csv` | (sku, effective_from) | baseline + one planted MRP hike |
| `new_launch_analogs.csv` | new_sku | cannibalization mapping for the new launch |
| `*_messy.csv` | — | deliberately-broken copies for resilience testing (see planted issues) |
| `data_dictionary.csv` | — | every field: type, meaning, **provenance** (grounded / derived / synthetic) |
| `golden_thread_trace.csv` | — | full weekly factor decomposition for the golden pair |

## Generative recipe (multiplicative — every factor independently inspectable)
```
qty(sku, distributor, week) =
      base_rate(ABC class × region_weight × channel)      # grounded footprint + channel mix
    × trend            (annual g ∈ [−5%, +18%])
    × seasonality_index(category, month)                  # grounded category curves (pack §5)
    × price_effect     ((current_mrp / launch_mrp) ^ elasticity)
    × promo_lift       (1 + depth × |elasticity| × type_mult)
    × festival_spike   (Confectionery ×1.5, Spices ×1.3, MouthFreshener ×1.2, else ×1.1)
    × cannibalization  (0.80 on the anchor SKU while the new launch ramps)
    × AR(1) noise      (autocorrelated, mean ≈ 1 — real series aren't IID)
```
Long-tail C-class SKUs flagged `is_intermittent` bypass the smooth curve and use
`Bernoulli(p) × Poisson(λ)` → the zero-heavy pattern Croston/TSB models are built for.

**Elasticities** (grounded basis: ₹1 impulse is price-point-protected → inelastic; premium/beverages
more elastic): Confectionery −0.6 · MouthFreshener −0.9 · Beverages −1.4 · Spices −1.1 · Dairy −1.2 ·
Snacks −1.3 (each ±15% per SKU).

## Planted realism (so it exercises a real pipeline)
- **Structural break 1 — distribution expansion:** 8 Northeast (Assam) distributors go live only on
  **2024-10-01**; no rows before that → a genuine zone-level step change. Matches DS Group's verified
  Northeast strength.
- **Structural break 2 — price change:** an A-class Rajnigandha SKU takes an MRP hike on **2025-01-01**;
  via elasticity −0.9 the volume steps down and stays down (logged in `price_history.csv`).
- **New launch + cannibalization:** `DS-CONFPULSE-149` (a new Pulse flavour) launches **2024-07-01** on
  an S-curve and pulls **20%** of its volume from analog `DS-CONFPULSE-001` for 9 months.
- **Intermittent long-tail, seasonality, festival spikes, promo uplift** as above.

## Controlled data-quality issues (messy variant — every defect logged)
See `planted_data_quality_issues.csv`. Summary: ~2% missing `dist_price`; one `#N/A` literal in a
numeric field; three gram-SKUs mislabelled `kg` (unit mismatch); one duplicate `distributor_code`
(PK collision); ~1% of fact rows in `DD-MM-YYYY` instead of ISO. Each row names the expected
resilient behavior — so the same file is a test fixture for a "never-fatal, warn-and-continue" pipeline.

## Golden thread (hand-verified canonical test)
**`DS-CONFPULSE-001` @ `DIST-NO-001`, week `2024-03-25` (Holi):**

| factor | value | running product |
|---|---:|---:|
| base | 1272.09 | 1272.09 |
| trend | 1.0386 | 1321.19 |
| seasonality (Mar, confectionery) | 1.1000 | 1453.31 |
| price_effect | 1.0000 | 1453.31 |
| promo_lift | 1.0000 | 1453.31 |
| festival (Holi spike) | 1.5000 | 2179.97 |
| cannibalization | 1.0000 | 2179.97 |
| AR(1) noise | 0.7709 | 1680.54 |

Reconstructed `1680.54 → round = 1681` = **stored qty 1681**. Factors multiply back to the fact row
exactly — the generator has no hidden steps.

## Verification (all pass on the clean set)
Referential integrity (every FK resolves) · reconciliation (SKU total = category rollup = fact total) ·
both structural breaks confirmed present · golden thread reconciles factor-by-factor.

## Reproduce / scale
`python generate_ds.py` → writes all CSVs to `./out/`. Change `N_SKUS`, `N_DISTRIBUTORS`, `GRAIN='D'`
(daily), or `END` at the top and re-run; the seed makes it deterministic.
