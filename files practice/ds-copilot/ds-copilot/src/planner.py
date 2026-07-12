"""Agent planner (rules mode, C1): decomposes fuzzy asks into doc-search + SQL + chart tool
calls with a VISIBLE trace; synthesizes a cited answer. No LLM required."""
import re, os, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from answer import answer as doc_answer, guard
from sqlgen import ask_data, parse_question
from retrieve import Index
import llm

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "out" / "charts"

NUMERIC_HINT = re.compile(r"volume|trend|offtake|units sold|transactions|revenue|gross margin by|monthly|compare .* zone", re.I)
POLICY_HINT = re.compile(r"policy|leave|entitle|claim|expense|travel|wfh|work from home|onboard|coa|scheme|beat|lpc|stop.?supply|credit|deadline|margin|roi|deposit", re.I)
OPS_FINANCE = re.compile(r"\bmargin|\broi\b|profitab|pricing structure|unit cost|cogs|inventory.?day", re.I)
WHY_HINT = re.compile(r"why|reason|cause|explain", re.I)

def make_chart(rows, columns, title):
    CHARTS.mkdir(parents=True, exist_ok=True)
    if not rows or len(rows[0]) < 2:
        return None
    xs = [str(r[0]) for r in rows]
    ys = [r[-1] for r in rows]
    fig, ax = plt.subplots(figsize=(7.5, 3), dpi=110)
    ax.plot(xs, ys, color="#b3282d", lw=2, marker="o", ms=3)
    ax.set_title(title, fontsize=10, loc="left", fontweight="bold", color="#1c1917")
    ax.grid(alpha=.25); ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    fig.tight_layout()
    f = CHARTS / (re.sub(r"[^a-z0-9]+", "-", title.lower())[:48] + ".png")
    fig.savefig(f); plt.close(fig)
    return str(f.relative_to(ROOT))

def ask(question, role="ops"):
    """Router: guards → (doc | sql | both) with visible trace."""
    trace = []
    g = guard(question)
    if g:
        return dict(answer=g, citations=[], refused=True, trace=[("guard", "refused")], chart=None)
    if role != "exec" and OPS_FINANCE.search(question):
        return dict(answer=("REFUSE — margin/ROI/pricing/cost information is executive-scoped "
                            "(margin memo + IT security policy). Operations can query volumes and "
                            "policies; request Executive access if needed. This request is logged."),
                    citations=[], refused=True, trace=[("role_guard", "ops finance refusal")], chart=None)
    wants_why = bool(WHY_HINT.search(question))
    wants_data = bool(NUMERIC_HINT.search(question)) and not (POLICY_HINT.search(question) and not wants_why)
    chart = None
    parts, cits = [], []
    sqlres = None
    if wants_data:
        sqlres = ask_data(question, role)
        trace.append(("run_sql", {"plan": sqlres.get("plan"), "sql": sqlres.get("sql"),
                                  "error": sqlres.get("error"), "n_rows": len(sqlres.get("rows", []))}))
        if sqlres.get("error"):
            if "REFUSE" in sqlres["error"]:
                return dict(answer=sqlres["error"], citations=[], refused=True, trace=trace, chart=None)
        elif sqlres.get("rows"):
            rows = sqlres["rows"]
            if len(rows) > 1 and len(rows[0]) >= 2:
                first, last = rows[0][-1], rows[-1][-1]
                delta = (last / first - 1) * 100 if first else 0
                parts.append(f"Data: {rows[0][0]} → {rows[-1][0]}: "
                             f"{first:,.0f} → {last:,.0f} ({delta:+.1f}%). [governed-db]")
                chart = make_chart(rows, sqlres["columns"], question[:60])
                trace.append(("make_chart", chart))
            else:
                val = rows[0][-1]
                parts.append(f"Data: {sqlres['columns'][-1]} = {val:,.0f}. [governed-db]")
    if wants_why or not wants_data or not (sqlres and sqlres.get("rows")):
        dq = question
        if wants_why and sqlres and sqlres.get("plan"):
            f = sqlres["plan"].get("filters", {})
            hint = " ".join(str(v) for v in f.values())
            dq = f"{question} {hint} price revision MRP circular scheme launch expansion"
            trace.append(("expand_doc_query", dq))
        d = doc_answer(dq, role)
        trace.extend(d["trace"])
        if d.get("refused"):
            return dict(answer=d["answer"], citations=[], refused=True, trace=trace, chart=None)
        if d["citations"]:
            parts.append(d["answer"])
            cits.extend(d["citations"])
        elif not parts:
            parts.append(d["answer"])
    ans = " ".join(parts)
    ai = {"used": False}
    if llm.available() and cits and ans and len(ans) > 0:
        sys_p = ("You rewrite an internal company answer to be clear and natural for a colleague. "
                 "Use ONLY the facts given. Keep EVERY bracketed [citation-id] token exactly as written. "
                 "Add no new facts, numbers, policies or names. 2-4 sentences.")
        usr_p = f"Question: {question}\n\nFacts (already retrieved, cite these):\n{ans}\n\nCitations that must remain: {' '.join(cits)}"
        txt, meta = llm.complete(sys_p, usr_p, cache_key="ans::" + question.lower().strip())
        # accept ONLY if every original citation survived -> grounded+cited law preserved
        if txt and all(c in txt for c in cits):
            ans = txt; ai = {"used": True, **{k: meta.get(k) for k in ("tokens", "usd", "latency_ms", "cached") if k in meta}}
        else:
            ai = {"used": False, "reason": meta.get("reason") or "citation-guard reverted"}
        trace.append(("llm_polish", ai))
    return dict(answer=ans, citations=cits, refused=False, trace=trace, chart=chart, ai=ai)

if __name__ == "__main__":
    os.environ.setdefault("DSCOPILOT_DB", str(ROOT / "out" / "copilot.db"))
    r = ask("Why did North-zone Rajnigandha volumes drop in early 2025?", "ops")
    print(json.dumps(r, indent=1, default=str)[:1400])
