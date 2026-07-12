"""
DS Group FMCG Synthetic Demand Generator — GOAT 1 spine
========================================================
Seeded, parameterized. Produces 7 related tables with referential integrity,
a documented multiplicative generative recipe, controlled+logged data-quality
issues, a hand-verifiable golden thread, and a provenance-tagged data dictionary.

Grounding: DS Group public grounding pack (portfolio §1, PPP §2, distribution §3,
geography §4, seasonality §5). Every parameter below is tagged in the data dictionary
as grounded / derived-from-grounded / synthetic.

Usage:  python generate_ds.py
Defaults: seed=42, 2024-01-01 -> 2025-12-31, 150 SKUs, 60 distributors, weekly grain.
"""
import numpy as np, pandas as pd
from pathlib import Path

# ============================ PARAMETERS ==================================
SEED           = 42
START          = pd.Timestamp("2024-01-01")
END            = pd.Timestamp("2025-12-31")
N_SKUS         = 150
N_DISTRIBUTORS = 60
GRAIN          = "W"          # 'W' weekly (default) or 'D' daily
SELL_THROUGH_P = 0.42         # fraction of distributors that stock a given SKU (sparse, realistic)
OUT            = Path("/home/claude/out"); OUT.mkdir(exist_ok=True)
rng            = np.random.default_rng(SEED)

# --- Grounded brand/category/variant scaffolding (pack §1) ---
PORTFOLIO = {
 "Confectionery":  {"Pulse":["KacchaAam","Guava","Orange","Pineapple","Litchi"],
                    "Chingles":["Mint","TuttiFrutti","Spearmint"],
                    "LuvIt":["Bar","Eclair","SharePack"], "FRU":["Jelly"], "Cherio":["Std"]},
 "MouthFreshener": {"Rajnigandha":["PanMasala","Meetha","Clove","Saffron"],
                    "BABASupari":["Std","Black"], "Tansen":["Supreme"], "Mastaba":["Std"]},
 "Beverages":      {"Catch":["Water","ClubSoda","TonicWater","MangoJuice","LimeJuice","GreenApple"]},
 "Spices":         {"Catch":["Turmeric","ChilliPwd","GaramMasala","Hing","Sprinkler"],
                    "Kewal":["Std"]},
 "Dairy":          {"Ksheer":["FullCreamMilk","Dahi","Paneer","Ghee","Whitener","FlavMilk"]},
 "Snacks":         {"NotJustNuts":["Cashew","Almond","TrailMix"], "SnackFactory":["Namkeen"]},
}
# grounded ₹ price ladders per category (pack §2 magic price points)
PRICE_LADDER = {
 "Confectionery":[1,2,5,10], "MouthFreshener":[2,5,10,25], "Beverages":[10,20,35,50],
 "Spices":[5,10,50,100], "Dairy":[12,25,30,60], "Snacks":[10,20,50],
}
PACK_BY_PRICE = {  # (pack_size, pack_unit) — [ESTIMATE], standard Indian LUP ladders
 1:("1 unit","unit"),2:("2g / 1 unit","unit"),5:("8g / 5ml","g"),10:("50g / 250ml","g"),
 12:("12g / 200ml","g"),
 20:("100g / 600ml","g"),25:("25g","g"),30:("500ml","ml"),35:("600ml","ml"),
 50:("200g / 1L","g"),60:("1L","ml"),100:("500g","g"),
}
# own-price elasticities (pack §2 basis: ₹1 impulse is price-point protected -> inelastic;
# premium/beverages more elastic)
ELASTICITY = {"Confectionery":-0.6,"MouthFreshener":-0.9,"Beverages":-1.4,
              "Spices":-1.1,"Dairy":-1.2,"Snacks":-1.3}
