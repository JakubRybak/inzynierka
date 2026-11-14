"""Jev second stage shared by the search UI and the offline ranking experiment."""
import base64
import html
import io
import math
from pathlib import Path
import random
import sys

import numpy as np
import requests

import common

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"
DEPTH = 30
BLEND = 0.25  # weight of the first-stage z-score, chosen on the dev queries
CRITERIA = {
    "3": "excellent: the product matches everything the query asks for, including any style, occasion, season, "
         "detail, material or colour shade the query mentions",
    "2": "good: it matches the main request, with a small mismatch or an aspect that cannot be verified",
    "1": "weak: the right kind of product whose explicit attributes fit, but it lacks the style, occasion, season, "
         "detail or colour shade the query asks for",
    "0": "wrong: not the kind of product asked for, or it contradicts an explicit attribute of the query"}
INSTRUCTIONS = ("Grade how well one product of PRODUCTS answers the shopper's QUERY in a fashion e-commerce search. "
                "Ignore sizes, plus size, maternity and children's sizes in the query. A negation such as "
                "'no graphics' means the product must not have that. Grade the product {label}.")
VISION_INSTRUCTIONS = (
    " Use the product's text and its own photo together. Judge visible colour, shade, pattern, silhouette and "
    "decoration from the photo; use the text for material composition. Focus on the garment being sold, not the "
    "model, other clothing, accessories or background. A detail hidden from this view is unknown, not absent. "
    "If photo is null, judge from the text only and do not invent visual evidence.")
# measured on 10 dev queries: 0.70 s and $0.0010 per search, against 2.30 s and $0.0040 with 1024 px photos; the
# grades of both agree (Spearman 0.82)
MAX_IMAGE_SIZE = 384
MIN_IMAGE_SIZE = 280  # Jev requires at least 280 px on each side.
PHOTO_CACHE = common.DATA / f"jev_photos_{MAX_IMAGE_SIZE}"


class NoProductImages(ValueError):
    pass


