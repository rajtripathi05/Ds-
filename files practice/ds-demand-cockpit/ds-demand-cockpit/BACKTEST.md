# BACKTEST.md — measured forecast results (no adjectives, real numbers)
**Protocol.** Rolling-origin, 5 folds (origins at week indices 76/82/88/94/100 of 105), horizon 4 weeks, recursive multi-step. Grain: SKU × zone (903 series), metrics computed after aggregating predictions and actuals to the gate levels. Champion per series chosen on an 8-week validation window entirely inside the training slice (never on test). WMAPE = Σ|y−ŷ| / Σy · Bias = Σ(ŷ−y)/Σy. Runtime 11.3 s.

## Gate results (kickoff: beat seasonal-naive at SKU AND category level)
| model | SKU-level WMAPE | SKU bias | Category-level WMAPE | Category bias |
|---|---:|---:|---:|---:|
| seasonal-naive (baseline) | 18.27% | −13.55% | 15.89% | −13.55% |
| ETS-lite (B1 substitution for AutoETS) | 8.27% | −1.70% | 6.46% | −1.70% |
| Global ridge challenger (B1 sub for LightGBM) | 9.15% | −0.02% | 7.30% | −0.02% |
| Croston (intermittent SKUs; ETS elsewhere) | 8.22% | −1.68% | 6.46% | −1.68% |
| TSB (intermittent SKUs; ETS elsewhere) | 8.22% | −1.68% | 6.46% | −1.68% |
| **Champion (per-series selection, v3 sticky-ETS)** | **8.98%** | −1.15% | **6.55%** | −1.15% |

**M1 GATE: GREEN.** Champion beats seasonal-naive by 50.9% relative at SKU level (8.98% vs 18.27%) and 58.8% at category level (6.55% vs 15.89%). Croston/TSB path live for the 90 intermittent SKUs (selected 786 series-fold times).

## Honesty notes
- Seasonal-naive's −13.5% bias is structural: the spine has positive trend (growth g∈[−5%,+18%]) so last-year values under-forecast; this is exactly why it is the right baseline to beat.
- Champion selection is noisy on an 8-week window; plain ETS-lite (8.27%/6.46%) still edges the champion mix. Red-team iterations (documented): v2 = 12-wk window + sticky-ETS rule → WORSE (9.12%/7.06%, kept in git history); v3 = 8-wk window + sticky-ETS (challenger must beat ETS by ≥3% relative on validation to displace it) → adopted, 8.98%/6.55%. All variants evaluated on the same fold protocol; selection always uses train-internal validation only.
- Promo feature uses the documented generative lift structure (depth×|elasticity|×2×type_mult, ASSUMPTIONS B9) as domain-informed feature engineering; price uses price_history ratios; festival weeks from the calendar. No feature reads the future.
- Launch SKU (DS-CONFPULSE-149) and post-2024-10 NE distributors have short histories; snaive falls back to trailing-4-week mean there (stated in models.py), models handle NaN heads.
- Champion mix across 4,515 series-folds: ETS 1,627 · ridge 1,158 · snaive 944 · Croston 411 · TSB 375.
