"""
Ranking evaluation on the pilot: the rankings of the search UI on the benchmark queries with their reviewed parses,
a pool of products to judge and the metrics.

    python experiments/ranking/evaluate.py run                   # data/runs.jsonl, data/pool.jsonl (embedding calls)
    python experiments/ranking/evaluate.py run --only hybrid_details   # rerun some rankings, keep the other runs
    python experiments/ranking/evaluate.py report                # dev metrics from data/judgments.jsonl
    python experiments/ranking/evaluate.py report --split test   # only at milestones, never for tuning

Queries: benchmark queries with a category, a residual and at least 2 candidates after their filters. Rankings:
random; combined, combined_features, concepts, bank and bank_heldout (the bank without the phrases that come only
from benchmark queries, so its phrases are as often unknown as in new queries), the rankings of baselines.py; and the
hybrid ranking of the search UI for every pair of weights in GRID, with both banks (hybrid_c<concept>_n<negation>,
hybrid_heldout_...), and with the weights of the search UI: hybrid_colour without the detail term, hybrid_details with
it, hybrid_details_w<weight> with other detail weights. The pool holds every candidate of queries with at most COMPLETE candidates and the union of the rankings'
top K otherwise. Products without a grade count as 0.
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
SEARCH_UI = HERE.parents[1] / "search_ui"
sys.path[:0] = [str(SEARCH_UI), str(SEARCH_UI / "core")]
import baselines  # noqa: E402
import bank  # noqa: E402
import colours  # noqa: E402
import details  # noqa: E402
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
DETAIL_WEIGHTS = (0.25, 0.5)
DETAILS = ["hybrid_details", "hybrid_details_heldout"] + [f"hybrid_details{h}_w{w:g}" for h in ("", "_heldout")
                                                          for w in DETAIL_WEIGHTS]
RANKINGS = BASE + tuple(HYBRIDS) + tuple(COLOUR) + tuple(DETAILS)
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
    """Bank rows that do not come only from benchmark queries: seen in more queries than the benchmark has, or in no
    benchmark residual at all (the Polish forms of detail and colour names, which come from no query)."""
    seen = defaultdict(int)
    for r in benchmark_parser.ROWS:
        for phrase in dict.fromkeys(bank.normalize_phrase(p) for p in r["residual"]):
            seen[phrase] += 1
    return [i for i, row in enumerate(rows) if not seen[row["phrase"]] or row["queries"] > seen[row["phrase"]]]


ORIGINAL_IMAGES = False  # --original-images: the embeddings of the original 256 px photos


def engines():
    """{"main": the search engine with the full bank, "heldout": the same with the bank without benchmark-only
    phrases, "concepts": the concepts ranking}."""
    products, meta = common.load_index()
    T, I = server.load_product_embeddings(products, meta, enhanced=not ORIGINAL_IMAGES)
    embedder = common.QueryEmbedder(meta["model"], meta["dim"])
    concept_data = concepts.load(common.DATA, meta, products)
    rows = bank.load_rows()
    vectors = np.load(common.DATA / bank.VECTORS)["vectors"]
    keep = heldout_rows(rows)

    colour_data, detail_data = colours.load(products), details.load(products)

    def bank_ranker(rs, vs):
        return bank.BankRanker(products, T, I, Path(meta["dataset"]), rs, vs, embedder,
                               concepts.scored_concepts(meta["concepts"]), concept_data.ids, concept_data.E,
                               colour_data, detail_data)

    parser = parser_adapter.Parser("benchmark", lambda q: None)
    F = server.load_feature_embeddings(products, common.DATA)
    main = server.SearchEngine(products, T, I, parser, embedder, concept_data, bank_ranker(rows, vectors), F)
    heldout = server.SearchEngine(products, T, I, parser, embedder, concept_data,
                                  bank_ranker([rows[i] for i in keep], vectors[keep]), F)
    print(f"bank {len(rows)} phrases, heldout bank {len(keep)}")
    return dict(main=main, heldout=heldout, concepts=baselines.ConceptRanking(concept_data, meta["concepts"], embedder))


def top_k(engine, cand, score, tie=None):
    idx = np.lexsort((-tie, -score)) if tie is not None else np.argsort(-score, kind="stable")
    return [engine.products[cand[i]]["product_id"] for i in idx[:K]]


def hybrids(engines, q):
    """Every hybrid variant from one base score and one set of terms per bank."""
    cand = np.array(q["candidates"])
    out, start = {}, time.perf_counter()
    first = engines["main"]
    jobs = first.query_vectors(q["query"])
    base = first.query_similarity(jobs, cand, {}, start)[0]
    image_base = first.query_similarity(jobs, cand, {}, start, image_weight=server.COLOUR_IMAGE_WEIGHT)[0]
    base_ms = (time.perf_counter() - start) * 1000
    for prefix, engine in (("hybrid", engines["main"]), ("hybrid_heldout", engines["heldout"])):
        start = time.perf_counter()
        terms, routes = engine.bank.adjustments(q["residual"], cand, q["category"], query=q["query"])
        ms = base_ms + (time.perf_counter() - start) * 1000
        matches = [r["match"] for r in routes]
        for w in GRID:
            name = f"{prefix}_c{w['concept']:g}_n{w['negation']:g}"
            out[name] = (top_k(engine, cand, engine.combine(base, terms, w)), ms, matches)
        colour = image_base if server.asks_colour(q["filters"], routes) else base
        suffix = prefix.removeprefix("hybrid")
        out["hybrid_colour" + suffix] = (top_k(engine, cand, engine.combine(colour, terms, dict(server.HYBRID, detail=0))),
                                         ms, matches)
        out["hybrid_details" + suffix] = (top_k(engine, cand, engine.combine(colour, terms, server.HYBRID)), ms, matches)
        for w in DETAIL_WEIGHTS:
            out[f"hybrid_details{suffix}_w{w:g}"] = (top_k(engine, cand, engine.combine(colour, terms,
                                                                                       dict(server.HYBRID, detail=w))),
                                                     ms, matches)
    return out


def order(engines, q, ranking):
    """The top K of a ranking of BASE: random or a ranking of baselines.py."""
    cand = np.array(q["candidates"])
    start, matches = time.perf_counter(), []
    engine = engines["heldout" if ranking == "bank_heldout" else "main"]
    if ranking == "random":
        score, tie = np.random.default_rng(zlib.crc32(q["id"].encode())).random(len(cand)), None
    else:
        v = baselines.query_vectors(engine, q["query"])
        if ranking in baselines.EMBEDDING:
            score, tie = baselines.embedding(engine, v, ranking, cand), None
        elif ranking == "concepts":
            score, tie = engines["concepts"].rank(q["residual"], q["category"], cand,
                                                  baselines.embedding(engine, v, "combined", cand))
        else:
            def whole_query(routes):
                weight = server.COLOUR_IMAGE_WEIGHT if server.asks_colour(q["filters"], routes) else 1.0
                return baselines.embedding(engine, v, "combined", cand, image_weight=weight)
            score, routes = baselines.bank_rank(engine.bank, q["residual"], cand, q["category"], q["query"], whole_query)
            tie, matches = whole_query(routes), [r["match"] for r in routes]
    ms = (time.perf_counter() - start) * 1000
    return top_k(engine, cand, score, tie), ms, matches


def run(split, limit, workers, only=None, suffix=""):
    """only: rerun just these rankings and keep the other runs and the pool of earlier runs; suffix: store them under
    their name with this suffix, to compare with the same rankings on earlier data."""
    built = engines()
    engine = built["main"]
    queries = load_queries(engine.products, engine.vocabulary, split)[:limit]
    DATA.mkdir(exist_ok=True)
    keep_runs, keep_pool = [], {}
    if only:
        keep_runs = [r for r in map(json.loads, RUNS.open(encoding="utf-8")) if r["ranking"] not in
                     {n + suffix for n in only}]
        keep_pool = {r["id"]: r for r in map(json.loads, POOL.open(encoding="utf-8"))}

    def one(q):
        out = {r: order(built, q, r) for r in BASE if not only or r in only}
        if not only or any(r.startswith("hybrid") for r in only):
            out |= {r: v for r, v in hybrids(built, q).items() if not only or r in only}
        return q, {r + suffix: v for r, v in out.items()}

    with ThreadPoolExecutor(workers) as pool:
        results = list(pool.map(one, queries))
    with RUNS.open("w", encoding="utf-8") as runs, POOL.open("w", encoding="utf-8") as pooled:
        for r in keep_runs:
            runs.write(json.dumps(r) + "\n")
        done = set()
        for q, by_ranking in results:
            done.add(q["id"])
            products = set(engine.products[i]["product_id"] for i in q["candidates"]) if q["n"] <= COMPLETE else set()
            products |= set(keep_pool.get(q["id"], {}).get("product_ids", []))
            for r, (top, ms, matches) in by_ranking.items():
                products.update(top)
                runs.write(json.dumps(dict(id=q["id"], ranking=r, top=top, ms=round(ms, 1), matches=matches)) + "\n")
            pooled.write(json.dumps(dict(id=q["id"], split=q["split"], query=q["query"], category=q["category"],
                                         residual=q["residual"], n=q["n"], product_ids=sorted(products, key=int)),
                                    ensure_ascii=False) + "\n")
        for qid, r in keep_pool.items():
            if qid not in done:
                pooled.write(json.dumps(r, ensure_ascii=False) + "\n")
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
    names = [n for n in RANKINGS if n in per_query] + sorted(n for n in per_query if n not in RANKINGS)
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
    ap.add_argument("--only", nargs="+", choices=RANKINGS, help="run: rerun just these rankings, keep the other runs")
    ap.add_argument("--suffix", default="", help="run: store the rerun rankings under their name with this suffix")
    ap.add_argument("--original-images", action="store_true", help="run: use the embeddings of the original photos")
    ap.add_argument("--baseline", default="combined", help="report: ranking the differences are measured against")
    a = ap.parse_args()
    ORIGINAL_IMAGES = a.original_images
    run(a.split, a.limit, a.workers, a.only, a.suffix) if a.command == "run" else report(a.split, a.baseline)
