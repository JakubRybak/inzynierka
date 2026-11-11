"""
Concept scores through Vertex AI batch prediction: the same requests as score_concepts.py at half the token price.
The product images go to Cloud Storage, the requests to JSONL files there, one batch job per chunk; the responses are
read back into the same log as the direct calls (search_ui/data/concept_scores/<log>.jsonl), and the main log rebuilds
ranking_data/concept_scores.parquet.

    python search_ui/offline/score_batch.py --bucket <bucket>             # plan, no API calls
    python search_ui/offline/score_batch.py --bucket <bucket> --execute   # paid

Products whose (product, concept) pairs are already in the log or in a --skip-log are left out. The jobs are kept in
data/concept_scores/batch_<log>/state.json, so a rerun resumes: it uploads only missing images, submits only chunks
without a job and reads back only jobs not read yet.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import quote

import score_concepts as sp
from score_concepts import DATA, MODEL, common
from vertex import retry

BATCH_RATES = (0.15 / 1_000_000, 1.25 / 1_000_000)
TERMINAL = {"JOB_STATE_SUCCEEDED", "JOB_STATE_PARTIALLY_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED"}


def batch_cost(usage):
    return (usage.get("promptTokenCount", 0) * BATCH_RATES[0]
            + (usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)) * BATCH_RATES[1])


def session():
    import google.auth
    from google.auth.transport.requests import AuthorizedSession, Request
    credentials, default_project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or default_project
    credentials.refresh(Request())
    return AuthorizedSession(credentials.with_quota_project(project)), project


def body(p, concepts, thinking, uri):
    """score_concepts.body with the images as Cloud Storage files instead of inline bytes."""
    request = sp.body_parts(p, concepts, thinking, [{"fileData": {"mimeType": "image/png", "fileUri": uri(path)}}
                                                    for path in sp.images(p)])
    return request


def tasks_for(args):
    concepts = sp.load_concepts()
    products, _ = common.load_index(args.index)
    if args.category:
        products = [p for p in products if p["category"] in args.category]
    products = [p for p in products if sp.images(p) is not None]
    log = sp.read_log(DATA / f"{args.log}.jsonl")
    skip = [r for name in args.skip_log for r in sp.read_log(DATA / f"{name}.jsonl")]
    scored = {(r["product_id"], cid) for r in log + skip for cid in (r.get("scores") or {})}
    tasks = [(p, [c for c in concepts if (p["product_id"], c["id"]) not in scored]) for p in products]
    return [(p, cs) for p, cs in tasks if cs]


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--index", type=Path, default=common.DATA, help="search index folder built by prepare.py")
    ap.add_argument("--category", action="append", help="only these categories (repeatable)")
    ap.add_argument("--thinking", default="MINIMAL", choices=["NONE", "MINIMAL", "LOW", "MEDIUM"])
    ap.add_argument("--log", default=sp.MAIN_LOG, help="log name in data/concept_scores/")
    ap.add_argument("--skip-log", action="append", default=[], help="also skip pairs scored in this log")
    ap.add_argument("--bucket", required=True, help="Cloud Storage bucket the Vertex service agent can read")
    ap.add_argument("--prefix", default="concept-scores")
    ap.add_argument("--chunk", type=int, default=1500, help="requests per batch job")
    ap.add_argument("--budget-usd", type=float, default=12.0, help="reservation limit for the jobs of this run")
    ap.add_argument("--poll-seconds", type=int, default=30)
    ap.add_argument("--execute", action="store_true", help="upload, submit and read back (paid)")
    args = ap.parse_args()

    folder = DATA / f"batch_{args.log}"
    state_path = folder / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else dict(jobs=[])
    version = sp.prompt_version(args.thinking)
    pending = {pid for job in state["jobs"] if not job.get("collected") for pid in job["products"]}
    tasks = [(p, cs) for p, cs in tasks_for(args) if p["product_id"] not in pending]
    # MINIMAL thinking used no thinking tokens in the online runs, so it is estimated like NONE
    thinking = "NONE" if args.thinking == "MINIMAL" else args.thinking
    reserve = sum(sp.estimated_cost(p, cs, thinking) for p, cs in tasks) / 2
    chunks = [tasks[k:k + args.chunk] for k in range(0, len(tasks), args.chunk)]
    print(f"{len(tasks)} products to score in {len(chunks)} new jobs (batch reservation up to ${reserve:.2f}); "
          f"{len(state['jobs'])} jobs from earlier runs; prompt version {version}, thinking {args.thinking}")
    if not args.execute:
        return
    if reserve > args.budget_usd:
        raise SystemExit(f"reservation ${reserve:.2f} is over --budget-usd {args.budget_usd}")
    folder.mkdir(parents=True, exist_ok=True)
    http, project = session()
    base = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global"
    storage = f"https://storage.googleapis.com/storage/v1/b/{args.bucket}/o"
    upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{args.bucket}/o"

    def save():
        state_path.write_text(json.dumps(state, indent=1), encoding="utf-8")

    def gs(name):
        return f"gs://{args.bucket}/{name}"

    def image_name(path):
        return f"{args.prefix}/images/{path}"

    def upload(name, data, mime, attempts=6):
        import requests
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

    if chunks:
        have = existing(f"{args.prefix}/images/")
        paths = sorted({path for p, _ in tasks for path in sp.images(p)} - {n.split("/images/", 1)[1] for n in have})
        print(f"uploading {len(paths)} images", flush=True)
        with ThreadPoolExecutor(8) as pool:
            list(pool.map(lambda path: upload(image_name(path), (common.DATASET / path).read_bytes(), "image/png"),
                          paths))
        run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        for k, chunk in enumerate(chunks):
            root = f"{args.prefix}/{args.log}-{run}-{k}"
            lines = [json.dumps({"request": body(p, cs, args.thinking, lambda path: gs(image_name(path)))})
                     for p, cs in chunk]
            upload(f"{root}/input.jsonl", ("\n".join(lines) + "\n").encode(), "application/jsonl")
            spec = {"displayName": f"concept-scores-{args.log}-{run}-{k}", "model": f"publishers/google/models/{MODEL}",
                    "inputConfig": {"instancesFormat": "jsonl", "gcsSource": {"uris": [gs(f"{root}/input.jsonl")]}},
                    "outputConfig": {"predictionsFormat": "jsonl",
                                     "gcsDestination": {"outputUriPrefix": gs(f"{root}/output")}}}
            r = http.post(f"{base}/batchPredictionJobs", json=spec, timeout=60)
            if not r.ok:
                save()
                raise SystemExit(f"batch submission HTTP {r.status_code}: {r.text[:300]}")
            state["jobs"].append(dict(name=r.json()["name"], root=root, products=[p["product_id"] for p, _ in chunk],
                                      concepts={p["product_id"]: [c["id"] for c in cs] for p, cs in chunk}))
            save()
            print(f"submitted {state['jobs'][-1]['name']} ({len(chunk)} requests)", flush=True)

    by_id = {p["product_id"]: p for p in common.load_index(args.index)[0]}
    log_path = DATA / f"{args.log}.jsonl"
    while True:
        open_jobs = [j for j in state["jobs"] if not j.get("collected")]
        if not open_jobs:
            break
        for job in open_jobs:
            info = retry(lambda: http.get(f"https://aiplatform.googleapis.com/v1/{job['name']}", timeout=60)).json()
            if info["state"] != job.get("state"):
                job["state"] = info["state"]
                save()
                print(f"{job['name'].rsplit('/', 1)[-1]} {info['state']}", flush=True)
            if info["state"] not in TERMINAL:
                continue
            directory = (info.get("outputInfo") or {}).get("gcsOutputDirectory", "")
            prefix = directory.removeprefix(f"gs://{args.bucket}/").rstrip("/") + "/"
            records, cost = [], 0.0
            for name in sorted(existing(prefix)) if directory else []:
                if not name.endswith(".jsonl"):
                    continue
                text = retry(lambda: http.get(f"{storage}/{quote(name, safe='')}", params=dict(alt="media"),
                                                 timeout=300)).text
                for line in filter(None, text.splitlines()):
                    row = json.loads(line)
                    uris = [part["fileData"]["fileUri"] for content in row["request"]["contents"]
                            for part in content["parts"] if part.get("fileData")]
                    pid = uris[0].split("/images/", 1)[1].split("/")[2]
                    p, ids = by_id[pid], job["concepts"][pid]
                    response = row.get("response") or {}
                    usage = response.get("usageMetadata") or {}
                    record = dict(product_id=pid, category=p["category"], concepts=ids, model=MODEL,
                                  thinking=args.thinking, prompt_version=version, batch_job=job["name"],
                                  scored_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                  images=sp.images(p), usage=usage, cost_usd=batch_cost(usage))
                    try:
                        if row.get("status"):
                            raise ValueError(str(row["status"])[:300])
                        record["scores"] = sp.parse_scores(response, ids)
                    except Exception as e:
                        record["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                    records.append(record)
                    cost += record["cost_usd"]
            with log_path.open("a", encoding="utf-8") as out:
                for record in records:
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
            job.update(collected=True, read=len(records), errors=sum("error" in r for r in records),
                       cost_usd=round(cost, 4))
            save()
            print(f"{job['name'].rsplit('/', 1)[-1]}: {len(records)} responses, {job['errors']} errors, ${cost:.4f}",
                  flush=True)
        if any(not j.get("collected") for j in state["jobs"]):
            time.sleep(args.poll_seconds)
    if args.log == sp.MAIN_LOG and log_path.exists():
        sp.to_frame(sp.read_log(log_path)).to_parquet(sp.SCORES, index=False)
    total = sum(j.get("cost_usd", 0) for j in state["jobs"])
    print(f"done: {sum(j.get('read', 0) for j in state['jobs'])} responses, "
          f"{sum(j.get('errors', 0) for j in state['jobs'])} errors, ${total:.4f} in batch jobs of this log")


if __name__ == "__main__":
    main()
