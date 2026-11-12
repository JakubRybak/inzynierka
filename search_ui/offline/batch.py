"""
Vertex AI batch prediction for per-product Gemini requests with product photos: the photos go to Cloud Storage (only
the missing ones), the requests to JSONL files there, one job per chunk; the responses are appended to a log. The jobs
are kept in <folder>/state.json, so a rerun resumes: it submits only products without a job and reads back only jobs
not read yet.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import time
from urllib.parse import quote

import common
import score_batch as sb
import vertex


def run(products, *, folder, log_path, bucket, prefix, image_prefix, display, paths, request, record, chunk=1500,
        poll_seconds=30):
    """products: the products to ask about. paths(p): its photo paths; request(p, uri): the request body, with uri(path)
    the Cloud Storage URI of a photo; record(p, response): the log record of a response (an exception makes an error
    record instead)."""
    import requests
    state_path = folder / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else dict(jobs=[])
    pending = {pid for job in state["jobs"] if not job.get("collected") for pid in job["products"]}
    todo = [p for p in products if p["product_id"] not in pending]
    folder.mkdir(parents=True, exist_ok=True)
    http, project = sb.session()
    base = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global"
    storage = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o"
    upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o"

    def save():
        state_path.write_text(json.dumps(state, indent=1), encoding="utf-8")

    def gs(name):
        return f"gs://{bucket}/{name}"

    def image_name(path):
        return f"{image_prefix}/{path}"

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

    def existing(prefix_):
        names, params = set(), dict(prefix=prefix_, fields="items(name),nextPageToken")
        while True:
            page = http.get(storage, params=params, timeout=60).json()
            names |= {o["name"] for o in page.get("items", [])}
            if not page.get("nextPageToken"):
                return names
            params["pageToken"] = page["nextPageToken"]

    if todo:
        have = {n.split(f"{image_prefix}/", 1)[1] for n in existing(f"{image_prefix}/")}
        missing = sorted({path for p in todo for path in paths(p)} - have)
        print(f"uploading {len(missing)} photos", flush=True)
        with ThreadPoolExecutor(8) as pool:
            list(pool.map(lambda path: upload(image_name(path), (common.DATASET / path).read_bytes(), "image/png"),
                          missing))
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        for k in range(0, len(todo), chunk):
            part = todo[k:k + chunk]
            root = f"{prefix}/{display}-{run_id}-{k // chunk}"
            lines = [json.dumps({"request": request(p, lambda path: gs(image_name(path)))}) for p in part]
            upload(f"{root}/input.jsonl", ("\n".join(lines) + "\n").encode(), "application/jsonl")
            spec = {"displayName": f"{display}-{run_id}-{k // chunk}", "model": f"publishers/google/models/{vertex.MODEL}",
                    "inputConfig": {"instancesFormat": "jsonl", "gcsSource": {"uris": [gs(f"{root}/input.jsonl")]}},
                    "outputConfig": {"predictionsFormat": "jsonl",
                                     "gcsDestination": {"outputUriPrefix": gs(f"{root}/output")}}}
            r = http.post(f"{base}/batchPredictionJobs", json=spec, timeout=60)
            if not r.ok:
                save()
                raise SystemExit(f"batch submission HTTP {r.status_code}: {r.text[:300]}")
            state["jobs"].append(dict(name=r.json()["name"], root=root, products=[p["product_id"] for p in part]))
            save()
            print(f"submitted {state['jobs'][-1]['name']} ({len(part)} requests)", flush=True)

    products_by_id = {p["product_id"]: p for p in common.load_index()[0]}
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
            out_prefix = directory.removeprefix(f"gs://{bucket}/").rstrip("/") + "/"
            records = []
            for name in sorted(existing(out_prefix)) if directory else []:
                if not name.endswith(".jsonl"):
                    continue
                text = vertex.retry(lambda: http.get(f"{storage}/{quote(name, safe='')}", params=dict(alt="media"),
                                                     timeout=300)).text
                for line in filter(None, text.splitlines()):
                    row = json.loads(line)
                    uri = next(part["fileData"]["fileUri"] for content in row["request"]["contents"]
                               for part in content["parts"] if part.get("fileData"))
                    p = products_by_id[uri.split(f"{image_prefix}/", 1)[1].split("/")[2]]
                    response = row.get("response") or {}
                    usage = response.get("usageMetadata") or {}
                    try:
                        if row.get("status"):
                            raise ValueError(str(row["status"])[:300])
                        rec = record(p, response)
                    except Exception as e:
                        rec = dict(id=p["product_id"], product_id=p["product_id"], category=p["category"],
                                   error=f"{type(e).__name__}: {str(e)[:300]}", usage=usage)
                    rec.update(batch_job=job["name"], cost_usd=sb.batch_cost(usage))
                    records.append(rec)
            with log_path.open("a", encoding="utf-8") as out:
                for rec in records:
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            job.update(collected=True, read=len(records), errors=sum("error" in r for r in records),
                       cost_usd=round(sum(r["cost_usd"] for r in records), 4))
            save()
            print(f"{job['name'].rsplit('/', 1)[-1]}: {len(records)} responses, {job['errors']} errors, "
                  f"${job['cost_usd']:.4f}", flush=True)
        if any(not j.get("collected") for j in state["jobs"]):
            time.sleep(poll_seconds)
