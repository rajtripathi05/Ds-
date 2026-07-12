# Turn on the AI layer (optional) — OpenRouter, ~$5 is plenty

The three demos run fully offline in **rules mode** with no key. Adding an OpenRouter key switches on
an **optional LLM layer** that only *phrases and parses* — the deterministic cores still decide, so
every gate/citation/rule stays intact. A $5 budget on the default model (`openai/gpt-4o-mini`,
~$0.15 / $0.60 per million tokens) is **thousands of demo calls**; a hard budget guard stops calling
the API at $5 and silently falls back to rules mode.

## Where to paste the key (ONE place)
1. Get a key at **https://openrouter.ai/keys** (looks like `sk-or-v1-…`).
2. Open **`openrouter_key.txt`** in the `files practice` folder.
3. **Delete everything** in it and paste **just the key** on the first line. Save.
   *(That file is git-ignored, so the key never gets published.)*
4. Double-click **`TEST_LLM_KEY.bat`** → it makes one cheap call and prints `LLM CONNECTED`.
5. Close the three server windows and double-click **`START_ALL.bat`** again. Each app's header now
   shows **✨ AI layer ON** with a live `$spent / $5` counter.

Prefer an environment variable? Set `OPENROUTER_API_KEY` instead and skip the file.

## What the AI layer adds (per app)
- **ds-copilot** — answers are rewritten to read naturally, but **every citation is preserved** (if the
  model drops one, the system reverts to the exact extractive answer). A ✨ badge + per-answer cost shows.
- **ds-demand-cockpit** — a **natural-language what-if** box: type *"run a 20% consumer promo on
  Confectionery for weeks 1–2 and cut the budget to 80%"* → the model fills the levers → the **same
  deterministic reconcile+optimize** runs. It only translates words to levers.
- **ds-doc-to-decision** — each queued exception gets a one-line **plain-English explanation** of why the
  rule routed it (the rule still made the decision; the LLM just explains it). Cached per reason code, so
  it costs almost nothing.

## Change the model or budget
Edit `openrouter_config.json` inside any repo (e.g. `ds-copilot/ds-copilot/openrouter_config.json`):
```json
{ "enabled": true, "model": "openai/gpt-4o-mini", "budget_usd": 5.0, "max_tokens": 400 }
```
Cheaper/free options you can drop in as `model`: `google/gemini-2.0-flash-lite-001`,
`deepseek/deepseek-chat`, or a free one like `meta-llama/llama-3.3-70b-instruct:free`.
Spend is tracked per app in `out/llm_ledger.json`.

## Honesty
This layer was built and wired with graceful fallback and verified to leave **rules-mode behaviour
identical** (copilot still 25/25, zero leaks; cockpit gates unchanged; doc-robot 40/40). The live LLM
path itself needs your key to exercise — `TEST_LLM_KEY.bat` is the one-command proof.
