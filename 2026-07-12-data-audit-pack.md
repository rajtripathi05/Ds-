# Week-1 Data Audit Pack — AI Transformation Blueprint · DS Group
**RAJ · 12 July 2026** · The execution bridge: every registered estimate (E1–E14) mapped to the exact extract that replaces it, its likely owner, an acceptance check, and the case numbers it re-bases. Goal: by day 10, the blueprint's aggregator runs on actuals, not assumptions.

## How to use
Request each extract below in week 1 (read-only, sampled where sensitive). When an extract lands, run its acceptance check, update the estimate register, and re-run the aggregator (blueprint Tab 4). Anything that fails acceptance gets a data-quality ticket before any model work — this is exactly the "resilience first" pattern the prototypes implement.

## Estimate → extract map
| E# | Assumption today | Extract to request (system) | Likely owner | Acceptance check | Re-bases |
|----|------------------|------------------------------|--------------|------------------|----------|
| E1 | ≈6,000 employees; ≈3,000 desk; ≈20 planners | Headcount by function/grade/location (HRMS) | CHRO office | Totals tie to payroll count ±2%; desk/field split defined | Cases 1, 2, 3, 6 hour-lines |
| E2 | Loaded costs ₹250–600/hr; build ₹8–10L/FTE-mo | Loaded-cost table by grade (Finance); actual vendor/GCC day-rates | CFO office | Finance sign-off memo | Every ₹ line |
| E3 | 10–20% relative WMAPE improvement | 24 mo secondary sales SKU×distributor×week (DMS) + current forecast archive if any | Sales ops / SC planning | ≥90% week-completeness per active distributor; spine ties to invoiced qty | Case 1 benefit A |
| E4 | 30–45 days cover; 10–12% carrying; 8–15% cut | FG + depot + distributor inventory snapshots, 12 mo (ERP/DMS); cost of capital | Supply chain + Treasury | Inventory identity holds (closing=opening+in−out) on sample | Cases 1, 4; one-time cash |
| E5 | Trade spend 8–12% of branded revenue | Scheme/trade-spend ledger by category, FY25 (ERP/TPM) | Sales finance | Ties to GL trade-spend heads ±5% | Case 3 leakage base |
| E6 | ~70k docs/yr; 12 min handling; 65–80% STP | AP invoice + GRN + claim counts, FY25, by entity (ERP); AP team time study (1 week sample) | Finance shared services | Doc counts from system logs, not memory; time study n≥30 | Case 3 |
| E7 | ₹15–25 cr production spend; 30–50% adaptation | Agency/production PO ledger FY25 tagged production-vs-media | Marketing procurement | Ties to marketing GL ±10% | Case 5 |
| E8 | 3 contacts/wk/distributor; 6 min; 50% containment | Telecaller/call-centre logs 3 mo; distributor mobile registry hygiene report | Sales ops / CS | Log-derived frequency distribution; registry ≥90% reachable | Case 6 |
| E9 | Shelf-vision & QC pilot norms | Third-party audit contracts + defect/rework logs on candidate lines | Sales dev / Plant heads | Baseline defect % from 3-mo logs | Cases 7, 8 |
| E10 | API/infra run-costs | Current cloud/API invoices; volume projections | IT | Unit-priced against live rate cards | Run-cost lines |
| E11 | Pilot slices (₹800 cr / ₹3,000 cr) | Divisional P&L category revenue FY25 | Category finance | Ties to audited segment totals | Cases 1, 4 scopes |
| E12 | 40% adoption; 30 min/wk saved; 20k tickets | HR/IT ticket volumes FY25 (ITSM); intranet search logs if any | IT + HR | System-report counts | Case 2 |
| E13 | ₹6 cr month-12 gate | (Derived — recompute after E1–E12 land) | AI Council | Gate reset memo signed | Roadmap gate |
| E14 | "21 units / 12 agri / 24 depots" directory claim | Authoritative site list: own + leased + co-packer (Manufacturing head office) | Operations | One list, one owner, dated | Footprint statements |

## Day-by-day (two weeks)
**D1–2** kickoff, access requests, NDAs/read-only roles · **D3–5** E3/E4/E6 extracts land (the big three), identity + completeness checks run · **D6–8** E1/E2/E5/E7/E8 land; time study starts · **D9–10** first re-based aggregator run; estimate register updated; portfolio re-scored; gate memo (E13) drafted · **D11–14** data-quality tickets triaged; Phase-0 pilot scopes frozen on actuals.

## Templates (governance pillar 4 & 5, ready to copy)
### Model card (one per production model)
```
Model: <name/version>            Owner (business): <name>   Owner (technical): <name>
Purpose & decision supported:    Tier: Assist / Augment / Automate
Training/grounding data:         Refresh cadence:
Eval results (frozen set):       Known failure modes:
Drift monitors & thresholds:     Fallback (manual process):
Last review date:                Next council review:
```
### Decision-log schema (Tier-2/3 actions — immutable, audit-replayable)
```
ts | system | model_version | input_ref | extracted_fields_hash | rule_fired | confidence |
decision (approve/route/reject/act) | human_id (if any) | override? | override_reason | outcome_ref
```
*Retention: 7 years for financial decisions (align with audit policy); PII minimised at write time.*

---
*Every row above replaces an ESTIMATE with a fact. Until then, the blueprint's numbers remain labelled estimates — that's the point of the labels.*
