"""Override-4 enforcement: decision-path code must never reference the scoring files."""
import sys, re
from pathlib import Path
BAD = ("ground_truth_labels", "planted_discrepancies")
hits = []
for f in Path("src").rglob("*.py"):
    t = f.read_text()
    for b in BAD:
        if b in t:
            hits.append(f"{f}: references {b}")
for f in Path("ui").rglob("*.html"):
    t = f.read_text()
    for b in BAD:
        if b in t:
            hits.append(f"{f}: references {b}")
for h in hits: print("❌", h)
print("NO-PEEK GATE:", "GREEN" if not hits else "RED")
sys.exit(0 if not hits else 1)
