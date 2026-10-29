"""
Concept ranking (poc/concepts): offline 0-10 scores per (product, concept) and embeddings of the concept names.
At query time the parser residual is embedded and compared with the concept names; the concepts above the
threshold (at most k) are weighted with softmax(similarity / T) and products are ranked by the weighted sum of
their scores, as score / 10 (default) or as percentiles within the category.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
import time

import numpy as np
import pandas as pd
import yaml

import common

CONCEPTS_DIR = common.REPO / "poc/concepts"
CONCEPTS_YAML = CONCEPTS_DIR / "concepts.yaml"
SCORES = CONCEPTS_DIR / "results/concept_scores.parquet"
MISSES = CONCEPTS_DIR / "data/misses.jsonl"
FILE = "concepts.parquet"
PREFIX = "concept__"
FORMATS = {"plain": lambda s: s, "query": common.query_text}
NORMS = ("percentile", "raw")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_list(path=CONCEPTS_YAML):
    return [dict(id=c["id"], name=c["name"], type=c["type"]) for c in yaml.safe_load(Path(path).read_text(encoding="utf-8"))]


def build(index, concept_list, scores, embed):
    """Index DataFrame + long scores -> (index with concept__<id> raw score columns, concept rows with embeddings,
    categories with scores). Unscored categories are allowed; a gap inside a scored category is an error."""
    ids = [c["id"] for c in concept_list]
    s = scores[scores["product_id"].isin(set(index["product_id"])) & scores["concept_id"].isin(ids)]
    wide = s.pivot(index="product_id", columns="concept_id", values="score").reindex(index=index["product_id"], columns=ids)
    scored = wide.notna().any(axis=1).to_numpy()
    categories = sorted(set(index.loc[scored, "category"]))
    gaps = wide[index["category"].isin(categories).to_numpy()].isna()
    if gaps.any().any():
        pid, cid = gaps.stack()[lambda g: g].index[0]
        raise ValueError(f"{int(gaps.to_numpy().sum())} missing (product, concept) scores in {categories}, "
                         f"e.g. {pid} / {cid}; score them first (poc/concepts/score_products.py)")
    index = index.assign(**{PREFIX + i: wide[i].to_numpy(dtype=float) for i in ids})
    rows = [dict(c, embedding=common.normalize(np.asarray(embed(c["name"]), np.float32)).tolist()) for c in concept_list]
    return index, pd.DataFrame(rows), categories


def percentiles(raw, categories):
    """Percentile rank in (0, 1] within the category; ties share the average rank, unscored stays NaN."""
    d = pd.DataFrame(raw)
    return d.groupby(np.asarray(categories)).rank(method="average", pct=True).to_numpy()


def select(sims, threshold, k, temperature):
    """-> (indexes of the chosen concepts, weights): similarity >= threshold, at most k, softmax(sim / T)."""
    chosen = [int(j) for j in np.argsort(-sims, kind="stable")[:k] if sims[j] >= threshold]
    if not chosen:
        return [], np.zeros(0)
    z = sims[chosen] / temperature
    w = np.exp(z - z.max())
    return chosen, w / w.sum()


class ConceptRanker:
    def __init__(self, products, rows, info, embedder, threshold, k=3, temperature=0.1, norm="raw",
                 misses=MISSES):
        self.ids, self.names = list(rows["id"]), list(rows["name"])
        self.E = common.normalize(np.stack([np.asarray(e, np.float32) for e in rows["embedding"]]))
        self.raw = np.array([[p.get(PREFIX + i, np.nan) for i in self.ids] for p in products], dtype=float)
        self.norm = norm
        self.pct = percentiles(self.raw, [p["category"] for p in products]) if norm == "percentile" else self.raw / 10
        self.categories = set(info["categories"])
        self.text = FORMATS[info["format"]]
        self.format = info["format"]
        self.embedder, self.threshold, self.k, self.temperature = embedder, threshold, k, temperature
        self.misses, self.lock = Path(misses), threading.Lock()

    def match(self, residual, category, query):
        """Embeds the residual and picks the concepts; called once per query, nothing is stored except misses."""
        t = time.perf_counter()
        out = dict(residual=residual, format=self.format, threshold=self.threshold, k=self.k, selected=[], sims=[])
        if not residual.strip():
            return dict(out, fallback="empty residual", ms=0.0)
        if category not in self.categories:
            return dict(out, fallback=f"no concept scores for {category}", ms=0.0)
        sims = self.E @ common.normalize(np.asarray(self.embedder(self.text(residual)), np.float32))
        out["sims"] = [dict(id=self.ids[j], name=self.names[j], sim=round(float(sims[j]), 3))
                       for j in np.argsort(-sims, kind="stable")]
        chosen, w = select(sims, self.threshold, self.k, self.temperature)
        out["selected"] = [dict(id=self.ids[j], name=self.names[j], sim=round(float(sims[j]), 3),
                                weight=round(float(wj), 3), column=j) for j, wj in zip(chosen, w)]
        if not chosen:
            out["fallback"] = "no concept above the threshold"
            self.log_miss(query, residual, out["sims"][:3])
        return dict(out, ms=(time.perf_counter() - t) * 1000)

    def scores(self, selected, cand):
        cols = [s["column"] for s in selected]
        w = np.array([s["weight"] for s in selected])
        return np.nan_to_num(self.pct[cand][:, cols]) @ (w / w.sum())

    def product_scores(self, i, selected=None):
        cols = [s["column"] for s in selected] if selected is not None else range(len(self.ids))
        return [dict(name=self.names[j], score=int(self.raw[i, j])) for j in cols if not np.isnan(self.raw[i, j])]

    def log_miss(self, query, residual, top):
        record = dict(query=query, residual=residual, top=[dict(id=x["id"], sim=x["sim"]) for x in top],
                      date=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        with self.lock:
            self.misses.parent.mkdir(parents=True, exist_ok=True)
            with self.misses.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load(folder, meta, products, embedder, **settings):
    """None when the index has no concepts; exits when concepts.yaml changed since prepare.py."""
    info = meta.get("concepts")
    if not info:
        return None
    if file_hash(info["yaml"]) != info["yaml_sha256"]:
        raise SystemExit(f"{info['yaml']} changed since prepare.py; rerun prepare.py --concepts")
    if Path(info["scores"]).exists() and file_hash(info["scores"]) != info["scores_sha256"]:
        print("Note: concept scores changed since prepare.py; the index uses the old ones until it is rebuilt")
    return ConceptRanker(products, pd.read_parquet(Path(folder) / FILE), info, embedder, **settings)
