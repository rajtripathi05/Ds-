# M2 — reconciliation + FVA (measured)

- Hierarchy nodes: 1117 (bottom 903 + SKU/brand/category/zone/cat-zone/total)
- Tie gaps per horizon (BU, MinT-OLS): [('0.0e+00', '0.0e+00'), ('0.0e+00', '0.0e+00'), ('0.0e+00', '0.0e+00'), ('0.0e+00', '0.0e+00')] — all < 1e-8 rel

## FVA at zone x category x month (5 backtest folds, 2025 H2)

| model       |   wmape |    bias |   n_cells |   fva_vs_plan_pp |
|:------------|--------:|--------:|----------:|-----------------:|
| champion    |  0.0618 | -0.0105 |       252 |          54.2494 |
| plan_target |  0.6043 |  0.4901 |       252 |           0      |
| snaive      |  0.1505 | -0.1355 |       252 |          45.3823 |

Positive fva_vs_plan_pp = model more accurate than the sales-target plan by that many WMAPE points.