# seasonality index by category x month (Jan..Dec), mean normalized ~1.0 (pack §5)
SEASON_IDX = {
 "Confectionery": [1.05,.95,1.10,.95,.90,1.15,1.20,1.25,1.00,1.15,1.30,1.00],
 "MouthFreshener":[1.25,1.20,1.00,.90,.95,.85,.80,.85,1.00,1.15,1.30,1.35],
 "Beverages":     [.75,.80,1.10,1.45,1.60,1.55,.90,.85,.95,1.00,.80,.75],
 "Spices":        [1.15,1.05,1.00,.95,1.00,.95,.90,.95,1.05,1.20,1.25,1.10],
 "Dairy":         [.95,.95,1.05,1.10,1.15,1.10,.95,.95,1.00,1.05,1.05,1.00],
 "Snacks":        [1.00,.95,1.00,.95,.95,1.05,1.10,1.10,1.00,1.10,1.15,1.05],
}
FEST_MULT = {"Confectionery":1.5,"Spices":1.3,"MouthFreshener":1.2}  # else 1.1
# distributor/retailer margins by category (pack §2), used for dist_price
DIST_MARGIN = {"Confectionery":.10,"MouthFreshener":.06,"Beverages":.07,"Spices":.06,"Dairy":.12,"Snacks":.09}
RET_MARGIN  = {"Confectionery":.22,"MouthFreshener":.12,"Beverages":.15,"Spices":.12,"Dairy":.08,"Snacks":.15}

ZONES = {"North":["Delhi","Uttar Pradesh","Haryana","Punjab","Rajasthan"],
         "West":["Maharashtra","Gujarat","Madhya Pradesh"],
         "South":["Karnataka","Tamil Nadu","Telangana","Kerala"],
         "East":["West Bengal","Bihar","Odisha","Jharkhand"],
         "Northeast":["Assam","Tripura","Meghalaya"],
         "Central":["Chhattisgarh","Madhya Pradesh"]}
# pack §4: over-index North + Northeast (plant footprint + hotels)
ZONE_WEIGHT = {"North":1.35,"Northeast":1.20,"East":1.05,"West":1.00,"Central":0.85,"South":0.80}
CITY_BY_STATE = {"Delhi":["Delhi"],"Uttar Pradesh":["Noida","Lucknow","Kanpur"],
  "Haryana":["Sonipat","Gurugram"],"Punjab":["Ludhiana"],"Rajasthan":["Sikar","Jaipur"],
  "Maharashtra":["Mumbai","Pune"],"Gujarat":["Ahmedabad"],"Madhya Pradesh":["Indore"],
  "Karnataka":["Bengaluru"],"Tamil Nadu":["Chennai"],"Telangana":["Hyderabad"],"Kerala":["Kochi"],
  "West Bengal":["Kolkata"],"Bihar":["Patna"],"Odisha":["Bhubaneswar"],"Jharkhand":["Ranchi"],
  "Assam":["Guwahati"],"Tripura":["Agartala"],"Meghalaya":["Shillong"],"Chhattisgarh":["Raipur"]}

# real Diwali/Holi/etc dates for 2024-25 (pack §5 verified pattern; actual calendar dates)
FESTIVALS = {"2024-03-25":"Holi","2024-08-19":"RakshaBandhan","2024-09-07":"GaneshChaturthi",
 "2024-11-01":"Diwali","2025-01-14":"MakarSankranti","2025-03-14":"Holi",
 "2025-08-09":"RakshaBandhan","2025-08-27":"GaneshChaturthi","2025-10-21":"Diwali"}

# planted structural constants
NE_GOLIVE       = pd.Timestamp("2024-10-01")   # distribution-expansion break
RAJ_HIKE_DATE   = pd.Timestamp("2025-01-01")   # price-change break
NEW_SKU         = "DS-CONFPULSE-149"           # cannibalizing new launch
ANCHOR_SKU      = "DS-CONFPULSE-001"           # its analog + the golden-thread SKU
NEW_LAUNCH_DATE = pd.Timestamp("2024-07-01")
CANN_END        = pd.Timestamp("2025-04-01")
CANN_PCT        = 0.20                          # new SKU pulls 20% from anchor
BASE_ABC        = {"A":900,"B":220,"C":40}      # avg weekly base units by ABC class

def season_of(m):
    return ("Winter" if m in (12,1,2) else "Summer" if m in (3,4,5)
            else "Monsoon" if m in (6,7,8,9) else "Autumn")

