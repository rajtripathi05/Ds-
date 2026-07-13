# Deploy & publish

## Why Netlify was blank / erroring — and what changed
1. **No `index.html` at the repo root** → Netlify had nothing to serve at `/` (blank page / 404). **Fixed:** a polished, business-first `index.html` is now the landing page — animated stats, a live ROI model, and three **Launch live demo** buttons.
2. **The three apps were Python servers** (ports 8765/8770/8780). Netlify is *static hosting* — it can't run Python. **Fixed:** each app now has a **fully client-side, browser-playable demo** under `demo/` that reads the **real engine output** (extracted by `files practice/build_demo_data.py`, de-branded, inlined into each page so it works on Netlify *and* offline). Visitors can actually drag the cockpit sliders, flip the assistant's role gate, and work the invoice queue — no server, no `localhost`.
3. **Heavy backup files** (`*.gitbundle`, ~81 MB) were bloating the repo. **Fixed:** git-ignored and removed from tracking.

## What's on the hosted site now
| Page | What a visitor can do |
|---|---|
| `index.html` | Landing — stats, live ROI scenario model, links into everything |
| `demo/cockpit/index.html` | **Playable** — price/demand sliders recompute via real elasticities; role gate hides ₹ |
| `demo/assistant/index.html` | **Playable** — 25 real cited answers; flip role → confidential Qs refuse vs answer; open sources |
| `demo/invoice/index.html` | **Playable** — work the review queue, approve/reject, answer key revealed |
| `data.html` | **Browse the dataset** — 6 datasets, ~978k rows, real preview tables + downloads |
| `2026-07-12-*.html` | Blueprint, board deck, one-pager, portfolio home |
| `showcase.html` | Screenshots + one-command local run for the **full** Python systems |

The full Python systems (with the LP solver, SQLite DB and test gates) still run locally via `files practice/START_ALL.bat`; the browser demos show the decision surface, the local apps run the complete engine.

`netlify.toml` sets `publish = "."`, an empty build command, a soft-404 fallback to `index.html` (real files/dirs always win, so `demo/*` resolve directly), and basic security headers.

## The synthetic dataset (integrated)
`synthetic-data/` is one seeded fictional FMCG company feeding every "implement-now" use-case (sales, promotions, AP invoices, HR/attrition, resumes+JDs, knowledge corpus) — each with planted signal + ground truth. It's surfaced on the site at **`data.html`** (linked from the landing page) with real preview tables and downloads.
**Deploy hygiene:** the full **81 MB** `synthetic-data/sales/sales_secondary.csv` is **git-ignored** (too big for GitHub/Netlify) and is regenerable via `generate_all.py`; a committed **5,000-row sample** (`sales_secondary_sample.csv`) backs the hosted page. All other datasets (~4 MB total) are committed.

## Publish it (one block — run in the repo root)
```bash
cd "C:\Users\ai\OneDrive - INDIA GLYCOLS LIMITED\Desktop\claude cowork playground\Practice"

# drop the heavy backup bundles from the repo (kept locally, just untracked)
git rm --cached --ignore-unmatch "files practice/ds-demand-cockpit/ds-demand-cockpit/ds-cockpit.gitbundle" "files practice/ds-copilot/ds-copilot/ds-copilot.gitbundle" "files practice/ds-doc-to-decision/ds-doc-to-decision/ds-doc-to-decision.gitbundle"

git add -A
git commit -m "Integrate synthetic dataset (data.html + committed sample); demo logic/UI fixes; playable demos + landing"
git push
```
If your Netlify site is connected to this GitHub repo, the push auto-deploys and **https://fmcgai.netlify.app/** will show the new landing page within a minute.

## If Netlify still errors after the push
In the Netlify dashboard → **Site configuration → Build & deploy**:
- **Build command:** leave **empty**
- **Publish directory:** `.` (repo root)
- **Base directory:** empty

(`netlify.toml` already sets these, but clearing any leftover UI values avoids conflicts.) Then **Deploys → Trigger deploy → Clear cache and deploy site**.

## Optional tidy-ups (your call)
- **Rename the repo** `Ds-` → `fmcg-ai-portfolio`: GitHub → repo **Settings → rename**. GitHub auto-redirects old links, so nothing breaks. (I can't do this — it needs your GitHub account.)
- **Rename the `ds-*` service folders** to drop the prefix: this touches `START_ALL.bat`, the "View source" links, and your currently-running local apps, so it's best done with the apps stopped. Say the word and I'll do it as a focused, re-verified change.
