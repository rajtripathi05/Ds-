# Deploy & publish

## Why Netlify was blank / erroring
1. **No `index.html` at the repo root** → Netlify had nothing to serve at `/` (blank page / 404). **Fixed:** a hand-written static `index.html` is now the landing page.
2. **The three apps are Python servers** (ports 8765/8770/8780). Netlify is *static hosting* — it cannot run Python, so any `localhost` links break once hosted. **Fixed:** the hosted page **showcases** the apps with screenshots + a "run locally" quick-start, and never links to `localhost`. The **strategy documents** (blueprint, deck, one-pager) are pure HTML and work perfectly on Netlify.
3. **Heavy backup files** (`*.gitbundle`, ~81 MB) were bloating the repo. **Fixed:** they're now git-ignored and removed from tracking.

## What's hosted vs. local
| Works on Netlify (static) | Runs locally only (Python) |
|---|---|
| `index.html` (landing) · `2026-07-12-fmcg-blueprint.html` · `-blueprint-deck.html` · `-exec-onepager.html` · `-portfolio-home.html` | Demand Cockpit · Company Assistant · Invoice Checker (`files practice/START_ALL.bat`) |

`netlify.toml` sets `publish = "."`, an empty build command (nothing to compile), a soft-404 fallback to `index.html`, and basic security headers.

## Publish it (one block — run in the repo root)
```bash
cd "C:\Users\ai\OneDrive - INDIA GLYCOLS LIMITED\Desktop\claude cowork playground\Practice"

# drop the heavy backup bundles from the repo (kept locally, just untracked)
git rm --cached --ignore-unmatch "files practice/ds-demand-cockpit/ds-demand-cockpit/ds-cockpit.gitbundle" "files practice/ds-copilot/ds-copilot/ds-copilot.gitbundle" "files practice/ds-doc-to-decision/ds-doc-to-decision/ds-doc-to-decision.gitbundle"

git add -A
git commit -m "De-brand to FMCG; next-level README; add index.html + netlify.toml; accessible UI redesign; optional AI layer"
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
