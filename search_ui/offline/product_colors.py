"""
Colours of every product, from its name and main photo, given offline by Gemini: one to three colours with a name,
a colour family, a hex value and a share of the product.

    python search_ui/offline/product_colors.py --sample 50 --log pilot             # plan only, no API calls
    python search_ui/offline/product_colors.py --sample 50 --log pilot --execute   # paid calls
    python search_ui/offline/product_colors.py --batch --bucket <bucket> --execute # all products, Batch API

Every call is logged in search_ui/data/product_colors/<log>.jsonl; a rerun colours only products missing from the
log. The main log also rebuilds the colour dictionary ranking_data/color_names.parquet: every colour name of the
products with its typical hex, family and product count; Gemini tells colour names from the other names the products
got ("leopard print", "grey knit"), which are left out (about $0.001, logged in data/product_colors/names.jsonl).
--batch sends the same requests through Vertex AI batch prediction at half the price, with the photos in Cloud
Storage (the ones uploaded for the concept scores are reused); the jobs are kept in data/product_colors/batch_<log>/
state.json, so a rerun resumes them. The main log rebuilds ranking_data/product_colors.parquet. --review writes an HTML page with the photos and
colour swatches.
"""
import argparse
import base64
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import random
import re
import sys
import time
from urllib.parse import quote

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import common  # noqa: E402
import vertex  # noqa: E402

HERE = Path(__file__).resolve().parent
SYSTEM = HERE / "prompts/color_system.txt"
DATA = common.DATA / "product_colors"
MAIN_LOG = "colors"
OUTPUT = common.SEARCH_UI / "ranking_data/product_colors.parquet"
NAMES = common.SEARCH_UI / "ranking_data/color_names.parquet"
NAMES_LOG = DATA / "names.jsonl"
NAME_CHECK = """For each name below, which describes the colour of a clothing product, say whether it is a colour name: a hue
or a shade, possibly with a lightness or tone ("light blue", "dusty rose", "light wash blue", "burgundy", "metallic
silver", "neon green", "heather grey"). Answer false when the name describes a pattern, a print, a texture, a material,
a finish other than a colour, or an object ("leopard print", "camo", "grey knit", "distressed white", "sheer white",
"strawberry"). Answer for every name, in the given order."""
FAMILIES = ["Black", "White", "Grey", "Blue", "Red", "Green", "Pink", "Beige", "Brown", "Yellow", "Orange", "Purple"]
THINKING = "MINIMAL"
HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def schema():
    colour = {"type": "OBJECT", "required": ["name", "family", "hex", "share"],
              "propertyOrdering": ["name", "family", "hex", "share"],
              "properties": {"name": {"type": "STRING"}, "family": {"type": "STRING", "enum": FAMILIES},
                             "hex": {"type": "STRING"}, "share": {"type": "NUMBER", "minimum": 0, "maximum": 1}}}
    return {"type": "OBJECT", "required": ["colors"],
            "properties": {"colors": {"type": "ARRAY", "minItems": 1, "maxItems": 3, "items": colour}}}


def prompt_version():
    blob = json.dumps(dict(model=vertex.MODEL, thinking=THINKING, schema=schema()), sort_keys=True)
    return hashlib.sha256((blob + SYSTEM.read_text(encoding="utf-8")).encode()).hexdigest()[:12]


def main_image(p):
    return next((path for path in p["images"] if "id_gridfs_1." in path), p["images"][0] if p["images"] else None)


def user_text(p):
    return f"Category: {p['category']}\nProduct name: {html.unescape(p['name'])}"


def body(p, file_uri=None):
    image = {"fileData": {"mimeType": "image/png", "fileUri": file_uri}} if file_uri else \
        {"inlineData": {"mimeType": "image/png",
                        "data": base64.b64encode((common.DATASET / main_image(p)).read_bytes()).decode()}}
    config = {"temperature": 0, "maxOutputTokens": 1024, "mediaResolution": "MEDIA_RESOLUTION_MEDIUM",
              "responseMimeType": "application/json", "responseSchema": schema(),
              "thinkingConfig": {"thinkingLevel": THINKING}}
    return {"systemInstruction": {"parts": [{"text": SYSTEM.read_text(encoding="utf-8")}]},
            "contents": [{"role": "user", "parts": [{"text": user_text(p)}, image]}],
            "generationConfig": config}


