"""
Details of every product (lace, sequins, cable knit, a skull graphic, ripped knees), from its name, description and
two photos, given offline by Gemini: each detail with a name and an extent (all-over, part or small).

    python search_ui/offline/product_details.py --sample 120 --log pilot                     # plan only, no API calls
    python search_ui/offline/product_details.py --sample 120 --log pilot --execute --review  # paid calls, review page
    python search_ui/offline/product_details.py --batch --bucket <bucket> --execute          # all products, Batch API

Every call is logged in search_ui/data/product_details/<log>.jsonl; a rerun asks only about products missing from
the log. --sample takes products spread over the categories, half of them at random and half among those whose
description names a detail, so that both plain and detailed products are checked. --review writes an HTML page with
the photos, the description and the details. --batch sends the same requests through Vertex AI batch prediction at
half the price, with the photos in Cloud Storage (the ones uploaded for the concept scores are reused). The main log
rebuilds ranking_data/product_details.parquet.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import batch  # noqa: E402
import common  # noqa: E402
import vertex  # noqa: E402
from product_colors import read_log, stratified  # noqa: E402
from score_concepts import images  # noqa: E402

SYSTEM = Path(__file__).resolve().parent / "prompts/detail_system.txt"
DATA = common.DATA / "product_details"
MAIN_LOG = "details"
OUTPUT = common.SEARCH_UI / "ranking_data/product_details.parquet"
EXTENTS = ["all-over", "part", "small"]
THINKING = "MINIMAL"
DETAILED = re.compile(r"lace|sequin|bead|embroider|ruffle|fringe|stud|crochet|eyelet|cable|quilt|mesh|sheer|pleat|"
                      r"cut-?out|slit|graphic|print|logo|distress|ripped|patch|tie-dye|bow|tassel|feather|metallic|"
                      r"velvet|appliqu", re.I)


def schema():
    detail = {"type": "OBJECT", "required": ["name", "extent"], "propertyOrdering": ["name", "extent"],
              "properties": {"name": {"type": "STRING"}, "extent": {"type": "STRING", "enum": EXTENTS}}}
    return {"type": "OBJECT", "required": ["details"],
            "properties": {"details": {"type": "ARRAY", "maxItems": 8, "items": detail}}}


def prompt_version():
    blob = json.dumps(dict(model=vertex.MODEL, thinking=THINKING, schema=schema()), sort_keys=True)
    return hashlib.sha256((blob + SYSTEM.read_text(encoding="utf-8")).encode()).hexdigest()[:12]


def user_text(p):
    return (f"Category: {p['category']}\nProduct name: {html.unescape(p['name'])}\n"
            f"Description: {html.unescape(p.get('description') or '')}")


def body(p, uri=None):
    """The request; uri(path) gives the Cloud Storage URI of a photo for a batch request, otherwise photos go inline."""
    photos = [{"fileData": {"mimeType": "image/png", "fileUri": uri(path)}} if uri else
              {"inlineData": {"mimeType": "image/png", "data": base64.b64encode((common.DATASET / path).read_bytes())
                              .decode()}} for path in images(p)]
    config = {"temperature": 0, "maxOutputTokens": 1024, "mediaResolution": "MEDIA_RESOLUTION_MEDIUM",
              "responseMimeType": "application/json", "responseSchema": schema(),
              "thinkingConfig": {"thinkingLevel": THINKING}}
    return {"systemInstruction": {"parts": [{"text": SYSTEM.read_text(encoding="utf-8")}]},
            "contents": [{"role": "user", "parts": [{"text": user_text(p)}, *photos]}],
            "generationConfig": config}


def parse_details(response):
    details = json.loads(vertex.response_text(response))["details"]
    out, seen = [], set()
    for d in details:
        name = " ".join(d["name"].strip().lower().split())
        if d["extent"] not in EXTENTS:
            raise ValueError(f"invalid extent: {d}")
        if name and name not in seen:
            seen.add(name)
            out.append(dict(name=name, extent=d["extent"]))
    return out


def record_for(p, version, response):
    return dict(id=p["product_id"], product_id=p["product_id"], category=p["category"], name=p["name"],
                images=images(p), model=vertex.MODEL, thinking=THINKING, prompt_version=version,
                at=datetime.now(timezone.utc).isoformat(timespec="seconds"), usage=response.get("usageMetadata", {}),
                details=parse_details(response))


def to_frame(log):
    """One row per product and detail, the latest record of each product; a product without details has no rows."""
    latest = {r["product_id"]: r for r in log if "details" in r}
    return pd.DataFrame([dict(product_id=pid, rank=i, **d, model=r["model"], prompt_version=r["prompt_version"])
                         for pid, r in latest.items() for i, d in enumerate(r["details"])],
                        columns=["product_id", "rank", "name", "extent", "model", "prompt_version"])


def pilot(products, n, seed=0):
    """n products over the categories: half at random, half among those whose description names a detail."""
    rich = [p for p in products if DETAILED.search(p.get("description") or "")]
    chosen = stratified(rich, n - n // 2, seed)
    ids = {p["product_id"] for p in chosen}
    return chosen + stratified([p for p in products if p["product_id"] not in ids], n // 2, seed)


def review(log, products, path):
    by_id = {p["product_id"]: p for p in products}
    cards = []
    for r in sorted((r for r in log if "details" in r), key=lambda r: (r["category"], r["product_id"])):
        p = by_id.get(r["product_id"])
        if p is None:
            continue
        photos = "".join(f'<img src="data:image/png;base64,{base64.b64encode((common.DATASET / path).read_bytes()).decode()}">'
                         for path in images(p))
        chips = "".join(f'<span class="chip {d["extent"]}">{html.escape(d["name"])} · {d["extent"]}</span>'
                        for d in r["details"]) or '<span class="none">no details</span>'
        cards.append(f'<div class="card">{photos}<div><b>{html.escape(html.unescape(p["name"]))}</b> '
                     f'<small>{html.escape(p["category"])}</small><p>{html.escape(html.unescape(p.get("description") or ""))}'
                     f'</p>{chips}</div></div>')
    style = ("body{font:14px sans-serif;margin:16px;background:#fff;color:#111}.card{display:flex;gap:12px;border:1px "
             "solid #ccc;padding:10px;margin:10px 0}img{width:150px;height:150px}p{color:#444;margin:6px 0}"
             ".chip{display:inline-block;border-radius:10px;padding:2px 8px;margin:3px;border:1px solid #999}"
             ".all-over{background:#f4c7c3}.part{background:#fde293}.small{background:#e8eaed}.none{color:#888}")
    path.write_text(f"<!doctype html><meta charset=utf-8><title>Product details</title><style>{style}</style>"
                    + "".join(cards), encoding="utf-8")
    print(f"{len(cards)} products -> {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, help="only N products: half at random, half with a detail in the description")
    ap.add_argument("--log", default=MAIN_LOG, help="log name in data/product_details/; only the main log writes the parquet")
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--budget-usd", type=float, default=0.12, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--review", action="store_true", help="write an HTML page with the photos and the details")
    ap.add_argument("--batch", action="store_true", help="use Vertex AI batch prediction (half price)")
    ap.add_argument("--bucket", help="Cloud Storage bucket the Vertex service agent can read (--batch)")
    ap.add_argument("--prefix", default="product-details", help="folder of the batch jobs in the bucket")
    ap.add_argument("--image-prefix", default="concept-scores/images", help="folder of the uploaded photos")
    ap.add_argument("--chunk", type=int, default=1500, help="requests per batch job")
    ap.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args()

    products, _ = common.load_index()
    products = [p for p in products if images(p)]
    chosen = pilot(products, args.sample) if args.sample else products
    log_path = DATA / f"{args.log}.jsonl"
    version = prompt_version()
    done = {r["product_id"] for r in read_log(log_path) if "details" in r and r.get("prompt_version") == version}
    tasks = [dict(id=p["product_id"], product=p) for p in chosen if p["product_id"] not in done]
    system = len(SYSTEM.read_text(encoding="utf-8"))
    # 150 output tokens: the longest answer of the pilot (65 on average)
    costs = [vertex.estimate(system + len(user_text(t["product"])), 150, images=len(images(t["product"])))
             for t in tasks]
    if args.batch:
        costs = [c / 2 for c in costs]
    spent = vertex.spent_in(log_path)
    print(f"{len(chosen)} products in {len({p['category'] for p in chosen})} categories, {len(tasks)} "
          f"{'batch requests' if args.batch else 'calls'} now (up to ${sum(costs):.3f}); prompt version {version}; "
          f"log {log_path.name}, spent so far ${spent:.4f}, budget ${args.budget_usd:.2f}")
    if tasks and args.execute and args.batch:
        if not args.bucket:
            ap.error("--batch needs --bucket")
        if spent + sum(costs) > args.budget_usd:
            raise SystemExit(f"estimate ${spent + sum(costs):.2f} with earlier runs is over --budget-usd {args.budget_usd}")
        DATA.mkdir(parents=True, exist_ok=True)
        batch.run([t["product"] for t in tasks], folder=DATA / f"batch_{args.log}", log_path=log_path,
                  bucket=args.bucket, prefix=args.prefix, image_prefix=args.image_prefix, display="product-details",
                  paths=images, request=body, record=lambda p, response: record_for(p, version, response),
                  chunk=args.chunk, poll_seconds=args.poll_seconds)
    elif tasks and args.execute:
        def work(task, client):
            return record_for(task["product"], version, client(body(task["product"]), timeout=120))

        DATA.mkdir(parents=True, exist_ok=True)
        vertex.run(tasks, costs, work, log_path, args.budget_usd, spent, args.workers)
    log = [r for r in read_log(log_path) if r.get("prompt_version") == version]
    if log and args.log == MAIN_LOG:
        frame = to_frame(log)
        frame.to_parquet(OUTPUT, index=False)
        print(f"{frame['product_id'].nunique()} of {len({r['product_id'] for r in log if 'details' in r})} products "
              f"with details, {len(frame)} details, {frame['name'].nunique()} names -> {OUTPUT}")
    if log and args.review:
        review(log, products, DATA / f"{args.log}_review.html")


if __name__ == "__main__":
    main()
