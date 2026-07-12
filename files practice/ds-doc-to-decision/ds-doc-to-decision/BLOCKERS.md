# BLOCKERS.md — honest record
| # | Spec item | What happened | What was done instead | Evidence |
|---|-----------|---------------|----------------------|----------|
| K1 | pdfplumber extraction | pip blocked (403) | Hand-rolled PDF text extractor (ASCII85+Flate content streams, stdlib) — 100% amount-field accuracy on all 40 machine-generated PDFs; production swaps in pdfplumber/OCR unchanged behind extract_set() | EXTRACTION_RESULTS.md |
| K2 | pypdfium2/PIL PDF rasterisation for degradation | No PDF rasteriser offline (PIL alone can't read PDF pages; no OCR to read images back) | Text-domain corruption at 7 intensities through the SAME pipeline → robustness.png (D3) | robustness.png, out/m6_robustness.json |
| K3 | Headless browser walk | No browser installable | Real UI JS logic exercised against the LIVE server via node (7/7): queue → review → staged retune → STP rise → hashed audit entries; screenshots are matplotlib renders of real pipeline state | tests/ui_walk.mjs output |
| K4 | Two learning-loop demo designs discarded | First demo passed its gate while demonstrating a 2.5% STP climb (fake-adjacent green); second at low noise had a 5-doc pool | Redesigned with a realistic 70/30 clean/noisy stream + capped threshold steps; gate STRENGTHENED to require ≥25pp climb to ≥40% STP with zero auto-errors → final: 0%→67.5% | PROGRESS.md trail, out/m5_loop.json |
No gate was weakened. The no-peek rule (ground truth never referenced in src/) is machine-enforced by tests/gate_no_peek.py — GREEN throughout.
