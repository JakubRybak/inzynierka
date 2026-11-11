"""
Concept ranking: offline 0-10 scores per (product, concept) from Gemini, from the product images and text, and
embeddings of the concept names. At query time every residual phrase is embedded and compared with the concept
names; a phrase takes its most similar concept when the similarity reaches the threshold. A product's scores of
these concepts, divided by 10, are combined over the phrases with the geometric mean (default), the mean or the
minimum.

A concept is used in a category only when every indexed product of the category has its score; a phrase whose
concept is not scored there, or a category without any, is ranked by the combined embedding similarity.
"""
from concurrent.futures import ThreadPoolExecutor
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

RANKING = common.SEARCH_UI / "ranking_data"
CONCEPTS_YAML = RANKING / "concepts.yaml"
SCORES = RANKING / "concept_scores.parquet"
NAMES = RANKING / "concept_names.parquet"
MISSES = common.DATA / "misses.jsonl"
FILE = "concepts.parquet"
PREFIX = "concept__"
COMBINE = {"geo": lambda s: np.prod(s, axis=1) ** (1 / s.shape[1]),
           "mean": lambda s: s.mean(axis=1),
           "min": lambda s: s.min(axis=1)}


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_list(path=CONCEPTS_YAML):
    return [dict(id=c["id"], name=c["name"], type=c["type"]) for c in yaml.safe_load(Path(path).read_text(encoding="utf-8"))]


def build(index, concept_list, scores, names, embed):
    """Index DataFrame + long scores -> (index with concept__<id> raw score columns, concept rows with embeddings,
    {category: concept ids every product of the category has a score of}, {category: [scored concepts, concepts]}
    for categories with only some concepts). Name embeddings come from `names` (id, name, embedding); a concept
    missing there is embedded with `embed` (one API call)."""
    ids = [c["id"] for c in concept_list]
    s = scores[scores["product_id"].isin(set(index["product_id"])) & scores["concept_id"].isin(ids)]
    wide = s.pivot(index="product_id", columns="concept_id", values="score").reindex(index=index["product_id"], columns=ids)
    present = wide.notna().to_numpy()
    scored, partial = {}, {}
    for category, rows in index.groupby("category").groups.items():
        full = [c for c, ok in zip(ids, present[np.asarray(rows)].all(axis=0)) if ok]
        if full:
            scored[category] = full
        if 0 < len(full) < len(ids):
            partial[category] = [len(full), len(ids)]
    index = index.assign(**{PREFIX + i: wide[i].to_numpy(dtype=float) for i in ids})
    known = {r.id: r for r in names.itertuples()} if names is not None else {}
    rows = []
    for c in concept_list:
        stored = known.get(c["id"])
        vector = stored.embedding if stored is not None and stored.name == c["name"] else embed(c["name"])
        rows.append(dict(c, embedding=common.normalize(np.asarray(vector, np.float32)).tolist()))
    return index, pd.DataFrame(rows), dict(sorted(scored.items())), partial


def scored_concepts(info):
    """{category: set of usable concept ids} from the index metadata; older indexes list only complete categories."""
    if info.get("scored") is not None:
        return {c: set(v) for c, v in info["scored"].items()}
    return {c: None for c in info.get("categories", [])}


class ConceptRanker:
    def __init__(self, products, rows, info, embedder, threshold, combine="geo", misses=MISSES):
        self.ids, self.names = list(rows["id"]), list(rows["name"])
        self.E = common.normalize(np.stack([np.asarray(e, np.float32) for e in rows["embedding"]]))
        self.raw = np.array([[p.get(PREFIX + i, np.nan) for i in self.ids] for p in products], dtype=float)
        scored = scored_concepts(info)
        self.allowed = {c: np.array([v is None or i in v for i in self.ids]) for c, v in scored.items()}
        self.categories = set(self.allowed)
        self.embedder, self.threshold, self.combine = embedder, threshold, combine
        self.pool = ThreadPoolExecutor(4)
        self.misses, self.lock = Path(misses), threading.Lock()

    def match(self, residual, category, query):
        """Embeds every residual phrase and picks its concept; called once per query, nothing is stored except
        misses. "selected" lists the concepts of the matched phrases, each with the index of its phrase."""
        t = time.perf_counter()
        out = dict(residual=residual, threshold=self.threshold, combine=self.combine, phrases=[], selected=[])
        if not residual:
            return dict(out, fallback="empty residual", ms=0.0)
        if category not in self.categories:
            return dict(out, fallback=f"no concept scores for {category}", ms=0.0)
        vectors = self.pool.map(lambda phrase: self.embedder(common.query_text(phrase)), residual)
        for i, (phrase, v) in enumerate(zip(residual, vectors)):
            sims = self.E @ common.normalize(np.asarray(v, np.float32))
            order = [j for j in np.argsort(-sims, kind="stable") if self.allowed[category][j]]
            part = dict(text=phrase, sims=[dict(id=self.ids[j], name=self.names[j], sim=round(float(sims[j]), 3))
                                           for j in order], selected=[])
            j = int(order[0])
            if sims[j] >= self.threshold:
                part["selected"] = [dict(id=self.ids[j], name=self.names[j], sim=round(float(sims[j]), 3), column=j,
                                         phrase=i)]
            else:
                part["fallback"] = "no concept above the threshold"
                self.log_miss(query, phrase, part["sims"][:3])
            out["phrases"].append(part)
            out["selected"] += part["selected"]
        if not out["selected"]:
            out["fallback"] = "no concept above the threshold"
        return dict(out, ms=(time.perf_counter() - t) * 1000)

    def scores(self, selected, cand):
        return COMBINE[self.combine](np.nan_to_num(self.raw[cand][:, [s["column"] for s in selected]] / 10))

    def product_scores(self, i, columns=None):
        cols = dict.fromkeys(columns) if columns is not None else range(len(self.ids))
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