def product_photo(product, image_dir, cache=None):
    """Prefer the enhanced main photo; return an upright JPEG of at most MAX_IMAGE_SIZE px or None if none can be read.
    cache: a folder that keeps the JPEG of every product once made, so a later search only reads it."""
    pid = product.get("product_id")
    cached = Path(cache) / f"{pid}.jpg" if cache is not None and pid else None
    if cached is not None and cached.is_file():
        return photo_part(cached.read_bytes())
    from PIL import Image, ImageOps

    root = Path(image_dir).resolve()
    paths = sorted(product.get("images") or [], key=lambda p: not Path(p).stem.endswith("_id_gridfs_1"))
    if pid:
        paths.insert(0, Path(common.PILOT.name) / "images_enhanced" / pid / f"{pid}_id_gridfs_1.webp")
    for name in paths:
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            continue
        try:
            with Image.open(path) as original:
                photo = ImageOps.exif_transpose(original).convert("RGBA")
                side = min(MAX_IMAGE_SIZE, max(MIN_IMAGE_SIZE, max(photo.size)))
                scale = side / max(photo.size)
                size = tuple(max(1, round(dimension * scale)) for dimension in photo.size)
                if size != photo.size:
                    photo = photo.resize(size, Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (side, side), "white")
                canvas.paste(photo, ((side - size[0]) // 2, (side - size[1]) // 2), photo)
                data = io.BytesIO()
                canvas.save(data, format="JPEG", quality=90)
        except (OSError, ValueError):
            continue
        if cached is not None:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(data.getvalue())
        return photo_part(data.getvalue())
    return None


def photo_part(jpeg):
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")}}


def prepare_photos(products, image_dir, cache=PHOTO_CACHE, workers=8):
    """Makes the cached JPEG of every product that has none yet. -> number made."""
    from concurrent.futures import ThreadPoolExecutor
    todo = [p for p in products if not (Path(cache) / f"{p['product_id']}.jpg").is_file()]
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(lambda p: product_photo(p, image_dir, cache), todo))
    return len(todo)


def api_key():
    if str(common.REPO) not in sys.path:
        sys.path.insert(0, str(common.REPO))
    from query_parsing.clients.credentials import load_api_key
    return load_api_key("OPENROUTER_API_KEY")


def product_text(p, extra=None):
    text = (f"{html.unescape(str(p.get('name') or ''))} | {p.get('brand', '')} | "
            f"{html.unescape(str(p.get('description') or ''))} | Composition: {p.get('composition', '')}")
    return f"{text} | {extra}" if extra else text


def payload(task, by_id, extra=None, photos=None):
    products = {label: product_text(by_id[pid], extra.get(pid) if extra else None)
                for label, pid in task["labels"].items()}
    if photos is not None:
        # OpenRouter multimodal decisions accepts inline image parts inside arbitrary state objects:
        # https://openrouter.ai/docs/guides/community/multimodal-decisions
        products = {label: dict(text=text, photo=photos.get(task["labels"][label]))
                    for label, text in products.items()}
    instructions = INSTRUCTIONS + (VISION_INSTRUCTIONS if photos is not None else "")
    return {"model": MODEL, "state": {"QUERY": task["query"], "CATEGORY": task["category"], "PRODUCTS": products},
            "questions": {label: {"type": "choice", "instructions": instructions.format(label=label),
                                  "criteria": CRITERIA} for label in products}}


def expected(answer):
    """Expected grade from the probabilities, or the chosen grade when none are returned."""
    p = answer.get("probabilities")
    if isinstance(p, dict) and p:
        if not set(p) <= set(CRITERIA):
            raise ValueError("Invalid Jev grade labels")
        weights = {k: float(v) for k, v in p.items()}
        if any(not math.isfinite(v) or v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
            raise ValueError("Invalid Jev grade probabilities")
        return sum(int(k) * v for k, v in weights.items()) / sum(weights.values())
    if answer.get("choice") not in CRITERIA:
        raise ValueError("Invalid Jev grade")
    return float(answer["choice"])


def blended_scores(top, score, answers, blend):
    score = np.asarray(score, dtype=float)
    z = (score - score.mean()) / (score.std() + 1e-9)
    grade = np.array([expected(answers[p]) if p in answers else 0.0 for p in top])
    return grade + blend * z


def rerank(stage, answers, depth=DEPTH, blend=BLEND):
    """Reorder the first depth candidates; keep the rest behind them in their original order."""
    top = stage["top"][:depth]
    if len(top) < 2:
        return stage["top"]
    score = blended_scores(top, stage["score"][:depth], answers, blend)
    order = np.argsort(-score, kind="stable")
    return [top[i] for i in order] + stage["top"][depth:]


class JevReranker:
    """One uncached request on selection, with a bounded timeout and no automatic retries."""

    def __init__(self, key=None, timeout=5.0, image_dir=None, photo_cache=None):
        self.key, self.timeout = key, timeout
        self.image_dir = Path(image_dir) if image_dir is not None else None
        self.photo_cache = photo_cache

    def __call__(self, query, category, products, scores):
        products, scores = products[:DEPTH], scores[:DEPTH]
        top = [p["product_id"] for p in products]
        if len(top) < 2:
            return top, {}, dict(status="skipped", reason="fewer than two candidates", count=0, cost_usd=0.0)
        shuffled = list(top)
        random.Random(f"{category}|{query}").shuffle(shuffled)
        labels = {f"P{i + 1:02d}": pid for i, pid in enumerate(shuffled)}
        task = dict(query=query, category=category, labels=labels)
        photos = None
        if self.image_dir is not None:
            photos = {p["product_id"]: product_photo(p, self.image_dir, self.photo_cache) for p in products}
            if not any(photos.values()):
                raise NoProductImages("No readable product photos for Jev vision")
        body = payload(task, {p["product_id"]: p for p in products}, photos=photos)
        # Load credentials only when this ranking is selected; constructing the engine is offline.
        key = self.key or api_key()
        headers = {"Authorization": f"Bearer {key}"}
        if photos is not None:
            headers["TypeSafe-Danger-Zone-Images"] = "true"
        response = requests.post(ENDPOINT, headers=headers, json=body,
                                 timeout=(3.05, self.timeout), allow_redirects=False)
        if not response.ok:
            raise RuntimeError(f"Jev HTTP {response.status_code}")
        data = response.json()
        answers = data.get("answers")
        if not isinstance(answers, dict) or set(answers) != set(labels):
            raise ValueError("Jev response does not cover every requested product")
        answers = {labels[label]: answer for label, answer in answers.items()}
        grades = {pid: expected(answer) for pid, answer in answers.items()}
        stage = dict(top=top, score=scores)
        combined = blended_scores(top, scores, answers, BLEND)
        parts = {pid: dict(grade=round(grades[pid], 4), score=round(float(score), 4))
                 for pid, score in zip(top, combined)}
        usage = data.get("usage") or {}
        cost = float(usage["cost"]) if usage.get("cost") is not None else None
        if cost is not None and (not math.isfinite(cost) or cost < 0):
            cost = None
        info = dict(status="applied", model=MODEL, count=len(top), blend=BLEND, cost_usd=cost)
        if photos is not None:
            info.update(vision=True, images=sum(photo is not None for photo in photos.values()))
            for pid, part in parts.items():
                part["image_used"] = photos[pid] is not None
        return rerank(stage, answers), parts, info
