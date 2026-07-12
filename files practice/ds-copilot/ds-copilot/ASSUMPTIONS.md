# ASSUMPTIONS — ds-copilot build
| # | Ambiguity | Decision | Why defensible |
|---|-----------|----------|----------------|
| C1 | pip blocked; no LLM key in env | Pure rules mode (override 5): hand-rolled BM25+TF-IDF hybrid, extractive cited answers, template text-to-SQL on stdlib sqlite3; no embeddings (install-clean impossible) | Explicitly sanctioned by tonight's override 5 |
| C2 | "embed" in kickoff M1 | TF-IDF cosine stands in for dense embeddings in the hybrid (BM25 0.65 + TFIDF 0.35) | Nearest offline equivalent, logged |
| C3 | Git on this mount fails (proven in cockpit build) | separate-git-dir + ds-copilot.gitbundle refreshed at milestones | Same B8 pattern, durable history |
| C4 | Eval answers are free-text | Harness checks = per-question key-fact regexes derived from ground_truth + required citations + role-leak deny-scan; checks written BEFORE tuning and committed | Measurable, anti-fabrication |
| C5 | M6 kickoff mentions router/actions; tonight's M6 = chat UI + walk | Tonight's explicit definition wins; router noted in README as production add | Instruction overrides kickoff where they conflict |
| C6 | No browser installable | UI verified by real-JS walk against live server + rendered transcript PNGs (cockpit B3 pattern) | Honest offline maximum |
| C7 | The cloud-synced mount cannot host sqlite either (disk I/O error on journal/locks — same class as the git issue) | DB path honours env DSCOPILOT_DB; in this sandbox it points to local scratch; on a normal machine the default ./out/copilot.db just works. Documented in README run section | Same B8-style workaround; zero code difference for the user |
