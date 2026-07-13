#!/usr/bin/env python3
"""
Synthetic FMCG enterprise data suite — one consistent fictional company,
"Northwind FMCG (Synthetic)", feeding every 'implement-now' use case:
  sales history -> forecasting / report-from-file / BI
  promotions    -> trade-promotion ROI (true elasticities as ground truth)
  AP invoices   -> invoice 3-way match / duplicate & anomaly detection
  HR + attrition-> attrition prediction / workforce analytics
  resumes + JDs -> resume<->JD matching (match ground truth)
  knowledge docs-> policy chatbot / knowledge search / summarisation
All seeded (SEED=42). Planted signal + ground-truth files included.
Run: python3 generate_all.py <stage>   where stage in
     masters sales finance hr talent knowledge all
"""
import numpy as np, pandas as pd, os, sys, json, random, math, datetime as dt, pathlib
SEED=42; rng=np.random.default_rng(SEED); random.seed(SEED)
ROOT=pathlib.Path(__file__).resolve().parent
def P(*a): return ROOT.joinpath(*a)
for d in ["masters","sales","promotions","finance","hr","talent/resumes","talent/jds","knowledge/corpus","ground_truth"]:
    P(d).mkdir(parents=True, exist_ok=True)

# ---------------- config ----------------
WEEKS = 120                      # ~2.3 years weekly history
START = dt.date(2023,10,2)       # a Monday
N_DIST = 220
CATS = {
 # category: (brands, price_range, true_price_elasticity, seasonality_profile)
 "Confectionery": (["FrostMint","ChocoLuv","FruitPop"], (1,15), 0.63, "festive"),
 "MouthFreshener":(["MouthRaj","FreshPan","SilverElaichi"], (1,120), 0.55, "festive"),
 "Beverages":     (["ZingCola","AquaFresh","MangoDew"], (10,90), 1.33, "summer"),
 "Dairy":         (["DairyBest","PureWhite"], (20,140), 1.20, "steady"),
 "Snacks":        (["CrispKing","NamkeenCo"], (5,60), 1.45, "steady"),
 "Spices":        (["MasalaMagic","SpiceKart"], (35,300), 0.90, "winter"),
}
ZONES = ["North","South","East","West","Central"]
STATES = {"North":["Delhi","Uttar Pradesh","Punjab","Haryana","Uttarakhand"],
          "South":["Karnataka","Tamil Nadu","Telangana","Kerala"],
          "East":["West Bengal","Odisha","Assam","Bihar"],
          "West":["Maharashtra","Gujarat","Rajasthan","Goa"],
          "Central":["Madhya Pradesh","Chhattisgarh"]}
PLANT_CITIES=[("Noida","Uttar Pradesh"),("Kanpur","Uttar Pradesh"),("Rudrapur","Uttarakhand"),
 ("Guwahati","Assam"),("Indore","Madhya Pradesh"),("Nagpur","Maharashtra"),("Pune","Maharashtra"),
 ("Ahmedabad","Gujarat"),("Jaipur","Rajasthan"),("Ludhiana","Punjab"),("Hyderabad","Telangana"),
 ("Bengaluru","Karnataka"),("Chennai","Tamil Nadu"),("Kolkata","West Bengal"),("Cuttack","Odisha")]

FIRST=["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna","Ishaan","Rohan",
 "Ananya","Diya","Aadhya","Saanvi","Aarohi","Anika","Navya","Myra","Kiara","Riya",
 "Rahul","Amit","Priya","Neha","Pooja","Sanjay","Vikram","Deepak","Kavya","Meera",
 "Farhan","Zoya","Imran","Ayesha","Karan","Simran","Manish","Sneha","Rajesh","Sunita"]
LAST=["Sharma","Verma","Gupta","Iyer","Nair","Reddy","Rao","Patel","Shah","Mehta",
 "Singh","Kaur","Das","Bose","Banerjee","Chatterjee","Mukherjee","Naidu","Pillai","Menon",
 "Khan","Ahmed","Kulkarni","Deshpande","Joshi","Malhotra","Kapoor","Chauhan","Yadav","Mishra"]
def name(): return f"{random.choice(FIRST)} {random.choice(LAST)}"
def gstin(state_code=27):
    return f"{state_code:02d}SYN{rng.integers(1000,9999)}{random.choice('ABCDEFGH')}1Z{rng.integers(0,9)}"

# ================================================================= MASTERS
def gen_masters():
    weeks=[START+dt.timedelta(weeks=int(i)) for i in range(WEEKS)]
    cal=pd.DataFrame({"week_start":[w.isoformat() for w in weeks]})
    cal["week_idx"]=range(WEEKS)
    cal["month"]=[w.strftime("%Y-%m") for w in weeks]
    cal["quarter"]=[f"{w.year}-Q{((w.month-1)//3)+1}" for w in weeks]
    # festival flags (approx: Holi ~Mar, RakshaBandhan ~Aug, Diwali ~Oct/Nov, Christmas ~Dec)
    def festive(w):
        m,d=w.month,w.day
        if m==10 or (m==11 and d<12): return "Diwali"
        if m==3 and d<20: return "Holi"
        if m==8: return "RakshaBandhan"
        if m==12 and d>18: return "Christmas/NewYear"
        return ""
    cal["festival"]=[festive(w) for w in weeks]
    cal["is_festive"]=(cal["festival"]!="").astype(int)
    cal.to_csv(P("masters","calendar.csv"),index=False)

    # products
    rows=[]; sku_n=0
    for cat,(brands,(lo,hi),el,prof) in CATS.items():
        n_sku = {"Confectionery":30,"MouthFreshener":28,"Beverages":24,"Dairy":18,"Snacks":18,"Spices":20}[cat]
        for i in range(n_sku):
            brand=random.choice(brands); sku_n+=1
            code=f"FMCG-{cat[:4].upper()}-{sku_n:03d}"
            mrp=round(float(rng.uniform(lo,hi)),0)
            mrp=max(1,mrp)
            cost=round(mrp*float(rng.uniform(0.45,0.70)),2)   # 30-55% margin
            pack=random.choice(["10g","18g","50g","100g","200g","250ml","500ml","1L","6-pack","pouch"])
            launch=""
            if rng.random()<0.10:  # ~10% are recent launches (launch signal)
                launch=(START+dt.timedelta(weeks=int(rng.integers(40,90)))).isoformat()
            rows.append([code,brand,cat,pack,mrp,cost,round(mrp-cost,2),launch,el])
    prod=pd.DataFrame(rows,columns=["sku","brand","category","pack","mrp","unit_cost","unit_margin","launch_week","cat_true_elasticity"])
    prod.to_csv(P("masters","products.csv"),index=False)

    # distributors
    drow=[]
    for i in range(1,N_DIST+1):
        z=random.choice(ZONES); st=random.choice(STATES[z])
        size=float(np.clip(rng.lognormal(0,0.5),0.3,4.0))   # relative size multiplier
        drow.append([f"DIST-{i:04d}",name()+" Distributors",z,st,
                     random.choice(["Metro","Tier-1","Tier-2","Rural"]),
                     round(size,3), gstin(rng.integers(2,37)),
                     (START-dt.timedelta(days=int(rng.integers(200,2500)))).isoformat(),
                     int(rng.integers(300000,5000000))])
    dist=pd.DataFrame(drow,columns=["distributor_code","distributor_name","zone","state","town_class","size_index","gstin","onboarded_date","credit_limit_inr"])
    dist.to_csv(P("masters","distributors.csv"),index=False)

    # plants
    prow=[]
    for i,(c,s) in enumerate(PLANT_CITIES,1):
        prow.append([f"PLNT-{i:02d}",f"{c} Plant",c,s,random.choice(list(CATS.keys())),
                     int(rng.integers(50,500)), gstin()])
    plants=pd.DataFrame(prow,columns=["plant_code","plant_name","city","state","primary_category","daily_capacity_k_units","gstin"])
    plants.to_csv(P("masters","plants.csv"),index=False)
    print(f"[masters] calendar={len(cal)}w products={len(prod)} distributors={len(dist)} plants={len(plants)}")