# ============================ 1. PRODUCT MASTER ===========================
def build_products():
    rows=[]; sid=0; cats=list(PORTFOLIO.keys())
    while len(rows) < N_SKUS:
        cat=rng.choice(cats); brand=rng.choice(list(PORTFOLIO[cat].keys()))
        variant=rng.choice(PORTFOLIO[cat][brand]); price=int(rng.choice(PRICE_LADDER[cat]))
        pack,unit=PACK_BY_PRICE[price]; sid+=1
        abc=rng.choice(["A","B","C"],p=[.20,.30,.50])         # ~20/30/50 split
        launch=START - pd.Timedelta(days=int(rng.integers(120,2500)))  # most pre-existing
        el=ELASTICITY[cat]*rng.uniform(0.85,1.15)
        rows.append(dict(
            sku_code=f"DS-{cat[:4].upper()}{brand[:3].upper()}-{sid:03d}",
            category=cat, brand=brand, variant=variant, pack_size=pack, pack_unit=unit,
            mrp=float(price),
            dist_price=round(price*(1-DIST_MARGIN[cat]-RET_MARGIN[cat]),2),
            launch_date=launch.date().isoformat(),
            abc_class=abc,
            mts_mto=("MTS" if abc in ("A","B") else rng.choice(["MTS","MTO"],p=[.7,.3])),
            base_elasticity=round(el,3),
            is_intermittent=bool(abc=="C" and rng.random()<0.6)))
    df=pd.DataFrame(rows).drop_duplicates("sku_code").reset_index(drop=True)

    # pin the anchor Pulse SKU (A-class, non-intermittent, ₹1)
    df.loc[0,"sku_code"]=ANCHOR_SKU
    df.loc[0,["category","brand","variant","mrp","dist_price","abc_class",
              "is_intermittent","base_elasticity","mts_mto"]] = \
        ["Confectionery","Pulse","KacchaAam",1.0,round(1*(1-.10-.22),2),"A",False,-0.6,"MTS"]

    # append the cannibalizing new launch (a new Pulse flavour)
    new=df.iloc[0].copy()
    new["sku_code"]=NEW_SKU; new["variant"]="Blackcurrant"
    new["launch_date"]=NEW_LAUNCH_DATE.date().isoformat(); new["abc_class"]="B"
    new["is_intermittent"]=False
    df=pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    return df

# ============================ 2. LOCATION MASTER ==========================
def build_locations():
    rows=[]; zone_list=list(ZONES.keys())
    w=np.array([ZONE_WEIGHT[z] for z in zone_list]); w=w/w.sum()
    alloc=(w*N_DISTRIBUTORS).round().astype(int); alloc[0]+=N_DISTRIBUTORS-alloc.sum()
    did=0
    for z,n in zip(zone_list,alloc):
        for _ in range(int(n)):
            did+=1
            state=rng.choice(ZONES[z]); city=rng.choice(CITY_BY_STATE.get(state,[state]))
            ch=rng.choice(["GT","MT","Ecom"],p=[.80,.13,.07])
            ur="Urban" if ch in ("MT","Ecom") or rng.random()<0.6 else "Rural"
            golive=NE_GOLIVE.date().isoformat() if (z=="Northeast" and rng.random()<0.6) \
                   else START.date().isoformat()
            rows.append(dict(
                distributor_code=f"DIST-{z[:2].upper()}-{did:03d}",
                super_stockist=f"SS-{z[:2].upper()}-{(did%6)+1:02d}",
                territory=f"{city}-T{rng.integers(1,4)}", city=city, state=state, zone=z,
                channel=ch, urban_rural=ur,
                region_weight=round(ZONE_WEIGHT[z]*rng.uniform(.85,1.15),3),
                golive=golive))
    return pd.DataFrame(rows)

# ============================ 3. CALENDAR =================================
def build_calendar():
    days=pd.date_range(START,END,freq="D"); rows=[]
    for d in days:
        fn=FESTIVALS.get(d.date().isoformat())
        iso=d.isocalendar()
        rows.append(dict(date=d.date().isoformat(), iso_year=int(iso.year),
            week=int(iso.week), month=d.month, year=d.year, day_of_week=d.weekday(),
            is_festival=fn is not None, festival_name=fn, season=season_of(d.month)))
    return pd.DataFrame(rows)

# ============================ 4. PROMO CALENDAR ===========================
def build_promos(products):
    rows=[]; pid=0
    a_skus=products[products.abc_class.isin(["A","B"])].sku_code.tolist()
    for _ in range(120):
        pid+=1; sku=rng.choice(a_skus)
        start=START+pd.Timedelta(weeks=int(rng.integers(0,102))); dur=int(rng.integers(1,5))
        rows.append(dict(promo_id=f"PROMO-{pid:04d}", sku=sku,
            location_scope=rng.choice(["ALL","North","West","South","East","Northeast"],
                                      p=[.4,.2,.1,.1,.1,.1]),
            type=rng.choice(["consumer","trade","display"],p=[.5,.35,.15]),
            start=start.date().isoformat(),
            end=(start+pd.Timedelta(weeks=dur)).date().isoformat(),
            depth_pct=round(float(rng.choice([.05,.10,.15,.20,.25])),2),
            mechanic=rng.choice(["Buy10Get1","ExtraGrammage","20%Off","DisplayBonus","ComboPack"])))
    return pd.DataFrame(rows)

