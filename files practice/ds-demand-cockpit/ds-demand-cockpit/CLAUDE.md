# CLAUDE.md — ds-demand-cockpit (operating rules for any agent in this repo)
## Architecture laws (never break)
1. FROZEN FORECAST CORE — src/pipeline.py is the only writer of out/plan/*; everything else reads.
2. ONE-WAY STATE — cockpit/server never mutate the plan snapshot; scenarios live in out/scenarios/ as overlays.
3. RECONCILIATION IS TRUTH — every what-if = intent → validate → reconcile (hierarchy ties exactly) → optimize → respond. Nothing bypasses src/hierarchy.reconcile.
4. NEVER STOPS — loaders warn+fallback+badge; a data defect must never raise past src/loaders.py. Prove on *_messy.csv.
## Discipline (from reference/ IGL rules)
PLAN before execution; protect existing work (data/ read-only; new versions -v2, never overwrite); deliverables named YYYY-MM-DD-*; every task ends with a File Change Report in PROGRESS.md; measured numbers only — no adjective may substitute for a metric; gates are never weakened to pass (anti-fabrication rule of 2026-07-12 overnight instruction).
## Test gates
tests/run_tests.py is the single entry; a red gate is reported red in BACKTEST.md/BLOCKERS.md — an honest red beats a fake green.
