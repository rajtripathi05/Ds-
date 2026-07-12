"""SQLite spine builder + strict read-only connector."""
import sqlite3, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
import os
DB = Path(os.environ.get("DSCOPILOT_DB", ROOT / "out" / "copilot.db"))
TABLES = ["product_master", "location_master", "calendar", "promo_calendar",
          "price_history", "sku_costs", "sales_secondary"]

def build(force=False):
    if DB.exists() and not force:
        try:
            return counts()
        except Exception:
            DB.unlink()          # corrupt/partial file -> rebuild from CSVs
    DB.parent.mkdir(exist_ok=True)
    if force and DB.exists():
        try: DB.unlink()
        except OSError: pass
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=OFF"); con.execute("PRAGMA synchronous=OFF")
    for t in TABLES:
        df = pd.read_csv(ROOT / "db" / f"{t}.csv")
        df.to_sql(t, con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS ix_sales ON sales_secondary(sku, distributor, date)")
    con.commit(); con.close()
    return counts()

def counts():
    con = ro()
    out = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
    con.close()
    return out

def ro():
    """Read-only connection — writes are impossible at the driver level."""
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

if __name__ == "__main__":
    c = build(force=True)
    print(json.dumps(c, indent=1))
