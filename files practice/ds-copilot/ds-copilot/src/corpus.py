"""Corpus loader: front-matter parse (access tags), section chunking, version families."""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"

def parse_doc(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    meta, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body

def chunk(body, doc_id):
    """Section-aware chunks; long sections split by paragraph; keeps heading context."""
    chunks, heading = [], ""
    parts = re.split(r"\n(?=#{1,3} )", body)
    for part in parts:
        lines = part.strip().splitlines()
        if not lines:
            continue
        if lines[0].startswith("#"):
            heading = lines[0].lstrip("# ").strip()
            content = "\n".join(lines[1:]).strip()
        else:
            content = part.strip()
        paras = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
        buf = ""
        for p in paras:
            if len(buf) + len(p) < 700:
                buf += ("\n\n" if buf else "") + p
            else:
                if buf: chunks.append((heading, buf))
                buf = p
        if buf:
            chunks.append((heading, buf))
    return [dict(doc_id=doc_id, heading=h, text=t, chunk_id=f"{doc_id}#{i}")
            for i, (h, t) in enumerate(chunks)]

def load_corpus():
    manifest = json.load(open(CORPUS.parent / "corpus_manifest.json"))
    if isinstance(manifest, dict):
        manifest = manifest.get("docs", list(manifest.values())[0])
    docs, chunks = {}, []
    for entry in manifest:
        p = CORPUS / entry["file"]
        meta, body = parse_doc(p)
        d = dict(entry)
        d["access"] = meta.get("access", entry.get("access", "all")).strip()
        d["effective"] = meta.get("effective", entry.get("effective", ""))
        d["title"] = meta.get("title", entry.get("title", ""))
        d["body"] = body
        docs[d["doc_id"]] = d
        chunks.extend(chunk(body, d["doc_id"]))
    # version families: same title, different effective dates
    fams = {}
    for d in docs.values():
        fams.setdefault(d["title"], []).append(d["doc_id"])
    version_map = {}
    for title, ids in fams.items():
        if len(ids) > 1:
            ids_sorted = sorted(ids, key=lambda i: docs[i]["effective"])
            for i in ids_sorted:
                version_map[i] = dict(family=title, newest=ids_sorted[-1],
                                      all=ids_sorted)
    return docs, chunks, version_map

if __name__ == "__main__":
    docs, chunks, vm = load_corpus()
    exec_only = [d for d in docs.values() if d["access"] == "exec_only"]
    out = dict(n_docs=len(docs), n_chunks=len(chunks),
               exec_only=[d["doc_id"] for d in exec_only],
               version_families={v["family"]: v["all"] for v in vm.values()})
    (ROOT / "out").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "out/parsed_manifest.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
