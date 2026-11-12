#!/usr/bin/env python3
"""wordnet.py — Filename tokens as addresses: co-occurrence net + queries (zero tokens, no model).

Build: walk a world root, tokenize entity names into tokens, count co-occurrence (window 3),
save PPMI edges + token->paths index. Optional: numpy SVD for 64-d embeddings.
Query: expand query tokens over the net, rank candidate paths (RRF-style fusion).
"""
import argparse, collections, json, math, os, re, sys

SPLIT = re.compile(r"[·@\[\]()（）.。、_\-—\s#>~|⨟/\\]+")
PURE_NUM = re.compile(r"^[\d%.]+$")


def tokens_of(name: str):
    stem = name.rsplit(".", 1)[0] if "." in name and not name.startswith(".") else name
    return [t for t in SPLIT.split(stem) if t]


def build(root: str, out: str, min_freq: int = 2, top_n: int = 3000):
    freq = collections.Counter()
    index = collections.defaultdict(list)
    for cur, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "node_modules", "__pycache__")]
        rel = os.path.relpath(cur, root)
        rel = "" if rel == "." else rel
        d_toks = []
        for p in (rel.split(os.sep) if rel else []):
            d_toks += tokens_of(p)
        for f in fs:
            p = os.path.join(rel, f) if rel else f
            toks = [t for t in (d_toks + tokens_of(f)) if t]
            for t in toks:
                freq[t] += 1
                if len(index[t]) < 8:
                    index[t].append(p)
    vocab = [w for w, c in freq.most_common(top_n) if not PURE_NUM.match(w)]
    vset = set(vocab)
    co = collections.Counter()
    for cur, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "node_modules", "__pycache__")]
        rel = os.path.relpath(cur, root); rel = "" if rel == "." else rel
        d_toks = []
        for p in (rel.split(os.sep) if rel else []):
            d_toks += [t for t in tokens_of(p) if t in vset]
        for f in fs:
            toks = [t for t in (d_toks + tokens_of(f)) if t in vset]
            for i, a in enumerate(toks):
                for j in range(i + 1, min(i + 3, len(toks))):
                    if toks[i] != toks[j]:
                        co[(a, toks[j])] += 1.0 / (j - i)
    os.makedirs(out, exist_ok=True)
    total = sum(freq.values()) or 1
    with open(os.path.join(out, "ppmi.tsv"), "w", encoding="utf-8") as fh:
        fh.write("#a\tb\tppmi\n")
        for (a, b), c in co.items():
            if c < 1.5:
                continue
            pmi = math.log(c * total / (freq[a] * freq[b] + 1e-9))
            if pmi > 0.3:
                fh.write(f"{a}\t{b}\t{pmi:.3f}\n")
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"freq": dict(freq.most_common(top_n)),
                   "index": {k: index[k] for k in vocab if index.get(k)}}, fh, ensure_ascii=False)
    print(f"built: {len(vocab)} tokens -> {out}")


def load_index(out):
    d = json.load(open(os.path.join(out, "index.json"), encoding="utf-8"))
    nb = collections.defaultdict(dict)
    p = os.path.join(out, "ppmi.tsv")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) == 3:
                a, b, w = c[0], c[1], float(c[2])
                nb[a][b] = max(nb[a].get(b, 0), w)
                nb[b][a] = max(nb[b].get(a, 0), w)
    return d["freq"], d["index"], nb


def query(out, q, top=8):
    freq, index, nb = load_index(out)
    toks = [t for t in tokens_of(q) if t]
    score = collections.defaultdict(float)
    for t in toks:
        if t in index:
            score[t] += 2.0
        for n, w in nb.get(t, {}).items():
            score[n] += w * 0.8
    paths = collections.defaultdict(float)
    for w, s in sorted(score.items(), key=lambda kv: -kv[1])[:10]:
        for p in index.get(w, [])[:8]:
            paths[p] += s
    ranked = sorted(paths.items(), key=lambda kv: -kv[1])[:top]
    print(f"query: {q}\n  tokens: {toks}\n  expanded: {' '.join(w for w, _ in sorted(score.items(), key=lambda kv: -kv[1])[:8])}")
    for p, s in ranked:
        print(f"  {s:6.2f}  {p}")
    return ranked


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Filename-token address network")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--root", required=True); b.add_argument("--out", default="./index")
    q = sub.add_parser("query"); q.add_argument("--index", default="./index"); q.add_argument("--q", required=True)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.root, a.out)
    else:
        query(a.index, a.q)
