# From IGL's NSU digital twin to an FMCG plant — the bridge note (Prototype #0)
**RAJ · 12 July 2026 · one page** · *All systems referenced here were built and measured on a
synthetic test bed with planted ground truth; independent work, not affiliated with the company.*

> **Provenance note (honesty first):** the NSU CLAUDE.md was not present in `reference/` at
> packaging time (see GAPS G1), so this note reconstructs the pattern from the IGL operating
> discipline quoted in all three project kickoffs and from the same four-law architecture that
> the three DS prototypes then shipped and measured. Where NSU's own wording matters, read the
> source document.

## What the NSU platform is
NSU is the digital-twin platform I built at India Glycols (IGL): a live, governed model of a
continuous-process plant in which *nothing acts directly on the asset*. Every proposed change —
an operator intent, a setpoint experiment, a schedule move — is expressed as an **intent**,
validated against a **deterministic truth layer** (mass/energy balances, interlocks, quality
constraints), simulated on the **twin**, and only then surfaced for action. The same operating
discipline that governs the code governs the plant model: plan before execution, protect
existing state, every change leaves an audit trail, ask instead of assume.

## The four architecture laws (as instantiated across every system I've since built)
1. **A frozen deterministic core is truth** — balances and constraints are computed, versioned
   and read-only; opinion layers never write into them. *(DS cockpit: frozen forecast core;
   doc-robot: written matching rules decide, extraction never does.)*
2. **One-way state** — a single pipeline writes the plant/plan snapshot; every consumer reads.
   *(All three DS builds enforce a single writer of `out/plan` or its equivalent.)*
3. **Every change is an intent that must reconcile before it applies** — no lever bypasses the
   validation step. *(Cockpit what-ifs pass reconcile+optimize in ≤31 ms, measured; copilot SQL
   passes a validator AND a driver-level authorizer.)*
4. **Never stops** — bad sensors, missing files, unreadable documents degrade to warn + fallback
   + completeness badge, never to a silent failure or a fatal one. *(Proven against planted
   messy data: 5/5 defect classes caught in the cockpit build; unreadable invoices route with a
   named reason in the doc-robot.)*

## Mapping the pattern to an FMCG plant
An FMCG site is a discrete-continuous hybrid, but the twin shape is identical:
**packing lines** are the units (OEE, changeover matrices, reject gates ↔ my vision-QC and
line-level intents); **shared fillers and blenders** are the contended resources the optimizer
allocates under capacity and sequence constraints (↔ the cockpit's constrained allocator that
names its binding constraint); **utilities** (steam, chilled water, compressed air, CIP) are the
common services whose balances form the deterministic layer, exactly as in a continuous plant.
Demand enters as the forecast spine (the cockpit), documents enter as governed decisions (the
doc-robot), and people query it all through a role-scoped copilot — the twin is what joins them.

## Why this is Prototype #0
The three FMCG-themed systems in this portfolio are not three ideas — they are the NSU pattern
applied three times: same laws, same discipline, same test-gated honesty. NSU is the industrial
original; the FMCG trilogy is the evidence the pattern transfers.
