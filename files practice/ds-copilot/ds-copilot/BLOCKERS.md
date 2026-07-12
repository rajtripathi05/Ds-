# BLOCKERS.md — honest record
| # | Spec item | What happened | What was done instead | Evidence |
|---|-----------|---------------|----------------------|----------|
| K1 | Playwright headless UI + browser screenshots (M6) | pip/npm blocked (403); no browser binary | tests/ui_walk.mjs runs the REAL UI JavaScript against the LIVE server (ask→cite→role-flip→refusal→chart, 4/4 GREEN); screenshots/ = matplotlib transcript renders of real copilot responses, labelled as renders | PROGRESS.md, screenshots/ |
| K2 | Embeddings in hybrid retrieval | No installable embedding model offline | TF-IDF cosine as the dense leg beside BM25 (C2); eval hit 25/25 without embeddings | EVAL_RESULTS.md |
| K3 | FastAPI/Flask | pip blocked | stdlib ThreadingHTTPServer (same pattern as ds-demand-cockpit) | src/server.py |
| K4 | Optional LLM rephrase layer (override 5) | No API key in environment | Rules mode throughout, as the override directs; config flag point documented in README for when a key exists | README.md |
| K5 | sqlite on the cloud-synced mount | disk I/O error (journal/locks) | DSCOPILOT_DB env override; default path works on normal machines (C7) | src/db.py |
No gate was weakened, mocked, or reworded. Eval improved 15→20→23→24→25 by fixing real retrieval/routing bugs; zero role leaks at every iteration.
