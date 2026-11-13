"""
Detail signal of the phrase bank. Every product has the details Gemini saw in its name, description and photos, each
with an extent (ranking_data/product_details.parquet, from offline/product_details.py); their names form the detail
dictionary. A phrase gets the name most similar to it, when the similarity reaches MATCH, and with it every name
close to that name (NEIGHBOUR), so that "with graphic" also finds "bunny graphic" and "with buckle" finds "buckles":
the similarity between two names is steadier than between a phrase and a name. Each name weighs by its closeness:
1 for the most similar name, 0.5 at NEIGHBOUR. A candidate scores by its best detail among them: the extent times
the weight of the name.
"""
import numpy as np
import pandas as pd

import common

PRODUCTS = common.SEARCH_UI / "ranking_data/product_details.parquet"
VECTORS = "detail_embeddings.npz"
MATCH = 0.80  # chosen on the phrase bank: 58% of its detail phrases and 5% of its "other" phrases reach it
NEIGHBOUR = 0.82  # names of one detail: "graphic" reaches 167 of the 189 "... graphic" names, "lace" 25 lace names
EXTENT = {"all-over": 1.0, "part": 0.7, "small": 0.4}


def names(frame):
    """Detail names, the most frequent first."""
    return list(frame["name"].value_counts().index)


def embed_names(names_, embed, folder):
    """Embeddings of the detail names (query format) in folder/VECTORS; only new names are embedded."""
    return common.embed_texts(list(names_), [common.query_text(n) for n in names_], embed, folder / VECTORS)


class Details:
    def __init__(self, products, frame, names_, vectors):
        index = {p["product_id"]: i for i, p in enumerate(products)}
        self.names = list(names_)
        column = {n: j for j, n in enumerate(self.names)}
        self.W = np.zeros((len(products), len(self.names)), np.float32)
        self.listed = {}
        for r in frame.sort_values(["product_id", "rank"]).itertuples():
            i, j = index.get(r.product_id), column.get(r.name)
            if i is not None and j is not None:
                self.W[i, j] = max(self.W[i, j], EXTENT[r.extent])
                self.listed.setdefault(i, []).append((r.name, r.extent))
        self.E = common.normalize(np.asarray(vectors, np.float32))

    def target(self, vector):
        """The detail names a phrase asks for, the closest first, or None when no name reaches MATCH."""
        if vector is None:
            return None
        sims = self.E @ vector
        b = int(np.argmax(sims))
        if sims[b] < MATCH:
            return None
        # closeness to the phrase's most similar name, or to the phrase itself
        closeness = np.maximum(self.E @ self.E[b], sims)
        chosen = np.flatnonzero((closeness >= NEIGHBOUR) | (sims >= MATCH))
        chosen = chosen[np.argsort(-closeness[chosen], kind="stable")]
        weights = 0.5 + 0.5 * np.clip((closeness[chosen] - NEIGHBOUR) / (1 - NEIGHBOUR), 0, 1)
        return dict(names=[self.names[j] for j in chosen], columns=chosen.tolist(),
                    weights=[round(float(w), 3) for w in weights], similarity=round(float(sims[b]), 3))

    def score(self, target, cand):
        """Each candidate's best detail among the target names: its extent times the weight of the name, 0 without
        one."""
        return (self.W[np.ix_(cand, target["columns"])] * np.asarray(target["weights"], np.float32)).max(axis=1)

    def of_product(self, i):
        """The details of product i as Gemini listed them: [(name, extent)]."""
        return self.listed.get(i, [])


def load(products, folder=common.DATA):
    """Details of the products, or None when the details or the name embeddings (prepare.py) are missing."""
    if not (PRODUCTS.exists() and (folder / VECTORS).exists()):
        return None
    frame = pd.read_parquet(PRODUCTS)
    names_ = names(frame)
    stored = np.load(folder / VECTORS)
    known = dict(zip(stored["ids"].tolist(), stored["vectors"]))
    if not all(n in known for n in names_):
        return None
    return Details(products, frame, names_, np.stack([known[n] for n in names_]))