# ============================ 5. PRICE HISTORY ============================
def build_price_history(products):
    rows=[]
    for _,p in products.iterrows():
        rows.append(dict(sku=p.sku_code, effective_from=START.date().isoformat(),
            mrp=p.mrp, dist_price=p.dist_price, reason="baseline"))
    raj=products[(products.brand=="Rajnigandha") & (products.abc_class=="A")]
    hiked_sku=None
    if len(raj):
        s=raj.iloc[0]; hiked_sku=s.sku_code
        rows.append(dict(sku=s.sku_code, effective_from=RAJ_HIKE_DATE.date().isoformat(),
            mrp=s.mrp+1, dist_price=round((s.mrp+1)*(1-DIST_MARGIN["MouthFreshener"]-RET_MARGIN["MouthFreshener"]),2),
            reason="MRP_HIKE_structural_break"))
    return pd.DataFrame(rows), hiked_sku

# ============================ 6. FACT: SALES_SECONDARY ====================
def build_sales(products, locations, promos, price_hist, golden_dist):
    freq="W-MON" if GRAIN=="W" else "D"
    periods=pd.date_range(START,END,freq=freq)

    # festival weeks keyed by (iso_year, iso_week)  <-- fixes the year-collision bug
    fest_weeks=set()
    for k in FESTIVALS:
        iso=pd.Timestamp(k).isocalendar(); fest_weeks.add((int(iso.year),int(iso.week)))

    # promo index by sku (fixes the O(all-promos) per-period scan)
    promo_by_sku={}
    tmap={"consumer":1.0,"trade":0.7,"display":0.5}
    for _,pr in promos.iterrows():
        promo_by_sku.setdefault(pr.sku,[]).append(
            (pd.Timestamp(pr.start),pd.Timestamp(pr.end),pr.depth_pct,tmap[pr.type],
             pr.location_scope,pr.promo_id))

    # price schedule by sku: sorted [(effective_from, mrp)]
    price_by_sku={}
    for _,r in price_hist.sort_values("effective_from").iterrows():
        price_by_sku.setdefault(r.sku,[]).append((pd.Timestamp(r.effective_from),r.mrp))

    def mrp_at(sku, base_mrp, t):
        sched=price_by_sku.get(sku)
        if not sched: return base_mrp
        cur=base_mrp
        for eff,m in sched:
            if eff<=t: cur=m
            else: break
        return cur

    rows=[]; golden_rows=[]
    loc_records=locations.to_dict("records")
    for _,p in products.iterrows():
        cat=p.category; el=p.base_elasticity; launch=pd.Timestamp(p.launch_date)
        s_idx=SEASON_IDX[cat]; trend_g=rng.uniform(-0.05,0.18); base_mrp=p.mrp
        p_promos=promo_by_sku.get(p.sku_code,[])
        for loc in loc_records:
            is_golden=(p.sku_code==ANCHOR_SKU and loc["distributor_code"]==golden_dist)
            if not is_golden and rng.random()>SELL_THROUGH_P:
                continue
            golive=pd.Timestamp(loc["golive"])
            ch_factor=1.0 if loc["channel"]=="GT" else 1.4 if loc["channel"]=="MT" else 0.8
            base=BASE_ABC[p.abc_class]*loc["region_weight"]*ch_factor*rng.uniform(0.7,1.3)
            ac=1.0
            for t in periods:
                if t<launch or t<golive:
                    continue
                m=t.month
                trend=(1+trend_g)**((t-START).days/365.0)
                seas=s_idx[m-1]
                cur_mrp=mrp_at(p.sku_code, base_mrp, t)
                price_eff=(cur_mrp/base_mrp)**el
                # promo
                lift=1.0; promo_id=None; depth_applied=0.0
                for (ps,pe,depth,tmult,scope,pidv) in p_promos:
                    if ps<=t<=pe and scope in ("ALL",loc["zone"],loc["distributor_code"]):
                        lift*=(1+depth*abs(el)*2.0*tmult); promo_id=pidv; depth_applied=depth
                # festival
                iso=t.isocalendar()
                fest=FEST_MULT.get(cat,1.1) if (int(iso.year),int(iso.week)) in fest_weeks else 1.0
                # cannibalization on the anchor SKU
                cann=CANN_PCT_FACTOR if (p.sku_code==ANCHOR_SKU and NEW_LAUNCH_DATE<=t<CANN_END) else 1.0
                if p.is_intermittent:
                    occ=1 if rng.random()<0.35 else 0
                    qty=int(rng.poisson(max(base,1)*2)*occ)
                    noise=np.nan
                else:
                    ac=0.6*ac+0.4*rng.gamma(9,1/9); noise=ac  # AR(1), mean~1, autocorrelated
                    dem=base*trend*seas*price_eff*lift*fest*cann*ac
                    if p.sku_code==NEW_SKU:                      # S-curve launch ramp
                        wsl=max((t-launch).days/30.0,0.1)
                        dem*=1/(1+np.exp(-(wsl-4)))
                    qty=int(max(0,round(dem)))
                if is_golden:
                    golden_rows.append(dict(date=t.date().isoformat(), base=round(base,2),
                        trend=round(trend,4), seasonality=round(seas,4),
                        price_effect=round(price_eff,4), promo_lift=round(lift,4),
                        festival=round(fest,4), cannibalization=round(cann,4),
                        ar1_noise=round(noise,4) if not np.isnan(noise) else None,
                        qty=qty, promo_id=promo_id))
                if qty<=0:
                    continue
                price_real=round(cur_mrp*(1-DIST_MARGIN[cat]-RET_MARGIN[cat]),2)
                if promo_id:
                    price_real=round(price_real*(1-0.4*depth_applied),2)
                rows.append(dict(date=t.date().isoformat(), sku=p.sku_code,
                    distributor=loc["distributor_code"], qty=qty,
                    price_realized=price_real, promo_id=promo_id))
    return pd.DataFrame(rows), pd.DataFrame(golden_rows)

