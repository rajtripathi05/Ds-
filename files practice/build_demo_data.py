#!/usr/bin/env python3
"""Build static, de-branded demo JSON from the REAL engines so the three apps
can run fully client-side on static hosting (Netlify). Nothing is invented:
- invoice decisions come from pipeline.run_all()
- assistant answers come from planner.ask() for both roles
- cockpit metrics come from the real snapshot.json
"""
import json, os, re, sys, csv, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT  = HERE.parent / "demo" / "data"
OUT.mkdir(parents=True, exist_ok=True)

# ---- de-brand: only cosmetic strings in the SYNTHETIC data ----
def debrand(x):
    if isinstance(x, str):
        x = x.replace("DS Foods", "Northwind Foods")
        x = re.sub(r"\bDS-([A-Z])", r"FMCG-\1", x)   # SKU codes DS-XXX -> FMCG-XXX
        return x
    if isinstance(x, list):  return [debrand(v) for v in x]
    if isinstance(x, dict):  return {k: debrand(v) for k, v in x.items()}
    return x

def dump(name, obj):
    p = OUT / name
    p.write_text(json.dumps(debrand(obj), ensure_ascii=False, separators=(",",":")), encoding="utf-8")
    print(f"  wrote {name:16} {p.stat().st_size/1024:6.1f} KB")

# ============================================================ COCKPIT
def build_cockpit():
    snap = json.load(open(HERE / "ds-demand-cockpit/ds-demand-cockpit/out/plan/snapshot.json"))
    k = snap["kpis"]
    out = {
        "built_at": snap.get("built_at"),
        "kpis": {
            "wmape_sku_champion": k["wmape_sku_champion"],
            "wmape_sku_snaive":   k["wmape_sku_snaive"],
            "wmape_cat_champion": k["wmape_cat_champion"],
            "wmape_cat_snaive":   k["wmape_cat_snaive"],
            "fva_vs_snaive_pp":   k["fva_vs_snaive_pp"],
            "champion_mix":       k.get("champion_mix", {}),
            "data_badges":        k.get("data_badges", {}),
        },
        "elasticity": snap["elasticity"],      # recovered vs true per category
        "promo_roi":  snap["promo_roi"],       # median + ranked promos
        "plan":       snap["plan"],            # binding constraint, budget, lines, stockouts
        "curves":     snap["curves"],          # nation/categories/launch series
    }
    dump("cockpit.json", out)

# ============================================================ INVOICE
def build_invoice():
    root = HERE / "ds-doc-to-decision/ds-doc-to-decision"
    sys.path.insert(0, str(root / "src"))
    os.chdir(root)
    from pipeline import run_all
    recs = {r["set_id"]: r for r in run_all("structured", audit=False)}

    # ground truth (answer key) + planted discrepancies
    gt = {}
    with open(root/"data/ground_truth_labels.csv") as f:
        for r in csv.DictReader(f):
            gt[r["set_id"]] = {"decision": r["decision"], "reason": r.get("reason",""),
                               "discrepancy_type": r.get("discrepancy_type",""),
                               "expected_confidence": r.get("expected_confidence","")}
    planted = set()
    pf = root/"data/planted_discrepancies.csv"
    if pf.exists():
        with open(pf) as f:
            for r in csv.DictReader(f):
                planted.add(r.get("set_id") or r.get("set") or "")

    sets = []
    for sid in sorted(recs):
        rec = recs[sid]
        inv = json.load(open(root/f"data/sets/{sid}/invoice.json"))
        sets.append({
            "set_id": sid,
            "invoice_no": rec.get("invoice_no"),
            "outcome": rec["outcome"],
            "reason": rec["reason"],
            "checks": rec["checks"],
            "confidence": rec["confidence"],
            "conf_gate": rec["conf_gate"],
            "seller": inv.get("seller",{}).get("name"),
            "invoice_date": inv.get("invoice_date"),
            "po_no": inv.get("po_no"),
            "lines": inv.get("lines", inv.get("items", [])),
            "totals": {kk: inv.get(kk) for kk in ("subtotal","tax","total","grand_total","amount") if kk in inv},
            "ground_truth": gt.get(sid, {}),
            "planted": sid in planted,
        })

    outcomes = {}
    for s in sets: outcomes[s["outcome"]] = outcomes.get(s["outcome"],0)+1
    n = len(sets)
    auto = outcomes.get("auto_approve",0)
    # correctness: does engine outcome == ground truth?
    correct = sum(1 for s in sets if s["outcome"] == s["ground_truth"].get("decision"))
    wrong_auto = sum(1 for s in sets if s["outcome"]=="auto_approve" and s["ground_truth"].get("decision")!="auto_approve")
    planted_total = sum(1 for s in sets if s["planted"])
    planted_caught = sum(1 for s in sets if s["planted"] and s["outcome"]!="auto_approve")
    summary = {
        "n": n, "outcomes": outcomes,
        "auto_clear_pct": round(100*auto/n,1),
        "match_ground_truth": f"{correct}/{n}",
        "wrong_auto_approvals": wrong_auto,
        "planted_caught": f"{planted_caught}/{planted_total}",
    }
    dump("invoice.json", {"summary": summary, "sets": sets})

# ============================================================ ASSISTANT
def build_assistant():
    root = HERE / "ds-copilot/ds-copilot"
    sys.path.insert(0, str(root / "src"))
    os.chdir(root)
    os.environ.setdefault("DSCOPILOT_DB", str(root/"data/copilot.db"))
    # ensure db exists
    try:
        import db as _db
        if hasattr(_db,"main"):
            try: _db.main()
            except SystemExit: pass
    except Exception as e:
        print("  db build note:", e)
    from planner import ask

    ev = json.load(open(root/"data/eval_set.json"))
    items = ev if isinstance(ev, list) else ev.get("questions") or ev.get("items") or []

    def trim(res):
        hits = []
        for step in res.get("trace") or []:
            if isinstance(step,list) and len(step)>=2 and isinstance(step[1],dict):
                for h in (step[1].get("hits") or [])[:4]:
                    if isinstance(h,list) and h: hits.append([h[0], h[1] if len(h)>1 else None])
        return {"answer":res.get("answer"), "citations":res.get("citations",[]),
                "refused":bool(res.get("refused")), "chart":res.get("chart"),
                "hits":hits[:4]}

    qs = []
    for it in items:
        q = it["question"]
        a_ops  = trim(ask(q, "ops"))
        a_exec = trim(ask(q, "exec"))
        qs.append({
            "id": it.get("id"), "question": q,
            "ground_truth": it.get("ground_truth"),
            "source_docs": it.get("source_docs", []),
            "expected_behavior": it.get("expected_behavior"),
            "note": it.get("note"),
            "role_sensitive": (a_ops["answer"] != a_exec["answer"]) or (a_ops["refused"] != a_exec["refused"]),
            "ops": a_ops, "exec": a_exec,
        })

    # ship corpus for citation viewer + client-side free search
    corpus = {}
    for md in sorted((root/"data/corpus").glob("*.md")):
        txt = md.read_text(encoding="utf-8", errors="ignore")
        title = txt.strip().splitlines()[0].lstrip("# ").strip() if txt.strip() else md.stem
        corpus[md.stem] = {"title": title, "text": txt}

    dump("assistant.json", {"questions": qs, "corpus": corpus})

if __name__ == "__main__":
    print("Building demo data →", OUT)
    build_cockpit()
    build_invoice()
    build_assistant()
    print("done.")
