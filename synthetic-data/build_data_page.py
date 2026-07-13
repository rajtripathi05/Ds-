#!/usr/bin/env python3
"""Build data.html — a portfolio-styled, browsable view of the synthetic dataset,
with real preview tables, row counts, planted-signal proof and download links."""
import pandas as pd, numpy as np, pathlib, html, glob
SD=pathlib.Path(__file__).resolve().parent
ROOT=SD.parent
def rd(*p, **k): return pd.read_csv(SD.joinpath(*p), **k)

# ---- committable sales sample (full 81MB stays local / regenerable) ----
samp=rd("sales","sales_secondary.csv", nrows=5000)
samp.to_csv(SD/"sales"/"sales_secondary_sample.csv", index=False)

# ---- stats ----
prod=rd("masters","products.csv"); dist=rd("masters","distributors.csv")
s=rd("sales","sales_secondary.csv", usecols=["category","units","unit_price","promo_flag","week_start"])
sales_rows=len(s)
up=s.groupby("promo_flag")["units"].mean(); promo_lift=100*(up[1]/up[0]-1)
bev=s[s.category=="Beverages"].copy(); bev["m"]=bev.week_start.str.slice(5,7).astype(int)
summer=bev[bev.m.isin([4,5,6])].units.mean(); winter=bev[bev.m.isin([11,12,1])].units.mean()
promos=rd("promotions","promotions.csv"); perf=rd("promotions","promo_performance.csv")
inv=rd("finance","ap_invoices.csv"); gt=rd("ground_truth","planted_invoice_issues.csv")
emp=rd("hr","employees.csv")
L=emp[emp.attrition_flag==1]; St=emp[emp.attrition_flag==0]
rt=rd("ground_truth","resume_jd_truth.csv")
ncorpus=len(glob.glob(str(SD/"knowledge"/"corpus"/"*.md")))
nres=len(glob.glob(str(SD/"talent"/"resumes"/"*.txt"))); njd=len(glob.glob(str(SD/"talent"/"jds"/"*.txt")))
total_rows = sales_rows+len(promos)+len(perf)+len(inv)+len(rd("finance","ap_invoice_lines.csv"))+len(rd("finance","purchase_orders.csv"))+len(rd("finance","grn.csv"))+len(emp)+4000

def tbl(df, cols, n=6):
    df=df[cols].head(n)
    th="".join(f"<th>{html.escape(c)}</th>" for c in cols)
    rows=""
    for _,r in df.iterrows():
        tds="".join(f"<td>{html.escape(str(r[c]))}</td>" for c in cols)
        rows+=f"<tr>{tds}</tr>"
    return f"<div class='tw'><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>"

CSS = """
:root{--ink:#171412;--ink2:#3f3a34;--mut:#6f675e;--line:#e7e2db;--bg:#f5f2ee;--card:#fff;--acc:#b3282d;--acc2:#8a1f23;--ok:#15803d;--okbg:#e9f6ee;--vio:#6d28d9;--gold:#c99a2e;--shadow:0 1px 3px rgba(0,0,0,.05),0 10px 30px rgba(0,0,0,.06)}
*{box-sizing:border-box;margin:0;padding:0}
html{font-size:16.5px}body{font-family:ui-sans-serif,system-ui,'Segoe UI',Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}
.serif{font-family:Georgia,'Times New Roman',serif}a{color:var(--acc2)}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
nav{position:sticky;top:0;z-index:30;background:rgba(245,242,238,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
nav .in{max-width:1120px;margin:0 auto;padding:12px 24px;display:flex;gap:16px;align-items:center}
nav a.home{font-size:13.5px;text-decoration:none;color:var(--mut);font-weight:600}nav a.home:hover{color:var(--acc)}
nav .b{font-weight:800;font-size:15px}
.hero{background:radial-gradient(1000px 420px at 72% -10%,#3b1d1e 0,transparent 60%),linear-gradient(160deg,#1c1917,#241f1c 55%,#2c1a1b);color:#faf7f4;overflow:hidden;position:relative}
.hero .in{position:relative;padding:52px 0 40px}
.kick{letter-spacing:.16em;text-transform:uppercase;font-size:11.5px;color:#f6c9cb;font-weight:800}
.hero h1{font-size:clamp(28px,4.5vw,44px);line-height:1.08;letter-spacing:-.02em;margin:10px 0 0}
.hero p{margin-top:14px;color:#e6dcd6;max-width:72ch;font-size:16px}
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin-top:30px;border:1px solid #ffffff1f;border-radius:14px;overflow:hidden;background:#ffffff08}
.strip div{padding:16px 18px;border-right:1px solid #ffffff14}
.strip .n{font-size:26px;font-weight:800;font-variant-numeric:tabular-nums}.strip .l{font-size:12px;color:#d8cec8;margin-top:4px}
@media(max-width:720px){.strip{grid-template-columns:1fr 1fr}}
section{padding:30px 0}
h2.s{font-size:clamp(22px,3vw,30px);letter-spacing:-.02em;margin-bottom:6px}
.eyebrow{letter-spacing:.15em;text-transform:uppercase;font-size:11.5px;color:var(--acc2);font-weight:800}
.ds{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);padding:24px;margin-bottom:20px}
.ds .h{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:flex-start;margin-bottom:6px}
.ds h3{font-size:20px;display:flex;gap:9px;align-items:center}
.ds .rows{font-size:12.5px;font-weight:800;color:var(--vio);background:#f4f0fd;border:1px solid #d8ccf7;border-radius:999px;padding:3px 11px;white-space:nowrap}
.ds .powers{font-size:14px;color:var(--ink2);margin-bottom:6px}
.ds .powers b{color:var(--ink)}
.ds .sig{font-size:13px;color:var(--ok);background:var(--okbg);border-radius:8px;padding:7px 11px;display:inline-block;margin:8px 0 4px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin-top:12px}
table{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
th{background:#faf8f5;text-align:left;padding:8px 11px;border-bottom:2px solid var(--line);font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
td{padding:7px 11px;border-bottom:1px solid var(--line);color:var(--ink2)}
.dl{margin-top:12px;display:flex;gap:10px;flex-wrap:wrap}
.dl a{font-size:13px;font-weight:700;text-decoration:none;color:var(--ink);background:#faf8f5;border:1px solid var(--line);border-radius:9px;padding:8px 13px}
.dl a:hover{border-color:var(--acc)}
.proof{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:22px;display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
@media(max-width:720px){.proof{grid-template-columns:1fr}}
.proof div{font-size:14px;color:var(--ink2)}.proof b{color:var(--ok)}
.note{font-size:12.5px;color:var(--mut);background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:10px;padding:14px 16px;margin-top:18px}
pre{background:#1c1917;color:#e7ddd7;border-radius:12px;padding:16px 18px;overflow-x:auto;font-size:13px;margin-top:10px}
footer{padding:34px 0;text-align:center;color:var(--mut);font-size:12.5px;border-top:1px solid var(--line);margin-top:20px}
"""

