"""
Ranking evaluation on the pilot: the rankings of the search UI on the benchmark queries with their reviewed parses,
a pool of products to judge and the metrics.

    python search_ui/evaluation/evaluate.py run                   # data/runs.jsonl, data/pool.jsonl (embedding calls)
    python search_ui/evaluation/evaluate.py report                # dev metrics from data/judgments.jsonl
    python search_ui/evaluation/evaluate.py report --split test   # only at milestones, never for tuning

Queries: benchmark queries with a category, a residual and at least 2 candidates after their filters. Rankings:
random, combined, combined_features, concepts, bank and bank_heldout (the bank without the phrases that come only
from benchmark queries, so its phrases are as often unknown as in new queries), and the hybrid ranking for every
pair of weights in GRID, with both banks (hybrid_c<concept>_n<negation>, hybrid_heldout_...). The pool holds every candidate of queries with at
most COMPLETE candidates and the union of the rankings' top K otherwise. Products without a grade count as 0.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time
import zlib

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "core")]
import bank  # noqa: E402
import benchmark_parser  # noqa: E402
import common  # noqa: E402
import concepts  # noqa: E402
import conditions  # noqa: E402
import parser_adapter  # noqa: E402
import server  # noqa: E402

DATA = HERE / "data"
RUNS = DATA / "runs.jsonl"
POOL = DATA / "pool.jsonl"
JUDGMENTS = DATA / "judgments.jsonl"
BASE = ("random", "combined", "combined_features", "concepts", "bank", "bank_heldout")
GRID = [dict(concept=c, negation=n) for c in (0.25, 0.5, 1.0) for n in (0.5, 1.0)]
HYBRIDS = [f"hybrid{h}_c{w['concept']:g}_n{w['negation']:g}" for h in ("", "_heldout") for w in GRID]
COLOUR = ["hybrid_colour", "hybrid_colour_heldout"]
RANKINGS = BASE + tuple(HYBRIDS) + tuple(COLOUR)
K = 10
COMPLETE = 20
RELEVANT = 2
BOOTSTRAP = 2000


def load_queries(products, vocabulary, split="all"):
    """Benchmark queries usable for the ranking, with their candidates."""
    out = []
    for r in benchmark_parser.ROWS:
        if not r["category"] or not r["residual"] or (split != "all" and r["split"] != split):
            continue
        tree, _ = conditions.canonicalize(parser_adapter.to_condition(r), vocabulary)
        cand = conditions.filter_products(tree, products)["candidates"]
        if len(cand) >= 2:
            out.append(dict(r, candidates=cand, n=len(cand)))
    return out


def heldout_rows(rows):
    """Bank rows seen in more queries than the benchmark has, so they also come from other sources."""
    seen = defaultdict(int)
    for r in benchmark_parser.ROWS:
        for phrase in dict.fromkeys(bank.normalize_phrase(p) for p in r["residual"]):
            seen[phrase] += 1
    return [i for i, row in enumerate(rows) if row["queries"] > seen[row["phrase"]]]


def engines():
    """{ranking: engine}: one engine with the full bank, one with the bank without benchmark-only phrases."""
    products, meta = common.load_index()
    T, I = server.load_product_embeddings(products, meta)
    embedder = common.QueryEmbedder(meta["model"], meta["dim"])
    ranker = concepts.load(common.DATA, meta, products, embedder, threshold=0.72)
    rows = bank.load_rows()
    vectors = np.load(common.DATA / bank.VECTORS)["vectors"]
    keep = heldout_rows(rows)

    def bank_ranker(rs, vs):
        return bank.BankRanker(products, T, I, Path(meta["dataset"]), rs, vs, embedder,
                               concepts.scored_concepts(meta["concepts"]), ranker.ids, ranker.E)

    parser = parser_adapter.Parser("benchmark", lambda q: None)
    F = server.load_feature_embeddings(products, common.DATA)
    engine = server.SearchEngine(products, T, I, parser, embedder, ranker, bank_ranker(rows, vectors), F)
    heldout = server.SearchEngine(products, T, I, parser, embedder, ranker,
                                  bank_ranker([rows[i] for i in keep], vectors[keep]), F)
    print(f"bank {len(rows)} phrases, heldout bank {len(keep)}")
    return {r: heldout if "heldout" in r else engine for r in RANKINGS}


def top_k(engine, cand, score, tie=None):
    idx = np.lexsort((-tie, -score)) if tie is not None else np.argsort(-score, kind="stable")
    return [engine.products[cand[i]]["product_id"] for i in idx[:K]]


def hybrids(engines, q):
    """Every hybrid variant from one base score and one set of terms per bank."""
    cand = np.array(q["candidates"])
    out, start = {}, time.perf_counter()
    first = engines["combined"]
    jobs = first.query_vectors(q["query"], "combined")
    base = first.embedding_scores(jobs, "combined_features", cand, {}, start)[0]
    image_base = first.embedding_scores(jobs, "combined_features", cand, {}, start,
                                        image_weight=server.COLOUR_IMAGE_WEIGHT)[0]
    base_ms = (time.perf_counter() - start) * 1000
    for prefix, engine in (("hybrid", engines["bank"]), ("hybrid_heldout", engines["bank_heldout"])):
        start = time.perf_counter()
        terms, routes = engine.bank.adjustments(q["residual"], cand, q["category"], query=q["query"])
        ms = base_ms + (time.perf_counter() - start) * 1000
        matches = [r["match"] for r in routes]
        for w in GRID:
            name = f"{prefix}_c{w['concept']:g}_n{w['negation']:g}"
            out[name] = (top_k(engine, cand, engine.combine(base, terms, w)), ms, matches)
        colour = image_base if server.asks_colour(q["filters"], routes) else base
        name = "hybrid_colour" + prefix.removeprefix("hybrid")
        out[name] = (top_k(engine, cand, engine.combine(colour, terms, server.HYBRID)), ms, matches)
    return out


def order(engine, q, ranking):
    cand = np.array(q["candidates"])
    out, timings = dict(parsed=dict(category=q["category"], residual=q["residual"])), {}
    start = time.perf_counter()
    if ranking == "random":
        score, tie = np.random.default_rng(zlib.crc32(q["id"].encode())).random(len(cand)), None
    else:
        score, _, _, tie = engine.rank(q["query"], "bank" if ranking == "bank_heldout" else ranking, cand,
                                       q["category"], timings, out)
    ms = (time.perf_counter() - start) * 1000
    idx = np.lexsort((-tie, -score)) if tie is not None else np.argsort(-score, kind="stable")
    routes = out.get("bank") or []
    return [engine.products[cand[i]]["product_id"] for i in idx[:K]], ms, [r["match"] for r in routes]


def run(split, limit, workers):
    by_ranking_engine = engines()
    engine = by_ranking_engine["combined"]
    queries = load_queries(engine.products, engine.vocabulary, split)[:limit]
    DATA.mkdir(exist_ok=True)

    def one(q):
        return q, {r: order(by_ranking_engine[r], q, r) for r in BASE} | hybrids(by_ranking_engine, q)

    with ThreadPoolExecutor(workers) as pool, RUNS.open("w", encoding="utf-8") as runs, \
            POOL.open("w", encoding="utf-8") as pooled:
        for q, by_ranking in pool.map(one, queries):
            products = set(engine.products[i]["product_id"] for i in q["candidates"]) if q["n"] <= COMPLETE else set()
            for r, (top, ms, matches) in by_ranking.items():
                products.update(top)
                runs.write(json.dumps(dict(id=q["id"], ranking=r, top=top, ms=round(ms, 1), matches=matches)) + "\n")
            pooled.write(json.dumps(dict(id=q["id"], split=q["split"], query=q["query"], category=q["category"],
                                         residual=q["residual"], n=q["n"], product_ids=sorted(products, key=int)),
                                    ensure_ascii=False) + "\n")
    sizes = [len(json.loads(line)["product_ids"]) for line in POOL.open(encoding="utf-8")]
    print(f"{len(queries)} queries ({split}), {len(RANKINGS)} rankings -> {RUNS}")
    print(f"pool: {sum(sizes)} (query, product) pairs, {np.mean(sizes):.1f} per query -> {POOL}")


def dcg(grades):
    return sum((2 ** g - 1) / np.log2(i + 2) for i, g in enumerate(grades))


def metrics(top, grades):
    """nDCG@K against the best order of every judged product, reciprocal rank and precision at 1 of a relevant one.
    A metric is None when the query cannot tell rankings apart: nDCG when every judged product has grade 0, MRR and
    P@1 when no judged product is relevant."""
    got = [grades.get(p, 0) for p in top[:K]]
    ideal = dcg(sorted(grades.values(), reverse=True)[:K])
    relevant = any(g >= RELEVANT for g in grades.values())
    first = next((i for i, g in enumerate(got) if g >= RELEVANT), None)
    return dict(ndcg=dcg(got) / ideal if ideal else None,
                mrr=(0.0 if first is None else 1 / (first + 1)) if relevant else None,
                p1=float(bool(got) and got[0] >= RELEVANT) if relevant else None,
                unjudged=sum(p not in grades for p in top[:K]))


def load_grades():
    grades = defaultdict(dict)
    if JUDGMENTS.exists():
        for r in map(json.loads, JUDGMENTS.open(encoding="utf-8")):
            for pid, g in r.get("grades", {}).items():
                grades[r["id"]][pid] = g
    return grades


def bootstrap(values, rounds=BOOTSTRAP, seed=0):
    """Mean and its 95% percentile interval over resampled queries."""
    v = np.asarray(values, dtype=float)
    means = v[np.random.default_rng(seed).integers(0, len(v), (rounds, len(v)))].mean(axis=1)
    return v.mean(), np.percentile(means, 2.5), np.percentile(means, 97.5)


def report(split, baseline):
    pool = {r["id"]: r for r in map(json.loads, POOL.open(encoding="utf-8")) if split == "all" or r["split"] == split}
    scored = set(concepts.scored_concepts(json.loads((common.DATA / common.META).read_text(encoding="utf-8"))["concepts"]))
    grades = load_grades()
    rows, per_query, times = defaultdict(list), defaultdict(dict), defaultdict(list)
    for r in map(json.loads, RUNS.open(encoding="utf-8")):
        q = pool.get(r["id"])
        if q is None:
            continue
        times[r["ranking"]].append(r["ms"])
        if r["id"] not in grades:
            continue
        m = metrics(r["top"], grades[r["id"]])
        per_query[r["ranking"]][r["id"]] = m
        size = "2-9" if q["n"] < 10 else "10-49" if q["n"] < 50 else "50+"
        for group in ("all", "concept categories" if q["category"] in scored else "other categories",
                      f"candidates {size}"):
            rows[r["ranking"], group].append(m)
    names = [n for n in RANKINGS if n in per_query]
    groups = ["all", "concept categories", "other categories", "candidates 2-9", "candidates 10-49", "candidates 50+"]
    lines = ["# Ranking evaluation on the pilot", "",
             f"Split: {split}. nDCG@{K}, MRR and P@1 with grade >= {RELEVANT} as relevant; products without a grade "
             "count as 0. Query counts in brackets.", ""]
    for metric in ("ndcg", "mrr", "p1"):
        lines += [f"## {metric}", "", "| ranking | " + " | ".join(groups) + " |",
                  "| --- | " + " | ".join("---:" for _ in groups) + " |"]
        for n in names:
            cells = []
            for g in groups:
                values = [m[metric] for m in rows[n, g] if m[metric] is not None]
                cells.append(f"{np.mean(values):.3f} ({len(values)})" if values else "-")
            lines.append(f"| {n} | " + " | ".join(cells) + " |")
        lines.append("")
    if baseline in names:
        lines += [f"## difference to {baseline} (mean and 95% bootstrap interval over queries)", "",
                  "| ranking | ndcg | mrr | p1 |", "| --- | ---: | ---: | ---: |"]
        base = per_query[baseline]
        for n in names:
            if n == baseline:
                continue
            cells = []
            for metric in ("ndcg", "mrr", "p1"):
                d = [m[metric] - base[qid][metric] for qid, m in per_query[n].items()
                     if qid in base and m[metric] is not None and base[qid][metric] is not None]
                cells.append("{:+.3f} [{:+.3f}, {:+.3f}]".format(*bootstrap(d)) if d else "-")
            lines.append(f"| {n} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## time per query (ms)", "", "| ranking | p50 | p95 |", "| --- | ---: | ---: |"]
    lines += [f"| {n} | {np.percentile(t, 50):.0f} | {np.percentile(t, 95):.0f} |" for n, t in times.items()]
    unjudged = {n: np.mean([m["unjudged"] for m in rows[n, "all"]] or [0]) for n in names}
    lines += ["", "Ungraded products in the top 10, on average: " + ", ".join(f"{n} {v:.2f}" for n, v in unjudged.items())]
    (DATA / f"report_{split}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("command", choices=["run", "report"])
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"],
                    help="test only at milestones, never for tuning")
    ap.add_argument("--limit", type=int, help="run: at most this many queries")
    ap.add_argument("--workers", type=int, default=4, help="run: queries in parallel")
    ap.add_argument("--baseline", default="combined", help="report: ranking the differences are measured against")
    a = ap.parse_args()
    run(a.split, a.limit, a.workers) if a.command == "run" else report(a.split, a.baseline)
