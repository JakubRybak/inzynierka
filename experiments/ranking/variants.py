"""
The ranking variants tried on the way to the sentence ranking, each as one named ranking in data/runs.jsonl, so
that evaluate.py reports them in the same table as the rankings of the search UI. A variant is a linear score over
signal columns, with fixed weights or with weights fitted like the sentence ranking (learn.py) and applied out of
fold. Embeddings come from the disk cache of evaluate.py.

    python experiments/ranking/variants.py                 # all variants -> data/runs.jsonl, data/pool.jsonl
    python experiments/ranking/variants.py --only v_soft   # the variants whose name starts so

Columns of a query (z-scored within its candidates unless said otherwise):
- text, image, features: similarity of the whole query to the description, image and feature text;
- image_colour: the image column when the hybrid ranking reads a colour in the query;
- concept, colour, detail, negation: the phrase terms of the hybrid ranking, summed over the phrases;
- lean_*: the parts of the sentence ranking (server.SENTENCE_PARTS), where the phrase bank is used without the
  colour and detail routes; lean_image_colour: the image column when the query has a colour filter or a phrase the
  bank reads as a shade;
- soft_colour, soft_detail, soft_concept: soft.py, raw values;
- phrase_z: the best sentence of every phrase as a z-score, not as the excess over the phrase's median;
- phrase_image, phrase_text, phrase_lex: every phrase against the image, the description and TF-IDF;
- filter_colour, filter_material: the share of a candidate's colours in the colour families of a colour filter
  (minus the share of an excluded family), and the share of a required material in its composition;
- q_name, q_best: the whole query against the name and against the single best sentence;
- phrase_both, phrase_one: the best sentence of every phrase that is not skipped, and only of the phrases that got
  no concept term.
"""
import argparse

import numpy as np
from sklearn.linear_model import LogisticRegression

import evaluate as ev
from evaluate import bank, common, server
from lab import Lab, save_runs, z
import learn
import soft

HYBRID_WEIGHTS = dict(server.HYBRID)
LEAN = ["lean_" + k for k in server.SENTENCE_PARTS]
HYBRID_TERMS = ["text", "image", "features", "image_colour", "concept", "colour", "detail", "negation"]


def columns(lab, softly, q, heldout=False):
    s = lab.signals(q, heldout)
    engine = lab.heldout if heldout else lab.engine
    cand, n = s["cand"], len(s["cand"])
    parts, routes = ev.sentence_parts(engine, q)
    c = {"lean_" + k: v for k, v in parts.items()}
    z_i = z(s["i"], s["mask"])
    if s["mask"].any():
        z_i[~s["mask"]] = z_i[s["mask"]].min() - 1
    c["lean_image_colour"] = z_i * float(server.asks_colour(q["filters"], routes))
    terms = engine.bank.sentence_terms(q["residual"], cand, q["category"], query=q["query"])[0]
    with_concept = {phrase for term, phrase, _ in terms if term == "concept"}
    c["phrase_both"] = sum((column for term, _, column in terms if term == "sentence"), np.zeros(n))
    c["phrase_one"] = sum((column for term, phrase, column in terms if term == "sentence" and phrase not in with_concept),
                          np.zeros(n))
    c |= dict(text=z(s["t"]), image=z_i, features=z(s["f"]), image_colour=z_i * float(s["asks_colour"]))
    for kind in ("concept", "colour", "detail", "negation"):
        c[kind] = sum((column for r, column in s["terms"] if r["term"] == kind), np.zeros(n))
    extra = {k: np.zeros(n) for k in ("soft_colour", "soft_detail", "soft_concept", "phrase_z", "phrase_image",
                                      "phrase_text", "phrase_lex")}
    sentences = engine.sentences
    for r in routes:
        if r["skipped"]:
            continue
        text = bank.bare_phrase(bank.normalize_phrase(r["phrase"]))
        v, plain, sign = lab.vector(common.query_text(text)), lab.vector(text), -1 if r["negated"] else 1
        extra["soft_colour"] += sign * softly.colour(v, cand)
        extra["soft_detail"] += sign * softly.detail(v, cand)
        extra["soft_concept"] += sign * softly.concept(v, cand)
        extra["phrase_z"] += sign * z(np.append(sentences.similarity(v), -1.0)[sentences.rows[cand]].max(axis=1))
        extra["phrase_image"] += sign * z(engine.I[cand] @ plain, s["mask"])
        extra["phrase_text"] += sign * z(engine.T[cand] @ v)
        lex = engine.bank.tfidf.transform([text])
        extra["phrase_lex"] += sign * z((engine.bank.tfidf_matrix[cand] @ lex.T).toarray().ravel())
    colour, material = np.zeros(n), np.zeros(n)
    for f in q["filters"]:
        values = f.get("values") or []
        if f.get("feature") == "colors":
            share = (softly.colours.share[cand] * np.isin(softly.colours.family[cand], values)).sum(axis=1)
            colour += share if f.get("operator") in server.POSITIVE else -share
        if f.get("feature") == "main_composition" and f.get("operator") in server.POSITIVE:
            material += np.array([sum((engine.products[i]["features"].get("main_composition") or {}).get(m, 0)
                                      for m in values) for i in cand]) / 100
    sims = np.append(sentences.similarity(lab.vector(common.query_text(q["query"]))), -1.0)
    return c | extra | dict(filter_colour=z(colour), filter_material=z(material), q_name=z(sims[sentences.rows[cand][:, 0]]),
                            q_best=z(sims[sentences.rows[cand]].max(axis=1)))