CANN_PCT_FACTOR = 1 - CANN_PCT   # 0.80 multiplier on anchor during window

# ============================ 7. NEW-LAUNCH ANALOGS ======================
def build_analogs():
    return pd.DataFrame([dict(new_sku=NEW_SKU, analog_sku=ANCHOR_SKU,
        cannibalization_pct=CANN_PCT, ramp_months=9)])

# ============================ 8. DATA-QUALITY INJECTION ==================
# Delivers a CLEAN canonical set (verified below) AND a messy overlay that
# deliberately breaks a *logged* set of rows so the dataset doubles as a
# resilience-path stress test. Every planted issue is recorded.
def inject_dq(products, locations, sales):
    log=[]; pm=products.copy(); lm=locations.copy(); ss=sales.copy()

    # (1) ~2% missing dist_price on product_master
    n=max(1,int(0.02*len(pm))); idx=rng.choice(pm.index,n,replace=False)
    pm.loc[idx,"dist_price"]=np.nan
    log.append(dict(table="product_master", issue="missing dist_price (blank)",
        rows_affected=n, keys="; ".join(pm.loc[idx,"sku_code"]),
        expected_system_behavior="impute from mrp*(1-margins) or warn+continue"))

    # (2) one SKU with #N/A poison string in mrp (cast column to object first)
    poison=pm.index[5]
    pm["mrp"]=pm["mrp"].astype(object)
    pm.loc[poison,"mrp"]="#N/A"
    log.append(dict(table="product_master", issue="#N/A literal in numeric mrp",
        rows_affected=1, keys=str(pm.loc[poison,"sku_code"]),
        expected_system_behavior="coerce-to-NaN + quarantine row, never fatal"))

    # (3) MT-vs-KG / unit inconsistency: a handful of gram SKUs mislabelled 'kg'
    gmask=pm.index[(pm["pack_unit"]=="g")][:3]
    pm.loc[gmask,"pack_unit"]="kg"
    log.append(dict(table="product_master", issue="unit mismatch: g rows labelled kg",
        rows_affected=len(gmask), keys="; ".join(pm.loc[gmask,"sku_code"]),
        expected_system_behavior="unit-normalize to internal base (÷1000) before aggregation"))

    # (4) duplicate distributor_code (two SS pointing at same code)
    dup=lm.iloc[0].copy(); dup["super_stockist"]="SS-DUPLICATE"; dup["territory"]="dup-collision"
    lm=pd.concat([lm,pd.DataFrame([dup])],ignore_index=True)
    log.append(dict(table="location_master", issue="duplicate distributor_code (PK collision)",
        rows_affected=2, keys=str(dup["distributor_code"]),
        expected_system_behavior="dedupe on PK, keep first / flag conflict"))

    # (5) mixed date formats on ~1% of fact rows (DD-MM-YYYY instead of ISO)
    n2=max(1,int(0.01*len(ss))); idx2=rng.choice(ss.index,n2,replace=False)
    ss.loc[idx2,"date"]=pd.to_datetime(ss.loc[idx2,"date"]).dt.strftime("%d-%m-%Y")
    log.append(dict(table="sales_secondary", issue="mixed date format (DD-MM-YYYY)",
        rows_affected=n2, keys=f"{n2} random rows",
        expected_system_behavior="dateutil/format-tolerant parse, not position-based"))

    return pm, lm, ss, pd.DataFrame(log)

