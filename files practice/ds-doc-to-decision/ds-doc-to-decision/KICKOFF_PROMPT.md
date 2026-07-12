# KICKOFF — ds-doc-to-decision (GOAT 3: Intelligent Document Automation)

You are my senior ML engineer. We are building Document-to-Decision: ingest messy distributor
documents, extract, 3-way match, and DECIDE (approve / route / reject) with a calibrated
confidence and a human-readable reason — plus a learning loop that raises straight-through rate.

KEEP-ALIVE + PROGRESS (mandatory, non-negotiable): my screen turns off after 5
minutes without visible activity (system sleep is already set to Never — this is display-off
only). Never go more than 3 minutes without a visible action: append a timestamped heartbeat
line to PROGRESS.md — current step, % done, next step — or open and close a file. Maintain
PROGRESS.md for the entire session; it doubles as the progress log I review.

OPERATING DISCIPLINE (from ./reference — my proven IGL rules): PLAN before
execution (objective / approach / affected files / risks) and WAIT for my approval; PROTECT
existing work (show diffs; never overwrite without explicit OK; new versions get -v2 suffix);
deliverable files named YYYY-MM-DD-descriptive-name.ext; END EVERY TASK with a File Change
Report (Created / Modified / Deleted + summary); ask instead of assuming.

FIRST ACTION: read ./data/matching_rules.md (THE decision truth), ./data/ground_truth_labels.csv,
./data/planted_discrepancies.csv, open 2-3 sets under ./data/sets, then give me the PLAN + repo
CLAUDE.md and WAIT for approval.

DATA (spine-consistent: real SKUs/dist codes from ./masters):
- ./data/sets/SET-0001..0040: po.json + grn.json (2 sets deliberately missing it) + invoice.json
  + invoice.txt + invoice.pdf (OCR-ready renders with GST math, amount-in-words, COA lines).
- 13 planted discrepancies (qty 2-10% and >10%, price mismatch, missing GRN, expired COA,
  duplicate invoice number SET-0001↔SET-0009, arithmetic error) — all logged.
- ground_truth_labels.csv: 27 auto_approve / 8 route_to_human / 5 reject — INDEPENDENTLY
  re-derived from matching_rules.md with zero mismatches. Rules mirror the copilot corpus
  policies (±2% qty tolerance; COA 12-month validity).

ARCHITECTURE LAWS:
1. RULES ARE TRUTH — LLM/OCR extracts; matching_rules.md decides. Extraction never auto-posts.
2. CONFIDENCE GATE — calibrated per-document confidence; above threshold → straight-through;
   below → human queue with the exact failing check. Never a silent post.
3. LEARNING LOOP — every human override is logged and re-tunes thresholds/rules; show the
   straight-through-processing rate CLIMB over simulated override rounds.
4. NEVER STOPS — unreadable/missing field → flag + route with reason, never fatal.

BUILD ORDER (gated; PROGRESS.md heartbeat):
M0 Plan + CLAUDE.md. M1 Extraction: parse invoice.pdf AND invoice.txt into a normalized schema
(pdfplumber first; LLM/vision fallback); field-level confidence; validate against invoice.json
(field accuracy report). M2 Match engine implementing matching_rules.md verbatim: per-line qty
vs GRN, price vs PO, dates, COA validity, duplicate invoice detector ACROSS sets, GST arithmetic.
M3 Decisions: run all 40 → target 40/40 vs ground_truth_labels.csv from structured inputs; then
end-to-end from PDFs with the accuracy delta reported; 13/13 planted-discrepancy catch rate.
M4 Confidence calibration (holdout + isotonic or Platt) with a threshold-tuning view (STP vs
error trade-off curve). M5 Exception-queue UI: aging, reason codes, one-click approve/override;
overrides feed the learning loop; audit log per decision (inputs, checks fired, actor).
M6 Robustness: degrade the PDFs (skew/blur/contrast/noise), plot accuracy-vs-noise; ROI
dashboard (STP%, exception%, error reduction, hours and ₹ saved — assumptions documented).

Start with the PLAN.
