"""Mini strict YAML-subset loader for semantic.yaml (PyYAML unavailable offline, C1)
+ role-aware allow-lists."""
import re
from pathlib import Path

def _parse(path):
    root, stack = {}, [( -1, None, {} )]
    root = {}
    stack = [(-1, root)]
    for raw in Path(path).read_text().splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, val = raw.strip().partition(":")
        val = val.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            node = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            if val.startswith("{"):
                node = {}
                inner = val.strip("{} ")
                if inner:
                    # quote- and bracket-aware split (commas may appear inside "..." or [...])
                    parts, buf, q, br = [], "", False, 0
                    for ch in inner:
                        if ch == '"': q = not q
                        if ch == "[" and not q: br += 1
                        if ch == "]" and not q: br -= 1
                        if ch == "," and not q and br == 0:
                            parts.append(buf); buf = ""
                        else:
                            buf += ch
                    if buf.strip(): parts.append(buf)
                    for part in parts:
                        k, _, v = part.partition(":")
                        v = v.strip()
                        if v.startswith("{"):
                            sub = {}
                            for p2 in v.strip("{} ").split(","):
                                if ":" in p2:
                                    a, _, b = p2.partition(":")
                                    sub[a.strip()] = _coerce(b.strip())
                            node[k.strip()] = sub
                        elif v.startswith("["):
                            node[k.strip()] = [x.strip() for x in v.strip("[] ").split(",") if x.strip()]
                        else:
                            node[k.strip()] = _coerce(v)
                parent[key] = node
            elif val.startswith("["):
                parent[key] = [x.strip() for x in val.strip("[] ").split(",") if x.strip()]
            else:
                parent[key] = _coerce(val)
    return root

def _coerce(v):
    v = v.strip().strip('"')
    if v == "true": return True
    if v == "false": return False
    if v.isdigit(): return int(v)
    return v

LAYER = _parse(Path(__file__).parent / "semantic.yaml")

def allowed_columns(role):
    out = {}
    for t, spec in LAYER["tables"].items():
        cols = set()
        for c, cs in spec["columns"].items():
            if role == "exec" or not (isinstance(cs, dict) and cs.get("exec")):
                cols.add(c)
        out[t] = cols
    return out

def allowed_metrics(role):
    return {m: s for m, s in LAYER["metrics"].items()
            if role == "exec" or not s.get("exec")}

if __name__ == "__main__":
    import json
    print("tables:", list(LAYER["tables"]))
    print("ops cols sales:", sorted(allowed_columns("ops")["sales_secondary"]))
    print("ops metrics:", list(allowed_metrics("ops")))
    print("exec metrics:", list(allowed_metrics("exec")))
    print("row_limit:", LAYER["row_limit"])
