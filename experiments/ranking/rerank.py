"""
Two-stage ranking: the sentence ranking picks the first DEPTH candidates, and a fast decision model (Jev, the model
of the parser's category step) grades each of them 0-3 against the query, reading the query and the product
together. One call per query, one question per product; the answer carries the probability of every grade, and the
candidates are ordered by their expected grade, with the first-stage score breaking ties and added with a small
weight.

    python experiments/ranking/rerank.py --variant text              # plan and cost estimate, no API calls
    python experiments/ranking/rerank.py --variant text --execute    # paid calls -> data/rerank.jsonl
    python experiments/ranking/rerank.py --variant text --report     # rankings -> data/runs.jsonl, metrics

Variants say what the model reads of a product: "text" its name, brand, description and composition; "facts" also
the colours and details Gemini gave it offline from the photos. The first stage uses the fold weights of learn.py,
so the result is out of fold like "sentences".
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import json
import sys
import threading
import time

import numpy as np
import pandas as pd
import requests

import evaluate as ev
from evaluate import colours, common, details
import judge
from lab import save_runs

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"
LOG = ev.DATA / "rerank.jsonl"
STAGE = ev.DATA / "rerank_stage1.json"
DEPTH = 30
USD_PER_PRODUCT = 0.000015  # measured: about $0.00026 for 20 products
CRITERIA = {
    "3": "excellent: the product matches everything the query asks for, including any style, occasion, season, "
         "detail, material or colour shade the query mentions",
    "2": "good: it matches the main request, with a small mismatch or an aspect that cannot be verified",
    "1": "weak: the right kind of product whose explicit attributes fit, but it lacks the style, occasion, season, "
         "detail or colour shade the query asks for",
    "0": "wrong: not the kind of product asked for, or it contradicts an explicit attribute of the query"}
INSTRUCTIONS = ("Grade how well one product of PRODUCTS answers the shopper's QUERY in a fashion e-commerce search. "
                "Ignore sizes, plus size, maternity and children's sizes in the query. A negation such as "
                "'no graphics' means the product must not have that. Grade the product {label}.")


def api_key():
    sys.path.insert(0, str(common.REPO))
    from query_parsing.clients.credentials import load_api_key
    return load_api_key("OPENROUTER_API_KEY")


def facts():
    """{product_id: "Colours: ... Details: ..."} from the files of ranking_data/."""
    out = defaultdict(list)
    for pid, rows in pd.read_parquet(colours.PRODUCTS).sort_values(["product_id", "rank"]).groupby("product_id"):
        out[pid].append("Colours: " + ", ".join(f"{r.name} {round(100 * r.share)}%" for r in rows.itertuples()))
    for pid, rows in pd.read_parquet(details.PRODUCTS).sort_values(["product_id", "rank"]).groupby("product_id"):
        out[pid].append("Details: " + ", ".join(f"{r.name} ({r.extent})" for r in rows.itertuples()))
    return {pid: " | ".join(parts) for pid, parts in out.items()}


def product_text(p, extra=None):
    text = (f"{html.unescape(p['name'])} | {p['brand']} | {html.unescape(str(p['description']))} | "
            f"Composition: {p['composition']}")
    return f"{text} | {extra}" if extra else text


def first_stage(depth=DEPTH):
    """{bank: {query id: {"top": product ids, "score": their first-stage scores}}}, computed once and stored."""
    if STAGE.exists():
        return json.loads(STAGE.read_text(encoding="utf-8"))
    engines = ev.engines()
    weights = json.loads(ev.FOLD_WEIGHTS.read_text(encoding="utf-8"))
    queries = ev.load_queries(engines["bank"].products, engines["bank"].vocabulary, "dev")
    out = {}
    for key, engine in (("full", engines["bank"]), ("heldout", engines["bank_heldout"])):
        out[key] = {}
        for q in queries:
            score = ev.weighted(ev.sentence_parts(engine, q)[0], weights[key]["folds"][ev.fold(q["id"])])
            order = np.argsort(-score, kind="stable")[:depth]
            out[key][q["id"]] = dict(top=[engine.products[q["candidates"][i]]["product_id"] for i in order],
                                     score=[float(score[i]) for i in order])
    STAGE.write_text(json.dumps(out), encoding="utf-8")
    return out


def payload(task, by_id, extra):
    products = {label: product_text(by_id[pid], extra.get(pid) if extra else None) for label, pid in task["labels"].items()}
    return {"model": MODEL, "state": {"QUERY": task["query"], "CATEGORY": task["category"], "PRODUCTS": products},
            "questions": {label: {"type": "choice", "instructions": INSTRUCTIONS.format(label=label),
                                  "criteria": CRITERIA} for label in products}}


def call(body, key):
    for attempt in range(4):
        start = time.perf_counter()
        r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=90)
        seconds = time.perf_counter() - start
        if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
            time.sleep(2 ** attempt)
            continue
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        return r.json(), seconds


def done(variant, bank):
    """{query id: record} of the calls made. The held-out bank reuses the answers of the full bank for the same
    query and product, so only queries with a product the full bank did not bring are called again."""
    out = {}
    if LOG.exists():
        rows = [r for r in map(json.loads, LOG.open(encoding="utf-8")) if r.get("variant") == variant and "answers" in r]
        for r in sorted(rows, key=lambda r: r["bank"] == bank):
            if r["bank"] in ("full", bank):
                merged = dict(out.get(r["id"], {}).get("answers", {}), **r["answers"])
                out[r["id"]] = dict(r, answers=merged)
    return out


def expected(answer):
    """Expected grade from the probabilities of an answer, or its choice when it has none."""
    p = answer.get("probabilities")
    if isinstance(p, dict) and p:
        return sum(int(k) * float(v) for k, v in p.items()) / max(sum(map(float, p.values())), 1e-9)
    return float(answer["choice"])


def execute(tasks, by_id, extra, variant, bank, budget, workers):
    key, lock = api_key(), threading.Lock()
    state = dict(spent=sum(json.loads(line).get("cost_usd", 0) for line in LOG.open(encoding="utf-8")) if LOG.exists() else 0.0,
                 done=0, errors=0)

    def one(task, out):
        with lock:
            if state["spent"] + USD_PER_PRODUCT * len(task["labels"]) > budget:
                return
        try:
            data, seconds = call(payload(task, by_id, extra), key)
            answers = {task["labels"][label]: a for label, a in data["answers"].items()}
            record = dict(id=task["id"], variant=variant, bank=bank, model=MODEL, seconds=round(seconds, 3),
                          usage=data.get("usage", {}), cost_usd=float(data.get("usage", {}).get("cost") or 0),
                          answers=answers)
        except Exception as e:
            record = dict(id=task["id"], variant=variant, bank=bank, error=f"{type(e).__name__}: {str(e)[:300]}",
                          cost_usd=0.0)
        with lock:
            state["spent"] += record["cost_usd"]
            state["done"] += 1
            state["errors"] += "error" in record
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if state["done"] % 50 == 0:
                print(f"{state['done']}/{len(tasks)}  ${state['spent']:.4f}", flush=True)

    with LOG.open("a", encoding="utf-8") as out, ThreadPoolExecutor(workers) as pool:
        for f in as_completed([pool.submit(one, t, out) for t in tasks]):
            f.result()
    print(f"done {state['done'] - state['errors']}, errors {state['errors']}; log total ${state['spent']:.4f}")


def rerank(stage, answers, depth, blend):
    """The first depth candidates of the first stage ordered by expected grade plus blend times the z-score of the
    first-stage score among them; the rest keep their order behind."""
    top, score = stage["top"][:depth], np.array(stage["score"][:depth])
    if len(top) < 2:
        return stage["top"]
    z = (score - score.mean()) / (score.std() + 1e-9)
    grade = np.array([expected(answers[p]) if p in answers else 0.0 for p in top])
    order = np.argsort(-(grade + blend * z), kind="stable")
    return [top[i] for i in order] + stage["top"][depth:]


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--variant", default="text", choices=["text", "facts"])
    ap.add_argument("--bank", default="full", choices=["full", "heldout"])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--report", action="store_true", help="write the rankings and print their metrics")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--budget-usd", type=float, default=1.0, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    stage = first_stage()[args.bank]
    products, _ = common.load_index()
    by_id = {p["product_id"]: p for p in products}
    pool = {r["id"]: r for r in map(json.loads, ev.POOL.open(encoding="utf-8"))}
    have = done(args.variant, args.bank)
    if args.report:
        grades = ev.load_grades()
        suffix = "_heldout" if args.bank == "heldout" else ""
        runs = {}
        for depth in (10, 20, 30):
            for blend in (0.0, 0.25, 0.5, 1.0):
                name = f"jev_{args.variant}_d{depth}_b{blend:g}{suffix}"
                runs[name] = {i: rerank(s, have[i]["answers"], depth, blend)[:ev.K] if i in have else s["top"][:ev.K]
                              for i, s in stage.items()}
        runs[f"sentences_top{suffix}"] = {i: s["top"][:ev.K] for i, s in stage.items()}
        for name, tops in runs.items():
            m = [ev.metrics(top, grades[i]) for i, top in tops.items()]
            print(f"{name:<28} nDCG {np.mean([x['ndcg'] for x in m if x['ndcg'] is not None]):.3f}  MRR "
                  f"{np.mean([x['mrr'] for x in m if x['mrr'] is not None]):.3f}  P@1 "
                  f"{np.mean([x['p1'] for x in m if x['p1'] is not None]):.3f}  ungraded "
                  f"{np.mean([x['unjudged'] for x in m]):.2f}")
        save_runs(None, {k: v for k, v in runs.items() if k.startswith("jev_")})
        seconds = [r["seconds"] for r in have.values()]
        print(f"{len(have)} queries; call seconds p50 {np.percentile(seconds, 50):.2f}, p95 {np.percentile(seconds, 95):.2f}; "
              f"cost per query ${np.mean([r['cost_usd'] for r in have.values()]):.5f}")
        return
    extra = facts() if args.variant == "facts" else None
    tasks = [dict(id=i, query=pool[i]["query"], category=pool[i]["category"], labels=judge.layout(i, s["top"]))
             for i, s in stage.items() if len(s["top"]) > 1
             and not set(s["top"]) <= set(have.get(i, {}).get("answers", {}))]
    tasks = tasks[:args.limit] if args.limit else tasks
    n = sum(len(t["labels"]) for t in tasks)
    print(f"{len(tasks)} calls, {n} products, model {MODEL}, variant {args.variant}, bank {args.bank}; estimate "
          f"${n * USD_PER_PRODUCT:.2f}")
    if args.execute and tasks:
        execute(tasks, by_id, extra, args.variant, args.bank, args.budget_usd, args.workers)


if __name__ == "__main__":
    main()
