# Synthetic FMCG data suite — one company, every "implement-now" use-case

A single, internally consistent fictional company — **Northwind FMCG (Synthetic)** — with data generated for every use-case you can stand up *without* a live enterprise integration. Everything is **seeded** (`SEED=42`, fully reproducible) and every dataset carries **planted signal + a ground-truth file**, so a model actually has something real to find and you can measure whether it found it.

> ⚠️ 100% synthetic. Fictional brands, vendors, people. No real company data. Regenerate anytime with `python generate_all.py all`.

## What powers what

| Folder | Dataset | Powers (right-now use-case) | First thing to try |
|---|---|---|---|
| `sales/` | `sales_secondary.csv` (**~927k rows**) | Demand forecasting · report-from-a-file · BI dashboard | Forecast weekly units by SKU; compare to a seasonal-naïve baseline |
| `sales/` | `sales_targets.csv` | Target-vs-actual analytics | Zone×category attainment %, colour-coded |
| `promotions/` | `promotions.csv` + `promo_performance.csv` | Trade-promotion ROI | Rank promos by ROI; which depths/types pay back |
| `finance/` | `ap_invoices.csv` + `purchase_orders.csv` + `grn.csv` | Invoice 3-way match · duplicate/anomaly detection | Flag invoices breaching the match rules; check vs ground truth |
| `finance/` | `monthly_pnl.csv` | Report-from-a-file · BI | Category P&L trend, EBITDA bridge |
| `hr/` | `employees.csv` + `engagement_survey.csv` | Attrition prediction · workforce analytics | Train a flight-risk model; validate drivers |
| `talent/` | `resumes/` + `jds/` | Resume ↔ JD matching | Embed both; rank resumes per JD; check vs truth |
| `knowledge/` | `corpus/` (39 docs) + `qa_examples.csv` | Policy chatbot · knowledge search · summarisation | RAG over the docs; answer the sample questions with citations |

## Ground truth (validation only — never train on these)

| File | Use |
|---|---|
| `ground_truth/promo_true_elasticities.csv` | The true price elasticity per category the sales data was built from |
| `ground_truth/planted_invoice_issues.csv` | Every invoice with a planted problem + type (659 of 5,088 ≈ 13%) |
| `ground_truth/attrition_drivers.md` | The documented logistic drivers behind the attrition flag |
| `ground_truth/resume_jd_truth.csv` | The intended best-match JD + strength for each resume |

## Planted signal (verified recoverable)

- **Sales:** promo weeks run **+40%** above non-promo; beverages peak in summer; ~10% of SKUs are recent launches (zero pre-launch).
- **Attrition (18%):** leavers have lower engagement (2.9 vs 3.5), below-band pay (0.93 vs 1.02), longer commutes — all in the generated direction.
- **Invoices:** 7 planted issue types (duplicate, price mismatch, qty variance, tax error, date anomaly, invalid GSTIN, missing GRN).
- **Resumes:** strong matches average **0.88** skill overlap vs **0.16** for weak.

## Regenerate

```bash
pip install pandas numpy
python generate_all.py all          # or: masters | sales | finance | hr | talent | knowledge
```

Data dictionary with every column is in `DATA_DICTIONARY.md`.

_Independent, synthetic dataset built for prototyping the FMCG AI use-cases — not affiliated with any real company._
