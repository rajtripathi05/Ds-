"""Optional OpenRouter LLM layer — config-flagged, budget-guarded, graceful fallback.
LAW: the LLM only PHRASES or PARSES; the deterministic cores still DECIDE. No key -> rules mode
(identical behaviour to before). Privacy: only the prompt built here is sent (question + already-
retrieved snippets), never raw data files or the database.
Key search order: env OPENROUTER_API_KEY  ->  <repo>/openrouter_key.txt  ->  <files practice>/openrouter_key.txt
"""
import os, json, time, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_CACHE = {}

def _key():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if k:
        return k
    for p in (REPO / "openrouter_key.txt", REPO.parent.parent / "openrouter_key.txt",
              REPO.parent / "openrouter_key.txt"):
        try:
            if p.exists():
                t = p.read_text(encoding="utf-8").strip()
                if t and not t.startswith("#"):
                    return t.splitlines()[0].strip()
        except Exception:
            pass
    return ""

_DEFAULT = {"enabled": True, "model": "openai/gpt-4o-mini", "budget_usd": 5.0,
            "price_in_per_m": 0.15, "price_out_per_m": 0.60, "max_tokens": 400, "timeout_s": 20}

def _cfg():
    c = dict(_DEFAULT)
    f = REPO / "openrouter_config.json"
    try:
        if f.exists():
            c.update(json.load(open(f)))
    except Exception:
        pass
    return c

_LEDGER = REPO / "out" / "llm_ledger.json"

def spent():
    try:
        return float(json.load(open(_LEDGER)).get("spent_usd", 0.0))
    except Exception:
        return 0.0

def _record(usd, tokens, latency, model, ok):
    try:
        _LEDGER.parent.mkdir(exist_ok=True)
        d = {"spent_usd": 0.0, "calls": []}
        try:
            d = json.load(open(_LEDGER))
        except Exception:
            pass
        d["spent_usd"] = round(float(d.get("spent_usd", 0.0)) + usd, 6)
        d["calls"] = (d.get("calls", []) + [dict(ts=time.strftime("%H:%M:%S"), usd=round(usd, 6),
                      tokens=tokens, latency_ms=round(latency * 1000), model=model, ok=ok)])[-300:]
        json.dump(d, open(_LEDGER, "w"), indent=1)
    except Exception:
        pass

def available():
    c = _cfg()
    return bool(c.get("enabled") and _key() and spent() < c.get("budget_usd", 5.0))

def status():
    c = _cfg()
    return dict(enabled=bool(c.get("enabled")), has_key=bool(_key()), model=c.get("model"),
                spent_usd=round(spent(), 4), budget_usd=c.get("budget_usd", 5.0),
                active=available())

def complete(system, user, temperature=0.2, cache_key=None):
    """(text, meta). Returns (None, meta) on any problem so the caller falls back to rules."""
    if cache_key and cache_key in _CACHE:
        return _CACHE[cache_key], {"used": True, "cached": True}
    c = _cfg(); key = _key()
    meta = {"used": False, "reason": ""}
    if not (c.get("enabled") and key):
        meta["reason"] = "no key / disabled"; return None, meta
    if spent() >= c.get("budget_usd", 5.0):
        meta["reason"] = "budget exhausted"; return None, meta
    body = json.dumps({"model": c["model"], "temperature": temperature, "max_tokens": c["max_tokens"],
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "HTTP-Referer": "http://localhost", "X-Title": "ds-portfolio-demo"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=c["timeout_s"]) as r:
            j = json.loads(r.read())
        txt = j["choices"][0]["message"]["content"].strip()
        u = j.get("usage", {}) or {}
        usd = (u.get("prompt_tokens", 0) * c["price_in_per_m"] +
               u.get("completion_tokens", 0) * c["price_out_per_m"]) / 1e6
        _record(usd, u.get("total_tokens", 0), time.time() - t0, c["model"], True)
        meta.update(used=True, tokens=u.get("total_tokens", 0), usd=round(usd, 6),
                    latency_ms=round((time.time() - t0) * 1000))
        if cache_key:
            _CACHE[cache_key] = txt
        return txt, meta
    except Exception as e:
        _record(0.0, 0, time.time() - t0, c["model"], False)
        meta["reason"] = "api error: " + type(e).__name__
        return None, meta

if __name__ == "__main__":
    print(json.dumps(status(), indent=1))
    t, m = complete("You are a test.", "Reply with exactly: OK", cache_key=None)
    print("call:", "OK" if t else "fell back", "| meta:", m)