# ================================================================= SALES + PROMO + TARGETS
def _season(prof, cal):
    n=len(cal); w=cal["week_idx"].values; fest=cal["is_festive"].values; month=[int(m.split('-')[1]) for m in cal["month"]]
    base=np.ones(n)
    ph=rng.uniform(0,6.28)
    if prof=="summer":  base=1+0.45*np.sin(2*np.pi*(np.array(month)-4)/12)   # peak ~Apr-Jun
    elif prof=="winter":base=1+0.40*np.sin(2*np.pi*(np.array(month)-11)/12)
    elif prof=="festive":base=1+0.10*np.sin(2*np.pi*w/52+ph)
    else: base=1+0.12*np.sin(2*np.pi*w/52+ph)
    if prof in("festive",): base=base+0.55*fest          # festival spike for confectionery/MF
    if prof in("winter",):  base=base+0.20*fest
    return np.clip(base,0.4,None)

def gen_sales():
    cal=pd.read_csv(P("masters","calendar.csv"))
    prod=pd.read_csv(P("masters","products.csv"))
    dist=pd.read_csv(P("masters","distributors.csv"))
    week_dates=cal["week_start"].values
    cat_season={cat:_season(prof,cal) for cat,(_,_,_,prof) in CATS.items()}
    # ---- promotions: build events, and per-sku weekly depth + id arrays ----
    promo_events=[]; sku_depth={s:np.zeros(WEEKS) for s in prod["sku"]}; sku_pid={s:np.array([""]*WEEKS,dtype=object) for s in prod["sku"]}; sku_ptype={s:np.array([""]*WEEKS,dtype=object) for s in prod["sku"]}
    pid=0
    for _ in range(170):
        pid+=1; PID=f"PROMO-{pid:04d}"
        sku=prod.sample(1,random_state=int(rng.integers(0,1e9))).iloc[0]
        start=int(rng.integers(0,WEEKS-3)); dur=int(rng.integers(1,4))
        depth=float(random.choice([0.05,0.08,0.10,0.12,0.15,0.20,0.25]))
        ptype=random.choice(["trade","consumer","festival"])
        for w in range(start,min(WEEKS,start+dur)):
            sku_depth[sku["sku"]][w]=depth; sku_pid[sku["sku"]][w]=PID; sku_ptype[sku["sku"]][w]=ptype
        promo_events.append([PID,sku["sku"],sku["category"],ptype,depth,
                             week_dates[start],int(dur),
                             round(float(sku["mrp"])*depth*float(rng.uniform(2000,60000)),0)])
    promos=pd.DataFrame(promo_events,columns=["promo_id","sku","category","promo_type","discount_depth","start_week","duration_weeks","planned_spend_inr"])
    promos.to_csv(P("promotions","promotions.csv"),index=False)
    # true elasticity ground truth
    el_gt=prod[["category"]].drop_duplicates().copy()
    el_gt["true_price_elasticity"]=[CATS[c][2] for c in el_gt["category"]]
    el_gt.to_csv(P("ground_truth","promo_true_elasticities.csv"),index=False)

    # ---- assign SKU coverage per distributor (sparsity), then build series ----
    prod_idx=prod.reset_index(drop=True)
    sku_pop={r.sku: float(np.clip(rng.lognormal(0,0.6),0.2,5)) for r in prod_idx.itertuples()}
    sku_meta={r.sku:(r.brand,r.category,float(r.mrp),float(r.unit_cost),CATS[r.category][2]) for r in prod_idx.itertuples()}
    all_units=[];all_dist=[];all_zone=[];all_state=[];all_sku=[];all_cat=[];all_brand=[];all_price=[];all_rev=[];all_pflag=[];all_pid=[]
    all_out=[];all_fac=[];all_ad=[];all_seas=[];all_ptype=[];all_pdepth=[]   # NEW demand drivers
    for d in dist.itertuples():
        ncarry=int(rng.integers(20,60))
        carried=prod_idx.sample(ncarry,random_state=int(rng.integers(0,1e9)))
        for r in carried.itertuples():
            brand,cat,mrp,cost,el=sku_meta[r.sku]
            base=5.6*sku_pop[r.sku]*d.size_index
            trend=1+float(rng.normal(0.04,0.10))*np.arange(WEEKS)/52.0
            season=cat_season[cat]                          # explicit seasonal_index
            depth=sku_depth[r.sku]; pids=sku_pid[r.sku]; ptypes=sku_ptype[r.sku]
            promo_mult=1+el*depth*3.0                       # uplift via true elasticity
            noise=rng.lognormal(0,0.18,WEEKS)
            launch_mask=np.ones(WEEKS)
            if isinstance(r.launch_week,str) and r.launch_week:
                lw=cal.index[cal["week_start"]==r.launch_week]
                if len(lw): launch_mask[:int(lw[0])]=0.0     # zero before launch
            # ---- demand drivers (distribution / merchandising / media) ----
            outlets0=float(np.clip(rng.normal(420*sku_pop[r.sku]*d.size_index,90),15,6000))
            num_outlets=np.clip(np.round(outlets0*(1+rng.normal(0,0.05,WEEKS))),8,None).astype(int)
            facings0=int(np.clip(round(1+sku_pop[r.sku]*1.3),1,8))
            shelf_facings=np.full(WEEKS,facings0)
            if rng.random()<0.3:                             # ~30% of SKUs get a facing change mid-horizon
                ch=int(rng.integers(WEEKS//3,2*WEEKS//3)); shelf_facings[ch:]=int(np.clip(facings0+rng.choice([-1,1,2]),1,8))
            camp=rng.random(WEEKS)<0.22                      # advertising campaign weeks
            ad_spend=np.where(camp,rng.uniform(8000,90000,WEEKS),rng.uniform(0,1500,WEEKS)).round(0)
            dist_mult=(num_outlets/outlets0)**0.6            # distribution elasticity ~0.6 (within-series)
            facing_mult=(shelf_facings/facings0)**0.30       # facing elasticity ~0.30
            ad_mult=1+0.12*np.log1p(ad_spend/8000.0)         # ad response, diminishing returns
            units=base*trend*season*promo_mult*noise*launch_mask*dist_mult*facing_mult*ad_mult
            # occasional stockouts
            so=rng.random(WEEKS)<0.03; units[so]*=rng.uniform(0,0.2,so.sum())
            units=np.round(np.clip(units,0,None)).astype(int)
            price=np.where(depth>0, np.round(mrp*(1-depth),2), mrp)
            rev=np.round(units*price,2)
            all_units.append(units); all_price.append(price); all_rev.append(rev)
            all_dist.append(np.full(WEEKS,d.distributor_code)); all_zone.append(np.full(WEEKS,d.zone)); all_state.append(np.full(WEEKS,d.state))
            all_sku.append(np.full(WEEKS,r.sku)); all_cat.append(np.full(WEEKS,cat)); all_brand.append(np.full(WEEKS,brand))
            all_pflag.append((depth>0).astype(int)); all_pid.append(pids)
            all_out.append(num_outlets); all_fac.append(shelf_facings); all_ad.append(ad_spend)
            all_seas.append(np.round(season,3)); all_ptype.append(ptypes); all_pdepth.append(np.round(depth,3))
    n_series=len(all_units)
    df=pd.DataFrame({
        "week_start":np.tile(week_dates,n_series),
        "distributor_code":np.concatenate(all_dist),
        "zone":np.concatenate(all_zone),
        "state":np.concatenate(all_state),
        "sku":np.concatenate(all_sku),
        "brand":np.concatenate(all_brand),
        "category":np.concatenate(all_cat),
        "units":np.concatenate(all_units),
        "unit_price":np.concatenate(all_price),
        "revenue":np.concatenate(all_rev),
        "promo_flag":np.concatenate(all_pflag),
        "promo_id":np.concatenate(all_pid),
        "promo_type":np.concatenate(all_ptype),
        "promo_depth":np.concatenate(all_pdepth),
        "num_outlets":np.concatenate(all_out),
        "shelf_facings":np.concatenate(all_fac),
        "ad_spend":np.concatenate(all_ad),
        "seasonal_index":np.concatenate(all_seas),
    })
    # drop all-zero pre-launch rows to keep file realistic & lean
    df=df[df["units"]>0].reset_index(drop=True)
    df.to_csv(P("sales","sales_secondary.csv"),index=False)
    # ground-truth demand-driver coefficients (for validating a forecaster)
    P("ground_truth","demand_drivers.md").write_text(
"""# Demand drivers — planted ground truth (sales_secondary.csv)

`units` (the TARGET) is generated as a product of these drivers. A good demand
model should recover each direction and rough strength:

| Driver (column) | Effect on units | Planted form |
|---|---|---|
| `unit_price` / `promo_depth` | price down -> units up | price elasticity per category (see promo_true_elasticities.csv); promo uplift = 1 + elasticity x depth x 3 |
| `promo_flag` / `promo_type` | promo weeks lift demand | trade/consumer/festival mechanic active |
| `num_outlets` (distribution) | more outlets -> more units | multiplier (num_outlets / baseline)^0.6, and baseline outlets scale with SKU popularity x distributor size |
| `shelf_facings` | more facings -> more units | multiplier (facings / baseline)^0.30 |
| `ad_spend` | more spend -> more units (diminishing) | multiplier 1 + 0.12 x ln(1 + ad_spend/8000) |
| `seasonal_index` | 1.0 = average; >1 peak | category seasonal profile (summer/winter/festive) |
| trend | mild per-SKU growth/decline | 1 + N(0.04, 0.10) x week/52 |

Product hierarchy = sku -> brand -> category; time = weekly `week_start`.
Use these only to validate a model — never as features beyond the columns themselves.
""",encoding="utf-8")

    # sales targets (monthly by zone x category = actual*factor)
    dm=df.copy(); dm["month"]=dm["week_start"].str.slice(0,7)
    agg=dm.groupby(["month","zone","category"],as_index=False)["revenue"].sum()
    agg["target_revenue"]=np.round(agg["revenue"]*rng.uniform(0.9,1.15,len(agg)),0)
    agg=agg.rename(columns={"revenue":"actual_revenue"})
    agg.to_csv(P("sales","sales_targets.csv"),index=False)

    # promo performance (realised incremental vs a naive baseline) for ROI analysis
    perf=[]
    for e in promos.itertuples():
        sub=df[(df["sku"]==e.sku)]
        on=sub[sub["promo_id"]==e.promo_id]["units"].sum()
        base_wk=sub[sub["promo_flag"]==0]["units"].mean() or 0
        inc=on - base_wk*max(1,e.duration_weeks)
        brand,cat,mrp,cost,el=sku_meta[e.sku]
        inc_margin=inc*(mrp-cost)
        roi=(inc_margin/e.planned_spend_inr) if e.planned_spend_inr>0 else 0
        perf.append([e.promo_id,e.sku,e.category,e.promo_type,e.discount_depth,int(max(0,inc)),round(inc_margin,0),e.planned_spend_inr,round(roi,2)])
    pd.DataFrame(perf,columns=["promo_id","sku","category","promo_type","depth","incremental_units","incremental_margin_inr","spend_inr","roi"]).to_csv(P("promotions","promo_performance.csv"),index=False)
    print(f"[sales] rows={len(df):,} file_MB={P('sales','sales_secondary.csv').stat().st_size/1e6:.1f} promos={len(promos)} targets={len(agg)}")

# ================================================================= FINANCE (AP + P&L)
VENDORS_KIND=["Raw Material","Packaging","Logistics","Services","Ingredients"]
MATERIALS={"Raw Material":["Refined Sugar","Menthol Crystals","Glucose Syrup","Milk Solids","Edible Starch"],
 "Ingredients":["Mint Flavour","Cardamom Oil","Cocoa Mass","Citric Acid","Permitted Colour"],
 "Packaging":["PET Bottle 500ml","Wrapper Film","Mono Carton","Shrink Sleeve","Corrugated Box"],
 "Logistics":["Primary Freight","Secondary Freight","Cold-Chain Haulage","Warehousing"],
 "Services":["Housekeeping","AMC-Machinery","Security Services","IT AMC","Consulting"]}
def gen_finance():
    plants=pd.read_csv(P("masters","plants.csv"))
    # vendor master
    vrows=[]
    for i in range(1,121):
        kind=random.choice(VENDORS_KIND); sc=int(rng.integers(2,37))
        vrows.append([f"VEND-{i:04d}",name().split()[1]+" "+random.choice(["Industries","Traders","Enterprises","Logistics","Agro","Packaging","Foods"]),
                      kind, gstin(sc), random.choice(["Net 30","Net 45","Net 60","Advance"]), random.choice(STATES[random.choice(ZONES)])])
    vend=pd.DataFrame(vrows,columns=["vendor_code","vendor_name","vendor_kind","gstin","payment_terms","state"])
    vend.to_csv(P("finance","vendors.csv"),index=False)

    N=5000
    po=[];grn=[];inv=[];lines=[];issues=[]
    d0=dt.date(2024,1,1)
    for k in range(1,N+1):
        v=vend.sample(1,random_state=int(rng.integers(0,1e9))).iloc[0]
        pl=plants.sample(1).iloc[0]
        po_no=f"PO-2024-{k:05d}"; inv_no=f"INV/{k:06d}"; grn_no=f"GRN-{k:05d}"
        po_date=d0+dt.timedelta(days=int(rng.integers(0,540)))
        grn_date=po_date+dt.timedelta(days=int(rng.integers(1,20)))
        inv_date=grn_date+dt.timedelta(days=int(rng.integers(0,10)))
        mats=MATERIALS[v.vendor_kind]
        nl=int(rng.integers(1,5)); sub=0.0; po_lines=[]
        for li in range(nl):
            mat=random.choice(mats); qty=int(rng.integers(50,5000)); rate=round(float(rng.uniform(8,900)),2)
            po_lines.append([mat,qty,rate]); sub+=qty*rate
        gst_rate=random.choice([0.05,0.12,0.18])
        # start clean
        issue=""; detail=""
        inv_qty_factor=1.0; inv_rate_factor=1.0; grn_qty_factor=1.0; gst_calc=gst_rate; vgstin=v.gstin; idate=inv_date
        r=rng.random()
        if r<0.11:  # ~11% planted issues
            issue=random.choice(["duplicate","price_mismatch","qty_variance","tax_error","date_anomaly","gstin_invalid","missing_grn"])
            if issue=="price_mismatch": inv_rate_factor=float(rng.uniform(1.04,1.25)); detail=f"invoice rate {round((inv_rate_factor-1)*100,1)}% above PO"
            elif issue=="qty_variance": grn_qty_factor=float(random.choice([0.80,0.85,1.15,1.20])); detail=f"GRN qty {round((1-grn_qty_factor)*100,1)}% vs invoice"
            elif issue=="tax_error": gst_calc=random.choice([0.05,0.12,0.18]); 
            elif issue=="date_anomaly": idate=po_date-dt.timedelta(days=int(rng.integers(1,8))); detail="invoice dated before PO"
            elif issue=="gstin_invalid": vgstin=v.gstin[:-1]+"X"; detail="malformed GSTIN"
            elif issue=="missing_grn": grn_no=""; detail="no GRN — goods not received"
            if issue=="tax_error": detail=f"GST charged {int(gst_calc*100)}% vs correct {int(gst_rate*100)}%"
        # write PO lines / invoice lines
        inv_sub=0.0
        for (mat,qty,rate) in po_lines:
            iqty=int(round(qty*inv_qty_factor)); irate=round(rate*inv_rate_factor,2); amt=round(iqty*irate,2); inv_sub+=amt
            po.append([po_no,v.vendor_code,pl.plant_code,po_date.isoformat(),mat,qty,rate,round(qty*rate,2)])
            grn.append([grn_no,po_no,grn_date.isoformat() if grn_no else "",mat,int(round(qty*grn_qty_factor)) if grn_no else 0])
            lines.append([inv_no,mat,iqty,irate,amt])
        gst_amt=round(inv_sub*gst_calc,2); total=round(inv_sub+gst_amt,2)
        inv.append([inv_no,po_no,grn_no,v.vendor_code,vgstin,idate.isoformat(),pl.plant_code,round(inv_sub,2),int(gst_calc*100),gst_amt,total])
        if issue: issues.append([inv_no,issue,detail or issue])
        # duplicate: emit a second near-identical invoice
        if issue=="duplicate":
            dup_no=f"INV/{k:06d}-D"
            inv.append([dup_no,po_no,grn_no,v.vendor_code,vgstin,idate.isoformat(),pl.plant_code,round(inv_sub,2),int(gst_calc*100),gst_amt,total])
            for (mat,qty,rate) in po_lines:
                lines.append([dup_no,mat,int(round(qty*inv_qty_factor)),round(rate*inv_rate_factor,2),round(qty*rate,2)])
            issues.append([dup_no,"duplicate",f"duplicate of {inv_no}"])
    pd.DataFrame(po,columns=["po_no","vendor_code","plant_code","po_date","material","qty","rate","amount"]).to_csv(P("finance","purchase_orders.csv"),index=False)
    pd.DataFrame(grn,columns=["grn_no","po_no","grn_date","material","received_qty"]).to_csv(P("finance","grn.csv"),index=False)
    pd.DataFrame(inv,columns=["invoice_no","po_no","grn_no","vendor_code","vendor_gstin","invoice_date","plant_code","subtotal","gst_pct","gst_amount","total_amount"]).to_csv(P("finance","ap_invoices.csv"),index=False)
    pd.DataFrame(lines,columns=["invoice_no","material","qty","rate","amount"]).to_csv(P("finance","ap_invoice_lines.csv"),index=False)
    pd.DataFrame(issues,columns=["invoice_no","issue_type","detail"]).to_csv(P("ground_truth","planted_invoice_issues.csv"),index=False)

    # monthly P&L from sales
    s=pd.read_csv(P("sales","sales_secondary.csv"),usecols=["week_start","category","units","revenue"])
    prod=pd.read_csv(P("masters","products.csv"))[["category","unit_cost","mrp"]].groupby("category").mean()
    s["month"]=s["week_start"].str.slice(0,7)
    g=s.groupby(["month","category"],as_index=False).agg(revenue=("revenue","sum"),units=("units","sum"))
    g["cogs"]=g.apply(lambda r: r["units"]*float(prod.loc[r["category"],"unit_cost"]),axis=1).round(0)
    g["gross_margin"]=(g["revenue"]-g["cogs"]).round(0)
    g["marketing"]=(g["revenue"]*0.08).round(0); g["distribution"]=(g["revenue"]*0.06).round(0)
    g["overheads"]=(g["revenue"]*0.10).round(0)
    g["ebitda"]=(g["gross_margin"]-g["marketing"]-g["distribution"]-g["overheads"]).round(0)
    g.to_csv(P("finance","monthly_pnl.csv"),index=False)
    ni=len(inv)
    print(f"[finance] vendors={len(vend)} invoices={ni} lines={len(lines)} planted_issues={len(issues)} ({round(100*len(issues)/ni,1)}%) pnl_rows={len(g)}")
# ================================================================= HR + ATTRITION
DEPTS={"Sales":["Field Sales","Key Accounts","Sales Ops"],"Manufacturing":["Production","Quality","Maintenance"],
 "Supply Chain":["Planning","Warehouse","Logistics"],"Finance":["Accounts Payable","FP&A","Controllership"],
 "HR":["HRBP","Talent Acquisition","Payroll"],"Marketing":["Brand","Trade Marketing","Digital"],
 "IT":["Applications","Infrastructure","Data & Analytics"],"Legal":["Contracts","Compliance"],
 "Customer Service":["Distributor Care","Consumer Care"],"R&D":["Product Dev","Packaging Dev"]}
BANDS=["M1","M2","M3","M4","M5","M6"]
def sigmoid(x): return 1/(1+np.exp(-x))
def gen_hr():
    N=4000
    dept=np.array([random.choice(list(DEPTS)) for _ in range(N)])
    sub=np.array([random.choice(DEPTS[d]) for d in dept])
    band=rng.choice(BANDS,N,p=[.30,.28,.20,.13,.06,.03])
    band_mid={"M1":35000,"M2":55000,"M3":85000,"M4":140000,"M5":230000,"M6":380000}
    age=np.clip(rng.normal(34,8,N),21,59).round(0)
    tenure=np.clip(rng.exponential(4,N),0.2,22).round(1)
    ctc=np.array([band_mid[b]*float(np.clip(rng.normal(1.0,0.16),0.7,1.5)) for b in band]).round(0)
    comp_ratio=np.array([ctc[i]/band_mid[band[i]] for i in range(N)]).round(3)
    last_promo=np.clip(rng.exponential(2.6,N),0,tenure).round(1)
    commute=np.clip(rng.exponential(14,N),1,70).round(0)
    engagement=np.clip(rng.normal(3.4,0.9,N),1,5).round(1)
    rating=rng.choice([1,2,3,4,5],N,p=[.04,.12,.46,.30,.08])
    workmode=rng.choice(["On-site","Hybrid","Remote"],N,p=[.7,.22,.08])
    gender=rng.choice(["M","F"],N,p=[.72,.28])
    # documented attrition logistic
    field_bump=np.where(np.isin(sub,["Field Sales","Warehouse","Logistics","Production"]),0.6,0.0)
    z=(-1.65 + 1.05*(3.2-engagement) + 1.35*(1.0-comp_ratio)*3 + 0.28*np.clip(last_promo-3,0,None)
       + 0.55*(commute-15)/30 + 0.70*(3-rating) + 0.50*(32-age)/20 + field_bump + rng.normal(0,0.4,N))
    p=sigmoid(z); attr=(rng.random(N)<p).astype(int)
    def reason(i):
        c={"low engagement":1.05*(3.2-engagement[i]),"below-band pay":1.35*(1.0-comp_ratio[i])*3,
           "no recent promotion":0.28*max(0,last_promo[i]-3),"long commute":0.55*(commute[i]-15)/30,
           "low performance rating":0.70*(3-rating[i])}
        return max(c,key=c.get)
    doj=[(dt.date(2026,1,1)-dt.timedelta(days=int(tenure[i]*365))).isoformat() for i in range(N)]
    amonth=[""]*N; areason=[""]*N
    for i in range(N):
        if attr[i]:
            amonth[i]=(dt.date(2025,random.randint(1,12),random.randint(1,28))).isoformat()
            areason[i]=reason(i)
    emp=pd.DataFrame({"emp_id":[f"EMP-{i+1:05d}" for i in range(N)],"name":[name() for _ in range(N)],
        "gender":gender,"age":age.astype(int),"department":dept,"sub_function":sub,"band":band,
        "location":[random.choice([c for c,_ in PLANT_CITIES]) for _ in range(N)],
        "date_of_joining":doj,"tenure_years":tenure,"monthly_ctc":ctc.astype(int),
        "band_midpoint":[band_mid[b] for b in band],"comp_ratio":comp_ratio,
        "last_promotion_years":last_promo,"commute_km":commute.astype(int),
        "engagement_score":engagement,"performance_rating":rating,"work_mode":workmode,
        "attrition_flag":attr,"attrition_month":amonth,"attrition_reason":areason})
    # assign managers within dept (higher band)
    mgr=[]
    for i in range(N):
        pool=emp.index[(emp["department"]==dept[i]) & (emp["band"].isin(BANDS[BANDS.index(band[i])+1:])) ] if band[i]!="M6" else []
        mgr.append(emp.loc[random.choice(list(pool)),"emp_id"] if len(pool) else "")
    emp["manager_id"]=mgr
    emp.to_csv(P("hr","employees.csv"),index=False)
    # engagement survey (separate export)
    dims=["manager_support","growth_opportunity","work_life_balance","recognition","pay_fairness"]
    sv=pd.DataFrame({"emp_id":emp["emp_id"]})
    for d in dims: sv[d]=np.clip(np.round(emp["engagement_score"]+rng.normal(0,0.6,N),1),1,5)
    sv["survey_month"]="2025-06"
    sv.to_csv(P("hr","engagement_survey.csv"),index=False)
    # attrition events
    ev=emp[emp["attrition_flag"]==1][["emp_id","department","sub_function","band","tenure_years","attrition_month","attrition_reason"]].copy()
    ev.to_csv(P("hr","attrition_events.csv"),index=False)
    # ground-truth drivers doc
    P("ground_truth","attrition_drivers.md").write_text(
"""# Attrition — planted ground-truth drivers

Attrition_flag was generated from a logistic model. A good model trained on
`hr/employees.csv` should recover these directions and rough importances:

| Driver | Direction | Weight (logit) |
|---|---|---|
| Low engagement_score | lower -> leaves | 1.05 |
| Below-band pay (comp_ratio < 1.0) | lower -> leaves | 1.35 (x3 scaled) |
| No recent promotion (last_promotion_years > 3) | higher -> leaves | 0.28 |
| Long commute_km | higher -> leaves | 0.55 |
| Low performance_rating | lower -> leaves | 0.70 |
| Younger age | younger -> leaves | 0.50 |
| Field roles (Field Sales/Warehouse/Logistics/Production) | +0.60 bump |

Intercept -1.65; Gaussian noise sd 0.40. Overall attrition ~ generated below.
`attrition_reason` = the single strongest contributing driver per leaver.
Use this only to validate a model — never as a training feature.
""",encoding="utf-8")
    print(f"[hr] employees={N} attrition={int(attr.sum())} ({round(100*attr.mean(),1)}%) survey_rows={len(sv)} events={len(ev)}")
# ================================================================= TALENT (resumes + JDs)
ROLES={
 "Data Analyst":["SQL","Power BI","Tableau","Python","Excel","statistics","data visualization","ETL"],
 "ML Engineer":["Python","machine learning","scikit-learn","TensorFlow","MLOps","NLP","model deployment","vector databases"],
 "RPA Developer":["UiPath","Power Automate","process automation","OCR","VBA","workflow design","exception handling"],
 "Field Sales Officer":["field sales","distributor management","FMCG","secondary sales","beat planning","DMS","negotiation"],
 "Brand Manager":["brand marketing","ATL BTL","campaign management","consumer insights","P&L ownership","agency management"],
 "Plant QA Executive":["quality control","FSSAI","HACCP","GMP","food safety","lab testing","COA"],
 "Finance Executive":["accounts payable","SAP FICO","GST","reconciliation","TDS","Tally","invoice processing"],
 "HRBP":["employee relations","HRMS","PeopleStrong","talent management","engagement","payroll"],
 "Maintenance Engineer":["preventive maintenance","PLC","electrical","mechanical","TPM","breakdown analysis"],
 "Supply Planner":["demand planning","S&OP","inventory management","forecasting","o9","SAP APO"],
 "Legal Counsel":["contract drafting","compliance","litigation","IPR","due diligence","negotiation"],
 "IT Support Engineer":["helpdesk","Windows","networking","Active Directory","troubleshooting","ticketing"],
}
COMPANIES=["Acme Foods","Zenith Retail","Orbit Beverages","Sunrise FMCG","Nimbus Consumer","Peak Dairy","Metro Snacks","Vertex Foods","Delta Trading","Horizon Ingredients"]
EDU=["B.Tech, Computer Science","MBA, Marketing","B.Com","M.Sc Statistics","B.Tech Mechanical","MBA HR","B.Sc Food Technology","MCA","LLB","B.Tech Electronics"]
def gen_talent():
    roles=list(ROLES); truth=[]; jid=0
    for role in roles:
        jid+=1; jd=f"JD-{jid:02d}"; sk=ROLES[role]
        yrs=random.choice(["3-6","5-8","2-4","6-10"])
        txt=f"""JOB DESCRIPTION — {role}
Requisition: {jd}   |   Location: {random.choice([c for c,_ in PLANT_CITIES])}   |   Experience: {yrs} years

About the role:
Northwind FMCG (Synthetic) is hiring a {role} to strengthen our {random.choice(['Sales','Operations','Corporate','Plant'])} team.

Key responsibilities:
- Own and deliver outcomes in the {role} function across our FMCG business.
- Collaborate with cross-functional teams (business, IT, vendors) to ship measurable impact.
- Bring rigour, documentation and a business-first mindset.

Required skills:
{chr(10).join('- '+s for s in sk)}

Preferred: prior FMCG / manufacturing exposure; strong communication; ownership.
"""
        (P("talent","jds")/f"{jd}_{role.replace(' ','_')}.txt").write_text(txt,encoding="utf-8")
    # resumes: 60, each a target role + strength
    rid=0
    for _ in range(60):
        rid+=1; RID=f"CV-{rid:03d}"
        role=random.choice(roles); jd=f"JD-{roles.index(role)+1:02d}"
        strength=rng.choice(["strong","medium","weak"],p=[.4,.35,.25])
        core=ROLES[role]
        if strength=="strong": skills=random.sample(core,k=min(len(core),random.randint(5,len(core))))
        elif strength=="medium":
            other=ROLES[random.choice([r for r in roles if r!=role])]
            skills=random.sample(core,k=max(2,len(core)//2))+random.sample(other,k=2)
        else:
            other=ROLES[random.choice([r for r in roles if r!=role])]
            skills=random.sample(other,k=min(4,len(other)))+random.sample(core,k=1)
        overlap=round(len(set(skills)&set(core))/len(core),2)
        nm=name()
        exp="\n".join(f"- {random.choice(['Sr. ','','Jr. ',''])}{role.split()[0]} {random.choice(['Associate','Executive','Specialist','Officer'])}, {random.choice(COMPANIES)} ({random.randint(2018,2024)}-{random.choice(['present','2023','2022'])})\n    Delivered {random.choice(['cost savings','productivity','quality','growth'])} through {random.choice(skills)} and {random.choice(skills)}." for _ in range(2))
        txt=f"""{nm}
{random.choice(['Bengaluru','Noida','Mumbai','Pune','Chennai'])}, India | {nm.split()[0].lower()}@example.com | +91-{rng.integers(70000,99999)}{rng.integers(10000,99999)}

SUMMARY
{role} with {random.randint(2,10)} years of experience in {random.choice(['FMCG','manufacturing','consumer goods','IT services'])}. Known for {random.choice(['ownership','analytical rigour','stakeholder management','delivery focus'])}.

SKILLS
{', '.join(skills)}

EXPERIENCE
{exp}

EDUCATION
{random.choice(EDU)}
"""
        (P("talent","resumes")/f"{RID}.txt").write_text(txt,encoding="utf-8")
        truth.append([RID,jd,role,strength,overlap])
    pd.DataFrame(truth,columns=["resume_id","best_match_jd","target_role","match_label","skill_overlap"]).to_csv(P("ground_truth","resume_jd_truth.csv"),index=False)
    print(f"[talent] jds={len(roles)} resumes={rid} truth_rows={len(truth)}")

# ================================================================= KNOWLEDGE CORPUS
def doc(fn,title,eff,body):
    (P("knowledge","corpus")/fn).write_text(f"# {title}\n\n_Effective date: {eff} · Northwind FMCG (Synthetic) · Internal_\n\n{body.strip()}\n",encoding="utf-8")
def gen_knowledge():
    qa=[]
    doc("hr-leave-policy.md","Leave Policy","2025-04-01","""
## Entitlements
Earned Leave (EL): **24 days per year**, accrued monthly, carry-forward capped at **45 days**.
Casual Leave (CL): 8 days per year, non-carry-forward. Sick Leave (SL): 10 days per year.
Maternity leave: 26 weeks. Paternity leave: 10 working days.
## Rules
Leave must be applied in the HRMS at least 3 days in advance except sick leave. Encashment of EL is allowed at separation, capped at 45 days.
""")
    qa+=[["How many earned leave days per year?","hr-leave-policy.md","24 days, capped at 45 days carry-forward."],
         ["What is the maternity leave duration?","hr-leave-policy.md","26 weeks."]]
    doc("hr-wfh-policy.md","Work-From-Home & Hybrid Policy","2025-01-15","""
Corporate roles may work hybrid: **up to 2 days/week remote** with manager approval. Plant, field-sales and warehouse roles are on-site. Remote work from outside India requires HR + IT security approval.
""")
    qa+=[["How many WFH days per week are allowed?","hr-wfh-policy.md","Up to 2 days per week for corporate roles, with manager approval."]]
    doc("hr-travel-policy.md","Domestic Travel Policy","2025-04-01","""
Air travel permitted for journeys over 500 km or 8 hours by road, economy class. Hotel ceilings: Metro **Rs 6,000/night**, Non-metro **Rs 4,000/night**. Local conveyance reimbursed at **Rs 12/km** for own vehicle. Daily allowance: Metro Rs 800, Non-metro Rs 600.
""")
    qa+=[["What is the hotel limit for metro cities?","hr-travel-policy.md","Rs 6,000 per night in metros."],
         ["What is the mileage reimbursement rate?","hr-travel-policy.md","Rs 12 per km for own vehicle."]]
    doc("hr-reimbursement-sop.md","Expense Reimbursement SOP","2025-04-01","""
Claims must be filed in the HRMS within **30 days** of expense with digital receipts. Approvals: up to Rs 25,000 by reporting manager; above by function head. Reimbursement is paid with the next payroll cycle after approval.
""")
    doc("hr-posh-policy.md","POSH Policy (Prevention of Sexual Harassment)","2024-08-01","""
Northwind maintains an Internal Committee (IC) at every location. Complaints may be filed with the IC within 3 months of an incident. The IC completes inquiry within 90 days. Retaliation against a complainant is a disciplinary offence.
""")
    qa+=[["Within how many days must a POSH complaint be filed?","hr-posh-policy.md","Within 3 months of the incident."]]
    doc("hr-code-of-conduct.md","Code of Conduct","2024-04-01","""
Employees must avoid conflicts of interest, protect confidential information, and never offer or accept bribes. Gifts from vendors above **Rs 2,500** must be declared. Moonlighting requires prior HR approval.
""")
    doc("hr-pf-gratuity.md","Provident Fund & Gratuity","2024-04-01","""
PF: 12% of basic by employee, matched by employer. Gratuity is payable after **5 years** of continuous service at 15 days' wages per completed year. Nomination is mandatory in the HRMS.
""")
    doc("hr-notice-period.md","Notice Period & Separation","2025-04-01","""
Notice period: M1-M3 **30 days**, M4-M6 **60 days**. Buy-out permitted with function-head approval. Full-and-final settlement within 45 days of last working day. Exit interview mandatory.
""")
    qa+=[["What is the notice period for senior grades M4-M6?","hr-notice-period.md","60 days."]]
    doc("hr-referral-policy.md","Employee Referral Policy","2024-11-01","""
Referral bonus: Rs 15,000 (M1-M3), Rs 40,000 (M4-M5), paid 50% on joining and 50% after 6 months. Referrer must not be in the candidate's reporting line.
""")
    doc("hr-grievance.md","Grievance Redressal","2024-04-01","""
Raise grievances with the reporting manager first; if unresolved in 7 days, escalate to HRBP, then to the Grievance Committee. Anonymous grievances may be filed via the ethics helpline.
""")
    # Finance
    doc("fin-ap-policy.md","Accounts Payable Policy","2025-04-01","""
All vendor invoices are settled on a **3-way match**: invoice = purchase order = goods receipt (GRN). Quantity tolerance **±2%**, price must match PO, totals must tie within Rs 1. Payment terms are as per the vendor master (Net 30/45/60). Duplicate invoice numbers are rejected automatically.
""")
    qa+=[["What is the quantity tolerance in AP three-way match?","fin-ap-policy.md","±2 percent."],
         ["What match is required before paying a vendor invoice?","fin-ap-policy.md","A 3-way match of invoice, PO and GRN."]]
    doc("fin-vendor-onboarding.md","Vendor Onboarding SOP","2025-02-01","""
New vendors require: PAN, **valid GSTIN**, cancelled cheque, and MSME declaration if applicable. GSTIN is validated against the GST portal. Vendor code is created only after Finance and Procurement approval.
""")
    doc("fin-travel-expense-limits.md","Travel Expense Limits (Finance)","2025-04-01","""
Reimbursement ceilings mirror the HR Travel Policy. Foreign travel requires CFO approval. Corporate credit-card statements must be reconciled monthly by the 5th.
""")
    doc("fin-delegation-authority.md","Delegation of Authority (DoA)","2025-04-01","""
Approval limits: Manager up to **Rs 1 lakh**, Function Head up to **Rs 10 lakh**, CFO up to **Rs 1 crore**, MD/Board above Rs 1 crore. Capex above Rs 25 lakh needs a business case.
""")
    qa+=[["What is a manager's spending approval limit?","fin-delegation-authority.md","Up to Rs 1 lakh."]]
    doc("fin-gst-sop.md","GST Compliance SOP","2025-04-01","""
Output GST is filed via GSTR-1 by the 11th and GSTR-3B by the 20th monthly. Input tax credit is claimed only on invoices appearing in GSTR-2B. E-invoicing applies to all B2B invoices; e-way bills are generated for consignments above Rs 50,000.
""")
    doc("fin-credit-policy.md","Distributor Credit Policy","2025-04-01","""
Distributor credit limit is set from a credit score and 6-month offtake. Standard terms: **Net 21 days**. Orders are blocked automatically if overdue beyond limit. Security deposit equals one week of average purchase.
""")
    # Supply chain / Mfg
    doc("sc-dispatch-sop.md","Dispatch SOP","2025-03-01","""
Dispatch is FEFO (First-Expiry-First-Out). Every consignment carries an e-way bill and QR-coded packing list. Vehicles are sealed; seal numbers are logged. Temperature-controlled SKUs require reefer confirmation before loading.
""")
    doc("sc-grn-sop.md","Goods Receipt (GRN) SOP","2025-03-01","""
GRN is booked within 24 hours of receipt against the PO. Quantity is counted 100%; damaged units are quarantined. Short/excess beyond **±2%** is escalated to Procurement. GRN posts to inventory only after QC clearance.
""")
    qa+=[["What quantity variance in GRN gets escalated?","sc-grn-sop.md","Anything beyond ±2 percent."]]
    doc("sc-coa-quality-policy.md","Quality & COA Policy","2025-03-01","""
Every incoming ingredient batch requires a valid Certificate of Analysis (COA) within its shelf-life. Finished goods release requires QC sign-off on microbiological and organoleptic tests. Retention samples are kept for the full shelf life plus 3 months.
""")
    doc("sc-cold-chain-sop.md","Cold-Chain SOP","2025-03-01","""
Dairy and specified SKUs must be held between **2 and 8 °C**. Data-loggers record temperature every 15 minutes; excursions above 8 °C for over 30 minutes trigger a quality hold.
""")
    qa+=[["What temperature range is required for cold-chain dairy?","sc-cold-chain-sop.md","Between 2 and 8 degrees Celsius."]]
    doc("sc-safety-ppe-sop.md","Safety & PPE SOP","2025-01-01","""
Mandatory PPE on the shop floor: hairnet, safety shoes, ear plugs in high-noise zones, and gloves at packing. Near-miss reporting is mandatory. Monthly safety drills are conducted at every plant.
""")
    doc("sc-warehouse-sop.md","Warehouse Management SOP","2025-03-01","""
Bin-level stock is cycle-counted weekly; full physical count quarterly. Discrepancies above 0.5% of SKU value are investigated. Expired or damaged stock moves to a blocked location pending disposal approval.
""")
    doc("sc-recall-sop.md","Product Recall SOP","2024-12-01","""
On a quality alert, a mock or actual recall is initiated within 4 hours. Batch traceability must reach distributor level within 24 hours. The Recall Committee (QA, Supply Chain, Legal, Comms) is convened immediately.
""")
    # Sales
    doc("sales-distributor-onboarding.md","Distributor Onboarding SOP","2025-02-01","""
A new distributor requires GSTIN, security deposit, signed agreement and territory mapping. DMS access and opening stock are released after Finance credit clearance. First order ships within 5 working days of activation.
""")
    doc("sales-trade-scheme-policy.md","Trade Scheme Policy","2025-04-01","""
Trade schemes are approved by the Sales Head and Finance. Claims are settled only against the approved scheme master, valid dates, and verified secondary sales. Over-claims beyond **10%** of entitlement are rejected and investigated.
""")
    qa+=[["When is a trade-scheme over-claim rejected?","sales-trade-scheme-policy.md","When it exceeds 10 percent of entitlement."]]
    doc("sales-returns-policy.md","Sales Returns Policy","2025-04-01","""
Saleable returns are accepted within 15 days with a credit note. Near-expiry (within 90 days of expiry) and damaged goods follow the write-off matrix. Returns above 2% of monthly billing require RSM approval.
""")
    doc("sales-beat-plan-sop.md","Beat Plan SOP","2025-02-01","""
Each sales officer follows a fixed weekly beat with a defined outlet list and target productive calls. Attendance and geo-tagged visits are logged in the sales app. Beat productivity target: **80% productive calls**.
""")
    doc("sales-distributor-credit-terms.md","Distributor Credit Terms","2025-04-01","""
Standard credit is Net 21 days from invoice. Early-payment incentive of 0.5% applies for settlement within 7 days. Persistent defaulters move to advance-payment terms.
""")
    # Product FAQs
    doc("prod-faq-confectionery.md","Product FAQ — Confectionery","2025-01-01","""
Shelf life of hard-boiled candy is 12 months from manufacture. Store below 25 °C, away from direct sunlight. All variants are vegetarian and comply with FSSAI labelling.
""")
    doc("prod-faq-beverages.md","Product FAQ — Beverages","2025-01-01","""
Carbonated beverages have a 6-month shelf life; juices 9 months. Best served chilled. Contains permitted class-II preservatives within FSSAI limits.
""")
    doc("prod-faq-dairy.md","Product FAQ — Dairy","2025-01-01","""
Flavoured milk shelf life is 90 days under cold chain (2-8 °C). Once opened, consume within 24 hours. Contains milk; may contain traces of nuts.
""")
    doc("prod-faq-mouthfreshener.md","Product FAQ — Mouth Freshener","2025-01-01","""
Mouth fresheners have an 18-month shelf life. Packed in moisture-barrier laminates. Sugar-free variants use permitted sweeteners; not recommended above stated daily limits.
""")
    doc("prod-faq-spices.md","Product FAQ — Spices","2025-01-01","""
Blended spices carry a 12-month shelf life in sealed packs. Store in a cool, dry place. Every batch is tested for microbial and pesticide-residue limits per FSSAI.
""")
    # Circulars (dated updates)
    doc("circular-2025-04-leave-update.md","Circular: Leave Policy Update FY25-26","2025-04-01","""
Effective 1 April 2025, Earned Leave entitlement is revised from 22 to **24 days**, and EL carry-forward cap raised to **45 days**. Two wellness days per year are introduced (non-carry-forward).
""")
    doc("circular-2025-03-gst-einvoice.md","Circular: E-Invoicing Threshold","2025-03-15","""
All B2B invoices must be e-invoiced regardless of turnover with effect from 1 April 2025. Teams must ensure IRN generation before dispatch; non-compliant invoices will be held in AP.
""")
    doc("circular-2025-06-travel-revision.md","Circular: Travel Ceiling Revision","2025-06-01","""
Metro hotel ceiling revised to **Rs 6,000/night** (from Rs 5,500). Daily allowance for metros increased to Rs 800. All other provisions of the Travel Policy remain unchanged.
""")
    # Meeting notes (for summarisation)
    doc("meeting-2025-05-sop-review.md","Meeting Notes — Monthly S&OP Review (May 2025)","2025-05-06","""
Attendees: Supply Chain, Sales, Finance, Manufacturing.
- Beverages demand up 18% MoM on early summer; two SKUs flagged near-stockout in West zone.
- Confectionery flat; Diwali build-up plan to start by August.
- Action: Planning to raise beverage production at Nagpur and Pune plants; Finance to review working-capital impact.
- Action: Sales to validate quick-commerce offtake spikes for MangoDew.
- Decision: hold safety stock at 2.5 weeks for top-20 SKUs.
""")
    doc("meeting-2025-06-ap-automation.md","Meeting Notes — Finance AP Automation (Jun 2025)","2025-06-12","""
Attendees: Finance, IT, Procurement.
- 13% of invoices currently need manual review; duplicates and price mismatches are the top two issues.
- Agreed to pilot straight-through processing on packaging vendors first.
- Action: IT to expose SAP AP and GRN read APIs; Finance to define exception queue SLAs.
- Decision: target 65% auto-clear in the pilot with zero wrong auto-approvals.
""")
    doc("meeting-2025-06-attrition-review.md","Meeting Notes — Quarterly Attrition Review (Jun 2025)","2025-06-20","""
Attendees: HR leadership, Sales HRBP.
- Field-sales attrition running above company average; pay competitiveness and long commutes cited.
- Engagement scores lowest on 'growth opportunity' and 'pay fairness'.
- Action: HR to model flight-risk and pilot targeted retention for high-risk, high-performer segment.
- Decision: fast-track promotion review for tenured field officers with no promotion in 3+ years.
""")
    pd.DataFrame(qa,columns=["question","expected_doc","answer"]).to_csv(P("knowledge","qa_examples.csv"),index=False)
    n=len(list((P('knowledge','corpus')).glob('*.md')))
    print(f"[knowledge] corpus_docs={n} qa_examples={len(qa)}")
if __name__=="__main__":
    stage=sys.argv[1] if len(sys.argv)>1 else "all"
    if stage in("masters","all"): gen_masters()
    if stage in("sales","all"): gen_sales()
    if stage in("finance","all"): gen_finance()
    if stage in("hr","all"): gen_hr()
    if stage in("talent","all"): gen_talent()
    if stage in("knowledge","all"): gen_knowledge()
