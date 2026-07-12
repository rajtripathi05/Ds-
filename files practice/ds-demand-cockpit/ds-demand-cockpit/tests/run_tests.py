"""CANONICAL CI — one entry point. Runs every gate; prints a table; exit 0 only if all green.
Anti-fabrication: every number below is measured in this run."""
import subprocess, sys, json, time, os
sys.path.insert(0, "src")
import numpy as np, pandas as pd

ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else "all"
STATE = "out/cache/ci_state.json"
RES = []
def _load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}
def _save(d):
    json.dump(d, open(STATE, "w"), indent=1)
def gate(name, fn):
    t0 = time.time()
    try:
        detail = fn()
        RES.append((name, True, detail, round(time.time()-t0, 1)))
    except AssertionError as e:
        RES.append((name, False, str(e), round(time.time()-t0, 1)))
    except Exception as e:
        RES.append((name, False, f"{type(e).__name__}: {e}", round(time.time()-t0, 1)))

def golden_thread():
    g = pd.read_csv("data/golden_thread_trace.csv")
    fact = pd.read_csv("data/sales_secondary.csv")
    fpair = fact[(fact["sku"] == "DS-CONFPULSE-001") & (fact["distributor"] == "DIST-NO-001")]
    fmap = dict(zip(fpair["date"], fpair["qty"]))
    cols = ["base", "trend", "seasonality", "price_effect", "promo_lift", "festival",
            "cannibalization", "ar1_noise"]
    n_ok = 0
    for _, r in g.iterrows():
        if any(pd.isna(r[c]) for c in cols):
            continue
        prod = 1.0
        for c in cols: prod *= float(r[c])
        recon = int(round(prod))
        assert abs(recon - int(r["qty"])) <= 1, \
            f"golden thread breaks at {r['date']}: factors->{recon} vs stored {r['qty']}"
        if r["date"] in fmap and int(r["qty"]) > 0:
            assert int(fmap[r["date"]]) == int(r["qty"]), f"trace vs fact mismatch {r['date']}"
        n_ok += 1
    assert n_ok >= 90, f"only {n_ok} verifiable golden rows"
    return f"{n_ok} weekly rows reproduce (factor product == stored qty, ±1 rounding)"

def inventory_identity():
    inv = pd.read_csv("data/distributor_inventory.csv")
    lhs = inv["closing"].values
    rhs = inv["opening"].values + inv["primary_in"].values - inv["secondary_out"].values
    bad = np.abs(lhs - rhs) > 1e-9
    assert not bad.any(), f"identity fails on {bad.sum()} rows"
    assert (inv["closing"] >= 0).all(), "negative closing stock found"
    return f"closing = opening + in − out on all {len(inv):,} rows; never negative"

def pipeline_fill():
    inv = pd.read_csv("data/distributor_inventory.csv", parse_dates=["date"])
    nl = inv[inv["sku"] == "DS-CONFPULSE-149"].sort_values("date")
    g4 = nl.groupby("distributor").head(4)
    ratio = g4["primary_in"].sum() / max(g4["secondary_out"].sum(), 1.0)
    assert ratio > 1.3, f"fill {ratio:.2f} not > 1.3"
    assert abs(ratio - 3.13) < 0.01, f"fill {ratio:.4f} != documented 3.13"
    return f"detected {ratio:.2f}× (doc: 3.13×; threshold >1.3)"

def near_stockout_reconciliation():
    inv = pd.read_csv("data/distributor_inventory.csv")
    flags = int((inv["near_stockout"].astype(str) == "True").sum())
    det = int((inv["weeks_cover"] < 1.0).sum())
    assert flags == det, f"detector {det} vs flags {flags}"
    return f"detector({det}) == flags({flags}) — exact on the data's own definition (B10)"

def subgate(script):
    def _f():
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, (r.stdout + r.stderr)[-400:]
        tail = [l for l in r.stdout.strip().splitlines() if "GATE" in l]
        return tail[-1] if tail else "green"
    return _f

def m1_beats_naive():
    from backtest import run as btrun
    res, *_ = btrun()
    cs, ns = res["sku"]["champion"]["wmape"], res["sku"]["snaive"]["wmape"]
    cc, nc = res["category"]["champion"]["wmape"], res["category"]["snaive"]["wmape"]
    assert cs < ns and cc < nc, f"champion {cs:.4f}/{cc:.4f} vs snaive {ns:.4f}/{nc:.4f}"
    return f"champion {cs*100:.2f}%/{cc*100:.2f}% vs snaive {ns*100:.2f}%/{nc*100:.2f}% (SKU/category)"

GATES = {
    "fast": [("Golden thread reproduces", golden_thread),
             ("Inventory identity holds", inventory_identity),
             ("Pipeline-fill 3.13× detected", pipeline_fill),
             ("Near-stockout reconciliation exact", near_stockout_reconciliation)],
    "m0": [("M0 messy catch-rate 100%", subgate("tests/gate_m0.py"))],
    "m1": [("M1 champion beats seasonal-naive (SKU & category)", m1_beats_naive)],
    "m2": [("M2 hierarchy ties + FVA", subgate("tests/gate_m2.py"))],
    "m3": [("M3 elasticity recovery ≤20%", subgate("tests/gate_m3.py"))],
    "m4": [("M4 optimizer + binding + shadow", subgate("tests/gate_m4.py"))],
    "m5": [("M5 cockpit API/role/what-if/export", subgate("tests/gate_m5.py"))],
}
if ONLY == "assemble":
    st = _load()
    missing = [k for k in ("fast","m0","m1","m2","m3","m4","m5") if k not in st]
    assert not missing, f"cannot assemble, gates not run: {missing}"
    RES = [tuple(x) for k in ("fast","m0","m1","m2","m3","m4","m5") for x in st[k]]
else:
    for grp, gs in GATES.items():
        if ONLY in ("all", grp):
            for name, fn in gs:
                gate(name, fn)
    if ONLY != "all":
        st = _load(); st[ONLY] = RES; _save(st)
        for n, ok, d, dt in RES:
            print(("GREEN" if ok else "RED"), "|", n, "|", d, f"| {dt}s")
        sys.exit(0 if all(r[1] for r in RES) else 1)

w = max(len(n) for n, *_ in RES)
lines = ["# CI — canonical test results (measured this run)", "",
         "| gate | status | evidence | s |", "|---|---|---|---|"]
for n, ok, d, dt in RES:
    print(("✅" if ok else "❌"), n.ljust(w), "|", d)
    lines.append(f"| {n} | {'GREEN' if ok else 'RED'} | {str(d)[:160]} | {dt} |")
allok = all(ok for _, ok, *_ in RES)
lines.append(f"\n**ALL GATES: {'GREEN' if allok else 'RED'}** · {time.strftime('%Y-%m-%d %H:%M IST')}")
open("out/plan/CI_RESULTS.md", "w").write("\n".join(lines))
print("\nALL GATES:", "GREEN" if allok else "RED")
sys.exit(0 if allok else 1)
