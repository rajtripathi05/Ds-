"""M2: rule-by-rule unit tests on constructed cases — engine matches matching_rules.md verbatim."""
import sys
sys.path.insert(0, "src")
from match import run_checks, decide

BASE_PO = dict(po_no="P1", po_date="2025-01-01",
               lines=[dict(sku="A", unit_price=10.0, qty=100, category="Confectionery")])
BASE_GRN = dict(po_no="P1", grn_date="2025-01-05", lines=[dict(sku="A", qty=100)])
def inv(**kw):
    d = dict(invoice_no="I1", invoice_date="2025-01-07", po_no="P1",
             lines=[dict(sku="A", unit_price=10.0, qty=100, category="Confectionery")],
             subtotal=1000.0, gst=180.0, grand_total=1180.0, coa=None,
             _doc_conf=1.0, _conf={})
    d.update(kw); return d

def outcome(i, po=BASE_PO, grn=BASE_GRN, seen=None, th=0.9):
    ch = run_checks(i, po, grn, seen or {})
    o, reason, _ = decide(ch, i["_doc_conf"], th)
    return o, reason[0], ch

T = []
o, r, _ = outcome(inv()); T.append(("clean set auto-approves", o == "auto_approve"))
o, r, _ = outcome(inv(), grn=None); T.append(("R1 missing GRN routes", o == "route_to_human" and r.startswith("R1")))
i = inv(); i["lines"][0]["qty"] = 103
o, r, _ = outcome(i); T.append(("R2 qty 3% routes", o == "route_to_human" and r.startswith("R2")))
i = inv(); i["lines"][0]["qty"] = 115
o, r, _ = outcome(i); T.append(("R2 qty 15% rejects", o == "reject" and r.startswith("R2")))
i = inv(); i["lines"][0]["qty"] = 101
o, r, _ = outcome(i); T.append(("R2 qty 1% passes (no action)", o == "auto_approve"))
i = inv(); i["lines"][0]["unit_price"] = 10.5
o, r, _ = outcome(i); T.append(("R3 any price diff routes", o == "route_to_human" and r.startswith("R3")))
i = inv(invoice_date="2025-01-03")
o, r, _ = outcome(i); T.append(("R4 invoice before GRN routes", o == "route_to_human" and r.startswith("R4")))
po2 = dict(BASE_PO, lines=[dict(sku="A", unit_price=10.0, qty=100, category="Dairy")])
i = inv(); i["lines"][0]["category"] = "Dairy"
o, r, _ = outcome(i, po=po2); T.append(("R5 dairy without COA rejects", o == "reject" and r.startswith("R5")))
i["coa"] = dict(coa_no="C", issue_date="2023-01-01", valid_till="2024-01-01")
o, r, _ = outcome(i, po=po2); T.append(("R5 expired COA rejects", o == "reject" and r.startswith("R5")))
i["coa"] = dict(coa_no="C", issue_date="2024-06-01", valid_till="2025-06-01")
o, r, _ = outcome(i, po=po2); T.append(("R5 valid COA passes", o == "auto_approve"))
o, r, _ = outcome(inv(), seen={"I1": "SET-X"}); T.append(("R6 duplicate rejects", o == "reject" and r == "R6_duplicate"))
ch = run_checks(inv(), BASE_PO, BASE_GRN, {"I1": "SET-X"})
T.append(("R6 names prior set", any("SET-X" in c[2] for c in ch if c[0] == "R6_duplicate")))
i = inv(grand_total=1190.0)
o, r, _ = outcome(i); T.append(("R7 math off by ₹10 rejects", o == "reject" and r.startswith("R7")))
i = inv(grand_total=1180.9)
o, r, _ = outcome(i); T.append(("R7 within ₹1 passes", o == "auto_approve"))
i = inv(_doc_conf=0.5)
o, r, _ = outcome(i); T.append(("R8 low confidence routes with named reason", o == "route_to_human" and r.startswith("R8")))
i = inv(_doc_conf=0.5); i["lines"][0]["qty"] = 115
o, r, _ = outcome(i); T.append(("severity: reject beats route", o == "reject"))

ok = all(p for _, p in T)
for n, p in T: print(("✅" if p else "❌"), n)
print("M2 GATE:", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