def hybrid(lab, q, heldout=False, weights=HYBRID_WEIGHTS, features=True, image_boost=True):
    """The hybrid score of the search UI with other weights, without the features in its base, or without the
    image counting twice in a colour query."""
    s = lab.signals(q, heldout)
    score = lab.combined(s, features=features,
                         image_weight=server.COLOUR_IMAGE_WEIGHT if s["asks_colour"] and image_boost else 1.0)
    for r, column in s["terms"]:
        score = score + (-1 if r["term"] == "negation" else 1) * weights.get(r["term"], 0.0) * column
    return score


def lambda_pairs(X, g, scores, cap=learn.PAIRS, seed=0):
    """Pairs of judged products with different grades, weighted as in LambdaRank: by how much nDCG changes when the
    two swap their places in the order given by the scores."""
    order = np.argsort(-scores, kind="stable")
    rank = np.empty(len(scores), int)
    rank[order] = np.arange(len(scores))
    judged = np.flatnonzero(~np.isnan(g))
    if len(judged) < 2:
        return None
    gain, discount = 2.0 ** g[judged] - 1, 1 / np.log2(rank[judged] + 2)
    ideal = (np.sort(gain)[::-1] / np.log2(np.arange(len(gain)) + 2)).sum()
    i, j = np.nonzero(g[judged][:, None] > g[judged][None, :])
    if not len(i) or ideal == 0:
        return None
    weight = np.abs((gain[i] - gain[j]) * (discount[i] - discount[j])) / ideal
    if len(i) > cap:
        keep = np.random.default_rng(seed).choice(len(i), cap, replace=False)
        i, j, weight = i[keep], j[keep], weight[keep] * len(i) / cap
    return X[judged][i] - X[judged][j], weight


def fit_lambda(data, names, rounds=4):
    """The pairwise fit of learn.py, refitted `rounds` times with LambdaRank weights from its own scores."""
    w = learn.fit(data, names)
    for _ in range(rounds):
        D, W = [], []
        for parts, g in data:
            X = np.column_stack([parts[k] for k in names])
            out = lambda_pairs(X, g, X @ np.array([w[k] for k in names]))
            if out is not None:
                D.append(out[0])
                W.append(out[1])
        D, W = np.vstack(D), np.concatenate(W)
        sign = np.where(np.arange(len(D)) % 2 == 0, 1.0, -1.0)
        model = LogisticRegression(fit_intercept=False, max_iter=2000)
        model.fit(D * sign[:, None], (sign > 0).astype(int), sample_weight=W / W.mean())
        w = dict(zip(names, model.coef_[0]))
    return w


