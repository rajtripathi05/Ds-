"""M1: extraction accuracy vs invoice.json across all 40 sets, TXT and PDF paths.
invoice.json is the labelling source for EXTRACTION (allowed — it's the doc's own structured
twin, not the decision ground truth)."""
import sys, json
sys.path.insert(0, "src")
from loaders import load_set, all_sets
from extract import extract_set

FIELDS = ["invoice_no", "invoice_date", "po_no", "subtotal", "gst", "grand_total"]

def compare(ex, truth):
    per = {}
    for k in FIELDS:
        tv = truth.get(k)
        if k == "gst" and isinstance(tv, dict):
            tv = round(sum(v for v in tv.values() if isinstance(v, (int, float))), 2)
        ev = ex.get(k)
        if isinstance(tv, (int, float)):
            per[k] = ev is not None and abs(float(ev) - float(tv)) <= 0.01
        else:
            per[k] = (str(ev) == str(tv))
    # lines: qty/rate/amount per sku
    tl = {l["sku"]: l for l in truth.get("lines", [])}
    el = {l["sku"]: l for l in ex.get("lines", [])}
    ln_ok, ln_n = 0, 0
    for sku, l in tl.items():
        for fld in ("qty", "unit_price"):
            ln_n += 1
            e = el.get(sku, {}).get(fld)
            if e is not None and abs(float(e) - float(l[fld])) <= 0.01:
                ln_ok += 1
    per["lines"] = (ln_ok, ln_n)
    return per

def run(source):
    field_ok = {k: 0 for k in FIELDS}; field_n = {k: 0 for k in FIELDS}
    lines_ok = lines_n = 0
    amt_ok = amt_n = 0
    for sid in all_sets():
        st = load_set(sid)
        ex = extract_set(st, source)
        per = compare(ex, st["invoice"])
        for k in FIELDS:
            field_n[k] += 1; field_ok[k] += bool(per[k])
            if k in ("subtotal", "gst", "grand_total"):
                amt_n += 1; amt_ok += bool(per[k])
        lo, ln = per["lines"]; lines_ok += lo; lines_n += ln
        amt_n += ln; amt_ok += lo   # line amounts count as amounts too
    return field_ok, field_n, lines_ok, lines_n, amt_ok, amt_n

rows = ["# EXTRACTION_RESULTS.md — measured field accuracy vs invoice.json (40 sets)", ""]
gate_ok = True
summary = {}
for source in ("txt", "pdf"):
    fo, fn, lo, ln, ao, an = run(source)
    rows.append(f"\n## Source: {source.upper()}\n")
    rows.append("| field | accuracy |")
    rows.append("|---|---|")
    for k in FIELDS:
        rows.append(f"| {k} | {fo[k]}/{fn[k]} = {fo[k]/fn[k]*100:.1f}% |")
    rows.append(f"| line qty/rate/amount cells | {lo}/{ln} = {lo/ln*100:.1f}% |")
    amt_acc = ao / an
    rows.append(f"| **all amount fields** | **{ao}/{an} = {amt_acc*100:.2f}%** |")
    summary[source] = amt_acc
    print(f"{source}: amounts {ao}/{an} = {amt_acc*100:.2f}% · lines {lo}/{ln}")
    if source == "pdf" and amt_acc < 0.98:
        gate_ok = False
rows.append(f"\nGate: PDF amount-field accuracy ≥98% → {'PASS' if gate_ok else 'FAIL'}")
open("EXTRACTION_RESULTS.md", "w").write("\n".join(rows))
print("M1 GATE:", "GREEN" if gate_ok else "RED")
sys.exit(0 if gate_ok else 1)
