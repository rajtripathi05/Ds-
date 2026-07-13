# Data dictionary — Northwind FMCG (Synthetic)

All files are CSV unless noted. Row counts are for `SEED=42`.

## masters/
**calendar.csv** (120) — `week_start, week_idx, month, quarter, festival, is_festive`. 120 weeks of weekly history (~2.3 yrs from 2023-10-02).
**products.csv** (138) — `sku, brand, category, pack, mrp, unit_cost, unit_margin, launch_week, cat_true_elasticity`. 6 categories; ~10% have a `launch_week`.
**distributors.csv** (220) — `distributor_code, distributor_name, zone, state, town_class, size_index, gstin, onboarded_date, credit_limit_inr`. `size_index` scales that distributor's volume.
**plants.csv** (15) — `plant_code, plant_name, city, state, primary_category, daily_capacity_k_units, gstin`.

## sales/
**sales_secondary.csv** (~926,947) — `week_start, distributor_code, zone, state, sku, brand, category, units, unit_price, revenue, promo_flag, promo_id`. Distributor×SKU×week offtake. `unit_price` reflects promo discount; `revenue = units × unit_price`. **This is the forecasting/BI workhorse.**
**sales_targets.csv** (840) — `month, zone, category, actual_revenue, target_revenue`. Monthly target-vs-actual.

## promotions/
**promotions.csv** (170) — `promo_id, sku, category, promo_type, discount_depth, start_week, duration_weeks, planned_spend_inr`. Event master (trade/consumer/festival).
**promo_performance.csv** (170) — `promo_id, sku, category, promo_type, depth, incremental_units, incremental_margin_inr, spend_inr, roi`. Realised incremental vs a naïve baseline. _ROI is a simple incremental-margin ÷ spend read for illustrating the analysis — expect a wide spread; the point is to find the winners._

## finance/
**vendors.csv** (120) — `vendor_code, vendor_name, vendor_kind, gstin, payment_terms, state`.
**purchase_orders.csv** (12,402) — `po_no, vendor_code, plant_code, po_date, material, qty, rate, amount`. PO lines.
**grn.csv** (12,402) — `grn_no, po_no, grn_date, material, received_qty`. Goods receipts (blank `grn_no` = not received).
**ap_invoices.csv** (5,088) — `invoice_no, po_no, grn_no, vendor_code, vendor_gstin, invoice_date, plant_code, subtotal, gst_pct, gst_amount, total_amount`. Invoice headers; includes planted duplicates (suffix `-D`).
**ap_invoice_lines.csv** (12,628) — `invoice_no, material, qty, rate, amount`.
**monthly_pnl.csv** (168) — `month, category, revenue, units, cogs, gross_margin, marketing, distribution, overheads, ebitda`. 28 months × 6 categories.

**3-way match logic to implement:** invoice qty ≈ GRN qty (±2%), invoice rate = PO rate, `subtotal + gst = total`, `po_date ≤ grn_date ≤ invoice_date`, valid 15-char GSTIN, no duplicate `(vendor, amount, date)`. Cross-check flags against `ground_truth/planted_invoice_issues.csv`.

## hr/
**employees.csv** (4,000) — `emp_id, name, gender, age, department, sub_function, band, location, date_of_joining, tenure_years, monthly_ctc, band_midpoint, comp_ratio, last_promotion_years, commute_km, engagement_score, performance_rating, work_mode, attrition_flag, attrition_month, attrition_reason, manager_id`. **Target = `attrition_flag`** (~18% positive). Do not use `attrition_month/reason` as features (leakage).
**engagement_survey.csv** (4,000) — `emp_id, manager_support, growth_opportunity, work_life_balance, recognition, pay_fairness, survey_month`.
**attrition_events.csv** (718) — leavers only, with month + dominant reason.

## talent/
**jds/** — 12 `.txt` job descriptions (one per role) with required skills.
**resumes/** — 60 `.txt` resumes, each written to a target role at strong/medium/weak strength.
Match truth: `ground_truth/resume_jd_truth.csv` — `resume_id, best_match_jd, target_role, match_label, skill_overlap`.

## knowledge/
**corpus/** — 39 `.md` policy/SOP/FAQ/circular/meeting-note documents with concrete facts (leave days, tolerances, limits, temperatures). For RAG / search / summarisation.
**qa_examples.csv** (13) — `question, expected_doc, answer`. A starter eval set for a policy chatbot.

## ground_truth/
`promo_true_elasticities.csv` (6) · `planted_invoice_issues.csv` (659) · `attrition_drivers.md` · `resume_jd_truth.csv` (60). **Validation only.**