# ============================ 9. DATA DICTIONARY ==========================
def data_dictionary():
    P="grounded"; D="derived-from-grounded"; S="synthetic"
    rows=[
     ("product_master","sku_code","STR","primary key DS-<CAT><BRD>-<NNN>",S),
     ("product_master","category","STR","6 grounded categories",P),
     ("product_master","brand","STR","grounded DS Group brand (pack §1)",P),
     ("product_master","variant","STR","grounded flavour/variant (pack §1)",P),
     ("product_master","pack_size","STR","standard Indian LUP ladder",D),
     ("product_master","pack_unit","STR","unit/g/ml/L",D),
     ("product_master","mrp","FLOAT ₹","grounded magic price point (pack §2)",P),
     ("product_master","dist_price","FLOAT ₹","mrp*(1-dist_margin-ret_margin)",D),
     ("product_master","launch_date","DATE","random pre-history; new launch pinned",S),
     ("product_master","abc_class","STR","A/B/C ~20/30/50 (Pareto)",D),
     ("product_master","mts_mto","STR","make-to-stock/order",S),
     ("product_master","base_elasticity","FLOAT","own-price elasticity by category ±15%",D),
     ("product_master","is_intermittent","BOOL","long-tail Croston flag",D),
     ("location_master","distributor_code","STR","primary key DIST-<ZONE>-<NNN>",S),
     ("location_master","super_stockist","STR","SS-<ZONE>-<NN>",S),
     ("location_master","territory/city/state","STR","grounded India geo (pack §4)",P),
     ("location_master","zone","STR","6 zones, count weighted to N+NE",D),
     ("location_master","channel","STR","GT/MT/Ecom ~80/13/7 (pack §3)",P),
     ("location_master","urban_rural","STR","~40%+ rural (pack §4)",P),
     ("location_master","region_weight","FLOAT","demand density (pack §4 footprint)",D),
     ("location_master","golive","DATE","NE cohort live 2024-10-01 (break)",S),
     ("calendar","date/iso_year/week/month","-","daily spine",S),
     ("calendar","is_festival/festival_name","-","real 2024-25 festival dates (pack §5)",P),
     ("calendar","season","STR","Winter/Summer/Monsoon/Autumn",D),
     ("promo_calendar","promo_id","STR","primary key",S),
     ("promo_calendar","type/depth_pct/mechanic","-","consumer/trade/display, grounded depths",D),
     ("sales_secondary","date/sku/distributor","-","composite PK (fact table)",S),
     ("sales_secondary","qty","INT","modelled weekly secondary off-take",D),
     ("sales_secondary","price_realized","FLOAT ₹","dist_price net of promo pass-through",D),
     ("sales_secondary","promo_id","STR|null","FK to promo_calendar",D),
     ("price_history","*","-","baseline + Rajnigandha hike (break)",D),
     ("new_launch_analogs","*","-","cannibalization mapping",S),
    ]
    return pd.DataFrame(rows, columns=["table","field","type","meaning","provenance"])

# ============================ BUILD ======================================
print("building master tables…")
products=build_products()
locations=build_locations()
calendar=build_calendar()
promos=build_promos(products)
price_hist,hiked_sku=build_price_history(products)
analogs=build_analogs()

