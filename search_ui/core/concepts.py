"""
Concepts: a score from 0 to 10 of every product for each concept (ranking_data/concept_scores.parquet, given offline
by Gemini, offline/score_concepts.py) and the embeddings of the concept names. prepare.py puts the scores into the
index as concept__<id> columns and the names with their embeddings into data/concepts.parquet. At search time the
phrase bank (bank.py) gives a residual phrase its concepts, and the page shows the scores of a product.

A concept is used in a category only when every indexed product of the category has its score.
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import common

RANKING = common.SEARCH_UI / "ranking_data"
CONCEPTS_YAML = RANKING / "concepts.yaml"
SCORES = RANKING / "concept_scores.parquet"
NAMES = RANKING / "concept_names.parquet"
FILE = "concepts.parquet"
PREFIX = "concept__"


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


class Concepts:
    def __init__(self, products, rows):
        """rows: the concepts with their name embeddings (data/concepts.parquet)."""
        self.ids, self.names = list(rows["id"]), list(rows["name"])
        self.E = common.normalize(np.stack([np.asarray(e, np.float32) for e in rows["embedding"]]))
        self.raw = np.array([[p.get(PREFIX + i, np.nan) for i in self.ids] for p in products], dtype=float)

    def product_scores(self, i, columns=None):
        """The scores of product i, of the given concept columns or of all."""
        cols = dict.fromkeys(columns) if columns is not None else range(len(self.ids))
        return [dict(name=self.names[j], score=int(self.raw[i, j])) for j in cols if not np.isnan(self.raw[i, j])]


def load(folder, meta, products):
    """None when the index has no concepts; exits when concepts.yaml changed since prepare.py."""
    info = meta.get("concepts")
    if not info:
        return None
    if file_hash(info["yaml"]) != info["yaml_sha256"]:
        raise SystemExit(f"{info['yaml']} changed since prepare.py; rerun prepare.py")
    if Path(info["scores"]).exists() and file_hash(info["scores"]) != info["scores_sha256"]:
        print("Note: concept scores changed since prepare.py; the index uses the old ones until it is rebuilt")
    return Concepts(products, pd.read_parquet(Path(folder) / FILE))
