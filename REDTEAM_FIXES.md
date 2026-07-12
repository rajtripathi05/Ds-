# REDTEAM_FIXES.md — every finding and fix (overnight Run 2, R0)
All fixes applied to `2026-07-12-ds-blueprint-v2.html`. v1 untouched (frozen baseline, contains the pre-fix state).

## A. Arithmetic (recomputed every ₹ line in all 8 ROI tables)
| # | Location | Finding | Fix |
|---|----------|---------|-----|
| F1 | Case 6 hours | 3,000 × 3/wk × 6 min × 46 wk × 50% = 20,700 hr, shown as "≈27,000 hr ≈ ₹1.1 cr" (annualisation dropped mid-calc) | Recomputed; then superseded by F13 (distributor count verified at 5,000+ → 34,500 hr ≈ ₹1.38 cr; basis string now shows every factor incl. 46 wk) |
| F2 | Case 3 net | "₹1.3–3.6 cr" didn't reproduce: 0.36+0.90−0.15=1.11 low end | Restated ₹1.1–3.6 cr net of run, with the subtraction shown |
| F3 | Case 4 release | Top end used ₹400 cr inventory base, but 45/365 × ₹3,000 cr = ₹370 cr → 15% = ₹55 cr not ₹60 | Base restated ₹247–370 cr; release ₹25–55 cr; carrying saving ₹2.5–6.6 cr/yr |
| F4 | Case 1 carrying + cash | ₹0.7–1.2 cr and ₹7–10 cr didn't reproduce from 8–12% × ₹66–99 cr × 10–12% | Restated: release ₹5.3–11.8 cr (shown), carrying ₹0.5–1.4 cr/yr; net ₹2.3–5.6 cr/yr |
| F5 | Case 5 verdict | "pays back <6 months" vague; no net shown | Net ₹0.8–2.8 cr/yr shown; payback <4 months at low end (0.25/0.8×12=3.75) |
| F6 | Case 7 verdict | "roughly breakeven" unquantified | −₹0.05 to +₹1.3 cr/yr with the arithmetic shown |
| F7 | Case 8 payback | "12–24 months" didn't reproduce; correct range from shown figures = (0.35–0.55)/(0.32–1.05) ≈ 4–20 months | Restated ~4–20 months with net-of-run benefits shown |
| F8 | Case 2 net | "₹0.9–1.5 cr" understated top end (1.89−0.35 wait: 1.89−0.20=1.69) | Restated ₹0.9–1.7 cr net of run |
| F9 | Tab 5 "12-month economics" | ₹8–17 cr line mislabelled ("sum of midpoints" is one number, not a range); one-time ₹32–70 cr stale | Reconciled to aggregator scenarios ₹9.7/17.9/26.2 cr net recurring; one-time ₹30–67 cr |
| F10 | E13 | Conservative sum didn't tie to corrected cases | Restated: 2.38+1.27+1.26+1.68 = ₹6.6 cr gross (₹5.9 net); gate ₹6 cr |

## B. Citations (every V-link re-fetched 12 Jul 2026; findings)
| # | Item | Finding | Fix |
|---|------|---------|-----|
| F11 | V8 "21 units, 12 agri, 24 depots" | NOT on the company's manufacturing page — it lists 15 sites across UP, Haryana, Assam, Rajasthan, Tripura (incl. a cattle farm). The 21/12/24 phrasing traces to third-party directories | V8 rewritten to the 15 listed sites; 21/12/24 demoted to new estimate E14; every "21 plants/24 depots" phrase in exec, BC2, BC3, BC4, BC8, MF-3, SC-3 rewritten |
| F12 | V9 "35 lakh outlets" | Primary sources say ~15 lakh outlets DIRECT and 35 lakh+ total (direct+indirect); super-stockist count differs across sources (o9: 100+, DS PR: 150+) | V9 rewritten with the direct/indirect split and the source discrepancy noted; exec card, BC1, BC6, BC7 updated |
| F13 | Distributor count | "3,000 (E8)" was an estimate — DS PR + o9 PR verify 5,000+ | Upgraded to VERIFIED; Case 6 recomputed upward (34,500 hr, ₹1.38 cr); E8 register rewritten; SL-1 rationale updated |
| F14 | V2 "₹3,000 cr investment push" | Not in the re-fetched BS article (which verifies: ₹20,000 cr by centenary 2029, top-10 ambition, ₹1,000 cr hospitality, ₹300 cr branding) | V2 rewritten; ₹3,000 cr kept only as "reported, not re-verifiable"; roadmap sentence rewritten to use verified lines |
| F15 | V14 Pulse ₹1,000 cr by 2027 | Secondary pages not re-fetched | Downgraded to REPORTED; noted "not used in any calculation" (true — checked) |
| F16 | V6/V7 brand & vertical lists | Company nav (fetched) shows 8 named verticals incl. Dairy, and a fuller brand list | V6/V7 rewritten from primary; BC2 "7 verticals" → 8 |
| F17 | New verified facts added | F&B 19% CAGR; company's own AI/automation focus; #2 non-chocolate / #1 ethnic confectionery, Pulse ≈45% of confectionery; confectionery mfg outsourced | Added V15–V18; V16 wired into exec thesis ("why now"); V18 re-scoped Case 8 pilot to own units (mouth-freshener + spices/foods lines) |
| F18 | Scope footnote | FY25 ₹10,000+ cr vs Wikipedia/Forbes ₹5,500 cr (2023) | Footnote added in Tab 7 (re-verified via Wikipedia fetch); explains timing/entity-scope difference |

## C. Consistency sweep
| # | Check | Result |
|---|-------|--------|
| F19 | Numbers stated twice must match | Exec top-8 quadrants = computed quadrants (script-verified); Tab-5 scenarios = aggregator PORT sums (script-asserted, see verify log); one-time release ₹30–67 cr consistent in Tab 4/Tab 5 |
| F20 | Scores/rationales | 30 use cases re-checked: all scores 1–5, 4 rationales each; SL-1/MF-1/MF-3/SC-3 rationale text updated where facts changed; no score CHANGES needed (fact corrections didn't cross any rubric boundary — 15 vs 21 sites doesn't alter Value-5 scale judgments) |

## D. Post-ladder 10x loop (Run 2 continuation)
| # | Finding | Fix |
|---|---------|-----|
| F21 | Case 6 payback "~2–3 months" understated reproducible lower bound (0.2/2.1×12 ≈ 1.1 mo) | Restated "~1–3 months" |
| F22 | Deck slide 4 / objection 12 claimed "peers are deploying the same tools" without a source | Verified from HUL's own newsroom (fetched): Envision ~2.5 crore shelf images/month, AI Nerve Center, Shikhar GenAI → new V19; deck, pitch kit and Case 7 now cite it (peer-proof for shelf vision) |
| F23 | Scripts had never been executed against a DOM (only parsed) | Built a node DOM shim; blueprint + deck scripts run clean — zero runtime errors, zero references to element IDs absent from the HTML (re-run after every 10x edit) |
