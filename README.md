<p align="center">
  <img src="assets/goat.svg" alt="A goat climbing a rising growth chart" width="100%">
</p>

<h1 align="center">DS Group — AI Transformation Blueprint</h1>

<p align="center">
  <em>30 AI use cases, scored and prioritised — and the three that were actually built to prove the numbers.</em>
</p>

---

Most AI strategy decks stop at the slide. This one ships the code: three working prototypes sit behind the three biggest business cases, so the claims can be checked rather than believed.

## For the business

**The problem.** An FMCG business knows AI *should* help — but not where, worth how much, or in what order. Vendor decks assert; nobody verifies.

**What this is.** A prioritised portfolio of 30 use cases, scored on value / feasibility / data-readiness / risk, with the top 8 written up as one-page business cases. Three of them were built end-to-end to test whether the estimates survive contact with real code.

| Prototype | The business problem | Verified result |
|---|---|---|
| **Demand Cockpit** | Planners guess what will sell; promos get run on instinct | Forecast error **9.0%** vs **18.3%** for the usual method. Test a promo before committing — answer in **~12 ms** |
| **Company Assistant** | Staff can't find answers across policies + data; sensitive numbers leak | Every answer **cited**. Margin data is **refused** to Operations, **served** to Executives — enforced, not promised |
| **Invoice Checker** | Every invoice gets human eyes, most for no reason | **67.5%** clear automatically. Humans see only the **8 of 40** that genuinely need judgement |

**Modelled portfolio value: ₹9.7 cr (conservative) / ₹17.9 cr (base) / ₹26.2 cr (aggressive)** net per year.
These are *estimates*, not measured results — every input is traced in [`ASSUMPTIONS.md`](ASSUMPTIONS.md), and the week-1 plan to re-base them against real extracts is in [`2026-07-12-data-audit-pack.md`](2026-07-12-data-audit-pack.md). The prototype metrics in the table above **are** measured.

**Start here:** [`2026-07-12-portfolio-home.html`](2026-07-12-portfolio-home.html) → the blueprint → the 14-slide board deck.

## For engineers

Three independent Python services, no cloud dependency, no API key required. Each runs deterministic **rules-mode** by default; an optional LLM layer is strictly additive.

| Service | Port | Core idea |
|---|---|---|
| [`ds-demand-cockpit`](files%20practice/ds-demand-cockpit) | `8765` | Hierarchical forecast (champion-mix per SKU) → elasticities recovered from matched-control promo analysis → LP optimiser under capacity + cash-budget constraints. Every scenario **reconciles** before it renders. |
| [`ds-copilot`](files%20practice/ds-copilot) | `8770` | Governed RAG + text-to-SQL. A semantic layer is the only queryable surface; SQL is validated read-only against allow-lists **before** execution. Role scope is enforced twice — retrieval tags *and* column policy. No citation, no claim. |
| [`ds-doc-to-decision`](files%20practice/ds-doc-to-decision) | `8780` | Invoice→PO→GRN matching with **Platt-calibrated** confidence (Brier 0.266 → 0.215). Human decisions retune the auto-approve gate, capped at 0.06/round — trust is earned gradually, not granted. |

```bash
cd "files practice"
python -m pip install pandas numpy matplotlib openpyxl        # Python 3.12

# each in its own shell
cd ds-demand-cockpit/ds-demand-cockpit   && python src/server.py                          # :8765
cd ds-copilot/ds-copilot                 && python src/db.py      && python src/server.py 8770
cd ds-doc-to-decision/ds-doc-to-decision && python src/calibrate.py && python src/server.py 8780
```

On Windows, `START_ALL.bat` does all of the above and opens `HOME.html`. Optional LLM features: copy `openrouter_key.example.txt` → `openrouter_key.txt` (gitignored) and see [`SETUP_LLM.md`](files%20practice/SETUP_LLM.md).

## Honest limits

- **Data is synthetic** (seeded generators, `SEED=42`). The pipelines are real; the numbers they produce describe generated data, not DS Group's books.
- **The ₹ figures are modelled**, and deliberately not presented as measured. Two source claims were downgraded during self-review rather than defended — see [`REDTEAM_FIXES.md`](REDTEAM_FIXES.md).
- Prototypes are demonstrators, not production systems: no auth, no HA, single-node, `127.0.0.1` only.

## Repo map

| Path | What |
|---|---|
| `2026-07-12-ds-blueprint-v2.html` | Master artifact — 7 tabs, live ROI aggregator, interactive prioritiser |
| `2026-07-12-blueprint-deck.html` | 14-slide board deck (print-to-PDF clean) |
| `2026-07-12-exec-onepager.md` | 3-minute CXO memo |
| `files practice/` | The three prototypes + `START_ALL.bat` |
| `MORNING_REPORT.md` · `REDTEAM_FIXES.md` · `ASSUMPTIONS.md` | Audit trail — what was built, what was wrong, what was assumed |
