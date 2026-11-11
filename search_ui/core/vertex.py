"""Gemini generateContent calls on Vertex AI with retries, a budget and cost accounting."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import random
import threading
import time

MODEL = "gemini-3.5-flash-lite"
INPUT_RATE = 0.30 / 1_000_000
OUTPUT_RATE = 2.50 / 1_000_000
IMAGE_TOKENS = 530  # one 256x256 image at MEDIA_RESOLUTION_MEDIUM


def call_cost(usage):
    return (usage.get("promptTokenCount", 0) * INPUT_RATE
            + (usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)) * OUTPUT_RATE)


def estimate(chars_in, tokens_out, images=0):
    """Upper cost estimate: 4 characters per text token."""
    return call_cost({"promptTokenCount": chars_in / 4 + images * IMAGE_TOKENS, "candidatesTokenCount": tokens_out})


def retry(f, attempts=4):
    for attempt in range(attempts):
        try:
            return f()
        except Exception as e:
            if attempt == attempts - 1 or not any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
                raise
            time.sleep(2 ** attempt + random.random())


def response_text(response):
    return "".join(p.get("text", "") for p in response["candidates"][0]["content"]["parts"] if not p.get("thought"))


class Client:
    def __init__(self, model=MODEL):
        import google.auth
        from google.auth.transport.requests import AuthorizedSession, Request
        credentials, default_project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or default_project
        credentials = credentials.with_quota_project(project)
        credentials.refresh(Request())
        self.session = AuthorizedSession(credentials, max_refresh_attempts=1)
        self.endpoint = (f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/"
                         f"google/models/{model}:generateContent")

    def __call__(self, body, timeout=180):
        def post():
            r = self.session.post(self.endpoint, json=body, timeout=timeout)
            if not r.ok:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            return r.json()
        return retry(post)


def spent_in(path):
    return sum(json.loads(line).get("cost_usd", 0) for line in path.open(encoding="utf-8")) if path.exists() else 0.0


def run(tasks, costs, work, log_path, budget, spent, workers=4):
    """Calls work(task, client) -> record for each task in parallel within the budget and appends every record to
    the log. A record carries usage and cost_usd from the response, or the reserved estimate when the call failed."""
    client = Client()
    lock, state = threading.Lock(), dict(spent=spent, reserved=0.0, done=0, errors=0, skipped=0)

    def one(task, reserve, out):
        with lock:
            if state["spent"] + state["reserved"] + reserve > budget:
                state["skipped"] += 1
                return
            state["reserved"] += reserve
        start = time.monotonic()
        try:
            record = work(task, client)
            record["cost_usd"] = call_cost(record["usage"]) if record.get("usage") else reserve
        except Exception as e:
            record = dict(id=task.get("id"), error=f"{type(e).__name__}: {str(e)[:300]}", cost_usd=reserve)
        record["seconds"] = round(time.monotonic() - start, 2)
        with lock:
            state["reserved"] -= reserve
            state["spent"] += record["cost_usd"]
            state["done"] += 1
            state["errors"] += "error" in record
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if "error" in record:
                print(f"error: {record['error']}", flush=True)
            if state["done"] % 25 == 0:
                print(f"{state['done']}/{len(tasks)}  ${state['spent']:.4f}", flush=True)

    pool = ThreadPoolExecutor(workers)
    try:
        with log_path.open("a", encoding="utf-8") as out:
            for f in as_completed([pool.submit(one, t, c, out) for t, c in zip(tasks, costs)]):
                f.result()
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    pool.shutdown()
    print(f"done {state['done'] - state['errors']}, errors {state['errors']}, skipped by the budget "
          f"{state['skipped']}; spent ${state['spent']:.4f}")
