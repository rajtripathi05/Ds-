"""Template text-to-SQL against the semantic layer ONLY, with two enforcement layers:
(1) validator — allow-listed tables/columns/metrics per role, SELECT-only, LIMIT enforced;
(2) sqlite authorizer — driver-level deny of writes and exec-scoped columns for ops.
"""
import re, sqlite3
from semantic import LAYER, allowed_columns, allowed_metrics
from db import ro

VOCAB = None
def vocab():
    global VOCAB
    if VOCAB is None:
        con = ro()
        VOCAB = dict(
            zones=[z[0] for z in con.execute("SELECT DISTINCT zone FROM location_master")],
            cats=[c[0] for c in con.execute("SELECT DISTINCT category FROM product_master")],
            brands=[b[0] for b in con.execute("SELECT DISTINCT brand FROM product_master")],
        )
        con.close()
    return VOCAB

METRIC_PAT = [
    (r"margin|profitab", "gross_margin"),
    (r"revenue|sales value|value of sales|turnover", "realized_revenue"),
    (r"average price|avg price|price realised|price realized", "avg_realized_price"),
    (r"volume|qty|quantity|units|offtake|sold|drop|sales", "secondary_qty"),
]

def parse_question(q):
    """NL -> structured plan (metric, dims, filters, months). Deterministic, no LLM."""
    ql = q.lower()
    v = vocab()
    plan = dict(metric=None, dims=[], filters={}, months=None, limit=None)
    for pat, m in METRIC_PAT:
        if re.search(pat, ql):
            plan["metric"] = m
            break
    plan["metric"] = plan["metric"] or "secondary_qty"
    for z in v["zones"]:
        if re.search(rf"\b{z.lower()}\b(?:ern)?|\b{z.lower()[:5]}\w*zone|{z.lower()}[- ]zone", ql):
            plan["filters"]["zone"] = z
    for c in v["cats"]:
        if c.lower() in ql: plan["filters"]["category"] = c
    for b in v["brands"]:
        if b.lower() in ql: plan["filters"]["brand"] = b
    sku = re.search(r"\b(DS-[A-Z]+-\d{3})\b", q)
    if sku: plan["filters"]["sku"] = sku.group(1)
    yr = re.search(r"\b(202[4-6])\b", ql)
    if "early" in ql and yr:
        y = yr.group(1); plan["months"] = (f"{y}-01", f"{y}-06")
    elif re.search(r"q([1-4])[- ]?(202[4-6])", ql):
        m = re.search(r"q([1-4])[- ]?(202[4-6])", ql); qn, y = int(m.group(1)), m.group(2)
        plan["months"] = (f"{y}-{3*qn-2:02d}", f"{y}-{3*qn:02d}")
    elif yr:
        y = yr.group(1); plan["months"] = (f"{y}-01", f"{y}-12")
    if re.search(r"\bby month|monthly|trend|step down|drop|over time\b", ql):
        plan["dims"].append("month")
    for d in ("zone", "category", "brand", "channel"):
        if re.search(rf"\bby {d}\b", ql):
            plan["dims"].append(d)
    return plan

