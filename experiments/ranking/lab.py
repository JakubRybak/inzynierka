"""
Workbench of the ranking experiments: the dev queries with their candidates, every signal of the search UI as a raw
column over the candidates, and the metrics of any score against the judge's grades. Embeddings come from the disk
cache, so everything after the first run is local.

    from lab import Lab
    lab = Lab()
    s = lab.signals(lab.queries[0])
"""
from collections import defaultdict
import json

import evaluate as ev
from evaluate import bank, common, server
import numpy as np


def z(x, mask=None):
    """z-scores within the candidates; a constant column gives zeros. mask: the candidates the mean and deviation
    are taken over."""
    x = np.asarray(x, dtype=float)
    m = x if mask is None else x[mask]
    s = m.std() if m.size else 0
    return (x - m.mean()) / s if s > 0 else np.zeros_like(x)


class Lab:
    def __init__(self, split="dev"):
        self.engines = ev.engines()
        self.engine, self.heldout = self.engines["bank"], self.engines["bank_heldout"]
        self.embedder = self.engine.embedder
        self.queries = ev.load_queries(self.engine.products, self.engine.vocabulary, split)
        self.by_id = {q["id"]: q for q in self.queries}
        self.pid = np.array([p["product_id"] for p in self.engine.products])
        self.grades = ev.load_grades()
        self.cache = {}

    def vector(self, text):
        return common.normalize(np.asarray(self.embedder(text), np.float32))

    def base(self, q):
        """Raw similarities of the whole query: description, image, feature text; and the image mask."""
        e, cand = self.engine, np.array(q["candidates"])
        v_t, v_i = self.vector(common.query_text(q["query"])), self.vector(q["query"])
        return dict(cand=cand, t=e.T[cand] @ v_t, i=e.I[cand] @ v_i, f=e.F[cand] @ v_t, mask=e.has_image[cand])

    def combined(self, b, features=True, image_weight=1.0):
        """The base score of the search UI (server.SearchEngine.embedding_scores)."""
        z_i = z(b["i"], b["mask"])
        if b["mask"].any():
            z_i[~b["mask"]] = z_i[b["mask"]].min() - 1
        parts = [z(b["t"]), image_weight * z_i] + ([z(b["f"])] if features else [])
        return sum(parts) / (len(parts) - 1 + image_weight)

    def terms(self, q, heldout=False):
        """The phrase terms of the hybrid ranking: [(route, z-scored column)] for the phrases that got a term, and
        all routes."""
        engine = self.heldout if heldout else self.engine
        cand = np.array(q["candidates"])
        terms, routes = engine.bank.adjustments(q["residual"], cand, q["category"], query=q["query"])
        columns = {k: iter(v) for k, v in terms.items()}
        return [(r, next(columns[r["term"]])) for r in routes if r.get("term")], routes

    def signals(self, q, heldout=False):
        key = (q["id"], heldout)
        if key not in self.cache:
            b = self.base(q)
            b["terms"], b["routes"] = self.terms(q, heldout)
            b["asks_colour"] = server.asks_colour(q["filters"], b["routes"])
            self.cache[key] = b
        return self.cache[key]

    def hybrid(self, q, weights=server.HYBRID, heldout=False):
        s = self.signals(q, heldout)
        score = self.combined(s, image_weight=server.COLOUR_IMAGE_WEIGHT if s["asks_colour"] else 1.0)
        for r, column in s["terms"]:
            score = score + (-1 if r["term"] == "negation" else 1) * weights.get(r["term"], 0.0) * column
        return score

    def top(self, q, score, k=ev.K):
        cand = np.array(q["candidates"])
        return [str(p) for p in self.pid[cand[np.argsort(-np.asarray(score), kind="stable")[:k]]]]

    def evaluate(self, tops):
        """tops: {query id: top product ids} -> {query id: metrics}."""
        return {qid: ev.metrics(top, self.grades.get(qid, {})) for qid, top in tops.items()}

    def summary(self, tops):
        m = self.evaluate(tops)
        out = {k: float(np.mean([x[k] for x in m.values() if x[k] is not None])) for k in ("ndcg", "mrr", "p1")}
        out["unjudged"] = float(np.mean([x["unjudged"] for x in m.values()]))
        return out

    def difference(self, tops, baseline, metric="ndcg"):
        """Mean difference to a baseline over the queries where the metric is defined, with its bootstrap interval,
        and the wins, losses and ties."""
        a, b = self.evaluate(tops), self.evaluate(baseline)
        d = [a[i][metric] - b[i][metric] for i in a if i in b and a[i][metric] is not None and b[i][metric] is not None]
        mean, low, high = ev.bootstrap(d)
        d = np.array(d)
        return dict(mean=mean, low=low, high=high, wins=int((d > 1e-9).sum()), losses=int((d < -1e-9).sum()),
                    ties=int((abs(d) <= 1e-9).sum()))

    def run(self, score_fn):
        """score_fn(q) -> scores of the candidates; -> {query id: top K}."""
        return {q["id"]: self.top(q, score_fn(q)) for q in self.queries}

    def stored(self, ranking):
        """The top lists of a ranking in data/runs.jsonl."""
        return {r["id"]: r["top"] for r in map(json.loads, ev.RUNS.open(encoding="utf-8")) if r["ranking"] == ranking}


