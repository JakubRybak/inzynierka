"""
Step B: offline scores 0-10 for (product, concept). One Gemini call per product rates every concept that has no
score for it yet, from the name, brand, description, composition, extracted features and two images
(poses 1 and 3, or the one of them the product has).

    python poc/concepts/score_products.py --category Dresses --limit 20            # prepare only, no API calls
    python poc/concepts/score_products.py --category Dresses --limit 20 --execute  # paid calls

Every call is logged in data/scores.jsonl. results/concept_scores.parquet (product_id, concept_id, score, model,
prompt_version, scored_at) is rebuilt from it after each run. --log NAME writes to data/NAME.jsonl instead and leaves
the parquet alone (comparisons, repeated scoring). --review writes data/<log>_review.html.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import random
import re
import sys
import threading
import time

import pandas as pd
import yaml

from derive_concepts import REPO, call_cost, retry
sys.path.insert(0, str(REPO / "poc/search_ui"))
import common  # noqa: E402
from query_parser import DEFAULT_PROJECT  # noqa: E402

HERE = Path(__file__).resolve().parent
CONCEPTS = HERE / "concepts.yaml"
SYSTEM = HERE / "prompts/score_system.txt"
USER = HERE / "prompts/score_prompt.md"
DATA = HERE / "data"
MAIN_LOG = "scores"
SCORES = HERE / "results/concept_scores.parquet"
MODEL = "gemini-3.5-flash-lite"
POSES = ("id_gridfs_1", "id_gridfs_3")
TYPES = ("occasion", "style", "season")
IMAGE_TOKENS = 530  # one 256x256 image at MEDIA_RESOLUTION_MEDIUM, measured in the extraction runs
THINKING_TOKENS = 1500
MAX_OUTPUT = 4096


def load_concepts(path=CONCEPTS):
    concepts = yaml.safe_load(path.read_text(encoding="utf-8"))
    for c in concepts:
        if set(c) != {"id", "name", "type", "added"} or c["type"] not in TYPES \
                or not re.fullmatch(r"[a-z][a-z0-9_]*", str(c["id"])):
            raise SystemExit(f"{path.name}: invalid entry {c}")
        c["added"] = str(c["added"])
    for field in ("id", "name"):
        values = [c[field] for c in concepts]
        if len(set(values)) != len(values):
            raise SystemExit(f"{path.name}: duplicate {field}")
    return concepts


def user_template():
    return re.search(r"```text\n(.*?)```", USER.read_text(encoding="utf-8"), re.DOTALL).group(1).strip()


def settings(thinking):
    return dict(model=MODEL, thinking=thinking, temperature=0, media_resolution="MEDIA_RESOLUTION_MEDIUM",
                poses=POSES, max_output_tokens=MAX_OUTPUT)


def prompt_version(thinking):
    blob = json.dumps(settings(thinking), sort_keys=True) + SYSTEM.read_text(encoding="utf-8") + user_template()
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def images(p):
    by_pose = {re.search(r"id_gridfs_\d+", path).group(0): path for path in p["images"]}
    return [by_pose[pose] for pose in POSES if pose in by_pose] or None


def user_text(p, concepts):
    product = dict(category=p["category"], name=p["name"], brand=p["brand"], description=p["description"],
                   composition=p["composition"], features=p["features"])
    lines = "\n".join(f"- {c['id']}: {c['name']} ({c['type']})" for c in concepts)
    return user_template().replace("{product}", json.dumps(product, ensure_ascii=False)).replace("{concepts}", lines)


def schema(concepts):
    ids = [c["id"] for c in concepts]
    return {"type": "OBJECT", "required": ids, "propertyOrdering": ids,
            "properties": {i: {"type": "INTEGER", "minimum": 0, "maximum": 10} for i in ids}}


def body(p, concepts, thinking):
    parts = [{"text": user_text(p, concepts)}]
    for path in images(p):
        data = base64.b64encode((common.DATASET / path).read_bytes()).decode()
        parts.append({"inlineData": {"mimeType": "image/png", "data": data}})
    config = {"temperature": 0, "maxOutputTokens": MAX_OUTPUT, "mediaResolution": "MEDIA_RESOLUTION_MEDIUM",
              "responseMimeType": "application/json", "responseSchema": schema(concepts)}
    if thinking != "NONE":
        config["thinkingConfig"] = {"thinkingLevel": thinking}
    return {"systemInstruction": {"parts": [{"text": SYSTEM.read_text(encoding="utf-8")}]},
            "contents": [{"role": "user", "parts": parts}], "generationConfig": config}


def estimated_cost(p, concepts, thinking):
    """Upper estimate: 4 characters per text token, measured image tokens, full thinking allowance."""
    text = len(SYSTEM.read_text(encoding="utf-8")) + len(user_text(p, concepts)) + len(json.dumps(schema(concepts)))
    tokens_in = text / 4 + len(POSES) * IMAGE_TOKENS
    tokens_out = 10 * len(concepts) + (0 if thinking == "NONE" else THINKING_TOKENS)
    return call_cost({"promptTokenCount": tokens_in, "candidatesTokenCount": tokens_out})


def parse_scores(response, ids):
    candidate = response["candidates"][0]
    if candidate.get("finishReason") != "STOP":
        raise ValueError(f"finishReason {candidate.get('finishReason')}")
    text = "".join(part.get("text", "") for part in candidate["content"]["parts"] if not part.get("thought"))
    scores = json.loads(text)
    if set(scores) != set(ids) or not all(type(v) is int and 0 <= v <= 10 for v in scores.values()):
        raise ValueError(f"invalid scores: {text[:300]}")
    return {i: scores[i] for i in ids}


def read_log(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def to_frame(log):
    rows = {}
    for r in log:
        for cid, score in (r.get("scores") or {}).items():
            rows[(r["product_id"], cid)] = dict(product_id=r["product_id"], concept_id=cid, score=score,
                                                model=r["model"], prompt_version=r["prompt_version"],
                                                scored_at=r["scored_at"])
    return pd.DataFrame(list(rows.values()), columns=["product_id", "concept_id", "score", "model",
                                                      "prompt_version", "scored_at"]).astype({"score": "int8"})


def summary(scores, products, concepts):
    d = scores[scores["product_id"].isin({p["product_id"] for p in products})]
    if d.empty:
        return
    stats = d.groupby("concept_id")["score"].agg(n="size", mean="mean", high=lambda s: int((s >= 7).sum()))
    print(f"\n{d['product_id'].nunique()} products scored; per concept: mean, products with score >= 7")
    for c in concepts:
        if c["id"] in stats.index:
            s = stats.loc[c["id"]]
            print(f"  {c['type']:8s} {c['name']:16s} {s['mean']:4.1f}  {int(s['high']):3d}/{int(s['n'])}")


def review(scores, products, concepts, path):
    by_product = {pid: dict(zip(g["concept_id"], g["score"])) for pid, g in scores.groupby("product_id")}
    cards = []
    for p in products:
        if p["product_id"] not in by_product:
            continue
        s = by_product[p["product_id"]]
        imgs = "".join(f'<img src="{html.escape(os.path.relpath(common.DATASET / image, path.parent))}">'
                       for image in images(p))
        rows = "".join(f'<tr class="s{s[c["id"]]}"><td>{c["name"]}</td><td>{s[c["id"]]}</td></tr>'
                       for c in sorted((c for c in concepts if c["id"] in s), key=lambda c: -s[c["id"]]))
        cards.append(f'<div class="card"><div>{imgs}</div><h3>{html.escape(p["brand"])} – {html.escape(p["name"])}'
                     f'</h3><p>{html.escape(p["description"])}</p><table>{rows}</table></div>')
    style = ("body{font:14px sans-serif;margin:16px}.card{border:1px solid #ccc;padding:12px;margin:12px 0}"
             "img{width:200px;margin-right:8px}table{border-collapse:collapse}td{padding:1px 8px}"
             + "".join(f".s{i}{{background:hsl(140,60%,{100 - 5 * i}%)}}" for i in range(11)))
    path.write_text(f"<!doctype html><meta charset=utf-8><title>Concept scores</title><style>{style}</style>"
                      + "".join(cards), encoding="utf-8")
    print(f"{len(cards)} products -> {path.relative_to(REPO)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--category", help="only this category, e.g. Dresses")
    ap.add_argument("--concepts", help="comma-separated concept ids; default all from concepts.yaml")
    ap.add_argument("--limit", type=int, help="score at most this many products now")
    ap.add_argument("--thinking", default="MEDIUM", choices=["NONE", "MINIMAL", "LOW", "MEDIUM"])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--budget-usd", type=float, default=0.25, help="total for the log, earlier runs included")
    ap.add_argument("--log", default=MAIN_LOG, help="log name in data/; only the main log updates the parquet")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--review", action="store_true", help="write an HTML page with images and scores")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9_-]+", args.log):
        ap.error("--log: lowercase letters, digits, _ and - only")
    log_path = DATA / f"{args.log}.jsonl"

    concepts = load_concepts()
    if args.concepts:
        wanted = args.concepts.split(",")
        if set(wanted) - {c["id"] for c in concepts}:
            raise SystemExit(f"unknown concepts: {sorted(set(wanted) - {c['id'] for c in concepts})}")
        concepts = [c for c in concepts if c["id"] in wanted]
    products, _ = common.load_index()
    if args.category:
        if args.category not in {p["category"] for p in products}:
            raise SystemExit(f"no products in category {args.category!r}")
        products = [p for p in products if p["category"] == args.category]
    products.sort(key=lambda p: p["product_id"])
    random.Random(0).shuffle(products)
    without_images = [p["product_id"] for p in products if images(p) is None]
    if without_images:
        print(f"skipped, no {' or '.join(POSES)} image: {without_images}")
        products = [p for p in products if images(p) is not None]

    log = read_log(log_path)
    scored = {(r["product_id"], cid) for r in log for cid in (r.get("scores") or {})}
    tasks = [(p, [c for c in concepts if (p["product_id"], c["id"]) not in scored]) for p in products]
    tasks = [(p, cs) for p, cs in tasks if cs][:args.limit]
    version, spent = prompt_version(args.thinking), sum(r["cost_usd"] for r in log)
    costs = [estimated_cost(p, cs, args.thinking) for p, cs in tasks]
    print(f"{len(products)} products, {len(concepts)} concepts, {len(tasks)} calls now (up to ${sum(costs):.2f}); "
          f"prompt version {version}, thinking {args.thinking}; log {log_path.name}, spent so far ${spent:.4f}, "
          f"budget ${args.budget_usd:.2f}")

    if tasks and not args.execute:
        p, cs = tasks[0]
        print(f"\nFirst request ({p['product_id']}), images {images(p)}:\n\n{user_text(p, cs)}")
        print("\nadd --execute to make the calls")
    elif tasks:
        run(tasks, costs, version, spent, args, log_path)
    log = read_log(log_path)
    if log:
        scores = to_frame(log)
        if args.log == MAIN_LOG:
            SCORES.parent.mkdir(exist_ok=True)
            scores.to_parquet(SCORES, index=False)
        summary(scores, products, concepts)
        if args.review:
            review(scores, products, concepts, DATA / f"{args.log}_review.html")


def run(tasks, costs, version, spent, args, log_path):
    import google.auth
    from google.auth.transport.requests import AuthorizedSession, Request
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", DEFAULT_PROJECT)
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"],
                                         quota_project_id=project)
    credentials.refresh(Request())
    session = AuthorizedSession(credentials.with_quota_project(project), max_refresh_attempts=1)
    endpoint = (f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/google/"
                f"models/{MODEL}:generateContent")
    lock, state = threading.Lock(), dict(spent=spent, reserved=0.0, done=0, errors=0, skipped=0)

    def post(request):
        r = session.post(endpoint, json=request, timeout=120)
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        return r.json()

    def work(p, concepts, reserve, out):
        with lock:
            if state["spent"] + state["reserved"] + reserve > args.budget_usd:
                state["skipped"] += 1
                return
            state["reserved"] += reserve
        ids = [c["id"] for c in concepts]
        record = dict(product_id=p["product_id"], category=p["category"], concepts=ids, model=MODEL,
                      thinking=args.thinking, prompt_version=version,
                      scored_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), images=images(p))
        start = time.monotonic()
        try:
            request = body(p, concepts, args.thinking)
            response = retry(lambda: post(request))
            record.update(usage=response.get("usageMetadata", {}))
            record["cost_usd"] = call_cost(record["usage"]) if record["usage"] else reserve
            record["scores"] = parse_scores(response, ids)
        except Exception as e:
            record["error"] = f"{type(e).__name__}: {str(e)[:300]}"
            record.setdefault("cost_usd", reserve)
        record["seconds"] = round(time.monotonic() - start, 2)
        with lock:
            state["reserved"] -= reserve
            state["spent"] += record["cost_usd"]
            state["done"] += 1
            state["errors"] += "error" in record
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if "error" in record:
                print(f"error {p['product_id']}: {record['error']}", flush=True)
            if state["done"] % 25 == 0:
                print(f"{state['done']}/{len(tasks)}  ${state['spent']:.4f}", flush=True)

    DATA.mkdir(exist_ok=True)
    pool = ThreadPoolExecutor(args.workers)
    try:
        with log_path.open("a", encoding="utf-8") as out:
            for f in as_completed([pool.submit(work, p, cs, cost, out) for (p, cs), cost in zip(tasks, costs)]):
                f.result()
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    pool.shutdown()
    print(f"scored {state['done'] - state['errors']}, errors {state['errors']}, skipped by the budget "
          f"{state['skipped']}; spent ${state['spent']:.4f}")


if __name__ == "__main__":
    main()
