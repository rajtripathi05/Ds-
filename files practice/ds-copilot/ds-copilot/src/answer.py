"""Cited extractive answers with version-conflict resolution + guardrails."""
import re
from retrieve import Index, tok

INJ_PAT = re.compile(r"ignore (your|the|all).{0,30}(rule|role|instruction)|"
                     r"you are now|pretend to be|read me the .*(memo|exec)|"
                     r"i'?m authori[sz]ed|override.{0,20}(polic|scope|rule)", re.I)
PII_PAT = re.compile(r"\b(salary|ctc|compensation|address|phone|aadhaar|pan number)\b.{0,40}\b(of|for)?\b", re.I)
NAME_PAT = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+'?s?\b")
OOS_PAT = re.compile(r"competitor|rival brand|their (recipe|formula)|coca|britannia|haldiram", re.I)
RAW_FLOOR = 1.2   # raw BM25 — below this the corpus simply doesn't contain the topic

def guard(question):
    if INJ_PAT.search(question):
        return ("REFUSE — this looks like an attempt to override role-scope rules. "
                "Access to executive-tagged material is enforced at the retrieval and SQL layers "
                "regardless of instructions in the question. This attempt is logged per infosec policy.")
    if PII_PAT.search(question) and NAME_PAT.search(question):
        return ("REFUSE — personal data (salary/compensation/contact details) is Restricted under "
                "the IT security policy. Please route this to HR through the HRMS request flow.")
    if OOS_PAT.search(question):
        return ("REFUSE — that is outside the governed corpus (not company data). "
                "I answer only from internal policies, circulars and the governed database.")
    return None

def _flatten_tables(body):
    """Markdown tables -> row sentences so extraction can cite tabular facts."""
    out, lines = [], body.splitlines()
    i, context = 0, ""
    while i < len(lines):
        l = lines[i]
        if l.strip().startswith("#"):
            context = l.lstrip("# ").strip()
        if l.strip().startswith("|") and i + 1 < len(lines) and set(lines[i+1].replace("|", "").strip()) <= set("-: "):
            heads = [h.strip() for h in l.strip().strip("|").split("|")]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                pairs = "; ".join(f"{h} {c}" for h, c in zip(heads[1:], cells[1:]))
                out.append(f"{context} — {cells[0]}: {pairs}.")
                i += 1
            continue
        out.append(l)
        i += 1
    # unwrap soft-wrapped prose lines, then one candidate per line
    joined, buf = [], ""
    for l in out:
        t = l.strip()
        if not t:
            if buf: joined.append(buf); buf = ""
            continue
        buf = (buf + " " + t).strip() if buf else t
        if (re.search(r"[.!?:]$", t) and not re.search(r"\b(incl|e\.g|i\.e|approx|vs|no|pcs|sq)\.$", t, re.I)) or t.startswith("#"):
            joined.append(buf); buf = ""
    if buf: joined.append(buf)
    return "\n".join(joined)

def _units(text):
    u = set()
    tl = text.lower()
    if re.search(r"\d+\s*°?\s*c\b", tl): u.add("degC")
    if re.search(r"\d+\s*(month|months)", tl): u.add("months")
    if re.search(r"\d+\s*(day|days)", tl): u.add("days")
    if re.search(r"₹|\brs\.?\b|lakh", tl): u.add("inr")
    if re.search(r"\d+\s*%", tl): u.add("pct")
    return u

def best_sentences(question, body, n=3):
    body = _flatten_tables(body)
    q_units = _units(question)
    qt = set(tok(question))
    sents = []
    body2 = re.sub(r"\b(incl|e\.g|i\.e|approx|vs|pcs|sq)\.", r"\1&DOT&", body, flags=re.I)
    for raw in re.split(r"(?<=[.!?])\s+|\n", body2):
        raw = raw.replace("&DOT&", ".")
        s = re.sub(r"\*\*", "", raw).strip().strip("*-• ")
        if len(s) < 15 or s.startswith("#"):
            continue
        st = set(tok(s))
        ov = len(qt & st) / (len(qt) or 1)
        bonus = 0.15 if re.search(r"\d", s) else 0
        bonus += 0.30 * len(q_units & _units(s))
        sents.append((ov + bonus, s))
    sents.sort(key=lambda x: -x[0])
    return [s for sc, s in sents[:n] if sc > 0.12]