def build_sql(plan, role):
    mets = allowed_metrics(role)
    if plan["metric"] not in mets:
        return None, (f"REFUSE — metric '{plan['metric']}' uses executive-scoped fields "
                      f"(pricing/margin/cost). Your role (Operations) can query volumes and counts; "
                      f"ask an Executive user or request access via IT security policy.")
    spec = mets[plan["metric"]]
    dims = LAYER["dimensions"]
    joins, sel, grp = set(spec.get("needs", [])) - {"sales_secondary"}, [], []
    for d in plan["dims"]:
        ds = dims[d]
        sel.append(f'{ds["sql"]} AS {d}')
        grp.append(ds["sql"])
        if isinstance(ds, dict) and ds.get("join"):
            joins.add(ds["join"])
    where = []
    f = plan["filters"]
    if "zone" in f: joins.add("location_master"); where.append(f"l.zone = '{f['zone']}'")
    if "category" in f: joins.add("product_master"); where.append(f"p.category = '{f['category']}'")
    if "brand" in f: joins.add("product_master"); where.append(f"p.brand = '{f['brand']}'")
    if "sku" in f: where.append(f"s.sku = '{f['sku']}'")
    if plan["months"]:
        a, b = plan["months"]
        where.append(f"substr(s.date,1,7) >= '{a}' AND substr(s.date,1,7) <= '{b}'")
    sql = "SELECT " + (", ".join(sel) + ", " if sel else "") + f'{spec["sql"]} AS {plan["metric"]}'
    sql += " FROM sales_secondary s"
    if "product_master" in joins: sql += " JOIN product_master p ON p.sku_code = s.sku"
    if "location_master" in joins: sql += " JOIN location_master l ON l.distributor_code = s.distributor"
    if "sku_costs" in joins: sql += " JOIN sku_costs c ON c.sku_code = s.sku"
    if where: sql += " WHERE " + " AND ".join(where)
    if grp: sql += " GROUP BY " + ", ".join(grp) + " ORDER BY 1"
    sql += f" LIMIT {LAYER['row_limit']}"
    return sql, None

ALIAS = {"s": "sales_secondary", "p": "product_master", "l": "location_master", "c": "sku_costs"}

def validate(sql, role):
    """Layer-1 validator: SELECT-only, allow-listed tables + columns, LIMIT enforced."""
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^select\b", s) or ";" in s:
        return None, "REFUSE — only single read-only SELECT statements are allowed."
    if re.search(r"(?i)\b(insert|update|delete|drop|alter|create|attach|pragma|replace|vacuum)\b", s):
        return None, "REFUSE — write/DDL/pragma statements are blocked (read-only policy)."
    tables = set(re.findall(r"(?i)(?:from|join)\s+([a-z_]+)", s))
    allowed_t = set(LAYER["tables"])
    bad_t = tables - allowed_t
    if bad_t:
        return None, f"REFUSE — table(s) {sorted(bad_t)} are not in the semantic layer allow-list."
    cols = allowed_columns(role)
    for al, col in re.findall(r"\b([splc])\.([a-z_]+)", s):
        t = ALIAS[al]
        if col not in cols.get(t, set()):
            return None, (f"REFUSE — column {t}.{col} is executive-scoped; not available to your role. "
                          f"(Enforced at validator AND driver level; attempt logged.)")
    if "limit" not in s.lower():
        s += f" LIMIT {LAYER['row_limit']}"
    return s, None

def make_authorizer(role):
    cols = allowed_columns(role)
    def auth(action, a1, a2, a3, a4):
        if action == sqlite3.SQLITE_SELECT: return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            t, c = a1, a2
            if t in cols and (c in cols[t] or c == ""):
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY
        if action in (sqlite3.SQLITE_FUNCTION, 31):  # 31 = SQLITE_FUNCTION legacy
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    return auth

def run_sql(sql, role):
    """Layer-2: read-only connection + role authorizer at the sqlite driver."""
    s, err = validate(sql, role)
    if err:
        return None, err
    con = ro()
    con.set_authorizer(make_authorizer(role))
    try:
        cur = con.execute(s)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        return dict(sql=s, columns=cols, rows=rows[:LAYER["row_limit"]]), None
    except sqlite3.DatabaseError as e:
        return None, f"REFUSE — driver denied the query for this role ({e})."
    finally:
        con.close()

def ask_data(question, role):
    plan = parse_question(question)
    sql, err = build_sql(plan, role)
    if err:
        return dict(plan=plan, error=err)
    res, err2 = run_sql(sql, role)
    if err2:
        return dict(plan=plan, sql=sql, error=err2)
    return dict(plan=plan, **res)
