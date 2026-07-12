# ds-copilot — Enterprise Agentic Copilot (rules mode, fully offline)
*A role-scoped copilot that answers from a governed 24-doc corpus WITH citations and from a
sqlite spine WITH validated SQL — deterministic (no LLM key needed), gated by a 25-question eval.*
**Synthetic corpus & data; no company internal information.**

## The problem
Company knowledge lives in policies nobody can find and databases nobody may touch. Generic
chatbots fail on the three hard parts: *prove it* (citations), *scope it* (who may see margins?),
and *govern it* (SQL that can't go rogue).

## Architecture (laws in CLAUDE.md, enforced in code)
```
data/corpus (24 docs, front-matter access tags)     db/*.csv → sqlite (read-only URI)
        │                                                   │
corpus.py  manifest + version families            semantic.yaml  ← THE only SQL surface
        │                                                   │      (metrics/dims, exec: true tags)
retrieve.py  BM25(×3-title) + TF-IDF hybrid,      sqlgen.py  NL→plan→SQL; validator (allow-lists,
   role-filtered index (exec docs absent for ops)     SELECT-only, LIMIT) + sqlite AUTHORIZER at
        │                                             the driver (denies exec columns for ops)
answer.py  extractive cited answers · newer-version-wins citing both · table flattening ·
   clause decomposition for conjunctive asks · guardrails (PII / injection / out-of-scope)
        │
planner.py  router: guards → docs/SQL/both → chart; VISIBLE tool trace on every answer
server.py + ui/  chat with role flip, citation chips, expandable ⛓ trace, inline charts
tests/  gates M0–M5 + eval_harness (canonical CI) + ui_walk + screenshots
```

## MEASURED results (this repo, this session — EVAL_RESULTS.md)
| Gate | Result |
|---|---|
| Eval harness | **25/25** (baseline 15/25 → fixes logged in PROGRESS.md; checkers keyed to dataset ground truth + its own source_docs) |
| Role leaks | **0 across all 5 role-split questions at every iteration** — enforced at retrieval (exec docs absent from ops index) AND at the sqlite driver (authorizer denies exec columns) |
| RF-02 prompt injection | REFUSED with logging language; PII (RF-01) and out-of-scope (RF-03) refused |
| Version conflict | 2025 leave policy wins, both versions cited (M1 gate 6/6) |
| Buried details | both found (21-day expense window; 30-day claim + ±2% tolerance) |
| Validated SQL | blocked table, blocked column, and write attempts refused at two layers (M2 gate 8/8); LIMIT always enforced |
| Agentic ask | "Why did North-zone Rajnigandha volumes drop in early 2025?" → SQL trend (−6.3% Jan→Jun) + price circular cited + rendered chart, all in one traced answer (M3 gate 5/5) |
| UI walk | 4/4 against the live server with the real UI JS |

## Run it
```bash
python3 src/db.py          # build sqlite spine (297,610-row sales table)
python3 src/server.py      # chat on http://localhost:8770  (role toggle top-right)
python3 tests/eval_harness.py   # canonical CI: 25/25 expected
```
Stack: pandas + numpy + matplotlib + stdlib sqlite3/http.server. No network, no keys (C1).
Git history: `ds-copilot.gitbundle`.

## What production adds
Dense embeddings + reranker behind the same hybrid interface; an LLM rephrase/planner layer
behind a config flag (privacy law 5: query + snippets only), with token/latency logging; SSO-backed
roles; document owners/retention from a DMS; the action layer (draft distributor emails) behind
human approval per the kickoff's M6.

## Honesty
Rules mode was mandated and delivered; the eval's 15→25 climb came from fixing real bugs
(router hijacks, stemming, title boost, clause decomposition) with zero leaks throughout —
PROGRESS.md is the audit trail; BLOCKERS.md lists what the offline sandbox forced around.
