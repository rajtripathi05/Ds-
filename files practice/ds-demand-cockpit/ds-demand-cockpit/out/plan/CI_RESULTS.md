# CI — canonical test results (measured this run)

| gate | status | evidence | s |
|---|---|---|---|
| Golden thread reproduces | GREEN | 105 weekly rows reproduce (factor product == stored qty, ±1 rounding) | 0.3 |
| Inventory identity holds | GREEN | closing = opening + in − out on all 377,442 rows; never negative | 0.3 |
| Pipeline-fill 3.13× detected | GREEN | detected 3.13× (doc: 3.13×; threshold >1.3) | 0.4 |
| Near-stockout reconciliation exact | GREEN | detector(0) == flags(0) — exact on the data's own definition (B10) | 0.5 |
| M0 messy catch-rate 100% | GREEN | M0 GATE: GREEN | 5.5 |
| M1 champion beats seasonal-naive (SKU & category) | GREEN | champion 8.98%/6.55% vs snaive 18.27%/15.89% (SKU/category) | 10.9 |
| M2 hierarchy ties + FVA | GREEN | M2 GATE: GREEN | 17.4 |
| M3 elasticity recovery ≤20% | GREEN | M3 GATE: GREEN (tolerance 20.0%) | 7.6 |
| M4 optimizer + binding + shadow | GREEN | M4 GATE: GREEN | 6.9 |
| M5 cockpit API/role/what-if/export | GREEN | M5 GATE: GREEN | 2.7 |

**ALL GATES: GREEN** · 2026-07-12 14:17 IST