"""
The rankings the evaluation compares the search UI with. The page no longer offers them, so they live here:
- text, image, combined and combined_features: the similarity of the whole query to the description, the main image,
  both (the mean of their z-scores) or both and the feature text;
- concepts: every residual phrase takes the concept with the most similar name, when the cosine reaches THRESHOLD,
  and the candidates are ranked by the scores of these concepts (divided by 10), combined over the phrases with the
  geometric mean; combined breaks ties, and orders the candidates when no phrase takes a concept;
- bank: every residual phrase, routed by the phrase bank (bank.py), gives one column of percentiles within the
  candidates: its concept scores (an occasion, style or season), the closeness of the candidates' colours (a shade),
  their details, or text signals (TF-IDF and the similarity of the phrase to the descriptions and images), inverted
  when negated; a phrase with no signal of its own takes the similarity of the whole query. The columns are combined
  with a soft AND (geometric mean); combined, with the image counted twice when the query asks for a colour, breaks
  ties.
"""
import sys
from pathlib import Path

import numpy as np

SEARCH_UI = Path(__file__).resolve().parents[2] / "search_ui"
sys.path[:0] = [str(SEARCH_UI), str(SEARCH_UI / "core")]
import bank  # noqa: E402
import common  # noqa: E402
import concepts  # noqa: E402
import server  # noqa: E402

EMBEDDING = ("text", "image", "combined", "combined_features")
THRESHOLD = 0.72  # cosine of a phrase and a concept name
COMBINE = {"geo": lambda s: np.prod(s, axis=1) ** (1 / s.shape[1]),
           "mean": lambda s: s.mean(axis=1),
           "min": lambda s: s.min(axis=1)}
CONCEPT_WEIGHT = 2.0  # a concept matched by name, against 1 for the text signals
FLOOR = 0.01  # keeps a single weak phrase from zeroing a product in the soft AND


def query_vectors(engine, q):
    """The normalized embeddings of the query: "t" for the descriptions and feature texts, "i" for the images."""
    return {k: common.normalize(f.result()) for k, f in engine.query_vectors(q).items()}


def embedding(engine, v, ranking, cand, image_weight=1.0):
    """The score of an embedding ranking of EMBEDDING. v: query_vectors(); image_weight: how much the image counts
    against the description (and the features)."""
    s_t, s_i = engine.T[cand] @ v["t"], engine.I[cand] @ v["i"]
    mask = engine.has_image[cand]
    if ranking == "text":
        return s_t
    if ranking == "image":
        return np.where(mask, s_i, -1.0)
    everyone = np.ones(len(cand), bool)
    shares = [server._z(s_t, everyone), image_weight * server.image_z(s_i, mask)]
    if ranking == "combined_features":
        shares.append(server._z(engine.F[cand] @ v["t"], everyone))
    return sum(shares) / (len(shares) - 1 + image_weight)


class ConceptRanking:
    def __init__(self, data, info, embedder, threshold=THRESHOLD, combine="geo"):
        """data: concepts.Concepts; info: the concepts of the index metadata (meta.json)."""
        self.data, self.embedder, self.threshold, self.combine = data, embedder, threshold, combine
        self.allowed = {c: np.array([v is None or i in v for i in data.ids])
                        for c, v in concepts.scored_concepts(info).items()}

    def match(self, residual, category):
        """The columns of the concepts the phrases take, at most one per phrase, among the concepts scored in the
        category."""
        if category not in self.allowed:
            return []
        columns = []
        for phrase in residual:
            v = common.normalize(np.asarray(self.embedder(common.query_text(phrase)), np.float32))
            sims = np.where(self.allowed[category], self.data.E @ v, -np.inf)
            j = int(np.argmax(sims))
            if sims[j] >= self.threshold:
                columns.append(j)
        return columns

    def rank(self, residual, category, cand, combined):
        """-> (score, tie-breaker or None); combined orders the candidates when no phrase takes a concept."""
        columns = self.match(residual, category)
        if not columns:
            return combined, None
        return COMBINE[self.combine](np.nan_to_num(self.data.raw[cand][:, columns] / 10)), combined


def own_signal(r):
    """The bank scores a phrase itself only when it knows something about it: its concepts, a negation, a shade or
    detail names. Any other phrase (a theme, an unknown phrase) is better judged by the whole query."""
    return bool(r["concepts"]) or r["negated"] or r["kind"] == "shade" or bool(r.get("detail"))


def phrase_column(b, r, cand, vectors):
    """Percentiles of one phrase within the candidates, or None for a phrase that gives no signal. b: the bank."""
    if r["skipped"]:
        return None
    colour = b.colour_score(r, cand)
    if colour is not None:
        return 1 - colour if r["negated"] else colour
    detail = b.detail_raw(r, cand)
    # an occasion, style or season phrase with concepts scored here uses only its concept scores
    text_signals = not (r["kind"] in bank.ABSTRACT and r["concepts"])
    parts = [(1.0, bank.percentiles(detail))] if detail is not None else \
        [(1.0, b.text_score(r["english"], cand, vectors, b.image_weight(r)))] if text_signals else []
    if r["concepts"]:
        raw = b.concepts[cand][:, [b.concept_column[c] for c in r["concepts"]]].mean(axis=1)
        parts.append((CONCEPT_WEIGHT if parts and r["match"] == "concept" else 1.0, bank.percentiles(raw)))
    if not parts:
        return None
    p = sum(w * s for w, s in parts) / sum(w for w, _ in parts)
    return 1 - p if r["negated"] else p


def soft_and(columns):
    """Geometric mean of per-phrase scores in [0, 1]."""
    s = np.clip(np.column_stack(columns), FLOOR, 1.0)
    return np.exp(np.log(s).mean(axis=1))


def bank_rank(b, residual, cand, category, query, whole_query):
    """-> (score, routes) of the bank ranking. b: the bank; whole_query(routes) -> the similarity of the whole query
    to the candidates."""
    residual = [p for p in residual if bank.normalize_phrase(p)]
    vectors = b.embed(residual, query)
    routes = [b.route(p, category, vectors.get(common.query_text(bank.normalize_phrase(p))), query, vectors)
              for p in residual]
    columns, whole = [], None
    for r in routes:
        if not r["skipped"] and not own_signal(r):
            whole = bank.percentiles(whole_query(routes)) if whole is None else whole
            columns.append(whole)
        else:
            c = phrase_column(b, r, cand, vectors)
            if c is not None:
                columns.append(c)
    return (soft_and(columns) if columns else np.zeros(len(cand))), routes
