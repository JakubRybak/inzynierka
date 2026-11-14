"""
Weights of the sentence ranking of the search UI, fitted on the judge's grades of the dev queries. The score is
linear in the parts of the ranking (server.SENTENCE_PARTS). The weights come from a pairwise logistic regression: of
two judged products of a query with different grades, the one with the higher grade should score higher. Every query
counts the same, and a pair counts by the difference of its grades.

    python experiments/ranking/learn.py            # fit, print, write data/sentence_fold_weights.json
    python experiments/ranking/learn.py --write    # also write search_ui/ranking_data/sentence_weights.json

The fold weights are fitted FOLDS times, each time without the queries of one fold (evaluate.fold); evaluate.py
ranks every query with the weights that did not see it, so the metrics of "sentences" are out of fold. The weights
written for the search UI are fitted on all dev queries, with the full phrase bank.
"""
import argparse
from datetime import date
import json

import numpy as np
from sklearn.linear_model import LogisticRegression

import evaluate as ev
from evaluate import server

PAIRS = 4000  # at most this many pairs of a query, drawn with a fixed seed
FIRST = "description"  # the weights are scaled so that this part has weight 1


def pairs(X, g, cap=PAIRS, seed=0):
    """Difference vectors of the judged products with different grades, the higher grade first, and the difference
    of their grades."""
    i, j = np.nonzero(g[:, None] > g[None, :])
    if len(i) > cap:
        keep = np.random.default_rng(seed).choice(len(i), cap, replace=False)
        i, j = i[keep], j[keep]
    return X[i] - X[j], (g[i] - g[j]).astype(float)


def fit(data, names, C=1.0):
    """data: [({part: column}, grades with nan for an ungraded product)] -> {part: weight}."""
    D, W = [], []
    for parts, g in data:
        judged = ~np.isnan(g)
        if judged.sum() < 2:
            continue
        d, gap = pairs(np.column_stack([parts[k] for k in names])[judged], g[judged])
        if len(d):
            D.append(d)
            W.append(gap / len(d))
    D, W = np.vstack(D), np.concatenate(W)
    sign = np.where(np.arange(len(D)) % 2 == 0, 1.0, -1.0)
    model = LogisticRegression(C=C, fit_intercept=False, max_iter=2000)
    model.fit(D * sign[:, None], (sign > 0).astype(int), sample_weight=W * len(W))
    return dict(zip(names, model.coef_[0]))


def scaled(weights, first=None):
    first = first or next(iter(weights))
    return {k: round(float(v / weights[first]), 4) for k, v in weights.items()}


def grades_of(engine, q, grades):
    g = grades.get(q["id"], {})
    return np.array([g.get(engine.products[i]["product_id"], np.nan) for i in q["candidates"]], dtype=float)


def cross_fit(data, names, C=1.0):
    """data: {query id: (parts, grades)} -> (the weights fitted without each fold, the weights fitted on all)."""
    folds = [scaled(fit([d for i, d in data.items() if ev.fold(i) != k], names, C)) for k in range(ev.FOLDS)]
    return folds, scaled(fit(list(data.values()), names, C))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the weights the search UI ships")
    args = ap.parse_args()
    engines = ev.engines()
    queries = ev.load_queries(engines["bank"].products, engines["bank"].vocabulary, "dev")
    grades = ev.load_grades()
    names, out = [FIRST] + [k for k in server.SENTENCE_PARTS if k != FIRST], {}
    for key, engine in (("full", engines["bank"]), ("heldout", engines["bank_heldout"])):
        data = {q["id"]: (ev.sentence_parts(engine, q)[0], grades_of(engine, q, grades)) for q in queries}
        folds, everything = cross_fit(data, names)
        out[key] = dict(folds=folds, all=everything)
        print(f"\n{key} bank: weights fitted on all {len(queries)} dev queries, and their range over the {ev.FOLDS} folds")
        for k in names:
            values = [w[k] for w in folds]
            print(f"  {k:<13} {everything[k]:>8.3f}   folds {min(values):.3f} to {max(values):.3f}")
    judged = sum(len(grades.get(q["id"], {})) for q in queries)
    ev.FOLD_WEIGHTS.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n{judged} graded (query, product) pairs -> {ev.FOLD_WEIGHTS}")
    if args.write:
        record = dict(weights=out["full"]["all"],
                      fitted=dict(date=date.today().isoformat(), queries=len(queries), graded_pairs=judged,
                                  method="pairwise logistic regression, experiments/ranking/learn.py"))
        server.SENTENCE_WEIGHTS.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(f"weights of the search UI -> {server.SENTENCE_WEIGHTS}")


if __name__ == "__main__":
    main()
