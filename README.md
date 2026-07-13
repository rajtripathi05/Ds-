<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=240&color=0:b3282d,45:6d28d9,100:c99a2e&text=FMCG%20AI%20Portfolio&fontColor=ffffff&fontSize=48&fontAlignY=38&desc=Strategy%20that%20ships%20as%20code%20%C2%B7%20Three%20systems%2C%20measured%20%C2%B7%20A%20live%20S%26OP%20control%20room&descSize=15&descAlignY=58" alt="FMCG AI Portfolio banner" />
</p>

<div align="center">

<a href="#-flight-deck"><img src="https://img.shields.io/badge/01-Flight%20Deck-b3282d?style=for-the-badge" alt="Flight Deck" /></a>
<a href="#-measured-not-claimed"><img src="https://img.shields.io/badge/02-Measured-15803d?style=for-the-badge" alt="Measured" /></a>
<a href="#-the-four-systems"><img src="https://img.shields.io/badge/03-Systems-6d28d9?style=for-the-badge" alt="Systems" /></a>
<a href="#-launch-sequence"><img src="https://img.shields.io/badge/04-Launch-c99a2e?style=for-the-badge" alt="Launch" /></a>

<br /><br />

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=800&size=23&pause=1000&color=B3282D&center=true&vCenter=true&width=920&lines=Most+AI+decks+stop+at+the+slide.;This+one+ships+the+code.;Forecast+error+9%25+vs+18%25+%E2%80%94+measured%2C+not+claimed.;25%2F25+cited+answers%2C+zero+data+leaks.;67.5%25+of+invoices+cleared%2C+zero+wrong+approvals.;A+%E2%82%B910%2C000-cr-scale+S%26OP+cockpit+%E2%80%94+running+live." alt="typing" />

<br /><br />

<img src="https://img.shields.io/badge/Live-fmcgai.netlify.app-0ea5e9?style=flat-square&logo=netlify&logoColor=white" alt="Live" />
<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Runs-100%25%20offline-15803d?style=flat-square" alt="Offline" />
<img src="https://img.shields.io/badge/AI-optional%20(BYO%20key)-6d28d9?style=flat-square&logo=openai&logoColor=white" alt="AI optional" />
<img src="https://img.shields.io/badge/Gates-cockpit%2010%2F10%20%C2%B7%20assistant%2025%2F25%20%C2%B7%20robot%2040%2F40-b3282d?style=flat-square" alt="Gates" />
<img src="https://img.shields.io/badge/Discipline-measured%20%3E%20claimed-c99a2e?style=flat-square" alt="Discipline" />

</div>

---

<a id="-flight-deck"></a>

## 🛰️ Flight Deck

**An end-to-end AI-transformation portfolio for a large FMCG business** — a prioritised map of *where* AI pays off, and the running software that proves the top bets. Everything runs on one laptop, offline, with no API key. Every headline number is either **printed by a test in this repo** or a **labelled estimate with its basis written down** — nothing is asserted.

<table>
<tr>
<td width="25%" align="center"><img src="https://img.shields.io/badge/STRATEGY-b3282d?style=for-the-badge" /><br/>30 scored use-cases · live prioritiser · ROI aggregator</td>
<td width="25%" align="center"><img src="https://img.shields.io/badge/PROTOTYPES-6d28d9?style=for-the-badge" /><br/>3 tested Python systems behind the top 3 cases</td>
<td width="25%" align="center"><img src="https://img.shields.io/badge/LIVE%20DEMOS-0ea5e9?style=for-the-badge" /><br/>Play every system in the browser — no install</td>
<td width="25%" align="center"><img src="https://img.shields.io/badge/DATA%20SPINE-15803d?style=for-the-badge" /><br/>968k-row synthetic dataset with planted signal</td>
</tr>
</table>

