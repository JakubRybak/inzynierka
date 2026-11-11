"""
Relevance grades 0-3 for the pooled (query, product) pairs from Gemini. One call per query grades all of its pooled
products without a grade: the query, then each product's name, brand, description, composition and main image, in a
shuffled order under neutral labels. The judge never sees which ranking returned a product.

    python search_ui/evaluation/judge.py                  # plan and cost estimate, no API calls
    python search_ui/evaluation/judge.py --execute        # paid calls

Every call is appended to data/judgments.jsonl; a rerun grades only what is missing for the current prompt version.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import random
import re

from evaluate import HERE, JUDGMENTS, POOL, common
import vertex  # noqa: E402  (search_ui/, put on the path by evaluate)

SYSTEM = HERE / "judge_system.txt"
POSE = "id_gridfs_1"
THINKING_TOKENS = 2000
MAX_OUTPUT = 8192


def prompt_version(thinking):
    blob = json.dumps(dict(model=vertex.MODEL, thinking=thinking, pose=POSE, temperature=0), sort_keys=True)
    return hashlib.sha256((blob + SYSTEM.read_text(encoding="utf-8")).encode()).hexdigest()[:12]


def judged(version):
    done = {}
    if JUDGMENTS.exists():
        for r in map(json.loads, JUDGMENTS.open(encoding="utf-8")):
            if r.get("prompt_version") == version and "grades" in r:
                done.setdefault(r["id"], set()).update(r["grades"])
    return done


def main_image(p):
    return next((path for path in p["images"] if re.search(rf"{POSE}\.", path)), p["images"][0])


def layout(query_id, product_ids):
    order = list(product_ids)
    random.Random(query_id).shuffle(order)
    return {f"P{i + 1:02d}": pid for i, pid in enumerate(order)}


def product_text(label, p):
    return f"{label}: {p['name']} | {p['brand']} | {p['description']} | Composition: {p['composition']}"


def body(task, by_id, thinking):
    parts = [{"text": f"Query: {task['query']}\nCategory of the results: {task['category']}\n\nProducts:"}]
    for label, pid in task["labels"].items():
        p = by_id[pid]
        parts.append({"text": product_text(label, p)})
        if p["images"]:
            data = base64.b64encode((common.DATASET / main_image(p)).read_bytes()).decode()
            parts.append({"inlineData": {"mimeType": "image/png", "data": data}})
    labels = list(task["labels"])
    config = {"temperature": 0, "maxOutputTokens": MAX_OUTPUT, "mediaResolution": "MEDIA_RESOLUTION_MEDIUM",
              "responseMimeType": "application/json",
              "responseSchema": {"type": "OBJECT", "required": labels, "propertyOrdering": labels,
                                 "properties": {k: {"type": "INTEGER", "minimum": 0, "maximum": 3} for k in labels}}}
    if thinking != "NONE":
        config["thinkingConfig"] = {"thinkingLevel": thinking}
    return {"systemInstruction": {"parts": [{"text": SYSTEM.read_text(encoding="utf-8")}]},
            "contents": [{"role": "user", "parts": parts}], "generationConfig": config}


def estimated_cost(task, by_id, thinking):
    chars = len(SYSTEM.read_text(encoding="utf-8")) + 200 + sum(len(product_text(k, by_id[p]))
                                                                 for k, p in task["labels"].items())
    out = 8 * len(task["labels"]) + (0 if thinking == "NONE" else THINKING_TOKENS)
    return vertex.estimate(chars, out, images=len(task["labels"]))


def parse(response, labels):
    text = vertex.response_text(response)
    grades = json.loads(text)
    if set(grades) != set(labels) or not all(isinstance(g, int) and 0 <= g <= 3 for g in grades.values()):
        raise ValueError(f"invalid grades: {text[:200]}")
    return {labels[k]: g for k, g in grades.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--thinking", default="MEDIUM", choices=["NONE", "MINIMAL", "LOW", "MEDIUM"])
    ap.add_argument("--limit", type=int, help="at most this many queries")
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--budget-usd", type=float, default=4.0, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    products, _ = common.load_index()
    by_id = {p["product_id"]: p for p in products}
    version = prompt_version(args.thinking)
    done = judged(version)
    tasks = []
    for r in map(json.loads, POOL.open(encoding="utf-8")):
        if args.split != "all" and r["split"] != args.split:
            continue
        missing = [pid for pid in r["product_ids"] if pid not in done.get(r["id"], set())]
        if missing:
            tasks.append(dict(id=r["id"], query=r["query"], category=r["category"], labels=layout(r["id"], missing)))
    tasks = tasks[:args.limit] if args.limit else tasks
    costs = [estimated_cost(t, by_id, args.thinking) for t in tasks]
    spent = vertex.spent_in(JUDGMENTS)
    print(f"{len(tasks)} calls for {sum(len(t['labels']) for t in tasks)} (query, product) pairs, model "
          f"{vertex.MODEL}, thinking {args.thinking}, prompt version {version}; estimate up to ${sum(costs):.2f}; "
          f"spent so far ${spent:.4f}, budget ${args.budget_usd:.2f}")
    if not (args.execute and tasks):
        return

    def work(task, client):
        response = client(body(task, by_id, args.thinking))
        return dict(id=task["id"], query=task["query"], model=vertex.MODEL, thinking=args.thinking,
                    prompt_version=version, labels=task["labels"], usage=response.get("usageMetadata", {}),
                    judged_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    grades=parse(response, task["labels"]))

    vertex.run(tasks, costs, work, JUDGMENTS, args.budget_usd, spent, args.workers)


if __name__ == "__main__":
    main()
