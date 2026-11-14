"""
Reference ceiling of the ranking: an LLM reorders the top DEPTH products of a ranking for every dev query, seeing the
query and each product's text and main photo. It runs offline only and is never part of the search. One call per
query; the model returns the labels from the best to the worst match. The reordered top K goes to data/runs.jsonl
as "<name>_llm_rerank"; "<name>_oracle" is the same top DEPTH ordered by the judge's own grades, the best any
reranker of these products could do. The input is the ranking "hybrid_top20", the top DEPTH of the hybrid ranking
of the search UI, written to data/runs.jsonl on the first run; judge.py must grade its products before the result
means anything.

    python experiments/ranking/ceiling.py                  # plan and cost estimate, no API calls
    python experiments/ranking/ceiling.py --execute        # paid calls
"""
import argparse
from datetime import datetime, timezone
import json

import numpy as np

import evaluate as ev
from evaluate import HERE, common
import judge
import lab as workbench
import vertex

SYSTEM = HERE / "ceiling_system.txt"
LOG = ev.DATA / "ceiling.jsonl"
DEPTH = 20
THINKING = "MEDIUM"
INPUT = "hybrid_top20"


def stored(ranking):
    return {r["id"]: r["top"][:DEPTH] for r in map(json.loads, ev.RUNS.open(encoding="utf-8"))
            if r["ranking"] == ranking}


def body(task, by_id):
    request = judge.body(task, by_id, THINKING)
    labels = list(task["labels"])
    request["systemInstruction"] = {"parts": [{"text": SYSTEM.read_text(encoding="utf-8")}]}
    request["generationConfig"]["responseSchema"] = {
        "type": "OBJECT", "required": ["ranking"],
        "properties": {"ranking": {"type": "ARRAY", "items": {"type": "STRING", "enum": labels}}}}
    return request


def parse(response, labels):
    """Product ids from the best to the worst; a label the model left out or repeated keeps its input order at the
    end."""
    order = list(dict.fromkeys(k for k in json.loads(vertex.response_text(response))["ranking"] if k in labels))
    return [labels[k] for k in order + [k for k in labels if k not in order]], len(order)


def estimated_cost(task, by_id):
    chars = len(SYSTEM.read_text(encoding="utf-8")) + 200 + sum(len(judge.product_text(k, by_id[p]))
                                                                 for k, p in task["labels"].items())
    return vertex.estimate(chars, 6 * len(task["labels"]) + judge.THINKING_TOKENS, images=len(task["labels"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--ranking", default=INPUT,
                    help="a ranking of data/runs.jsonl with DEPTH products; the default is written when missing")
    ap.add_argument("--name", default="hybrid", help="prefix of the rankings written")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--budget-usd", type=float, default=3.5, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    products, _ = common.load_index()
    by_id = {p["product_id"]: p for p in products}
    tops = stored(args.ranking)
    if not tops and args.ranking == INPUT:
        lab = workbench.Lab()
        workbench.save_runs(lab, {INPUT: {q["id"]: lab.top(q, lab.hybrid(q), k=DEPTH) for q in lab.queries}})
        tops = stored(INPUT)
        print(f"wrote {INPUT}: the top {DEPTH} of hybrid for {len(tops)} queries; grade them with judge.py")
    pool = {r["id"]: r for r in map(json.loads, ev.POOL.open(encoding="utf-8")) if r["split"] == "dev"}
    done = {}
    if LOG.exists():
        done = {r["id"]: r for r in map(json.loads, LOG.open(encoding="utf-8"))
                if "order" in r and r["ranking"] == args.ranking}
    tasks = [dict(id=i, query=pool[i]["query"], category=pool[i]["category"], labels=judge.layout(i, top))
             for i, top in tops.items() if i in pool and i not in done and len(top) > 1]
    tasks = tasks[:args.limit] if args.limit else tasks
    costs = [estimated_cost(t, by_id) for t in tasks]
    spent = vertex.spent_in(LOG)
    print(f"{len(tasks)} calls, {sum(len(t['labels']) for t in tasks)} products, model {vertex.MODEL}, thinking "
          f"{THINKING}; estimate up to ${sum(costs):.2f}; spent so far ${spent:.4f}, budget ${args.budget_usd:.2f}")
    if args.execute and tasks:
        def work(task, client):
            response = client(body(task, by_id))
            order, returned = parse(response, task["labels"])
            return dict(id=task["id"], query=task["query"], ranking=args.ranking, model=vertex.MODEL,
                        thinking=THINKING, usage=response.get("usageMetadata", {}), order=order, returned=returned,
                        at=datetime.now(timezone.utc).isoformat(timespec="seconds"))

        vertex.run(tasks, costs, work, LOG, args.budget_usd, spent, args.workers)
        done = {r["id"]: r for r in map(json.loads, LOG.open(encoding="utf-8"))
                if "order" in r and r["ranking"] == args.ranking}
    if not done:
        return
    grades = ev.load_grades()
    reranked = {i: (done[i]["order"] if i in done else top)[:ev.K] for i, top in tops.items()}
    oracle = {i: sorted(top, key=lambda p: -grades[i].get(p, 0))[:ev.K] for i, top in tops.items()}
    workbench.save_runs(None, {f"{args.name}_llm_rerank": reranked, f"{args.name}_oracle": oracle})
    for name, t in (("input", {i: top[:ev.K] for i, top in tops.items()}), ("llm rerank", reranked), ("oracle", oracle)):
        m = [ev.metrics(top, grades[i]) for i, top in t.items()]
        print(f"{name}: nDCG {np.mean([x['ndcg'] for x in m if x['ndcg'] is not None]):.3f}, "
              f"ungraded {np.mean([x['unjudged'] for x in m]):.2f}")


if __name__ == "__main__":
    main()
