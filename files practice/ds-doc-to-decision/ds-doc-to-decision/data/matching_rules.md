# 3-Way Match Decision Rules (deterministic — labels derive from THESE)
Cross-references the policy corpus: claims policy (±2% qty tolerance), quality-cert
requirements (COA valid 12 months, must cover the invoice date).

1. JOIN: invoice.po_no -> PO; GRN with same po_no. **GRN missing -> route_to_human.**
2. QTY (invoice vs GRN, per line): |diff| <= 2% -> pass (within tolerance, no action);
   2% < |diff| <= 10% -> **route_to_human**; > 10% -> **reject**.
3. PRICE (invoice vs PO, per line): any unit-price difference -> **route_to_human** (pricing desk).
4. DATES: grn_date >= po_date and invoice_date >= grn_date, else route_to_human.
5. CERT: Dairy/Spices lines require a COA with valid_till >= invoice_date, else **reject** (non-payable).
6. DUPLICATE: an invoice_no seen before -> **reject** the later occurrence.
7. MATH: grand_total must equal subtotal + GST within Rs 1 rounding, else **reject**.
8. ALL PASS -> **auto_approve** if extraction confidence >= threshold; below threshold -> route.
Severity order when multiple fire: reject > route_to_human > auto_approve.
