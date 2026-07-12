"""
DS Group extension pack v2 — derived layers on the FROZEN v1 spine.
Law: v1 tables (esp. sales_secondary) are truth and are never modified.
Adds: primary_sales (company->distributor, order-up-to policy + pipeline fill),
distributor_inventory (exact accounting identity), sku_costs (COGS/margin),
sales_targets (zone x category monthly), plus verification + a golden inventory walk.
Seed=42 continuity. Run AFTER generate_ds.py.
"""
import numpy as np, pandas as pd
from pathlib import Path

OUT = Path("/home/claude/out")
rng = np.random.default_rng(4242)  # separate stream; v1 untouched

pm   = pd.read_csv(OUT/"product_master.csv")
lm   = pd.read_csv(OUT/"location_master.csv")
fact = pd.read_csv(OUT/"sales_secondary.csv", parse_dates=["date"])

NEW_SKU, ANCHOR, GOLD_DIST = "DS-CONFPULSE-149", "DS-CONFPULSE-001", "DIST-NO-001"
START, END = pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31")
WEEKS = pd.date_range(START, END, freq="W-MON")

CASE = {"Confectionery":200,"MouthFreshener":100,"Beverages":24,"Spices":48,"Dairy":24,"Snacks":48}
MFG_GM = {"Confectionery":0.45,"MouthFreshener":0.55,"Beverages":0.40,"Spices":0.42,"Dairy":0.28,"Snacks":0.38}

cat_of  = dict(zip(pm.sku_code, pm.category))
dp_of   = dict(zip(pm.sku_code, pm.dist_price))
zone_of = dict(zip(lm.distributor_code, lm.zone))

# ---------------- 1. sku_costs (ESTIMATE-tagged manufacturer economics) ------
rows=[]
for _,p in pm.iterrows():
    gm = MFG_GM[p.category] + rng.uniform(-0.05,0.05)
    rows.append(dict(sku_code=p.sku_code, category=p.category,
        unit_cogs=round(p.dist_price*(1-gm),3),
        mfr_gross_margin_pct=round(gm,3),
        provenance="ESTIMATE: category GM band +/-5%, applied to derived dist_price"))
sku_costs = pd.DataFrame(rows); sku_costs.to_csv(OUT/"sku_costs.csv", index=False)

# ---------------- 2/3. primary_sales + distributor_inventory -----------------
# Weekly order-up-to policy per (sku, distributor):
#   safety(t)   = 1.0 x trailing-4wk avg secondary
#   order o(t)  = ceil_to_case( max(0, s(t) + safety(t) - inv_end(t-1)) )   [receive-before-sell]
#   inv_end(t)  = inv_end(t-1) + o(t) - s(t)        -> identity, never negative by construction
# Launch push: NEW_SKU first 2 order weeks x1.5 (visible primary>secondary pipeline-fill gap).
fact["week"] = fact["date"]
piv = fact.pivot_table(index=["sku","distributor"], columns="week", values="qty", aggfunc="sum").fillna(0)
week_cols = [w for w in WEEKS if w in piv.columns]
piv = piv.reindex(columns=WEEKS, fill_value=0)

prim_rows=[]; inv_rows=[]
for (sku,dist), s in piv.iterrows():
    arr = s.to_numpy(dtype=float)
    nz  = np.nonzero(arr)[0]
    if len(nz)==0: continue
    first = nz[0]
    case  = CASE[cat_of[sku]]
    inv_end = 0.0; pushes = 0
    trail = []
    for i in range(first, len(arr)):
        st = arr[i]
        trail.append(st); trail = trail[-4:]
        safety = float(np.mean(trail))
        need = max(0.0, st + safety - inv_end)
        o = int(np.ceil(need/case)*case) if need>0 else 0
        if sku==NEW_SKU and o>0 and pushes<2:
            o = int(np.ceil(o*1.5/case)*case); pushes+=1
        inv_open = inv_end + o
        inv_end  = inv_open - st
        wk = WEEKS[i].date().isoformat()
        if o>0:
            prim_rows.append(dict(date=wk, sku=sku, distributor=dist, qty=o,
                dist_price=dp_of[sku], value=round(o*dp_of[sku],2)))
        inv_rows.append(dict(date=wk, sku=sku, distributor=dist,
            opening=int(round(inv_open-o)), primary_in=o, secondary_out=int(st),
            closing=int(round(inv_end)),
            weeks_cover=round(inv_end/max(safety,1e-9),2),
            near_stockout=bool(inv_end < 0.5*safety)))
