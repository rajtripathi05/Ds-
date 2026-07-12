"""Deterministic 3-way match — implements data/matching_rules.md VERBATIM (LAW 1).
Each check returns (check_name, outcome, detail); outcome in {pass, route_to_human, reject}.
Severity: reject > route_to_human > auto_approve. Extraction never decides."""
from datetime import date

SEV = {"pass": 0, "route_to_human": 1, "reject": 2}
COA_CATS = {"Dairy", "Spices"}
# SKU key encodes category: DS-<CAT><BRD>-<NNN> (dataset spine convention)
SKU_CAT = {"DAIR": "Dairy", "SPIC": "Spices", "CONF": "Confectionery",
           "MOUT": "MouthFreshener", "BEVE": "Beverages", "SNAC": "Snacks"}

def sku_category(sku):
    try:
        return SKU_CAT.get(str(sku)[3:7].upper())
    except Exception:
        return None

def _d(s):
    return date.fromisoformat(str(s)[:10])

def run_checks(inv, po, grn, seen_invoice_nos):
    """inv: normalized invoice fields; po/grn: structured JSONs; seen: dict invoice_no->set_id."""
    checks = []
    # Rule 1 — JOIN / GRN missing
    if po is None:
        checks.append(("R1_join_po", "route_to_human", "PO missing for invoice.po_no"))
    if grn is None:
        checks.append(("R1_grn_missing", "route_to_human", "GRN missing -> route_to_human (rule 1)"))
    # Rule 2 — QTY invoice vs GRN per line
    if grn is not None:
        g = {l["sku"]: float(l["qty"]) for l in grn.get("lines", [])}
        for l in inv.get("lines", []):
            sku, q = l.get("sku"), l.get("qty")
            if q is None or sku not in g:
                checks.append((f"R2_qty[{sku}]", "route_to_human", "line missing on GRN or qty unreadable"))
                continue
            gq = g[sku]
            diff = abs(q - gq) / gq * 100 if gq else 100.0
            if diff <= 2.0:
                checks.append((f"R2_qty[{sku}]", "pass", f"{diff:.2f}% within ±2% tolerance"))
            elif diff <= 10.0:
                checks.append((f"R2_qty[{sku}]", "route_to_human", f"qty diff {diff:.2f}% in (2%,10%]"))
            else:
                checks.append((f"R2_qty[{sku}]", "reject", f"qty diff {diff:.2f}% > 10%"))
    # Rule 3 — PRICE invoice vs PO per line
    if po is not None:
        p = {l["sku"]: float(l["unit_price"]) for l in po.get("lines", [])}
        for l in inv.get("lines", []):
            sku, up = l.get("sku"), l.get("unit_price")
            if up is None or sku not in p:
                checks.append((f"R3_price[{sku}]", "route_to_human", "line missing on PO or price unreadable"))
            elif abs(up - p[sku]) > 1e-9:
                checks.append((f"R3_price[{sku}]", "route_to_human",
                               f"unit price {up} != PO {p[sku]} -> pricing desk"))
            else:
                checks.append((f"R3_price[{sku}]", "pass", "price matches PO"))
    # Rule 4 — date ordering
    try:
        if po is not None and grn is not None:
            if not (_d(grn["grn_date"]) >= _d(po["po_date"])):
                checks.append(("R4_dates", "route_to_human", "grn_date < po_date"))
            elif not (_d(inv["invoice_date"]) >= _d(grn["grn_date"])):
                checks.append(("R4_dates", "route_to_human", "invoice_date < grn_date"))
            else:
                checks.append(("R4_dates", "pass", "po <= grn <= invoice"))
    except Exception as e:
        checks.append(("R4_dates", "route_to_human", f"unparseable dates: {e}"))
    # Rule 5 — COA for Dairy/Spices lines
    cats = {l.get("category") for l in (po.get("lines", []) if po else [])} | \
           {l.get("category") for l in inv.get("lines", []) if isinstance(l, dict)} | \
           {sku_category(l.get("sku")) for l in inv.get("lines", []) if isinstance(l, dict)}
    needs_coa = bool(cats & COA_CATS)
    if needs_coa:
        coa = inv.get("coa")
        if not coa or not coa.get("valid_till"):
            checks.append(("R5_coa", "reject", "Dairy/Spices line but COA absent/unreadable -> non-payable"))
        else:
            try:
                if _d(coa["valid_till"]) >= _d(inv["invoice_date"]):
                    checks.append(("R5_coa", "pass", f"COA valid till {coa['valid_till']}"))
                else:
                    checks.append(("R5_coa", "reject",
                                   f"COA expired {coa['valid_till']} < invoice {inv['invoice_date']}"))
            except Exception:
                checks.append(("R5_coa", "reject", "COA dates unreadable"))
    # Rule 6 — duplicate invoice number (cross-set)
    ino = inv.get("invoice_no")
    if ino and ino in seen_invoice_nos:
        checks.append(("R6_duplicate", "reject",
                       f"invoice_no {ino} already seen in {seen_invoice_nos[ino]}"))
    # Rule 7 — GST arithmetic within Rs 1
    st, gst, gt = inv.get("subtotal"), inv.get("gst"), inv.get("grand_total")
    if None in (st, gst, gt):
        checks.append(("R7_math", "route_to_human", "totals unreadable"))
    elif abs((st + gst) - gt) > 1.0:
        checks.append(("R7_math", "reject",
                       f"grand_total {gt} != subtotal {st} + GST {gst} (Δ{(st+gst)-gt:+.2f} > ₹1)"))
    else:
        checks.append(("R7_math", "pass", f"totals tie within ₹1 (Δ{(st+gst)-gt:+.2f})"))
    return checks

def decide(checks, doc_conf, threshold):
    worst = max((SEV[o] for _, o, _ in checks), default=0)
    if worst == 2:
        outcome = "reject"
    elif worst == 1:
        outcome = "route_to_human"
    else:
        outcome = "auto_approve" if doc_conf >= threshold else "route_to_human"
    fails = [(n, o, d) for n, o, d in checks if o != "pass"]
    if outcome == "route_to_human" and worst == 0:
        fails = [("R8_confidence", "route_to_human",
                  f"all checks pass but doc confidence {doc_conf:.2f} < threshold {threshold:.2f}")]
    reason = fails[0] if fails else ("all_pass", "pass", "all checks green")
    return outcome, reason, fails
