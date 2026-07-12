"""THE one writer of out/plan/* (FROZEN FORECAST CORE / ONE-WAY STATE).
Builds: snapshot.json (KPIs, curves, tables) + whatif_state.npz (arrays for the scenario engine).
Everything downstream (server, cockpit, exports) READS these artifacts only.
"""
import json, sys, time
import numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from features import build_panel
from backtest import run as backtest_run, assemble, choose_champions, forecast_all
from hierarchy import build_S, bottom_up, assert_ties
from fva import fva_table
from causal import uplift_study, category_recovery, TYPE_MULT
from optimizer import prepare, solve, risk_lists

H = 4

def main():
    t0 = time.time()
    res, series_bt, Y_bt, folds = backtest_run()
    panel, fr, rep = build_panel()
    series, weeks, months, fest, Y, PR, PX, catd, zoned = assemble(panel)

    # ---- forward forecast (origin = last observed week) ----
    ext_w = [pd.Timestamp(weeks[-1]) + pd.Timedelta(weeks=k) for k in range(1, H + 1)]
    months_x = np.concatenate([months, [w.month for w in ext_w]])
    fest_x = np.concatenate([fest, np.zeros(H)])
    Y_x = np.concatenate([Y, np.full((len(series), H), np.nan)], 1)
    PR_x = np.concatenate([PR, np.repeat(PR[:, -1:], H, 1)], 1)
    PX_x = np.concatenate([PX, np.zeros((len(series), H))], 1)
    origin = len(weeks) - 1
    champ = choose_champions(series, Y_x, months_x, fest_x, PR_x, PX_x, catd, zoned, origin)
    fc = forecast_all(series, Y_x, months_x, fest_x, PR_x, PX_x, catd, zoned, origin, H,
                      champ=champ)["champion"]

    # ---- reconciliation on the forward plan (ties asserted) ----
    S, names = build_S(series, fr["product"])
    for h in range(H):
        allv = bottom_up(S, np.nan_to_num(fc[:, h]))
        assert_ties(S, allv, np.nan_to_num(fc[:, h]))

    # ---- causal layer ----
    updf, roi = uplift_study(panel, fr["promo"], fr["product"], fr["costs"])
    rec = category_recovery(updf)
    el_cat = dict(zip(rec["category"], rec["el_recovered"]))

    # ---- optimizer baseline ----
    prod = fr["product"]
    prim = fr["primary"].merge(prod[["sku_code", "category"]], left_on="sku", right_on="sku_code")
    last8 = sorted(prim["date"].unique())[-8:]
    cap_by_cat = (prim[prim["date"].isin(last8)].groupby("category")["qty"].sum() / 8 * 1.15 * 4).to_dict()
    dpmap = prod.set_index("sku_code")["dist_price"]
    prim["val"] = prim["qty"] * prim["sku"].map(dpmap)
    budget = float(prim[prim["date"].isin(sorted(prim["date"].unique())[-4:])]["val"].sum())
    P = prepare(series, fc, fr["inventory"], fr["location"], prod, fr["costs"], fr["primary"])
    sol = solve(series, P, budget, cap_by_cat)
    fwd_risk, recon = risk_lists(series, P, sol, fr["inventory"], fr["location"])

    # ---- FVA ----
    fva, _ = fva_table(series_bt, Y_bt, weeks, folds, fr["targets"])

    # ---- curves ----
    def curve(mask):
        act = np.nansum(np.where(np.isnan(Y[mask]), 0, Y[mask]), 0)
        fwd = np.nan_to_num(fc[mask]).sum(0)
        return act.tolist(), fwd.tolist()
    nation_a, nation_f = curve(np.ones(len(series), bool))
    cats = {c: curve((series["category"] == c).values) for c in sorted(series["category"].unique())}
    # launch pipeline view (nation weekly primary vs secondary for the launch SKU)
    NEW = "DS-CONFPULSE-149"
    p_new = (fr["primary"][fr["primary"]["sku"] == NEW].groupby("date")["qty"].sum()
             .reindex(pd.Index(weeks)).fillna(0))
    s_new = (panel[panel["sku"] == NEW].groupby("date")["qty"].sum()
             .reindex(pd.Index(weeks)).fillna(0))
    # canonical pipeline-fill definition (matches extend_ds.py verification):
    # per distributor, FIRST 4 inventory rows of the launch SKU; ratio of sums
    nl = fr["inventory"][fr["inventory"]["sku"] == NEW].sort_values("date")
    g4 = nl.groupby("distributor").head(4)
    fill = float(g4["primary_in"].sum() / max(g4["secondary_out"].sum(), 1.0))

    snapshot = dict(
        built_at=pd.Timestamp.now().isoformat(), horizon=H,
        weeks=[str(w)[:10] for w in weeks], fwd_weeks=[str(w)[:10] for w in ext_w],
        kpis=dict(
            wmape_sku_champion=res["sku"]["champion"]["wmape"],
            wmape_sku_snaive=res["sku"]["snaive"]["wmape"],
            wmape_cat_champion=res["category"]["champion"]["wmape"],
            wmape_cat_snaive=res["category"]["snaive"]["wmape"],
            fva_vs_plan_pp=float(fva.loc["champion", "fva_vs_plan_pp"]),
            fva_vs_snaive_pp=float((fva.loc["snaive", "wmape"] - fva.loc["champion", "wmape"]) * 100),
            data_badges=rep.badges, champion_mix=res["champions"],
            pipeline_fill_first4wk=round(fill, 2) if fill else None,
            launch_sku=NEW),
        curves=dict(nation=dict(actual=nation_a, fwd=nation_f),
                    categories={c: dict(actual=a, fwd=f) for c, (a, f) in cats.items()},
                    launch=dict(primary=p_new.values.tolist(), secondary=s_new.values.tolist())),
        elasticity=dict(recovered={k: float(v) for k, v in el_cat.items()},
                        table=rec.to_dict("records")),
        promo_roi=dict(median=float(roi["roi"].median()),
                       top=roi.sort_values("roi", ascending=False).head(5).to_dict("records"),
                       bottom=roi.sort_values("roi").head(5).to_dict("records")),
        plan=dict(binding=sol["binding"], objective_margin=float(sol["objective"]),
                  budget=budget, budget_util=float(sol["util_budget"]),
                  cap_util={k: float(v) for k, v in sol["cap_util"].items()},
                  total_ship_value=float((sol["ship"] * P["dp"]).sum()),
                  lines=int((sol["ship"] > 0).sum()),
                  forward_risk=fwd_risk.head(50).to_dict("records"),
                  near_stockout_reconciliation=recon),
        build_seconds=round(time.time() - t0, 1),
    )
    Path("out/plan").mkdir(parents=True, exist_ok=True)
    json.dump(snapshot, open("out/plan/snapshot.json", "w"), indent=1, default=float)

    np.savez_compressed(
        "out/plan/whatif_state.npz",
        fc=fc, d4=P["d4"], davg=P["davg"], opening=P["opening"], dp=P["dp"],
        margin=P["margin"], casem=P["casem"],
        abc=series["sku"].map(prod.set_index("sku_code")["abc_class"]).values.astype("U1"),
        sku=series["sku"].values.astype("U24"), zone=series["zone"].values.astype("U16"),
        category=series["category"].values.astype("U20"),
        el_sku=series["elast"].abs().values,
        el_cat_names=np.array(list(el_cat.keys()), dtype="U20"),
        el_cat_vals=np.array([el_cat[k] for k in el_cat], float),
        budget=np.array([budget]), cap_names=np.array(list(cap_by_cat.keys()), dtype="U20"),
        cap_vals=np.array([cap_by_cat[k] for k in cap_by_cat], float),
        nation_actual=np.array(nation_a), fwd_weeks_months=np.array([w.month for w in ext_w]))
    print("snapshot built in", snapshot["build_seconds"], "s | binding:", sol["binding"],
          "| pipeline fill:", snapshot["kpis"]["pipeline_fill_first4wk"])

if __name__ == "__main__":
    main()