primary   = pd.DataFrame(prim_rows); primary.to_csv(OUT/"primary_sales.csv", index=False)
inventory = pd.DataFrame(inv_rows);  inventory.to_csv(OUT/"distributor_inventory.csv", index=False)

# ---------------- 4. sales_targets (monthly, zone x category) -----------------
m = fact.merge(pm[["sku_code","category"]], left_on="sku", right_on="sku_code")
m["zone"]  = m.distributor.map(zone_of)
m["month"] = m.date.dt.to_period("M").astype(str)
act = m.groupby(["month","zone","category"]).qty.sum().reset_index(name="actual_qty")
t24 = act[act.month<"2025-01"].copy()
t24["target_qty"]=(t24.actual_qty*rng.uniform(0.92,1.12,len(t24))).round().astype(int)
base24 = t24.assign(m2=t24.month.str.replace("2024","2025"))
t25 = base24[["m2","zone","category","actual_qty"]].rename(columns={"m2":"month"})
t25["target_qty"]=(t25.actual_qty*(1+rng.uniform(0.10,0.18,len(t25)))).round().astype(int)
targets = pd.concat([t24[["month","zone","category","target_qty"]],
                     t25[["month","zone","category","target_qty"]]]).sort_values(["month","zone","category"])
targets["provenance"]="synthetic plan: 2024=actual x U(0.92,1.12); 2025=2024 actual x (1+10-18% stretch)"
targets.to_csv(OUT/"sales_targets.csv", index=False)

# ---------------- VERIFICATION ------------------------------------------------
def chk(n,c): print(f"[{'PASS' if c else 'FAIL'}] {n}")
print("================ V2 VERIFICATION ================")
chk("inventory identity closing==opening+in-out (all rows)",
    bool(((inventory.opening+inventory.primary_in-inventory.secondary_out)==inventory.closing).all()))
chk("inventory never negative", bool((inventory.closing>=0).all()))
tot = inventory.groupby(["sku","distributor"]).agg(p=("primary_in","sum"), s=("secondary_out","sum"))
chk("primary >= secondary for every sku-dist pair", bool((tot.p>=tot.s).all()))
case_ok = primary.merge(pm[["sku_code","category"]],left_on="sku",right_on="sku_code")
case_ok["case"]=case_ok.category.map(CASE)
chk("every primary order is a case multiple", bool((case_ok.qty % case_ok["case"] == 0).all()))
nl = inventory[inventory.sku==NEW_SKU].sort_values("date")
g  = nl.groupby("distributor").head(4)
ratio = g.primary_in.sum()/max(g.secondary_out.sum(),1)
chk(f"pipeline fill on {NEW_SKU}: first-4wk primary/secondary = {ratio:.2f}x (>1.3)", ratio>1.3)
chk("sku_costs covers all SKUs & 0<GM<1",
    bool(set(sku_costs.sku_code)==set(pm.sku_code) and sku_costs.mfr_gross_margin_pct.between(0.05,0.95).all()))
chk("targets: 24 months x 6 zones present", targets.month.nunique()==24 and targets.zone.nunique()==6)

# golden inventory walk (anchor pair, first 8 weeks)
walk = inventory[(inventory.sku==ANCHOR)&(inventory.distributor==GOLD_DIST)].sort_values("date").head(8)
walk.to_csv(OUT/"golden_inventory_walk.csv", index=False)
print("\nGOLDEN INVENTORY WALK  (DS-CONFPULSE-001 @ DIST-NO-001, first 8 wks)")
print(walk.to_string(index=False))
print(f"\nrows: primary={len(primary):,}  inventory={len(inventory):,}  targets={len(targets):,}")