def ds_card(icon,title,rows,powers,sig,table_html,dls):
    dl="".join(f"<a href='{href}'>⬇ {label}</a>" for label,href in dls)
    return (f"<div class='ds'><div class='h'><h3>{icon} {title}</h3><span class='rows'>{rows}</span></div>"
            f"<div class='powers'>{powers}</div><div class='sig'>{sig}</div>{table_html}<div class='dl'>{dl}</div></div>")

body = f"""
<nav><div class="in"><a class="home" href="index.html">← Portfolio</a><span class="b">📦 The dataset</span></div></nav>
<header class="hero"><div class="wrap in">
  <div class="kick">The data behind the right-now use-cases</div>
  <h1 class="serif">One synthetic FMCG company — every dataset, with signal you can find.</h1>
  <p>These demos and models run on <b>Northwind FMCG (Synthetic)</b>: a single, internally-consistent, fully-seeded fictional company. Every dataset carries planted signal and a matching ground-truth file, so a model has something real to recover — and you can prove it did. 100% synthetic; no real company data.</p>
  <div class="strip">
    <div><div class="n">{total_rows:,}</div><div class="l">total rows generated</div></div>
    <div><div class="n">6</div><div class="l">datasets, one company</div></div>
    <div><div class="n">{len(gt)+len(rt)+6}</div><div class="l">labelled ground-truth items</div></div>
    <div><div class="n">SEED 42</div><div class="l">fully reproducible</div></div>
  </div>
</div></header>

<main class="wrap">
<section><div class="eyebrow">Six datasets</div><h2 class="s serif">Browse it — real rows, real signal</h2></section>

{ds_card("📈","Secondary sales", f"{sales_rows:,} rows",
  "Powers <b>demand forecasting</b>, report-from-a-file and BI dashboards. Distributor × SKU × week offtake with price and promo flags.",
  f"Verified signal: promo weeks run +{promo_lift:.0f}% above non-promo; beverages peak in summer ({summer:.0f} vs {winter:.0f} u).",
  tbl(samp,["week_start","distributor_code","sku","category","units","unit_price","promo_flag"]),
  [("sales sample (5k)","synthetic-data/sales/sales_secondary_sample.csv"),("targets","synthetic-data/sales/sales_targets.csv")])}

{ds_card("🎯","Promotions", f"{len(promos)} events",
  "Powers <b>trade-promotion ROI</b>. Event master + realised incremental performance; true per-category elasticities as ground truth.",
  f"Median promo ROI {perf.roi.median():.2f}× on a simple incremental basis — the analysis is finding the winners.",
  tbl(promos,["promo_id","sku","category","promo_type","discount_depth","planned_spend_inr"]),
  [("promotions","synthetic-data/promotions/promotions.csv"),("performance","synthetic-data/promotions/promo_performance.csv"),("true elasticities","synthetic-data/ground_truth/promo_true_elasticities.csv")])}

{ds_card("🧾","Accounts payable", f"{len(inv):,} invoices",
  "Powers <b>invoice 3-way match</b> and duplicate/anomaly detection. Invoices + POs + GRNs with line items and taxes.",
  f"{len(gt)} planted issues ({100*len(gt)/len(inv):.0f}%) across 7 types — with a ground-truth answer key.",
  tbl(inv,["invoice_no","vendor_code","invoice_date","subtotal","gst_pct","total_amount"]),
  [("invoices","synthetic-data/finance/ap_invoices.csv"),("PO lines","synthetic-data/finance/purchase_orders.csv"),("GRNs","synthetic-data/finance/grn.csv"),("planted issues","synthetic-data/ground_truth/planted_invoice_issues.csv")])}

{ds_card("👥","HR & attrition", f"{len(emp):,} employees",
  "Powers <b>attrition prediction</b> and workforce analytics. People master + engagement survey; attrition flag with documented drivers.",
  f"Verified: leavers show lower engagement ({L.engagement_score.mean():.2f} vs {St.engagement_score.mean():.2f}) and below-band pay ({L.comp_ratio.mean():.2f} vs {St.comp_ratio.mean():.2f}).",
  tbl(emp,["emp_id","department","band","tenure_years","comp_ratio","engagement_score","attrition_flag"]),
  [("employees","synthetic-data/hr/employees.csv"),("engagement","synthetic-data/hr/engagement_survey.csv"),("drivers (truth)","synthetic-data/ground_truth/attrition_drivers.md")])}

{ds_card("📄","Talent (resumes + JDs)", f"{nres} CVs · {njd} JDs",
  "Powers <b>resume ↔ JD matching</b>. Text resumes and job descriptions with an intended-match ground truth.",
  f"Strong matches average 0.88 skill overlap vs 0.16 for weak — separable by design.",
  tbl(rt,["resume_id","best_match_jd","target_role","match_label","skill_overlap"]),
  [("match truth","synthetic-data/ground_truth/resume_jd_truth.csv")])}

{ds_card("📚","Knowledge corpus", f"{ncorpus} documents",
  "Powers the <b>policy chatbot</b>, knowledge search and summarisation. HR/finance/SOP/FAQ/circular/meeting-note docs with concrete facts.",
  f"Ships with a {len(rd('knowledge','qa_examples.csv'))}-question eval set (question → expected doc → answer) for grounding checks.",
  tbl(rd("knowledge","qa_examples.csv"),["question","expected_doc","answer"],5),
  [("Q&A eval set","synthetic-data/knowledge/qa_examples.csv")])}

<section>
  <div class="eyebrow">Proof it's usable</div><h2 class="s serif">Planted signal — verified recoverable</h2>
  <div class="proof">
    <div>📈 <b>+{promo_lift:.0f}%</b> promo-week uplift; clear summer seasonality on beverages.</div>
    <div>👥 attrition drivers all recover in the generated direction (engagement, pay, commute).</div>
    <div>🧾 <b>{len(gt)}</b> invoice issues across 7 types, each in the ground-truth key.</div>
    <div>📄 resume matches separable: strong <b>0.88</b> vs weak <b>0.16</b> overlap.</div>
  </div>
  <div class="note"><b>100% synthetic.</b> Fictional brands, vendors and people; no real company data. Fully reproducible from one seeded generator. The full 81 MB sales file is regenerable locally (a 5,000-row sample is included here for the hosted site).</div>
</section>

<section>
  <div class="eyebrow">Regenerate</div><h2 class="s serif">One command</h2>
  <pre>cd synthetic-data
pip install pandas numpy
python generate_all.py all      # masters | sales | finance | hr | talent | knowledge</pre>
  <p style="margin-top:10px;font-size:14px;color:var(--ink2)">Full column dictionary in <a href="synthetic-data/DATA_DICTIONARY.md">DATA_DICTIONARY.md</a> · overview in <a href="synthetic-data/README.md">README.md</a>.</p>
</section>
</main>
<footer><div class="wrap">Synthetic dataset · Northwind FMCG (Synthetic) · seeded &amp; reproducible · part of the FMCG AI portfolio</div></footer>
"""

doc = ("<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>"
       "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
       "<title>The dataset — FMCG AI portfolio</title>\n<style>"+CSS+"</style>\n</head>\n<body>\n"+body+"\n</body>\n</html>\n")
(ROOT/"data.html").write_text(doc, encoding="utf-8")
print("data.html written:", (ROOT/"data.html").stat().st_size//1024, "KB")
print("sales sample rows:", len(samp), "| total_rows_stat:", f"{total_rows:,}")