def fit_ascent(lab, data, ids, names, start, steps=(0.5, 0.75, 1.33, 2.0), rounds=3):
    """Coordinate ascent on the mean nDCG@K of the queries ids (an ungraded product counts as 0): every weight but
    the first in turn is multiplied by each step, and the best value is kept."""
    def quality(w):
        values = [ev.metrics(lab.top(lab.by_id[i], sum(w[k] * data[i][0][k] for k in names)),
                             lab.grades.get(i, {}))["ndcg"] for i in ids]
        return float(np.mean([v for v in values if v is not None]))

    w, best = dict(start), quality(start)
    for _ in range(rounds):
        improved = False
        for k in names[1:]:
            for step in steps:
                trial = dict(w, **{k: w[k] * step})
                value = quality(trial)
                if value > best + 1e-5:
                    w, best, improved = trial, value, True
        if not improved:
            break
    return w


def fixed(weights):
    return dict(weights=weights)


def fitted(names, how="logistic"):
    return dict(names=names, how=how)


BOTH = "both banks"
VARIANTS = {
    # the hybrid ranking with one part changed
    "v_hybrid_no_features": dict(hybrid=dict(features=False)),
    "v_hybrid_no_image_boost": dict(hybrid=dict(image_boost=False)),
    "v_hybrid_colour_w0.5": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, colour=0.5))),
    "v_hybrid_concept_w0": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, concept=0.0))),
    "v_hybrid_concept_w1": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, concept=1.0))),
    "v_hybrid_detail_w1": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, detail=1.0))),
    "v_hybrid_filter_fit": dict(hybrid={}, plus=dict(filter_colour=0.5, filter_material=0.5)),
    # soft matching instead of the thresholds of one term
    "v_soft_detail": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, detail=0.0)), plus=dict(soft_detail=4.0)),
    "v_soft_colour": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, colour=0.0)), plus=dict(soft_colour=4.0)),
    "v_soft_concept": dict(hybrid=dict(weights=dict(HYBRID_WEIGHTS, concept=0.0)), plus=dict(soft_concept=4.0)),
    # the sentence term of every phrase added to the hybrid ranking: as z-scores, and with larger weights
    "v_hybrid_sentence_z0.25": dict(hybrid={}, plus=dict(phrase_z=0.25)),
    "v_hybrid_sentence_z0.5": dict(hybrid={}, plus=dict(phrase_z=0.5)),
    "v_hybrid_sentence_w8": dict(hybrid={}, plus=dict(lean_phrase=8.0)),
    "v_hybrid_sentence_w16": dict(hybrid={}, plus=dict(lean_phrase=16.0)),
    # fitted weights over the signals of the hybrid ranking, then with the sentence signals
    "v_fitted_hybrid": fitted(HYBRID_TERMS) | {BOTH: True},
    "v_fitted_hybrid_lambda": fitted(HYBRID_TERMS, "lambda"),
    "v_fitted_hybrid_ascent": fitted(HYBRID_TERMS, "ascent"),
    "v_fitted_hybrid_phrase": fitted(HYBRID_TERMS + ["lean_phrase"]) | {BOTH: True},
    "v_fitted_hybrid_sentences": fitted(HYBRID_TERMS + ["lean_phrase", "lean_sentences"]) | {BOTH: True},
    # the sentence ranking with a part left out, changed or added
    "v_lean_hand_weights": fixed(dict(lean_description=1, lean_image=1, lean_features=1, lean_image_colour=1,
                                      lean_concept=1.5, lean_phrase=12)) | {BOTH: True},
    "v_lean_no_whole_query": fitted([k for k in LEAN if k != "lean_sentences"]) | {BOTH: True},
    "v_lean_no_phrase": fitted([k for k in LEAN if k != "lean_phrase"]),
    "v_lean_no_sentences": fitted([k for k in LEAN if k not in ("lean_phrase", "lean_sentences")]),
    "v_lean_no_features": fitted([k for k in LEAN if k != "lean_features"]) | {BOTH: True},
    "v_lean_no_concept": fitted([k for k in LEAN if k != "lean_concept"]),
    "v_lean_best_sentence": fitted(["q_best" if k == "lean_sentences" else k for k in LEAN]),
    "v_lean_image_colour": fitted(LEAN + ["lean_image_colour"]) | {BOTH: True},
    "v_lean_soft_colour": fitted(LEAN + ["soft_colour"]) | {BOTH: True},
    "v_lean_soft_concept": fitted([k for k in LEAN if k != "lean_concept"] + ["soft_concept"]),
    "v_lean_filter_fit": fitted(LEAN + ["filter_colour", "filter_material"]),
    "v_lean_phrase_image": fitted(LEAN + ["phrase_image"]),
    "v_lean_phrase_text": fitted(LEAN + ["phrase_text"]),
    "v_lean_phrase_lex": fitted(LEAN + ["phrase_lex"]),
    "v_lean_name": fitted(LEAN + ["q_name"]),
    "v_lean_lambda": fitted(LEAN, "lambda"),
    # the best sentence for every phrase, also one with concepts; and only for a phrase without concepts
    "v_lean_phrase_both": fitted(LEAN[:-1] + ["phrase_both"]) | {BOTH: True},
    "v_lean_phrase_one": fitted(LEAN[:-1] + ["phrase_one"]) | {BOTH: True},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--only", help="only the variants whose name starts with this")
    args = ap.parse_args()
    lab = Lab()
    softly = soft.Soft(lab.engine)
    chosen = {k: v for k, v in VARIANTS.items() if not args.only or k.startswith(args.only)}
    C = {h: {q["id"]: columns(lab, softly, q, h) for q in lab.queries} for h in (False, True)}
    G = {q["id"]: learn.grades_of(lab.engine, q, lab.grades) for q in lab.queries}
    ids, runs = [q["id"] for q in lab.queries], {}
    for name, spec in chosen.items():
        for h in ((False, True) if spec.get(BOTH) else (False,)):
            key, tops = name + ("_heldout" if h else ""), {}
            if "names" in spec:
                names, data = spec["names"], {i: (C[h][i], G[i]) for i in ids}
                shown = []
                for k in range(ev.FOLDS):
                    train = [data[i] for i in ids if ev.fold(i) != k]
                    if spec["how"] == "lambda":
                        w = fit_lambda(train, names)
                    else:
                        w = learn.fit(train, names)
                        if spec["how"] == "ascent":
                            w = fit_ascent(lab, data, [i for i in ids if ev.fold(i) != k], names, w)
                    shown.append(learn.scaled(w))
                    for i in ids:
                        if ev.fold(i) == k:
                            tops[i] = lab.top(lab.by_id[i], sum(w[c] * C[h][i][c] for c in names))
                print(key, {c: round(float(np.mean([w[c] for w in shown])), 2) for c in names})
            else:
                for q in lab.queries:
                    score = hybrid(lab, q, h, **spec["hybrid"]) if "hybrid" in spec else np.zeros(q["n"])
                    for c, w in (spec.get("plus") or spec.get("weights") or {}).items():
                        score = score + w * C[h][q["id"]][c]
                    tops[q["id"]] = lab.top(q, score)
            runs[key] = tops
            print(key, lab.summary(tops))
    save_runs(lab, runs)
    print(f"{len(runs)} rankings -> {ev.RUNS}")


if __name__ == "__main__":
    main()
