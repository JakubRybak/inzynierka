"""
Sentence signal of the ranking. A product is read as a list of short texts: its name and the sentences of its
description ("Two-button placket at front.", "Velcro tabs at cuffs."). Every unique one is embedded verbatim, like the
descriptions themselves (prepare.py), and kept in its first DIM dimensions. Two scores come from them:
- whole(): how well the whole query matches the TOP most similar sentences of a candidate;
- phrase(): how well one residual phrase matches the best sentence of a candidate. The similarity counts only by how
  far it is above the phrase's typical similarity to a sentence (its median over all sentences), so a phrase that no
  sentence speaks about ("for a funeral") adds almost nothing, without a threshold.
"""
from concurrent.futures import ThreadPoolExecutor
import html
import re

import numpy as np

import common

VECTORS = "sentence_embeddings.npz"
DIM = 768  # measured on the dev queries: the ranking is as good with 768 dimensions as with all 3072
TOP = 2


def clean(text):
    """Plain text: HTML entities resolved, tags such as <br> turned into spaces, so that they end a sentence, and
    the replacement character of a lost accent (in "piqu\ufffd") read as e."""
    return re.sub(r"<[^>]*>", " ", html.unescape(str(text or ""))).replace("\ufffd", "e").strip()


def split(p):
    """The name of a product and the sentences of its description."""
    return [clean(p["name"])] + [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean(p.get("description"))) if s.strip()]


def shorten(vectors):
    """Unit vectors of the first DIM dimensions."""
    return common.normalize(np.asarray(vectors, np.float32)[..., :DIM])


def embed(products, embed_one, folder, workers=24, step=4000):
    """Embeds the sentences missing from folder/VECTORS (one API call each) and saves all of them, a part at a time.
    -> (number of unique sentences, number of new calls)."""
    path = folder / VECTORS
    texts = list(dict.fromkeys(s for p in products for s in split(p)))
    known = {}
    if path.exists():
        stored = np.load(path)
        known = dict(zip(stored["texts"].tolist(), stored["vectors"]))
    missing = [t for t in texts if t not in known]
    for start in range(0, len(missing), step):
        part = missing[start:start + step]
        with ThreadPoolExecutor(workers) as pool:
            known.update(zip(part, (shorten(v).astype(np.float16) for v in pool.map(embed_one, part))))
        done = [t for t in texts if t in known]
        np.savez(path, texts=np.array(done), vectors=np.stack([known[t] for t in done]))
    if not missing and len(known) != len(texts):
        np.savez(path, texts=np.array(texts), vectors=np.stack([known[t] for t in texts]))
    return len(texts), len(missing)


class Sentences:
    def __init__(self, products, texts, vectors):
        row = {t: i for i, t in enumerate(texts)}
        rows = [[row[s] for s in split(p)] for p in products]
        width = max(map(len, rows))
        self.rows = np.array([r + [-1] * (width - len(r)) for r in rows])
        self.count = (self.rows >= 0).sum(axis=1)
        self.E = common.normalize(np.asarray(vectors, np.float32))

    def similarity(self, vector):
        """Similarity of a query-format embedding to every sentence."""
        return self.E @ shorten(vector)

    def whole(self, vector, cand):
        """Mean similarity of the query to the TOP most similar sentences of each candidate."""
        best = -np.sort(-np.append(self.similarity(vector), -1.0)[self.rows[cand]], axis=1)
        return np.where(self.count[cand] >= TOP, best[:, :TOP].mean(axis=1), best[:, 0])

    def phrase(self, vector, cand):
        """Each candidate's best sentence for a phrase: its similarity above the phrase's median over all
        sentences, 0 when below."""
        sims = self.similarity(vector)
        return np.append(np.maximum(sims - np.median(sims), 0), 0.0)[self.rows[cand]].max(axis=1)


def load(products, folder=common.DATA):
    """The sentences of the products, or None when prepare.py did not embed them all."""
    path = folder / VECTORS
    if not path.exists():
        return None
    stored = np.load(path)
    texts = stored["texts"].tolist()
    known = set(texts)
    if not all(s in known for p in products for s in split(p)):
        return None
    return Sentences(products, texts, stored["vectors"])