def parse_colors(response):
    colors = json.loads(vertex.response_text(response))["colors"]
    for c in colors:
        c["hex"] = "#" + c["hex"].strip().lstrip("#")
    if not colors or not all(HEX.fullmatch(c["hex"]) and c["family"] in FAMILIES for c in colors):
        raise ValueError(f"invalid colours: {colors}")
    total = sum(max(c["share"], 0) for c in colors) or 1
    return [dict(name=c["name"].strip().lower(), family=c["family"], hex=c["hex"].upper(),
                 share=round(max(c["share"], 0) / total, 3)) for c in colors]


def lab(hex_value):
    """CIELAB (L*, a*, b*) of an sRGB hex colour, D65."""
    rgb = [int(hex_value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    xyz = ((0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b,
           (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883)
    fx, fy, fz = [t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116 for t in xyz]
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def name_key(name):
    return " ".join(name.replace("-", " ").lower().split())


def name_table(frame):
    """Every colour name of the products: the hex nearest the mean colour in Lab, the commonest family, products."""
    rows = []
    for key, g in frame.assign(key=frame["name"].map(name_key)).groupby("key"):
        points = [lab(h) for h in g["hex"]]
        centre = [sum(c) / len(points) for c in zip(*points)]
        nearest = min(range(len(points)), key=lambda i: sum((a - b) ** 2 for a, b in zip(points[i], centre)))
        rows.append(dict(name=key, hex=g["hex"].iloc[nearest], family=g["family"].mode()[0],
                         products=g["product_id"].nunique()))
    return pd.DataFrame(rows)


def check_names(names, budget):
    """-> {name: is a colour name}, asking Gemini only about names not in the log yet."""
    v = hashlib.sha256((NAME_CHECK + vertex.MODEL).encode()).hexdigest()[:12]
    done = {x["name"]: x["colour"] for r in read_log(NAMES_LOG) if r.get("prompt_version") == v for x in r["items"]}
    todo = [n for n in names if n not in done]
    tasks = [dict(id=f"names-{k}", names=todo[k:k + 100]) for k in range(0, len(todo), 100)]
    costs = [vertex.estimate(len(NAME_CHECK) + 25 * len(t["names"]), 15 * len(t["names"])) for t in tasks]
    print(f"colour names: {len(names)}, {len(todo)} to check in {len(tasks)} calls (up to ${sum(costs):.4f})")
    if tasks:
        item = {"type": "OBJECT", "required": ["name", "colour"],
                "properties": {"name": {"type": "STRING"}, "colour": {"type": "BOOLEAN"}}}

        def work(task, client):
            text = "Names:\n" + "\n".join(f"{i + 1}. {n}" for i, n in enumerate(task["names"]))
            response = client({"systemInstruction": {"parts": [{"text": NAME_CHECK}]},
                               "contents": [{"role": "user", "parts": [{"text": text}]}],
                               "generationConfig": {"temperature": 0, "maxOutputTokens": 8192,
                                                    "responseMimeType": "application/json",
                                                    "responseSchema": {"type": "OBJECT", "required": ["results"],
                                                                       "properties": {"results": {"type": "ARRAY", "items": item}}},
                                                    "thinkingConfig": {"thinkingLevel": THINKING}}})
            results = json.loads(vertex.response_text(response))["results"]
            if len(results) != len(task["names"]):
                raise ValueError(f"{len(results)} results for {len(task['names'])} names")
            return dict(id=task["id"], prompt_version=v, items=[dict(name=n, colour=bool(r["colour"]))
                                                                 for n, r in zip(task["names"], results)],
                        usage=response.get("usageMetadata", {}))
        vertex.run(tasks, costs, work, NAMES_LOG, budget + vertex.spent_in(NAMES_LOG), vertex.spent_in(NAMES_LOG))
        done = {x["name"]: x["colour"] for r in read_log(NAMES_LOG) if r.get("prompt_version") == v for x in r["items"]}
    return done


def lightness(hex_value):
    """CIELAB L* (0 black, 100 white) of an sRGB hex colour."""
    rgb = [int(hex_value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else 24389 / 27 * y


def read_log(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stratified(products, n, seed=0):
    """n products spread over the categories: shuffled within each category, taken in turns."""
    by_category = defaultdict(list)
    for p in sorted(products, key=lambda p: p["product_id"]):
        by_category[p["category"]].append(p)
    rng = random.Random(seed)
    for group in by_category.values():
        rng.shuffle(group)
    out, k = [], 0
    while len(out) < n and any(k < len(g) for g in by_category.values()):
        out += [g[k] for g in by_category.values() if k < len(g)][:n - len(out)]
        k += 1
    return out


def to_frame(log):
    rows = {}
    for r in log:
        if r.get("colors"):
            rows[r["product_id"]] = [dict(product_id=r["product_id"], rank=i, **c, model=r["model"],
                                          prompt_version=r["prompt_version"]) for i, c in enumerate(r["colors"])]
    return pd.DataFrame([row for group in rows.values() for row in group])


def review(log, products, path):
    by_id = {p["product_id"]: p for p in products}
    cards = []
    for r in log:
        p = by_id.get(r["product_id"])
        if p is None or not r.get("colors"):
            continue
        image = base64.b64encode((common.DATASET / main_image(p)).read_bytes()).decode()
        chips = "".join(f'<div class="chip"><span style="background:{c["hex"]}"></span>{html.escape(c["name"])} · '
                        f'{c["family"]} · {c["hex"]} · L {lightness(c["hex"]):.0f} · {c["share"]:.0%}</div>'
                        for c in r["colors"])
        cards.append(f'<div class="card"><img src="data:image/png;base64,{image}"><div><b>{html.escape(html.unescape(p["name"]))}'
                     f'</b><br><small>{html.escape(p["category"])} · features: '
                     f'{html.escape(", ".join(p["features"].get("colors") or []))}</small>{chips}</div></div>')
    style = ("body{font:14px sans-serif;margin:16px;background:#fff;color:#111}.card{display:flex;gap:16px;border:1px "
             "solid #ccc;padding:10px;margin:10px 0}img{width:180px}.chip{margin-top:8px}.chip span{display:inline-block;"
             "width:44px;height:22px;border:1px solid #999;vertical-align:middle;margin-right:8px}")
    path.write_text(f"<!doctype html><meta charset=utf-8><title>Product colours</title><style>{style}</style>"
                    + "".join(cards), encoding="utf-8")
    print(f"{len(cards)} products -> {path}")


def record_for(p, version, response):
    return dict(id=p["product_id"], product_id=p["product_id"], category=p["category"], name=p["name"],
                image=main_image(p), model=vertex.MODEL, thinking=THINKING, prompt_version=version,
                at=datetime.now(timezone.utc).isoformat(timespec="seconds"), usage=response.get("usageMetadata", {}))


def run_batch(todo, by_id, version, args, log_path):
    import requests
    import score_batch as sb
    folder = DATA / f"batch_{args.log}"
    state_path = folder / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else dict(jobs=[])
    pending = {pid for job in state["jobs"] if not job.get("collected") for pid in job["products"]}
    todo = [p for p in todo if p["product_id"] not in pending]
    folder.mkdir(parents=True, exist_ok=True)
    http, project = sb.session()
    base = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global"
    storage = f"https://storage.googleapis.com/storage/v1/b/{args.bucket}/o"
    upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{args.bucket}/o"

    def save():
        state_path.write_text(json.dumps(state, indent=1), encoding="utf-8")

    def gs(name):
        return f"gs://{args.bucket}/{name}"

    def image_name(path):
        return f"{args.image_prefix}/{path}"

    def upload(name, data, mime, attempts=6):
        for attempt in range(attempts):
            try:
                r = http.post(upload_url, params=dict(uploadType="media", name=name), data=data,
                              headers={"Content-Type": mime}, timeout=120)
                if r.ok:
                    return
                if r.status_code not in (408, 429, 500, 502, 503, 504):
                    raise RuntimeError(f"upload {name}: HTTP {r.status_code} {r.text[:200]}")
            except (requests.ConnectionError, requests.Timeout):
                if attempt == attempts - 1:
                    raise
            time.sleep(2 ** attempt)
        raise RuntimeError(f"upload {name}: still failing after {attempts} attempts")

    def existing(prefix):
        names, params = set(), dict(prefix=prefix, fields="items(name),nextPageToken")
        while True:
            page = http.get(storage, params=params, timeout=60).json()
            names |= {o["name"] for o in page.get("items", [])}
            if not page.get("nextPageToken"):
                return names
            params["pageToken"] = page["nextPageToken"]

    if todo:
        have = {n.split(f"{args.image_prefix}/", 1)[1] for n in existing(f"{args.image_prefix}/")}
        missing = sorted({main_image(p) for p in todo} - have)
        print(f"uploading {len(missing)} images", flush=True)
        with ThreadPoolExecutor(8) as pool:
            list(pool.map(lambda path: upload(image_name(path), (common.DATASET / path).read_bytes(), "image/png"),
                          missing))
        run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        for k in range(0, len(todo), args.chunk):
            chunk = todo[k:k + args.chunk]
            root = f"{args.prefix}/{args.log}-{run}-{k // args.chunk}"
            lines = [json.dumps({"request": body(p, gs(image_name(main_image(p))))}) for p in chunk]
            upload(f"{root}/input.jsonl", ("\n".join(lines) + "\n").encode(), "application/jsonl")
            spec = {"displayName": f"product-colors-{args.log}-{run}-{k // args.chunk}",
                    "model": f"publishers/google/models/{vertex.MODEL}",
                    "inputConfig": {"instancesFormat": "jsonl", "gcsSource": {"uris": [gs(f"{root}/input.jsonl")]}},
                    "outputConfig": {"predictionsFormat": "jsonl", "gcsDestination": {"outputUriPrefix": gs(f"{root}/output")}}}
            r = http.post(f"{base}/batchPredictionJobs", json=spec, timeout=60)
            if not r.ok:
                save()
                raise SystemExit(f"batch submission HTTP {r.status_code}: {r.text[:300]}")
            state["jobs"].append(dict(name=r.json()["name"], root=root, products=[p["product_id"] for p in chunk]))
            save()
            print(f"submitted {state['jobs'][-1]['name']} ({len(chunk)} requests)", flush=True)

    while any(not j.get("collected") for j in state["jobs"]):
        for job in [j for j in state["jobs"] if not j.get("collected")]:
            info = vertex.retry(lambda: http.get(f"https://aiplatform.googleapis.com/v1/{job['name']}", timeout=60)).json()
            if info["state"] != job.get("state"):
                job["state"] = info["state"]
                save()
                print(f"{job['name'].rsplit('/', 1)[-1]} {info['state']}", flush=True)
            if info["state"] not in sb.TERMINAL:
                continue
            directory = (info.get("outputInfo") or {}).get("gcsOutputDirectory", "")
            prefix = directory.removeprefix(f"gs://{args.bucket}/").rstrip("/") + "/"
            records = []
            for name in sorted(existing(prefix)) if directory else []:
                if not name.endswith(".jsonl"):
                    continue
                text = vertex.retry(lambda: http.get(f"{storage}/{quote(name, safe='')}", params=dict(alt="media"),
                                                     timeout=300)).text
                for line in filter(None, text.splitlines()):
                    row = json.loads(line)
                    uri = next(part["fileData"]["fileUri"] for content in row["request"]["contents"]
                               for part in content["parts"] if part.get("fileData"))
                    p = by_id[uri.split(f"{args.image_prefix}/", 1)[1].split("/")[2]]
                    response = row.get("response") or {}
                    record = record_for(p, version, response) | dict(batch_job=job["name"])
                    record["cost_usd"] = sb.batch_cost(record["usage"])
                    try:
                        if row.get("status"):
                            raise ValueError(str(row["status"])[:300])
                        record["colors"] = parse_colors(response)
                    except Exception as e:
                        record["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                    records.append(record)
            with log_path.open("a", encoding="utf-8") as out:
                for record in records:
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
            job.update(collected=True, read=len(records), errors=sum("error" in r for r in records),
                       cost_usd=round(sum(r["cost_usd"] for r in records), 4))
            save()
            print(f"{job['name'].rsplit('/', 1)[-1]}: {len(records)} responses, {job['errors']} errors, "
                  f"${job['cost_usd']:.4f}", flush=True)
        if any(not j.get("collected") for j in state["jobs"]):
            time.sleep(args.poll_seconds)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, help="only N products, spread over the categories")
    ap.add_argument("--log", default=MAIN_LOG, help="log name in data/product_colors/; only the main log writes the parquet")
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--budget-usd", type=float, default=0.05, help="total for the log, earlier runs included")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--review", action="store_true", help="write an HTML page with photos and colours")
    ap.add_argument("--batch", action="store_true", help="use Vertex AI batch prediction (half price)")
    ap.add_argument("--bucket", help="Cloud Storage bucket the Vertex service agent can read (--batch)")
    ap.add_argument("--prefix", default="product-colors", help="folder of the batch jobs in the bucket")
    ap.add_argument("--image-prefix", default="concept-scores/images", help="folder of the uploaded photos")
    ap.add_argument("--chunk", type=int, default=1500, help="requests per batch job")
    ap.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args()

    products, _ = common.load_index()
    products = [p for p in products if main_image(p)]
    chosen = stratified(products, args.sample) if args.sample else products
    log_path = DATA / f"{args.log}.jsonl"
    done = {r["product_id"] for r in read_log(log_path) if r.get("colors")}
    tasks = [dict(id=p["product_id"], product=p) for p in chosen if p["product_id"] not in done]
    system = len(SYSTEM.read_text(encoding="utf-8"))
    costs = [vertex.estimate(system + len(user_text(t["product"])) + 600, 150, images=1) for t in tasks]
    spent = vertex.spent_in(log_path)
    if args.batch:
        costs = [c / 2 for c in costs]
    print(f"{len(chosen)} products, {len(tasks)} {'batch requests' if args.batch else 'calls'} now (up to "
          f"${sum(costs):.3f}); prompt version {prompt_version()}; log {log_path.name}, spent so far ${spent:.4f}, "
          f"budget ${args.budget_usd:.2f}")
    if args.execute and args.batch:
        if not args.bucket:
            ap.error("--batch needs --bucket")
        if spent + sum(costs) > args.budget_usd:
            raise SystemExit(f"estimate ${spent + sum(costs):.2f} with earlier runs is over --budget-usd {args.budget_usd}")
        DATA.mkdir(parents=True, exist_ok=True)
        run_batch([t["product"] for t in tasks], {p["product_id"]: p for p in products}, prompt_version(), args,
                  log_path)
    elif tasks and args.execute:
        version = prompt_version()

        def work(task, client):
            p = task["product"]
            response = client(body(p), timeout=120)
            record = record_for(p, version, response)
            record["colors"] = parse_colors(response)
            return record

        DATA.mkdir(parents=True, exist_ok=True)
        vertex.run(tasks, costs, work, log_path, args.budget_usd, spent, args.workers)
    log = read_log(log_path)
    if log and args.log == MAIN_LOG:
        frame = to_frame(log)
        frame.to_parquet(OUTPUT, index=False)
        names = name_table(frame)
        colour = check_names(sorted(names["name"]), 0.05) if args.execute else {}
        if colour and set(names["name"]) <= set(colour):
            kept = names[names["name"].map(lambda n: colour.get(n, False))]
            kept.sort_values("products", ascending=False).to_parquet(NAMES, index=False)
            print(f"{len(kept)} of {len(names)} names are colours -> {NAMES}; left out: "
                  f"{', '.join(sorted(set(names['name']) - set(kept['name'])))}")
    if log and args.review:
        review(log, products, DATA / f"{args.log}_review.html")


if __name__ == "__main__":
    main()