> **▶ Try it live:** **[fmcgai.netlify.app](https://fmcgai.netlify.app/)** — three playable demos, a ₹10,000-cr-scale S&OP cockpit, and the interactive strategy blueprint. Connect your own OpenRouter key once and an AI copilot lights up across every app (key stays in your browser).

---

<a id="-measured-not-claimed"></a>

## 📊 Measured, Not Claimed

The differentiator: this repo quotes **only what its tests print**. Where a number is an estimate, it says so and links its basis.

<div align="center">

| System | Metric | Result | vs baseline |
|:--|:--|:--:|:--:|
| 📈 Demand Cockpit | Forecast error (WMAPE, SKU) | **9.0%** | 18.3% seasonal-naïve |
| 📈 Demand Cockpit | What-if → reconcile → re-optimise | **≤ 31 ms** | — |
| 💬 Company Assistant | Grounded-answer evaluation | **25 / 25** | with **0** role-scoped leaks |
| 🧾 Invoice Checker | Decisions vs ground truth | **40 / 40** | 13/13 planted issues caught |
| 🧾 Invoice Checker | Auto-cleared with no human | **67.5%** | **0** wrong auto-approvals |
| 🗄️ Data spine | Distribution → demand correlation | **+0.85** | driver recovered from planted signal |

</div>

<div align="center">
<img src="https://img.shields.io/badge/cockpit-10%2F10%20gates-15803d?style=flat-square" />
<img src="https://img.shields.io/badge/assistant-25%2F25%20·%200%20leaks-15803d?style=flat-square" />
<img src="https://img.shields.io/badge/robot-40%2F40%20·%2013%2F13-15803d?style=flat-square" />
<img src="https://img.shields.io/badge/self%20red--team-2%20claims%20downgraded-c99a2e?style=flat-square" />
</div>

> **Honesty by construction:** a self red-team *downgraded two of its own source claims* rather than defend them ([`REDTEAM_FIXES.md`](REDTEAM_FIXES.md)); ground-truth files are provably absent from the decision code (enforced by a test); every ₹ figure is tagged **ESTIMATE** with a stated basis in [`ASSUMPTIONS.md`](ASSUMPTIONS.md).

---

<a id="-the-four-systems"></a>

## 🧩 The Four Systems

| System | The business problem | What it proves (measured) | Try it |
|:--|:--|:--|:--:|
| **📈 Demand Cockpit** | Planners guess what will sell; promos run on instinct | Forecast error **9.0%** vs **18.3%**; test a promo, get a reconciled + re-optimised answer in **~30 ms** | [demo](https://fmcgai.netlify.app/demo/cockpit/) |
| **💬 Company Assistant** | Answers scattered across policies + data; sensitive figures leak | Every answer **cited**; margins **refused** to Operations, **served** to Executives — enforced twice. **25/25**, **0** leaks | [demo](https://fmcgai.netlify.app/demo/assistant/) |
| **🧾 Invoice Checker** | Every invoice gets human eyes, most for no reason | **40/40** match ground truth · **13/13** planted problems caught · **67.5%** auto-cleared, **0** wrong | [demo](https://fmcgai.netlify.app/demo/invoice/) |
| **🛰️ FMCG Cockpit** | No single, consistent S&OP picture; what-ifs take days | A zero-install control room: demand→supply→capacity→OTIF→₹ re-solves in **~1 s** on any change, at **₹10,000-cr scale** | [launch](https://fmcgai.netlify.app/fmcg-cockpit.html) |

---

## 🔀 System Flow

```mermaid
flowchart LR
    subgraph Strategy
      A[30 scored use-cases] --> B[Top-8 business cases]
      B --> C[0-6-12 roadmap + governance]
    end
    subgraph Proof
      D[Demand Cockpit]:::p
      E[Company Assistant]:::p
      F[Invoice Checker]:::p
    end
    subgraph LiveControlRoom
      G[FMCG Cockpit<br/>demand → supply → OTIF → ₹]:::g
    end
    B --> D & E & F
    H[(968k-row synthetic spine<br/>+ planted drivers)] --> D & E & F & G
    D & E & F & G --> I{{Optional AI copilot<br/>BYO OpenRouter key}}:::ai
    classDef p fill:#6d28d9,color:#fff,stroke:#4c1d95;
    classDef g fill:#b3282d,color:#fff,stroke:#8a1f23;
    classDef ai fill:#0ea5e9,color:#fff,stroke:#0369a1;
```

---

## ⚛️ Feature Reactor

| Module | What it delivers | Status |
|:--|:--|:--:|
| Playable browser demos | Every system runs client-side on real engine output — no server | ![Ready](https://img.shields.io/badge/Live-15803d?style=flat-square) |
| Deterministic core | Frozen engines; models/rules are read-only, presentation never writes into them | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| AI copilot (BYO key) | One OpenRouter key works across **every** app; validates every proposal against the engine | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Streaming answers | Token-by-token responses in a shared floating copilot (`demo/ai.js`) | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Monte-Carlo risk | 800-run OTIF confidence bands (P10/P50/P90) + fragility flags | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| War-room agents | Five expert agents debate and converge on one recommendation | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Auto-plan | Multi-step, engine-validated plan to hit the OTIF target | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Role gate | Operations sees zero ₹ — not shown, not computed into anything visible | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Resilience contract | Missing/dirty data → warn + fallback + completeness badge, never a crash | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Workbook-driven | Drop an Excel/CSV master; the whole chain re-solves | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |
| Synthetic data spine | 968k sales rows with distribution, facings, ad-spend, seasonality drivers + ground truth | ![Ready](https://img.shields.io/badge/Ready-15803d?style=flat-square) |

---

## 🤝 The Deterministic Contract

> The engine is deterministic; the AI only *proposes*. Every AI / slider / command becomes an **intent** the frozen core validates before it can change the plan. No second solver, no hallucinated numbers.

```mermaid
sequenceDiagram
    participant User
    participant UI as Cockpit UI
    participant AI as OpenRouter (your key)
    participant Engine as Frozen engine
    User->>UI: "we won a big Diwali carbonated order — what breaks?"
    UI->>AI: question + live plan context
    AI-->>UI: proposed intent {order, +cases, Carbonated}
    UI->>Engine: validate + re-solve (deterministic)
    Engine-->>UI: new OTIF, binding constraint, ₹ at risk
    UI-->>User: narrated result — undoable, reproducible
    Note over Engine: invalid instruction changes nothing
```

---

## 🏛️ Architecture

```mermaid
mindmap
  root((FMCG AI Portfolio))
    Strategy
      Interactive blueprint
      Board deck + one-pager
      AGM production roadmap
    Systems
      Demand Cockpit (forecast + S&OP)
      Company Assistant (RAG + text-to-SQL)
      Invoice Checker (3-way match)
      FMCG Cockpit (S&OP control room)
    Data
      968k sales + drivers
      AP invoices + planted issues
      HR + attrition
      Knowledge corpus
      Ground truth
    Intelligence
      Deterministic engines
      Optional OpenRouter copilot
      Monte-Carlo + agents
    Governance
      VERIFIED / ESTIMATE / PROTOTYPED tags
      Role-scoped access
      Model cards + audit trail
```

---

## 🧱 Tech Wall

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,js,html,css,sklearn,github,netlify" alt="stack" />
  <br/>
  <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/LightGBM-2ea44f?style=for-the-badge" />
  <img src="https://img.shields.io/badge/SheetJS-217346?style=for-the-badge" />
  <img src="https://img.shields.io/badge/OpenRouter-6d28d9?style=for-the-badge" />
  <img src="https://img.shields.io/badge/vanilla%20ES%20modules-f7df1e?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/zero%20build-111827?style=for-the-badge" />
</p>

<div align="center"><i>No framework, no bundler for the demos — plain HTML + hand-written CSS + vanilla JS, so they run anywhere, even offline.</i></div>

---

<a id="-launch-sequence"></a>

## 🚀 Launch Sequence

<table>
<tr>
<td width="50%">

### ▶ Run the live apps (Windows)

```bash
# double-click, or:
cd "files practice"
START_ALL.bat
# installs deps, starts all 3 servers, opens HOME.html
```

Then open the three ports (or `HOME.html`):
```text
:8765  Demand Cockpit
:8770  Company Assistant
:8780  Invoice Checker
```

</td>
<td width="50%">

### ▶ Run the test gates yourself

```bash
cd "files practice/ds-demand-cockpit/ds-demand-cockpit"   && python tests/run_tests.py     # 10 gates
cd "files practice/ds-copilot/ds-copilot"                 && python tests/eval_harness.py  # 25/25 · 0 leaks
cd "files practice/ds-doc-to-decision/ds-doc-to-decision" && python tests/gate_m3.py       # 40/40 · 13/13
```

### ▶ Optional AI layer

Open any demo or the cockpit → **🤖** → paste an OpenRouter key. One key, every app. It stays in your browser and is sent only to OpenRouter.

</td>
</tr>
</table>

---

## 🗄️ The Data Spine

One seeded fictional company feeds every "implement-now" use-case, each with **planted signal + a ground-truth file** so a model has something real to find.

```mermaid
flowchart TD
    M[Masters: products · distributors · plants · calendar] --> S[Secondary sales<br/>968,287 rows]
    S -->|drivers| D1[num_outlets +0.85]
    S -->|drivers| D2[shelf_facings +0.55]
    S -->|drivers| D3[ad_spend +20% on campaigns]
    S -->|drivers| D4[seasonal_index]
    M --> AP[AP invoices<br/>13% planted issues]
    M --> HR[4,000 employees<br/>18% attrition]
    M --> KB[39-doc knowledge corpus]
    S & AP & HR & KB --> GT[(Ground truth<br/>validation only)]
    style S fill:#6d28d9,color:#fff
    style GT fill:#c99a2e,color:#111
```

Full column dictionary → [`synthetic-data/DATA_DICTIONARY.md`](synthetic-data/DATA_DICTIONARY.md) · browse it live → [**data.html**](https://fmcgai.netlify.app/data.html)

---

## 🗺️ Project Map

```text
.
├─ index.html                     # Live landing (stats · ROI model · launch buttons)
├─ fmcg-cockpit.html              # ⭐ Zero-install S&OP control room (12 tabs, AI copilot)
├─ data.html                      # Browse the dataset (previews + downloads)
├─ 2026-07-12-fmcg-blueprint.html # Master artifact — 30 use-cases, live prioritiser, ROI
├─ 2026-07-12-blueprint-deck.html # 14-slide board deck (prints to PDF)
├─ demo/
│  ├─ ai.js                       # Shared AI copilot (one key, every demo, streaming)
│  ├─ cockpit/  assistant/  invoice/   # Playable, client-side, real engine output
│  └─ data/                       # Inlined engine output powering the demos
├─ synthetic-data/                # generate_all.py · 6 datasets · ground truth · dictionary
└─ files practice/                # The 3 Python prototypes · START_ALL.bat · SETUP_LLM.md
```

---

## 🔐 Governance & Honesty Vault

<table>
<tr><td align="center"><img src="https://img.shields.io/badge/Tagged-VERIFIED%20%2F%20ESTIMATE%20%2F%20PROTOTYPED-c99a2e?style=for-the-badge"/></td><td>Every fact is a re-fetched public citation; every ₹ is an estimate with a basis; every system claim is a printed test result.</td></tr>
<tr><td align="center"><img src="https://img.shields.io/badge/Role--scoped-No%20%E2%82%B9%20for%20Operations-b3282d?style=for-the-badge"/></td><td>Sensitive figures are refused to the wrong role — not shown and not computed into anything visible.</td></tr>
<tr><td align="center"><img src="https://img.shields.io/badge/Keys-Browser%20only-15803d?style=for-the-badge"/></td><td>The optional AI key lives in your browser's localStorage and is sent only to OpenRouter — never to this site or the repo.</td></tr>
<tr><td align="center"><img src="https://img.shields.io/badge/Data-100%25%20synthetic-6d28d9?style=for-the-badge"/></td><td>Seeded generators. The pipelines are real; the numbers describe generated data. The strategy's worked example uses only public facts about one listed FMCG.</td></tr>
</table>

---

## 📈 Roadmap Console

```mermaid
timeline
    title FMCG AI Portfolio Roadmap
    Shipped
      : Strategy blueprint + board deck + one-pager
      : 3 tested prototypes (10/10 · 25/25 · 40/40)
      : Playable browser demos + live landing
      : FMCG Cockpit v2 (Monte-Carlo · agents · India map)
      : 968k-row dataset with demand drivers
      : Shared OpenRouter AI copilot across all apps
    Next
      : Campaign / advertisement / seasonal masters as cockpit levers
      : Simple / Pro cockpit modes
      : A 'Models' page — trained forecaster + fairness check
    Later
      : Live SAP / DMS / HRMS adapters
      : CI gate (gates + demo harness on every push)
      : Voice input · PDF / Excel plan export
```

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&height=80&color=0:15803d,50:0ea5e9,100:6d28d9&text=Built%20and%20measured%2C%20not%20asserted&fontColor=ffffff&fontSize=22" alt="footer" />
</p>

<div align="center">
  <img src="https://img.shields.io/badge/Status-Active%20development-15803d?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Data-Synthetic-6d28d9?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Independent-portfolio%20project-b3282d?style=for-the-badge" />
  <br/><br/>
  <sub>Independent portfolio project · synthetic test data · not affiliated with or endorsed by any company · RAJ · 2026</sub>
</div>
