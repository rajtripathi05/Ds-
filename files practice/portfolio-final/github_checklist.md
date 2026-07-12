# GITHUB PUBLISH CHECKLIST
*Bundles are complete git histories saved in each repo root (mount couldn't host .git; see each
repo's ASSUMPTIONS). Publishing = clone the bundle, add remote, push.*

## Repo names
| local folder | GitHub repo | one-line description (repo tagline) |
|---|---|---|
| ds-demand-cockpit | `fmcg-demand-cockpit` | Hierarchical forecasting + causal promo ROI + constrained S&OP what-if cockpit — gate-tested, offline, synthetic bed |
| ds-copilot | `governed-enterprise-copilot` | Role-scoped RAG + validated text-to-SQL, 25/25 eval, zero leaks — no API keys required |
| ds-doc-to-decision | `doc-to-decision` | 3-way-match invoice automation: rules decide, calibrated gate, learning loop 0→67.5% STP |

## Publish commands (per repo; example: cockpit)
```bash
# 1. clone the bundle into a fresh working copy (full history comes with it)
git clone "ds-demand-cockpit/ds-demand-cockpit/ds-cockpit.gitbundle" fmcg-demand-cockpit
cd fmcg-demand-cockpit

# 2. hygiene sweep BEFORE the remote exists
git log --oneline                # sanity: milestone commits present
grep -RIn --exclude-dir=.git -iE "api[_-]?key|secret|token|password" . || echo clean
rm -f *.gitbundle                # don't ship the bundle inside the repo
# out/ artifacts: KEEP small result JSONs/pngs referenced by README; delete out/cache/

# 3. publish
git remote add origin git@github.com:<username>/fmcg-demand-cockpit.git
git push -u origin master
```
Repeat with `ds-copilot.gitbundle → governed-enterprise-copilot` and
`ds-doc-to-decision.gitbundle → doc-to-decision`.

## Every README's top screen MUST show (before any scrolling)
1. **Hero image** — GAP G2: current screenshots are matplotlib data renders; spend 5 minutes
   on your machine first: run each server, take REAL browser screenshots (cockpit what-if,
   copilot role-flip pair, exception queue), save as `screenshots/hero.png`, commit.
2. **Three measured numbers** (already in each README's results table — surface them as badges/bold):
   cockpit `8.98% vs 18.27% WMAPE · ties 0.0 · what-if ≤31 ms` · copilot `25/25 eval · 0 role
   leaks · injection refused` · doc-robot `40/40 decisions · 13/13 planted caught · STP 0→67.5%`.
3. **The honesty line, verbatim:** "Built and measured on a synthetic test bed with planted
   ground truth — methods and engineering, not production results."
4. **The independence line:** "Independent portfolio project — not affiliated with, or endorsed
   by, DS Group. All domain facts from cited public sources."

## Exclude / check before push
- [ ] `*.gitbundle` files (history is in git itself once cloned)
- [ ] `out/cache/`, `__pycache__/` (gitignored already — verify)
- [ ] any machine-specific paths in docs (`/sessions/...` appears in ASSUMPTIONS/BLOCKERS —
      acceptable as build-log honesty, but skim once)
- [ ] reference/ placeholder txt is fine to keep; do NOT publish your real IGL CLAUDE.md
      (company material) — keep Prototype #0 as the bridge note only
- [ ] secrets grep (step 2) is clean in all three

## Pinned-repos layout (profile order)
1. `fmcg-demand-cockpit` — the flagship (deepest ML)
2. `governed-enterprise-copilot` — the governance story
3. `doc-to-decision` — the automation-with-audit story
4. (optional 4th pin) a gist/page hosting the blueprint HTML suite — link it from all three READMEs
Profile README one-liner: "I build decision systems with deterministic truth layers and test
gates. Three FMCG prototypes below — every number measured, every failure logged."
