# MORNING REPORT — ds-doc-to-decision overnight build
_M0–M6 GREEN · all three prototype builds now complete and measured._

## Gate table (measured this session)
| Gate | Result |
|---|---|
| M0 loaders + manifest | GREEN — 40 sets, 2 GRN-missing flagged; no-peek grep gate live |
| M1 extraction | GREEN — 100% amounts on TXT AND PDF (282/282 each; a85-EOD extractor bug found & fixed) |
| M2 rules engine | GREEN — matching_rules.md verbatim, 16 unit checks, named failing check on every decision |
| M3 scored runs | GREEN — structured 40/40 · planted 13/13 · PDF end-to-end 40/40 (after SKU-prefix category fix; delta honestly tracked from 38/40) |
| M4 calibration | GREEN — GT-free Platt (holdout Brier 0.266→0.215; isotonic honestly worse, reported); measured operating threshold 0.798 |
| M5 queue + learning | GREEN — STP 0%→67.5% staged, zero auto-errors, 54 overrides logged with hashes; UI walk 7/7 |
| M6 robustness + ROI | GREEN — degradation curve to 25% noise; 0 false approvals at 12% noise (fails safe); ROI dashboard with labelled scenario (≈12,483 hr ≈ ₹50 L/yr at 70k docs) |

## Read these three first
1. **DECISIONS.md + tests/gate_no_peek.py** — 40/40 and 13/13 with ground truth provably outside the decision path.
2. **out/m5_loop.json + screenshots/05-stp-learning-curve.png** — the learning loop's staged climb, and BLOCKERS K4 for the two weaker demo designs I discarded en route (that trail is the anti-fabrication discipline working).
3. **The queue itself**: `python3 src/server.py` → approve the R8 items → hit ↺ retune twice → watch threshold and STP move, then check the hashed audit trail.

## Honest gaps
Offline forced: hand-rolled PDF extraction (100% here, but real scans need real OCR), text-domain robustness (no rasteriser), matplotlib renders instead of browser screenshots. All in BLOCKERS.md.

## With more time
Real OCR A/B behind extract_set(); per-vendor fraud analytics on the duplicate detector; queue SLAs + assignment; posting adapters; the claims/contract phases from blueprint Case 3.
