# KICKOFF — ds-copilot (GOAT 2: Enterprise Agentic Copilot)

You are my senior AI engineer. We are building "the company's second brain" for an FMCG major
(DS Group theme): a role-scoped agentic copilot that answers from documents WITH citations and
from a governed database WITH validated SQL — and can act behind approval.

KEEP-ALIVE + PROGRESS (mandatory, non-negotiable): my screen turns off after 5
minutes without visible activity (system sleep is already set to Never — this is display-off
only). Never go more than 3 minutes without a visible action: append a timestamped heartbeat
line to PROGRESS.md — current step, % done, next step — or open and close a file. Maintain
PROGRESS.md for the entire session; it doubles as the progress log I review.

OPERATING DISCIPLINE (from ./reference — my proven IGL rules): PLAN before
execution (objective / approach / affected files / risks) and WAIT for my approval; PROTECT
existing work (show diffs; never overwrite without explicit OK; new versions get -v2 suffix);
deliverable files named YYYY-MM-DD-descriptive-name.ext; END EVERY TASK with a File Change
Report (Created / Modified / Deleted + summary); ask instead of assuming.

FIRST ACTION: read ./data/corpus_manifest.json, skim ./data/corpus (24 docs), read ./db/schema.md
and ./data/eval_set.json, then give me the PLAN + repo CLAUDE.md and WAIT for approval.

DATA:
- ./data/corpus: 24 internal docs with front-matter access tags (all | exec_only). Planted:
  a version-conflict pair (leave policy 2023 vs 2025 — newer must win), a near-duplicate pair
  (travel policy vs FAQ), 2 buried answers (21-day expense window; 30-day claim window + ±2%
  tolerance), 2 EXEC-ONLY docs (margin memo, ROI note), spine-tied circulars (DS-MOUTRAJ-145
  price hike; 8 NE distributors live 2024-10-01; Pulse Blackcurrant DS-CONFPULSE-149 launch).
- ./data/eval_set.json: 25 questions with ground truth, source docs, expected behavior
  (answer / answer_newer_version / multi_doc / buried_detail / role_split / refuse /
  refuse_injection) and per-role expectations.
- ./db: product_master, location_master, calendar, promo_calendar, price_history, sku_costs,
  sales_secondary (297,610 rows) + schema.md. Price/margin/cost fields are EXEC-scoped.

ARCHITECTURE LAWS:
1. SEMANTIC LAYER IS TRUTH — define metrics/dimensions in a YAML semantic layer (e.g.
   secondary_qty, realized_revenue, margin[exec]); text-to-SQL generates ONLY against it; every
   query is validated (read-only, allowed tables/columns, row limits) BEFORE execution; the
   model phrases results, never invents a metric.
2. GROUNDED + CITED — RAG answers cite doc_ids; no citation → say so, don't claim.
3. ROLE-SCOPED — Operations NEVER receives pricing/margin/ROI/cost data: enforce at retrieval
   (access-tag filter) AND at SQL (column/table policy). Same question, two roles, two answers.
4. GUARDRAILS — PII refusal, prompt-injection defense (eval RF-02 must pass), out-of-scope refusal.
5. PRIVACY — model calls carry the query + retrieved snippets only, never the raw database.

BUILD ORDER (gated; PROGRESS.md heartbeat):
M0 Plan + CLAUDE.md. M1 Ingest→chunk→embed→hybrid retrieve+rerank; cited answers; version-
conflict logic (newer effective date wins, cite both). M2 Semantic layer + validated text-to-SQL
with a visible tool-trace. M3 Agent planner: decompose fuzzy asks ("why did North-zone
Rajnigandha drop in Q2-2025?") into doc+SQL tool calls; synthesize with citations; render a chart
when numeric. M4 Roles: login stub (Operations / Executive), enforcement at both layers, leak
tests. M5 EVAL HARNESS as CI: score all 25 eval questions (faithfulness, groundedness,
hallucination, role-leak, refusal correctness); regression report; target ≥23/25 with ZERO
role leaks. M6 Router (cheap default / frontier for hard; config-driven IDs; offline rules
mode; token+latency log) + action drafting (e.g. distributor email) strictly behind my approval.

Start with the PLAN.
