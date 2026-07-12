"""Minimal PDF text extractor for machine-generated PDFs (D1):
ASCII85+Flate content streams -> BT/ET text objects -> (y,x)-ordered lines."""
import re, zlib, base64
from pathlib import Path

def _streams(raw):
    out = []
    for m in re.finditer(rb"stream\r?\n", raw):
        end = raw.find(b"endstream", m.end())
        if end < 0:
            continue
        dict_start = raw.rfind(b"<<", 0, m.start())
        head = raw[dict_start:m.start()] if dict_start >= 0 else b""
        data = raw[m.end():end].rstrip(b"\r\n")
        try:
            if b"ASCII85Decode" in head:
                if data.endswith(b"~>"):
                    data = data[:-2]          # strip EXACTLY the EOD marker, nothing else
                data = base64.a85decode(data, adobe=False)
            if b"FlateDecode" in head:
                data = zlib.decompress(data)
            out.append(data)
        except Exception:
            continue
    return out

def _unescape(s):
    return (s.replace(rb"\(", b"(").replace(rb"\)", b")").replace(rb"\\", b"\\")
             .decode("latin-1"))

def extract_text(pdf_path):
    raw = Path(pdf_path).read_bytes()
    frags = []                      # (y, x, text)
    for data in _streams(raw):
        x = y = 0.0
        for op in re.finditer(
                rb"(-?[\d.]+)\s+(-?[\d.]+)\s+(Td|TD)|\(((?:[^()\\]|\\.)*)\)\s*Tj|1 0 0 1 (-?[\d.]+) (-?[\d.]+) Tm",
                data):
            if op.group(3):                       # Td/TD relative move
                x += float(op.group(1)); y += float(op.group(2))
            elif op.group(5) is not None:         # Tm absolute
                x, y = float(op.group(5)), float(op.group(6))
            elif op.group(4) is not None:         # Tj show text
                frags.append((round(-y, 1), x, _unescape(op.group(4))))
    if not frags:
        return ""
    frags.sort(key=lambda t: (t[0], t[1]))
    lines, cur_y, cur = [], None, []
    for yy, xx, tx in frags:
        if cur_y is None or abs(yy - cur_y) > 0.5:
            if cur: lines.append(" ".join(cur))
            cur, cur_y = [tx], yy
        else:
            cur.append(tx)
    if cur: lines.append(" ".join(cur))
    return "\n".join(lines)

if __name__ == "__main__":
    t = extract_text("data/sets/SET-0001/invoice.pdf")
    print(t[:600])
    print("...lines:", len(t.splitlines()))