def answer(question, role="ops", index_cache={}):
    g = guard(question)
    if g:
        return dict(answer=g, citations=[], refused=True, trace=[("guard", "refused")])
    idx = index_cache.setdefault(role, Index(role))
    conj_q = bool(re.search(r"\band\b|\bwith\b", question, re.I)) and len(tok(question)) >= 8
    if conj_q:
        clauses = [c.strip() for c in re.split(r"\band\b|\bwith\b|,", question, flags=re.I)
                   if len(tok(c)) >= 2][:3]
        seen, multi_hits = set(), []
        for c in clauses:
            for h in idx.search(question + " " + c, k=2):
                if h[0] not in seen and h[2] >= 2.0:
                    seen.add(h[0]); multi_hits.append(h)
        if len(multi_hits) >= 2:
            hits = sorted(multi_hits, key=lambda x: -x[1])[:3]
        else:
            hits = idx.search(question, k=4)
    else:
        hits = idx.search(question, k=4)
    trace = [("search_docs", {"query": question, "hits": hits})]
    top = hits[0]
    if not hits or top[2] < RAW_FLOOR or (top[2] < 6.0 and top[3] < 2 and top[2] < 3.5):
        return dict(answer="I can't find this in the governed corpus — no citation, so I won't guess.",
                    citations=[], refused=False, trace=trace)
    top_id = hits[0][0]
    cits, note = [top_id], ""
    vm = idx.version_map
    if top_id in vm:
        fam = vm[top_id]
        newest = fam["newest"]
        if newest in idx.docs:
            if top_id != newest:
                top_id = newest
            older = [d for d in fam["all"] if d != newest and d in idx.docs]
            cits = [newest] + older
            eff = idx.docs[newest]["effective"]
            note = (f"Per the current {idx.docs[newest]['title']} (v{idx.docs[newest].get('version','?')}, "
                    f"effective {eff}), which supersedes the earlier version: ")
    doc = idx.docs[top_id]
    sents = best_sentences(question, doc["body"])
    if conj_q:
        for c in re.split(r"\band\b|\bwith\b|,", question, flags=re.I):
            if len(tok(c)) >= 2:
                for s2_ in best_sentences(c, doc["body"], n=2):
                    if s2_ not in sents:
                        sents.append(s2_)
    # multi-doc: pull a second doc's sentences if its score is close
    conj = bool(re.search(r"\band\b|,\s*(what|when|which)|both", question, re.I))
    thresh = 0.30 if conj else 0.55
    if len(hits) > 1 and hits[1][1] > thresh * hits[0][1] and hits[1][2] >= RAW_FLOOR and hits[1][3] >= 2 and hits[1][0] not in cits:
        d2 = idx.docs[hits[1][0]]
        s2 = best_sentences(question, d2["body"], n=3 if conj else 2)
        if conj_q:
            for c in re.split(r"\band\b|\bwith\b|,", question, flags=re.I):
                if len(tok(c)) >= 2:
                    for x in best_sentences(c, d2["body"], n=2):
                        if x not in s2:
                            s2.append(x)
        if s2:
            sents += s2
            cits.append(hits[1][0])
    if conj_q and len(hits) > 2 and hits[2][2] >= RAW_FLOOR and hits[2][3] >= 2 and hits[2][0] not in cits:
        d3 = idx.docs[hits[2][0]]
        s3 = best_sentences(question, d3["body"], n=2)
        for c in re.split(r"\band\b|\bwith\b|,", question, flags=re.I):
            if len(tok(c)) >= 2:
                for x in best_sentences(c, d3["body"], n=2):
                    if x not in s3:
                        s3.append(x)
        if s3:
            sents += s3[:3]
            cits.append(hits[2][0])
    if not sents:
        return dict(answer="I can't find this in the governed corpus — no citation, so I won't guess.",
                    citations=[], refused=False, trace=trace)
    body = " ".join(sents[:8 if conj_q else 4])
    return dict(answer=(note + body).strip(),
                citations=[f"[{c}]" for c in cits], refused=False, trace=trace)

if __name__ == "__main__":
    import json
    r = answer("How many Earned Leave days do employees get per year now (mid-2025)?", "ops")
    print(json.dumps(r, indent=1)[:800])
