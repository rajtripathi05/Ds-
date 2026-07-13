# DS Group Production Cockpit — data upgrade (v1 → v2)

**Kept DS-branded** (Rajnigandha, DS Group, real segments/plants) — this is a private / interview-prep build, **not** wired into the public de-branded site. All numbers are realistic **synthetic** placeholders (DS Group publishes none).

## What was cleaned
- **`7_Washing_Matrix_Tidy`** — the raw reactor-washing sheet parsed as 30 "Unnamed" columns (a legend block + a from×to grid). Rebuilt into a tidy **729-row** table: `Line · From Product · To Product · Wash Code · Changeover Minutes`, with the legend decoded (NO=0, NF=120, ST=180, W1=90, W2=135, W3=315; compound codes like `ST/NF` summed). This is the sequence-dependent changeover cost the scheduler needs.
- **`2_Stock`** — the junk header `a` renamed to **Material Code**.

## What was added (all four upgrade areas)
| Area | Added |
|---|---|
| **Economics** | `Selling Price INR/KG` + `Std Margin %` on 135 packaged FGs; `Changeover Cost INR` on every washing transition (minutes × line rate) → the plan can now be **costed and margin-aware**. |
| **Capacity realism** | `Alternate Lines` per resource (same-family fallback) + `Planned Maint Days (90d)`; new **`11_Calendar`** sheet (3 shifts × 8h, 6-day week, 4 holidays) → realistic finite scheduling. |
| **Customer / service** | `Customer Priority` (1–3) + `OTIF Penalty INR/day` on every demand line → prioritised, penalty-aware scheduling. |
| **Historical actuals** | new **`12_Yield_Forecast_Actuals`** (yield variance ±pp, forecast bias %, MAPE % per FG) and **`13_Leadtime_Actuals`** (lead-time variance, on-time-PO % per component) → enables **validation** and **Monte-Carlo / probabilistic** planning. |

**Output:** `DS_GROUP_MASTER_MOCK_DATA_v2.xlsx` (13 working sheets) + `ds_master.json` / `ds_master_min.json` (compact, for the cockpit engine).

## Scenario calibration (v2 → planning-consistent)
The raw v1 mock had demand, plant capacity and RM stock generated independently, so the committed order book came out **~38× the tightest line's quarterly capacity** — every line read as thousands-of-% over and the plan was trivially infeasible. To make the cockpit tell a realistic story, the demand book and RM stock were **calibrated into one internally-consistent 90-day scenario** (per-line demand scaled to land 55–108 % utilisation; RM stock/open-POs scaled so a believable subset falls short). The engine itself is untouched — only the input quantities were fitted, and the same calibrated numbers are written back to the workbook so the **upload path matches**.

**Resulting reference plan** (what the cockpit shows on load): **OTIF 88.2 %**, binding line **DY-02 @ 108 %** (MF-03 103 %, FB-01 99 %), **19 RM shortages**, **₹61.2 cr** planned procurement, ~5.0 M kg demand. A real S&OP tension: one line over, a handful of materials to expedite, most orders shippable.

## The app — `ds-production-cockpit.html`
Deterministic MRP engine in the browser (no server). Tabs: **Overview** (KPIs + what-if levers), **Demand**, **Requirements** (BOM explosion), **Procurement** (planned POs, expedite flags), **Capacity** (line utilisation heat), **Economics** (role-gated ₹), **Validation**. **Operations** role hides every ₹; **Executive** unlocks them. What-if: demand ±%, take a line offline → re-solves instantly. Floating **AI copilot** (BYO OpenRouter key, shared with the rest of the site) can narrate the plan and answer "which POs do I expedite?".

**Run it:** `fetch()` needs a server, so from this folder: `python -m http.server 8000` → open `http://localhost:8000/ds-production-cockpit.html` (or just click **⬆ Workbook** and upload the v2 xlsx).

## What the Production Cockpit does with it
1. **Demand netting** — firm + forecast vs on-hand stock, per material.
2. **Multi-level BOM explosion** — FG → SFG → RM/PM gross requirements (verified: a 63,000 kg Rajnigandha order explodes to 9 components with correct quantities).
3. **MRP / procurement plan** — net vs RM stock + open POs; respect MOQ, order-multiple, domestic/import lead times → planned POs with **need-by dates, shortage & expedite flags** → lower working capital, fewer stockouts, less air-freight.
4. **Finite-capacity scheduling** — batches on lines with batch-cycle-time + **sequence-dependent washing** → feasibility, OTIF by due date, the binding constraint (line vs RM vs washing), makespan → more effective capacity, fewer changeovers.
5. **Shelf-life-aware** planning (less write-off), **economics** (material cost, margin, penalty), **Monte-Carlo** (demand/yield/lead-time → OTIF confidence), and an **AI copilot** (BYO OpenRouter key): *"which POs do I expedite to hit the 25-Sep Rajnigandha order?"*

Everything stays deterministic; the AI only proposes, the engine validates.