def save_runs(lab, named):
    """Writes {ranking: {query id: top}} into data/runs.jsonl (replacing these rankings) and adds their products to
    data/pool.jsonl, so that judge.py grades what is new."""
    keep = [r for r in map(json.loads, ev.RUNS.open(encoding="utf-8")) if r["ranking"] not in named]
    pool = [json.loads(line) for line in ev.POOL.open(encoding="utf-8")]
    extra = defaultdict(set)
    with ev.RUNS.open("w", encoding="utf-8") as f:
        for r in keep:
            f.write(json.dumps(r) + "\n")
        for name, tops in named.items():
            for qid, top in tops.items():
                extra[qid].update(top)
                f.write(json.dumps(dict(id=qid, ranking=name, top=top, ms=0.0, matches=[])) + "\n")
    with ev.POOL.open("w", encoding="utf-8") as f:
        for r in pool:
            r["product_ids"] = sorted(set(r["product_ids"]) | extra[r["id"]], key=int)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def by_kind(lab, rankings, heldout=False):
    """nDCG@K of stored rankings by what the phrases of a query are: the kind the phrase bank gives them without the
    colour and detail routes (the sentence ranking), unknown phrases as "unknown". A query counts in the group of
    each of its phrases. -> markdown lines."""
    engine = lab.heldout if heldout else lab.engine
    groups = defaultdict(list)
    for q in lab.queries:
        kinds = {("skipped" if r["skipped"] else r["kind"] or "unknown") for r in ev.sentence_parts(engine, q)[1]}
        for k in kinds | {"all"}:
            groups[k].append(q["id"])
    metrics = {r: lab.evaluate(lab.stored(r)) for r in rankings}
    lines = ["| phrase kind | queries | " + " | ".join(rankings) + " |", "| --- | ---: | " + " | ".join("---:" for _ in rankings) + " |"]
    for k in sorted(groups, key=lambda k: (k != "all", -len(groups[k]))):
        cells = []
        for r in rankings:
            values = [metrics[r][i]["ndcg"] for i in groups[k] if metrics[r][i]["ndcg"] is not None]
            cells.append(f"{np.mean(values):.3f}")
        lines.append(f"| {k} | {len(groups[k])} | " + " | ".join(cells) + " |")
    return lines


if __name__ == "__main__":
    import sys
    print("\n".join(by_kind(Lab(), sys.argv[1:] or ["combined", "hybrid_details_w0.25", "sentences", "hybrid_llm_rerank"])))
