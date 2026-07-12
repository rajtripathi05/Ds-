# RESUME PACK — RAJ
*Every number below is quoted from a results file in this portfolio (BACKTEST.md, EVAL_RESULTS.md,
DECISIONS.md, CI_RESULTS.md, out/m5_loop.json, out/roi.json). Mandatory companion sentence
wherever these bullets are pasted: "All three systems were built and measured on a synthetic
test bed with planted ground truth; independent work, not affiliated with DS Group."*

## 8 quantified bullets — engineer flavour (E) and leadership flavour (L)

1. **Demand forecasting.**
   E: Built a hierarchical FMCG forecasting engine (ETS + global ridge + Croston/TSB, MinT
   reconciliation) that cut WMAPE to **8.98% vs 18.27% seasonal-naive at SKU level** (6.55% vs
   15.89% at category) on 5-fold rolling-origin backtests over a 297,610-row spine.
   L: Halved forecast error vs the standard baseline on a full FMCG demand spine — and published
   the backtest protocol so the number can be attacked, not just admired.

2. **Causal promo measurement.**
   E: Recovered per-category price elasticities from promo data via matched-control causal
   analysis to **within ≤17% of generative truth in all 6 categories**, then priced promo ROI in ₹.
   L: Replaced correlation-driven trade-spend claims with a causal method proven against known
   ground truth — the discipline FMCG promo budgets usually lack.

3. **Constrained S&OP optimisation.**
   E: Built an exact allocation optimizer that names its binding constraint and shadow price
   (stress test: working-capital budget @100% utilisation, **₹0.215 margin per budget rupee**);
   what-if → reconcile → optimize round trip measured at **≤31 ms**.
   L: Gave planners a cockpit where every scenario is validated before it can be believed —
   sub-second answers, zero bypass paths.

4. **Governed enterprise RAG.**
   E: Shipped a role-scoped copilot (BM25+TF-IDF hybrid, extractive citations, validated
   text-to-SQL with a sqlite driver-level authorizer) scoring **25/25 on a 25-question eval with
   zero role leaks** across all role-split questions and a refused prompt-injection test.
   L: Proved "AI with access control" is buildable: the same margin question answers for an
   executive and refuses—with reasons—for operations, enforced at two independent layers.

5. **Document-to-decision automation.**
   E: Built 3-way-match automation (PO/GRN/invoice) with a hand-rolled PDF extractor at **100%
   amount-field accuracy (282/282 on both TXT and PDF paths)** and rules-as-code decisions:
   **40/40 vs ground truth end-to-end, 13/13 planted discrepancies caught**.
   L: Delivered audit-grade invoice automation where written rules — not the model — decide,
   and every decision carries its named failing check.

6. **Learning-loop operations.**
   E: Designed a calibrated confidence gate (Platt, holdout Brier 0.266→0.215) whose threshold
   learns from human overrides: **STP 0%→67.5% across staged rounds with zero auto-approve
   errors** and **0 false approvals at 12% input corruption**.
   L: Showed automation that earns trust instead of assuming it — throughput tripled-then-some
   while the error budget stayed at zero.

7. **Engineering discipline / AI governance.**
   E: Every build gate-controlled in git (31 commits across 3 repos) with anti-fabrication CI:
   ground truth machine-verifiably absent from decision code (grep-enforced), red-team logs, and
   honest RED→GREEN iteration trails (e.g., copilot eval 15→25).
   L: Institutionalised "measured beats claimed": no gate weakened, failures documented, two
   premature success claims caught and corrected in-history — governance as practice, not policy.

8. **Strategy-to-system leadership.**
   E: Authored a 30-use-case AI blueprint (interactive scoring matrix, ROI aggregator) and then
   personally built the top-3 use cases as working systems in three overnight builds.
   L: Took an FMCG AI strategy from board deck to three demonstrable systems — 19 verified public
   facts, 14 registered estimates, and a 12-month gate-controlled roadmap a CFO can stop cheaply.

## LinkedIn About (120 words)
I build decision systems the way plants run: a deterministic truth layer, one-way state, and
no change that bypasses validation. At India Glycols I lead digital-twin work for continuous
process operations; on my own time I stress-test the same pattern elsewhere — most recently an
FMCG suite: a demand cockpit that halved forecast error vs baseline (8.98% vs 18.27% WMAPE), a
role-scoped copilot that went 25/25 on its eval with zero permission leaks, and invoice
automation that matched ground truth 40/40 while raising straight-through processing from 0% to
67.5% with zero errors — all on synthetic test beds with planted truth, all gate-tested in git.
I like measured numbers, named constraints, and systems that refuse politely.

## Cover note — DS Group AGM (AI/ML) role (200 words)
Dear Hiring Team,

I'm applying for the AGM role with something more concrete than enthusiasm: a role-specific
portfolio I built independently to test whether I could do this job before asking you to bet on
it. It contains a 30-use-case AI strategy for a company of DS Group's shape — every public fact
cited, every estimate labelled — and working prototypes of the three use cases I'd start with:
a demand/S&OP cockpit (WMAPE 8.98% vs 18.27% baseline), a governed GenAI copilot with RAG and
role-scoped SQL (25/25 eval, zero leaks, prompt-injection refused), and document automation
(40/40 decisions vs ground truth, STP 0→67.5% with zero errors). All were built and measured on
synthetic test beds with planted ground truth — I claim the methods and the engineering, not
production results. My day job is digital-twin and analytics leadership at India Glycols, where
the same laws — deterministic truth, human-in-the-loop, audit everything — run a real plant.
I'd welcome the chance to walk you through a 10-minute live demo and the honest BLOCKERS files.
This is independent work, not affiliated with DS Group.

Regards, RAJ
