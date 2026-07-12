"""Hybrid lexical retrieval: BM25 (0.65) + TF-IDF cosine (0.35), role-filtered index (C2)."""
import math, re
from collections import Counter
from corpus import load_corpus

STOP = set("the a an is are was were be been of in on at to for from with and or as by that this it its we our you your do does did not no".split())

def _stem(w):
    for suf in ("ings", "ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w

def tok(s):
    s = s.lower().replace("-", " ").replace("/", " ")
    return [_stem(w) for w in re.findall(r"[a-z0-9₹%.]+", s) if w not in STOP and len(w) > 1]

class Index:
    def __init__(self, role="ops"):
        docs, chunks, self.version_map = load_corpus()
        self.role = role
        self.docs = {i: d for i, d in docs.items()
                     if role == "exec" or d["access"] != "exec_only"}
        self.ids = list(self.docs)
        self.toks = {i: tok((self.docs[i]["title"] + " ") * 3 + self.docs[i]["body"]) for i in self.ids}
        self.tf = {i: Counter(t) for i, t in self.toks.items()}
        self.df = Counter()
        for t in self.tf.values():
            self.df.update(t.keys())
        self.N = len(self.ids)
        self.avgdl = sum(len(t) for t in self.toks.values()) / self.N

    def bm25(self, q, k1=1.5, b=0.75):
        qt = tok(q)
        scores = {}
        for i in self.ids:
            s, dl = 0.0, len(self.toks[i])
            for w in qt:
                f = self.tf[i].get(w, 0)
                if not f: continue
                idf = math.log(1 + (self.N - self.df[w] + .5) / (self.df[w] + .5))
                s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / self.avgdl))
            scores[i] = s
        return scores

    def tfidf_cos(self, q):
        qt = Counter(tok(q))
        qv = {w: c * math.log(1 + self.N / (self.df.get(w, 0) + 1)) for w, c in qt.items()}
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1
        out = {}
        for i in self.ids:
            dv = {w: f * math.log(1 + self.N / (self.df[w] + 1)) for w, f in self.tf[i].items()}
            dn = math.sqrt(sum(v * v for v in dv.values())) or 1
            out[i] = sum(qv.get(w, 0) * dv.get(w, 0) for w in qv) / (qn * dn)
        return out

    def search(self, q, k=4):
        b, t = self.bm25(q), self.tfidf_cos(q)
        bmax = max(b.values()) or 1; tmax = max(t.values()) or 1
        hyb = {i: 0.65 * b[i] / bmax + 0.35 * t[i] / tmax for i in self.ids}
        qt = set(tok(q))
        ranked = sorted(hyb.items(), key=lambda x: -x[1])
        # raw BM25 + distinct matched-term count: floors must use these, not normalised scores
        return [(i, round(s, 4), round(b[i], 3), len(qt & set(self.tf[i])))
                for i, s in ranked[:k]]
