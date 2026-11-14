"""
A second relevance judge from another model family, to check how much of the evaluation depends on the first judge
(Gemini, which also made the concept scores, colours and details of the products). It grades, with the prompt and
the product layout of judge.py, every product in the top K of the rankings in RANKINGS for the dev queries, and all
candidates of queries with at most COMPLETE candidates. One call per query through OpenRouter.

    python experiments/ranking/judge2.py                  # plan and cost estimate, no API calls
    python experiments/ranking/judge2.py --execute        # paid calls -> data/judgments2.jsonl
    python experiments/ranking/judge2.py --report         # agreement with the first judge, metrics by both judges

OPENROUTER_API_KEY comes from the environment or the .env of the repository, as for the query parser.
"""
import argparse
import base64
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import re
import sys
import threading
import time

import numpy as np
import requests

import evaluate as ev
from evaluate import HERE, common
import judge

MODEL = "anthropic/claude-haiku-5.5"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
INPUT_RATE, OUTPUT_RATE = 0.10 / 1_000_000, 0.50 / 1_000_000
IMAGE_TOKENS = 120  # one 256x256 image
LOG = ev.DATA / "judgments2.jsonl"
RANKINGS = ("random", "combined", "bank_heldout", "hybrid_details_w0.25", "hybrid_details_heldout_w0.25",
            "hybrid_sentence", "sentences", "sentences_heldout", "sentences_fitted", "hybrid_llm_rerank")
ASK = ("\n\nReturn only a JSON object that maps every product label to its grade, for example "
       '{"P01": 3, "P02": 1}.')


def api_key():
    sys.path.insert(0, str(common.REPO))
    from query_parsing.clients.credentials import load_api_key
    return load_api_key("OPENROUTER_API_KEY")


def messages(task, by_id):
    content = [{"type": "text", "text": f"Query: {task['query']}\nCategory of the results: {task['category']}\n\nProducts:"}]
    for label, pid in task["labels"].items():
        p = by_id[pid]
        content.append({"type": "text", "text": judge.product_text(label, p)})
        if p["images"]:
            data = base64.b64encode((common.DATASET / judge.main_image(p)).read_bytes()).decode()
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}})
    return [{"role": "system", "content": judge.SYSTEM.read_text(encoding="utf-8") + ASK},
            {"role": "user", "content": content}]


def estimated_cost(task, by_id):
    chars = len(judge.SYSTEM.read_text(encoding="utf-8")) + 300 + sum(len(judge.product_text(k, by_id[p]))
                                                                       for k, p in task["labels"].items())
    return (chars / 4 + IMAGE_TOKENS * len(task["labels"])) * INPUT_RATE + 12 * len(task["labels"]) * OUTPUT_RATE


def parse(text, labels):
    found = re.search(r"\{.*\}", text, re.S)
    if not found:
        raise ValueError(f"no JSON object: {text[:200]}")
    grades = json.loads(found.group(0))
    if set(grades) != set(labels) or not all(isinstance(g, int) and 0 <= g <= 3 for g in grades.values()):
        raise ValueError(f"invalid grades: {text[:200]}")
    return {labels[k]: g for k, g in grades.items()}


def call(task, by_id, key):
    for attempt in range(4):
        r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"}, timeout=180,
                          json={"model": MODEL, "messages": messages(task, by_id), "temperature": 0,
                                "max_tokens": 4000, "usage": {"include": True}})
        if r.status_code in (429, 500, 502, 503, 529) and attempt < 3:
            time.sleep(2 ** attempt)
            continue
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        return r.json()


def cost_of(usage):
    if usage.get("cost") is not None:
        return float(usage["cost"])
    return usage.get("prompt_tokens", 0) * INPUT_RATE + usage.get("completion_tokens", 0) * OUTPUT_RATE


def load_grades(path=LOG):
    grades = defaultdict(dict)
    if path.exists():
        for r in map(json.loads, path.open(encoding="utf-8")):
            for pid, g in r.get("grades", {}).items():
                grades[r["id"]][pid] = g
    return grades


def tasks_for(rankings, limit=None):
    pool = {r["id"]: r for r in map(json.loads, ev.POOL.open(encoding="utf-8")) if r["split"] == "dev"}
    wanted = defaultdict(set)
    for r in map(json.loads, ev.RUNS.open(encoding="utf-8")):
        if r["ranking"] in rankings and r["id"] in pool:
            wanted[r["id"]].update(r["top"][:ev.K])
    done = load_grades()
    products, _ = common.load_index()
    by_category = defaultdict(list)
    tasks = []
    for i, q in pool.items():
        missing = sorted(wanted[i] - set(done.get(i, {})), key=int)
        if missing:
            tasks.append(dict(id=i, query=q["query"], category=q["category"], labels=judge.layout(i, missing)))
    return (tasks[:limit] if limit else tasks), {p["product_id"]: p for p in products}


