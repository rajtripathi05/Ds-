# ds-doc-to-decision — Intelligent Document Automation
*Ingest messy distributor documents → extract with field-level confidence → let WRITTEN RULES
decide (approve / route / reject) with the named failing check → calibrated confidence gate →
exception queue whose overrides teach the gate. Fully offline; every number below measured.*
**Synthetic documents; no company data.**

## The problem
3-way matching (PO ↔ GRN ↔ invoice) is high-volume, rule-bound, and leaky exactly because humans
tire: duplicate invoice numbers, out-of-tolerance quantities, expired COAs and arithmetic errors
hide in routine. LLM-only automation fails audits because nobody can say *why* something posted.

## Architecture (laws in CLAUDE.md)
```
data/sets/SET-0001..0040 (po/grn/invoice JSON + TXT + PDF renders)
     │ loaders.py (schema-validated; 2 GRN-missing sets flagged, never fatal)
     ▼
extract.py   TXT parser + hand-rolled PDF text extractor (ASCII85+Flate, stdlib — K1)
             field-level confidence (.98 labelled hit /.70 fallback /0 missing; math cross-checks)
     ▼
match.py     matching_rules.md VERBATIM: R1 join/GRN · R2 qty ±2%/10% · R3 price · R4 dates
             R5 COA (Dairy/Spices; SKU-prefix category) · R6 cross-set duplicates · R7 GST ±₹1
             R8 confidence gate · severity reject > route > approve — named failing check ALWAYS
     ▼
calibrate.py GT-FREE Platt calibration (target: extracted-path decision agrees with structured
             path), holdout-validated; writes the measured operating threshold (0.798)
     ▼
pipeline.py  the only writer: decisions + immutable hashed audit log (inputs, checks, conf, actor)
server.py+ui exception queue: aging, reason codes, one-click review; overrides → learning.py
             retune (capped steps — trust extends gradually)
tests/       gates M0–M6 + no-peek enforcement (ground truth greppable NOWHERE in src/)
```

## MEASURED results
| Gate | Result |
|---|---|
| Extraction (M1) | **100% amount-field accuracy on BOTH paths** — TXT 282/282, PDF 282/282, line cells 162/162 (EXTRACTION_RESULTS.md) |
| Rules engine (M2) | 16/16 unit checks; every decision carries the named failing check |
| Decisions (M3) | **Structured path 40/40 vs ground truth · 13/13 planted discrepancies caught · end-to-end PDF path also 40/40** (DECISIONS.md) |
| Calibration (M4) | Platt beats raw confidence on holdout (Brier 0.266 → 0.215; isotonic attempt 0.240 reported); STP-vs-error threshold curve produced; operating point 0.798 measured, not chosen |
| Learning loop (M5) | STP **0% → 67.5%** across staged override rounds with **zero auto-approve errors**; threshold learned 0.92 → 0.803 from 54 logged overrides |
| Queue UI (M5) | live walk 7/7: aging + reason codes → review → capped retune → STP rise → hashed audit entries |
| Robustness (M6) | clean = 100%/100%; degradation curve measured to 25% corruption — and the failure mode is SAFE: **0 false approvals even at 12% noise** (corruption trips checks → routes) |
| ROI (M6) | measured STP 67.5%, exceptions 20%; at the blueprint's 70k-docs/yr scenario: **≈12,483 hours ≈ ₹50 L/yr** saved (assumptions on the dashboard) |

## Run it
```bash
python3 src/calibrate.py         # fit calibrator + measured operating threshold
python3 src/server.py            # exception queue on http://localhost:8780
python3 tests/gate_m3.py         # 40/40 + 13/13 scored run
```
Stack: pandas/numpy/matplotlib + stdlib. Git history: `ds-doc-to-decision.gitbundle`.

## What production adds
Real OCR (pdfplumber/vision) behind the same extract_set() seam; ERP posting + GST edge-case
sign-off queues; per-vendor duplicate analytics; the trade-claims and contract phases (blueprint
Case 3); SSO roles on the queue; retention per audit policy.

## Honesty
Ground truth is machine-verifiably absent from decision code (no-peek gate). Two weak learning-loop
demos were discarded and the gate strengthened before the final 0→67.5% result (PROGRESS.md).
The robustness curve is text-domain by necessity (K2) and says so on the figure.
