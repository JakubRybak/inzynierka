"""
Embeddings of the enhanced front photos (`images_enhanced/` of the pilot, 1024 px) with the model and dimension of
the product embeddings, kept next to the original ones in search_ui/data/image_embeddings_enhanced.npz. An image
costs as many tokens as the original photo (258), so all products cost about $1.15.

    python search_ui/offline/image_embeddings.py             # plan only, no API calls
    python search_ui/offline/image_embeddings.py --execute   # paid calls

A rerun embeds only products missing from the file; the file is saved every SAVE_EVERY products.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import sys
import threading

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import common  # noqa: E402
import vertex  # noqa: E402

OUTPUT = common.DATA / common.ENHANCED_IMAGE_VECTORS
TOKENS = 258
USD_PER_MILLION = 0.45
SAVE_EVERY = 500


def photo(p):
    path = common.PILOT / "images_enhanced" / p["product_id"] / f"{p['product_id']}_id_gridfs_1.webp"
    return path if path.is_file() else None


def session():
    import google.auth
    from google.auth.transport.requests import AuthorizedSession, Request
    credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or project
    credentials = credentials.with_quota_project(project)
    credentials.refresh(Request())
    return AuthorizedSession(credentials), project


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--budget-usd", type=float, default=1.3)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    products, meta = common.load_index()
    known = {}
    if OUTPUT.exists():
        stored = np.load(OUTPUT)
        known = dict(zip(stored["ids"].tolist(), stored["vectors"]))
    todo = [(p["product_id"], photo(p)) for p in products if p["product_id"] not in known and photo(p)]
    missing = sum(photo(p) is None for p in products)
    estimate = len(todo) * TOKENS * USD_PER_MILLION / 1e6
    print(f"{len(products)} products, {len(known)} embedded, {len(todo)} to embed (about ${estimate:.2f}), "
          f"{missing} without an enhanced photo; model {meta['model']}, {meta['dim']} dims")
    if not todo or not args.execute:
        return
    if estimate > args.budget_usd:
        raise SystemExit(f"estimate ${estimate:.2f} is over --budget-usd {args.budget_usd}")
    http, project = session()
    url = (f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/google/models/"
           f"{meta['model']}:embedContent")
    lock, state = threading.Lock(), dict(tokens=0, done=0)

    def save():
        ids = list(known)
        np.savez(OUTPUT, ids=np.array(ids), vectors=np.stack([known[i] for i in ids]).astype(np.float32))

    def one(pid, path):
        body = {"content": {"parts": [{"inlineData": {"mimeType": "image/webp",
                                                      "data": base64.b64encode(path.read_bytes()).decode()}}]},
                "outputDimensionality": meta["dim"]}

        def post():
            r = http.post(url, json=body, timeout=120)
            if not r.ok:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            return r.json()
        data = vertex.retry(post, attempts=6)
        v = np.asarray(data["embedding"]["values"], np.float32)
        return pid, v / np.linalg.norm(v), data.get("usageMetadata", {}).get("promptTokenCount", TOKENS)

    errors = 0
    with ThreadPoolExecutor(args.workers) as pool:
        for f in as_completed([pool.submit(one, pid, path) for pid, path in todo]):
            try:
                pid, v, tokens = f.result()
            except Exception as e:
                errors += 1
                print(f"error: {type(e).__name__}: {str(e)[:200]}", flush=True)
                continue
            with lock:
                known[pid] = v
                state["tokens"] += tokens
                state["done"] += 1
                if state["done"] % SAVE_EVERY == 0:
                    save()
                    print(f"{state['done']}/{len(todo)}  ${state['tokens'] * USD_PER_MILLION / 1e6:.3f}", flush=True)
    save()
    print(f"done {state['done']}, errors {errors}; {state['tokens']} tokens, about "
          f"${state['tokens'] * USD_PER_MILLION / 1e6:.3f} -> {OUTPUT}")


if __name__ == "__main__":
    main()