# choose golden distributor: first North GT Urban distributor
gd=locations[(locations.zone=="North")&(locations.channel=="GT")&(locations.urban_rural=="Urban")]
golden_dist=gd.iloc[0].distributor_code if len(gd) else locations.iloc[0].distributor_code

print(f"building fact table (grain={GRAIN}, golden pair={ANCHOR_SKU} @ {golden_dist})…")
sales,golden=build_sales(products,locations,promos,price_hist,golden_dist)

# clean canonical outputs
for name,df in [("product_master",products),("location_master",locations),
    ("calendar",calendar),("promo_calendar",promos),("sales_secondary",sales),
    ("price_history",price_hist),("new_launch_analogs",analogs)]:
    df.to_csv(OUT/f"{name}.csv",index=False)

# messy overlay + planted-issue log
pm_m,lm_m,ss_m,dq_log=inject_dq(products,locations,sales)
pm_m.to_csv(OUT/"product_master_messy.csv",index=False)
lm_m.to_csv(OUT/"location_master_messy.csv",index=False)
ss_m.to_csv(OUT/"sales_secondary_messy.csv",index=False)
dq_log.to_csv(OUT/"planted_data_quality_issues.csv",index=False)

# docs
data_dictionary().to_csv(OUT/"data_dictionary.csv",index=False)
golden.to_csv(OUT/"golden_thread_trace.csv",index=False)

# ============================ VERIFY =====================================
print("\n================ VERIFICATION ================")
# referential integrity (on CLEAN set)
def chk(name,cond): print(f"[{'PASS' if cond else 'FAIL'}] {name}")
sku_set=set(products.sku_code); dist_set=set(locations.distributor_code); promo_set=set(promos.promo_id)
chk("sales.sku ⊆ product_master", set(sales.sku)<=sku_set)
chk("sales.distributor ⊆ location_master", set(sales.distributor)<=dist_set)
chk("sales.promo_id ⊆ promo_calendar", set(sales.promo_id.dropna())<=promo_set)
chk("promo.sku ⊆ product_master", set(promos.sku)<=sku_set)
chk("analog skus valid", set(analogs.new_sku)|set(analogs.analog_sku)<=sku_set)
chk("no null qty / all qty>0", (sales.qty>0).all())

# reconciliation: SKU -> brand -> category rollup is exact
m=sales.merge(products[["sku_code","brand","category"]],left_on="sku",right_on="sku_code")
by_sku=m.groupby("sku").qty.sum().sum()
by_cat=m.groupby("category").qty.sum().sum()
chk("SKU total == category rollup total", by_sku==by_cat==sales.qty.sum())

# structural break 1: NE distributors have zero rows pre-golive
ne=locations[locations.zone=="Northeast"]
ne_live=ne[ne.golive==NE_GOLIVE.date().isoformat()].distributor_code
ne_sales=sales[sales.distributor.isin(ne_live)]
pre=ne_sales[pd.to_datetime(ne_sales.date)<NE_GOLIVE]
chk(f"NE cohort ({len(ne_live)} dists) has no sales before 2024-10-01", len(pre)==0)

# structural break 2: hiked SKU price steps up in 2025
if hiked_sku:
    hs=sales[sales.sku==hiked_sku]
    pre_p=hs[pd.to_datetime(hs.date)<RAJ_HIKE_DATE].price_realized.max()
    post_p=hs[pd.to_datetime(hs.date)>=RAJ_HIKE_DATE].price_realized.max()
    chk(f"price break on {hiked_sku}: {pre_p} -> {post_p}", post_p>pre_p)

# ============================ SUMMARY ====================================
print("\n================ DATASET SUMMARY ================")
print(f"SKUs: {len(products)} | distributors: {len(locations)} | "
      f"promos: {len(promos)} | fact rows: {len(sales):,}")
print(f"date span: {sales.date.min()} -> {sales.date.max()} | grain: {GRAIN}")
print(f"total units (2yr): {sales.qty.sum():,}")
print("\nABC mix:"); print(products.abc_class.value_counts().to_string())
print("\ndistributors by zone:"); print(locations.zone.value_counts().to_string())
print("\ntop 5 categories by volume:")
print(m.groupby("category").qty.sum().sort_values(ascending=False).to_string())

print("\n================ FILES WRITTEN ================")
for f in sorted(OUT.glob("*.csv")):
    print(f"  {f.name:38s} {f.stat().st_size/1024:8.1f} KB")
