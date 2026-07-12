"""Screenshot pack (B3): matplotlib renders of the cockpit's four data views, from the SAME
snapshot + live what-if API the UI reads. Not browser captures (see BLOCKERS.md)."""
import json, subprocess, sys, time
from urllib.request import urlopen, Request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PORT = 8795
srv = subprocess.Popen([sys.executable, "src/server.py", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
try:
    for _ in range(40):
        try: urlopen(f"http://127.0.0.1:{PORT}/snapshot?role=exec", timeout=5); break
        except Exception: time.sleep(0.5)
    S = json.load(open("out/plan/snapshot.json"))
    ACC, INK, MUT = "#b3282d", "#44403c", "#a8a29e"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUT, "axes.labelcolor": INK})

    def style(ax, title):
        ax.set_title(title, fontsize=11, fontweight="bold", color=INK, loc="left")
        ax.grid(alpha=.25); ax.spines[["top", "right"]].set_visible(False)

    # 1 · nation demand + base plan + promo scenario
    sc = json.loads(urlopen(Request(f"http://127.0.0.1:{PORT}/whatif?role=exec",
        data=json.dumps({"promo": {"category": "Confectionery", "depth": .25,
                                   "type": "consumer", "weeks": [1, 2, 3, 4]}}).encode(),
        method="POST")).read())
    a = S["curves"]["nation"]["actual"]; f = S["curves"]["nation"]["fwd"]; g = sc["nation_fwd"]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=110)
    ax.plot(range(len(a)), a, color=INK, lw=1.4, label="actual (105 wks)")
    ax.plot(range(len(a)-1, len(a)+4), [a[-1]]+f, color=ACC, lw=2, label="base 4-wk plan")
    ax.plot(range(len(a)-1, len(a)+4), [a[-1]]+g, color="#1d4ed8", lw=2, ls="--",
            label="scenario: Confectionery promo 25% consumer")
    style(ax, "Nation weekly demand — frozen core + what-if overlay (reconciled before display)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig("screenshots/01-nation-demand-whatif.png"); plt.close(fig)

    # 2 · launch pipeline fill
    L = S["curves"]["launch"]
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=110)
    ax.plot(L["primary"], color=ACC, lw=1.6, label="primary (company→distributor)")
    ax.plot(L["secondary"], color=INK, lw=1.4, label="secondary (distributor→retail)")
    style(ax, f"Launch pipeline — DS-CONFPULSE-149 · first-4wk fill {S['kpis']['pipeline_fill_first4wk']}× (canonical)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig("screenshots/02-launch-pipeline-fill.png"); plt.close(fig)

    # 3 · categories small multiples
    cats = S["curves"]["categories"]
    fig, axes = plt.subplots(2, 3, figsize=(11, 5), dpi=110)
    for ax, (c, v) in zip(axes.flat, cats.items()):
        ax.plot(v["actual"], color=INK, lw=1)
        ax.plot(range(len(v["actual"])-1, len(v["actual"])+4), [v["actual"][-1]]+v["fwd"], color=ACC, lw=1.6)
        style(ax, c)
    fig.suptitle("Category demand — actual + 4-wk plan", fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig("screenshots/03-category-grid.png"); plt.close(fig)

    # 4 · elasticity recovery
    t = S["elasticity"]["table"]
    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=110)
    x = np.arange(len(t)); w = 0.38
    ax.bar(x - w/2, [r["el_true"] for r in t], w, color=MUT, label="generative truth")
    ax.bar(x + w/2, [r["el_recovered"] for r in t], w, color=ACC, label="recovered (matched controls)")
    ax.set_xticks(x, [r["category"] for r in t], rotation=15)
    style(ax, "Causal promo analysis — elasticity recovered vs truth (all ≤20% err)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig("screenshots/04-elasticity-recovery.png"); plt.close(fig)

    # 5 · optimizer utilisation + binding under stress
    m4 = json.load(open("out/plan/m4_summary.json"))
    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=110)
    caps = m4["capacity_utilisation"]; names = list(caps) + ["WC budget (base)", "WC budget (stress)"]
    vals = [caps[c] for c in caps] + [m4["budget_utilisation"], m4["stress_scenario"]["budget_utilisation"]]
    cols = [MUT]*len(caps) + [MUT, ACC]
    ax.barh(names, [v*100 for v in vals], color=cols)
    ax.axvline(99.5, color=ACC, ls="--", lw=1)
    ax.set_xlabel("% utilisation")
    style(ax, f"Constraint utilisation — stress binding: {m4['stress_scenario']['BINDING_CONSTRAINT'][:60]}…  shadow ₹{m4['stress_scenario']['shadow_price_margin_per_budget_rupee']}/₹")
    fig.tight_layout()
    fig.savefig("screenshots/05-optimizer-binding.png"); plt.close(fig)
    print("5 screenshots written")
finally:
    srv.terminate()