def execute(tasks, by_id, budget, workers):
    key, lock, state = api_key(), threading.Lock(), dict(spent=sum(
        json.loads(line).get("cost_usd", 0) for line in LOG.open(encoding="utf-8")) if LOG.exists() else 0.0,
        done=0, errors=0, skipped=0)

    def one(task, out):
        reserve = estimated_cost(task, by_id)
        with lock:
            if state["spent"] + reserve > budget:
                state["skipped"] += 1
                return
        paid = 0.0
        try:
            response = call(task, by_id, key)
            usage = response.get("usage", {})
            paid = cost_of(usage)
            record = dict(id=task["id"], query=task["query"], model=MODEL, labels=task["labels"], usage=usage,
                          judged_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), cost_usd=paid,
                          grades=parse(response["choices"][0]["message"]["content"] or "", task["labels"]))
        except Exception as e:
            record = dict(id=task["id"], error=f"{type(e).__name__}: {str(e)[:300]}", cost_usd=paid)
        with lock:
            state["spent"] += record["cost_usd"]
            state["done"] += 1
            state["errors"] += "error" in record
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if state["done"] % 25 == 0:
                print(f"{state['done']}/{len(tasks)}  ${state['spent']:.4f}", flush=True)

    with LOG.open("a", encoding="utf-8") as out, ThreadPoolExecutor(workers) as pool:
        for f in as_completed([pool.submit(one, t, out) for t in tasks]):
            f.result()
    print(f"done {state['done'] - state['errors']}, errors {state['errors']}, skipped by the budget "
          f"{state['skipped']}; spent ${state['spent']:.4f}")


def report(rankings):
    first, second = ev.load_grades(), load_grades()
    a, b = [], []
    for i, grades in second.items():
        for pid, g in grades.items():
            if pid in first.get(i, {}):
                a.append(first[i][pid])
                b.append(g)
    a, b = np.array(a), np.array(b)
    table = np.zeros((4, 4), int)
    np.add.at(table, (a, b), 1)
    expected = (table.sum(1)[:, None] * table.sum(0)[None, :] / table.sum())
    weights = (np.arange(4)[:, None] - np.arange(4)[None, :]) ** 2
    lines = ["# Second judge", "",
             f"{MODEL} graded {len(b)} (query, product) pairs of {len(second)} dev queries that the first judge "
             "also graded.", "",
             f"- same grade: {np.mean(a == b):.1%}; within one grade: {np.mean(abs(a - b) <= 1):.1%}",
             f"- same side of the relevance line (grade >= {ev.RELEVANT}): {np.mean((a >= ev.RELEVANT) == (b >= ev.RELEVANT)):.1%}",
             f"- quadratic weighted kappa: {1 - (weights * table).sum() / (weights * expected).sum():.3f}",
             f"- mean grade: first judge {a.mean():.2f}, second judge {b.mean():.2f}", "",
             "Grades of the first judge in rows, of the second judge in columns:", "",
             "| | 0 | 1 | 2 | 3 |", "| --- | ---: | ---: | ---: | ---: |"]
    lines += [f"| {g} | " + " | ".join(map(str, table[g])) + " |" for g in range(4)]
    runs = defaultdict(dict)
    for r in map(json.loads, ev.RUNS.open(encoding="utf-8")):
        if r["ranking"] in rankings and r["id"] in second:
            runs[r["ranking"]][r["id"]] = r["top"]
    for title, grades in (("first judge, on the products the second judge graded", {
            i: {p: g for p, g in first[i].items() if p in second[i]} for i in second}), ("second judge", second)):
        per = {n: {i: ev.metrics(top, grades[i]) for i, top in tops.items()} for n, tops in runs.items()}
        lines += ["", f"## Metrics by the {title}", "",
                  "| ranking | nDCG@10 | MRR | P@1 | nDCG difference to hybrid_details_w0.25 | ungraded |",
                  "| --- | ---: | ---: | ---: | ---: | ---: |"]
        base = per.get("hybrid_details_w0.25", {})
        for n in [r for r in rankings if r in per]:
            m = per[n]
            cells = [f"{np.mean([x[k] for x in m.values() if x[k] is not None]):.3f}" for k in ("ndcg", "mrr", "p1")]
            d = [m[i]["ndcg"] - base[i]["ndcg"] for i in m if i in base and m[i]["ndcg"] is not None
                 and base[i]["ndcg"] is not None]
            diff = "{:+.3f} [{:+.3f}, {:+.3f}]".format(*ev.bootstrap(d)) if d and n != "hybrid_details_w0.25" else "-"
            lines.append(f"| {n} | " + " | ".join(cells) + f" | {diff} | {np.mean([x['unjudged'] for x in m.values()]):.2f} |")
    (ev.DATA / "report_judge2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--report", action="store_true", help="agreement and metrics, no API calls")
    ap.add_argument("--rankings", nargs="+", default=list(RANKINGS))
    ap.add_argument("--limit", type=int, help="at most this many queries")
    ap.add_argument("--budget-usd", type=float, default=2.0, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    if args.report:
        return report(args.rankings)
    tasks, by_id = tasks_for(set(args.rankings), args.limit)
    estimate = sum(estimated_cost(t, by_id) for t in tasks)
    print(f"{len(tasks)} calls for {sum(len(t['labels']) for t in tasks)} (query, product) pairs, model {MODEL}; "
          f"estimate ${estimate:.2f}, budget ${args.budget_usd:.2f}")
    if args.execute and tasks:
        execute(tasks, by_id, args.budget_usd, args.workers)


if __name__ == "__main__":
    main()
