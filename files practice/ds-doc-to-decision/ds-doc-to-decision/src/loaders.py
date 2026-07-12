"""Set loaders + light schema validation. data/ is read-only."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SETS = ROOT / "data" / "sets"

REQ_INV = {"invoice_no", "invoice_date", "po_no", "lines", "subtotal", "gst", "grand_total"}
REQ_PO = {"po_no", "po_date", "lines"}
REQ_GRN = {"po_no", "grn_date", "lines"}

def load_set(set_id):
    d = SETS / set_id
    out = dict(set_id=set_id, issues=[])
    for name, req in (("po", REQ_PO), ("grn", REQ_GRN), ("invoice", REQ_INV)):
        f = d / f"{name}.json"
        if not f.exists():
            out[name] = None
            out["issues"].append(f"{name}.json missing")
            continue
        try:
            obj = json.loads(f.read_text())
        except Exception as e:
            out[name] = None
            out["issues"].append(f"{name}.json unreadable: {e}")
            continue
        missing = req - set(obj)
        if missing:
            out["issues"].append(f"{name}.json missing fields: {sorted(missing)}")
        out[name] = obj
    out["txt"] = (d / "invoice.txt").read_text(encoding="utf-8") if (d / "invoice.txt").exists() else None
    out["pdf_path"] = str(d / "invoice.pdf") if (d / "invoice.pdf").exists() else None
    return out

def all_sets():
    return sorted(p.name for p in SETS.iterdir() if p.is_dir())

if __name__ == "__main__":
    ids = all_sets()
    manifest = []
    for s in ids:
        st = load_set(s)
        manifest.append(dict(set_id=s, has_po=st["po"] is not None, has_grn=st["grn"] is not None,
                             has_invoice=st["invoice"] is not None, has_txt=st["txt"] is not None,
                             has_pdf=st["pdf_path"] is not None, issues=st["issues"]))
    (ROOT / "out").mkdir(exist_ok=True)
    json.dump(manifest, open(ROOT / "out/sets_manifest.json", "w"), indent=1)
    n_grn_missing = sum(1 for m in manifest if not m["has_grn"])
    print(f"{len(ids)} sets · GRN missing in {n_grn_missing} · all invoices present:",
          all(m["has_invoice"] for m in manifest))
