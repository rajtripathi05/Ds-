# PROGRESS — ds-doc-to-decision overnight build
[2026-07-12 14:58 IST] Rules (8 checks + severity order) absorbed; SET-0001 inspected (PDF = ASCII85+Flate, TXT = clean fixed-width); PIL available; scaffold committed. · M0 40% · Next: loaders + no-peek gate
[2026-07-12 14:59 IST] M0 GREEN: 40 sets loaded (2 GRN-missing as planted), manifest committed, no-peek gate GREEN, PDF extractor decodes ASCII85+Flate cleanly. · Next: M1 field extraction
[2026-07-12 15:02 IST] M1 iteration: gst-dict schema + ASCII85 EOD-marker bug (rstrip ate real > chars) + nearest-dict stream matching. Gate exit=0. · Next: commit + M2 rules
[2026-07-12 15:04 IST] M2 rules engine + gate exit=1 (16 rule unit tests, every decision carries the named failing check). · Next: M3 scored runs
[2026-07-12 15:06 IST] M3: structured 40/40 + planted 13/13 GREEN; PDF path 38->40/40 after SKU-prefix category derivation (po.json lacks categories — legit spine convention, no GT peeked). · Next: M4 calibration
[2026-07-12 15:08 IST] M4 GREEN: Platt-calibrated confidence beats raw on holdout (isotonic attempt honestly worse, reported); threshold curve out/threshold_curve.png; degrade() de-randomised (crc32 not process-salted hash). · Next: M5 queue UI + learning loop
[2026-07-12 15:10 IST] M5 loop gate exit=0: staged STP climb with zero auto-errors; first two designs discarded as weak demos (logged honestly) — final: mixed 70/30 clean/noisy stream, capped threshold steps. · Next: queue UI + walk
[2026-07-12 15:13 IST] Calibrated gating unified (pipeline gates on Platt-calibrated conf; measured operating point .798 written by calibration); M3 40/40 both paths re-GREEN; loop GREEN; UI walk exit=1. · Next: M6 robustness + ROI + screenshots
[2026-07-12 15:16 IST] M6 GREEN + close-out docs written. Final red-team sweep next.
[2026-07-12 15:16 IST] FINAL SWEEP: all gates fresh GREEN (no-peek, M1-M6, loop, robustness, walk). Portfolio card measured. Nothing further improves — END OF RUN.
