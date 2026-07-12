# MORNING REPORT — ds-copilot overnight build
_M0–M6 GREEN · eval 25/25 · zero role leaks · runnable at every commit · history in ds-copilot.gitbundle_

## Gate table (all measured this session)
| Gate | Result |
|---|---|
| M0 corpus+db loaders | GREEN — 24 docs w/ access tags, version family detected, sqlite 297,610 rows |
| M1 cited retrieval + version conflict | GREEN 6/6 — 2025 policy wins citing both; honest no-citation path (raw-BM25 floor) |
| M2 semantic layer + validated SQL | GREEN 8/8 — validator + sqlite driver authorizer; blocked table/column/write refused; LIMIT enforced |
| M3 agent planner | GREEN 5/5 — Rajnigandha why-question: SQL (−6.3% Jan→Jun 2025) + price circular cited + chart, visible trace |
| M4 dual-layer roles | GREEN 7/7 — same margin question: exec answers w/ memo cite, ops refused; leak tests at retrieval AND SQL |
| M5 eval harness | GREEN — **25/25**, zero leaks on all 5 role-splits, RF-02 refused, both buried answers found |
| M6 UI + walk + screenshots | GREEN — chat UI with role flip/citation chips/trace/charts; real-JS walk 4/4 vs live server; 5 transcript renders |

## The honest story you should read first
1. **EVAL_RESULTS.md** — per-question pass/fail. Baseline was 15/25; the climb to 25 is documented fix-by-fix in PROGRESS.md (router hijack, stemming, ops finance-scope refusal, clause decomposition, title boost). Zero leaks at every stage — the security invariant never wobbled.
2. **Commit-message mistakes, owned**: TWO early commits (5c91f4b, 208b67a) claimed "M1 GREEN" while the gate was still red — the commit command ran before/despite the check. The true green is b92fd33, and this red-team sweep caught the second instance. All three remain in history; the lesson (gate exit code must gate the message) is now in CLAUDE.md.
3. **The UI**: `python3 src/server.py` → ask the margin question as Operations, flip to Executive, ask again — then expand the ⛓ tool trace.

## Honest gaps (BLOCKERS.md)
No browser/embeddings/LLM key offline → real-JS walk + TF-IDF hybrid + rules mode (all sanctioned by override 5); sqlite/git need env-pathed workarounds on this cloud mount only.

## With more time
Embedding+reranker leg; LLM rephrase behind the config flag with the privacy contract; action drafting behind approval; richer NL→SQL grammar (joins on promo/calendar); eval expansion beyond the planted 25.
