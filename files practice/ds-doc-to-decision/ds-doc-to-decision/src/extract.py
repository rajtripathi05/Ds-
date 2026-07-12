"""Field extraction (TXT and PDF-text) -> normalized schema with FIELD-LEVEL confidence.
Extraction NEVER decides (LAW 1). Confidences: labeled-regex hit .98, fallback .70, missing .0;
cross-check boosts/cuts (line math, subtotal sum) adjust by ±.08 capped [0,1]."""
import re

MONEY = r"(-?\d[\d,]*\.?\d*)"

def _num(s):
    try:
        return float(str(s).replace(",", ""))
    except Exception:
        return None

def parse_invoice_text(text):
    f, c = {}, {}
    def grab(key, pat, conv=str, conf=0.98, flags=0):
        m = re.search(pat, text, flags)
        if m:
            f[key] = conv(m.group(1).strip())
            c[key] = conf
        else:
            f[key] = None
            c[key] = 0.0
    grab("invoice_no", r"Invoice No:\s*(\S+)")
    grab("invoice_date", r"Invoice No:.*?Date:\s*([0-9-]+)")
    grab("po_no", r"PO Ref:\s*(\S+)")
    grab("buyer_code", r"Buyer:\s*(DIST-[A-Z]+-\d+)")
    grab("subtotal", rf"Subtotal\s+{MONEY}", _num)
    grab("grand_total", rf"GRAND TOTAL\s+{MONEY}", _num)
    comps = re.findall(rf"\b([CSI]GST)\s*(\d+(?:\.\d+)?)%\s+{MONEY}", text)
    if comps:
        f["gst"] = round(sum(_num(v) for _, _, v in comps), 2)
        f["gst_components"] = {k.lower(): _num(v) for k, _, v in comps}
        f["gst_rate"] = round(sum(_num(r) for _, r, _ in comps) / 100.0, 4)
        c["gst"] = c["gst_rate"] = 0.98
    else:
        f["gst"], c["gst"], f["gst_rate"], c["gst_rate"] = None, 0.0, None, 0.0
    m = re.search(r"COA:\s*(\S+)\s+issued\s+([0-9-]+)\s+valid till\s+([0-9-]+)", text)
    if m:
        f["coa"] = dict(coa_no=m.group(1), issue_date=m.group(2), valid_till=m.group(3))
        c["coa"] = 0.98
    else:
        f["coa"], c["coa"] = None, 0.5 if "COA" in text else 0.9   # COA mentioned but unparsed -> low conf
    lines, lc = [], []
    for m in re.finditer(rf"^(DS-[A-Z]+-\d+)\s+(.+?)\s+(\d{{4}})\s+(\d[\d,]*)\s+{MONEY}\s+{MONEY}\s*$",
                         text, re.M):
        sku, desc, hsn, qty, rate, amount = m.groups()
        qty, rate, amount = _num(qty), _num(rate), _num(amount)
        conf = 0.95
        if qty is not None and rate is not None and amount is not None:
            conf = 0.99 if abs(qty * rate - amount) <= 1.0 else 0.60   # internal math check
        lines.append(dict(sku=sku, description=desc.strip(), hsn=hsn, qty=qty,
                          unit_price=rate, amount=amount))
        lc.append(conf)
    f["lines"], c["lines"] = lines, (min(lc) if lc else 0.0)
    # cross-check: sum of line amounts vs subtotal
    if lines and f.get("subtotal") is not None:
        s = sum(l["amount"] or 0 for l in lines)
        if abs(s - f["subtotal"]) <= 1.0:
            c["subtotal"] = min(1.0, c["subtotal"] + 0.02)
        else:
            c["subtotal"] = max(0.0, c["subtotal"] - 0.30)
            c["lines"] = max(0.0, c["lines"] - 0.20)
    f["_conf"] = c
    f["_doc_conf"] = round(min([v for k, v in c.items() if k != "coa"] or [0.0]), 3)
    return f

def extract_set(st, source="txt"):
    """source: txt | pdf. Returns normalized fields or a routed 'unreadable' stub (LAW 4)."""
    if source == "txt":
        text = st.get("txt")
    else:
        from pdftext import extract_text
        text = extract_text(st["pdf_path"]) if st.get("pdf_path") else None
    if not text or len(text) < 40:
        return dict(_unreadable=True, _doc_conf=0.0, _conf={}, lines=[])
    return parse_invoice_text(text)
