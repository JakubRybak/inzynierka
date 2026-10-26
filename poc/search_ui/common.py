"""Paths, feature-file loader, product embeddings and the query embedder."""
import json
import random
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "data"
DATASET = REPO / "data/processed/fashiongen"
EMBEDDINGS = REPO / "poc/feature_extraction/embeddings/gemini_embedding_2"
INDEX = "index.parquet"
META = "meta.json"
JSON_COLUMNS = ["features", "feature_metadata", "exclusion_reasons"]


def _from_json(v):
    if isinstance(v, str):
        return json.loads(v) if v.strip() else None
    return v


def load_features(paths):
    """Extraction output (.csv, .parquet or .jsonl) -> DataFrame."""
    parts = []
    for path in map(Path, paths):
        if path.suffix == ".parquet":
            d = pd.read_parquet(path)
        elif path.suffix == ".jsonl":
            d = pd.read_json(path, lines=True, dtype={"product_id": str})
        elif path.suffix == ".csv":
            d = pd.read_csv(path, dtype={"product_id": str}, keep_default_na=False)
        else:
            raise ValueError(f"Unsupported format: {path}")
        for k in JSON_COLUMNS:
            if k in d:
                d[k] = d[k].map(_from_json)
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d["product_id"] = d["product_id"].astype(str)
    if d["product_id"].duplicated().any():
        raise ValueError(f"Duplicate product_id: {d.loc[d.product_id.duplicated(), 'product_id'].head().tolist()}")
    missing = {"product_id", "section", "category", "features", "status"} - set(d.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    d["features"] = d["features"].map(lambda f: f if isinstance(f, dict) else {})
    return d


def load_embeddings(directory=EMBEDDINGS):
    """-> (manifest, {product_id: description vector}, {product_id: image vector})."""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    vectors = []
    for name in ("text.parquet", "image.parquet"):
        d = pd.read_parquet(directory / name, columns=["product_id", "embedding"])
        vectors.append({str(i): np.asarray(v, np.float32) for i, v in zip(d["product_id"], d["embedding"])})
    return manifest, *vectors


def query_text(q):
    return f"task: search result | query: {q}"


def normalize(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


class QueryEmbedder:
    def __init__(self, model, dim):
        from google import genai
        self.model, self.dim = model, dim
        self.client = genai.Client()

    def __call__(self, text):
        from google.genai import types
        cfg = types.EmbedContentConfig(output_dimensionality=self.dim)
        for attempt in range(3):
            try:
                r = self.client.models.embed_content(model=self.model, contents=[text], config=cfg)
                return np.array(r.embeddings[0].values, dtype=np.float32)
            except Exception as e:
                last = e
                if isinstance(e, httpx.TransportError) or \
                        any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "500", "503", "UNAVAILABLE")):
                    time.sleep(0.5 * 2 ** attempt + random.random() / 4)
                    continue
                raise
        raise last


HYDE_PROMPT = """You write a short product description in the style of the SSENSE catalogue
(e.g. "Short sleeve cotton jersey t-shirt in black. Crewneck collar. Tonal stitching.")
for an imaginary product that matches a customer's search query.
- Describe only what the query states or clearly implies. Do not invent colours, brands, prints,
  materials or details that the query does not suggest.
- If the query excludes something (e.g. "without print"), describe the product as not having it.
- 1-2 sentences, plain catalogue style, English, no marketing language, no price.
Product category: {category}."""


class HydeWriter:
    """HyDE: an LLM writes the description of an ideal product; its embedding is compared with product descriptions."""

    def __init__(self, model="gemini-3.5-flash-lite"):
        from google import genai
        self.model = model
        self.client = genai.Client()

    def __call__(self, query, category):
        from google.genai import types
        cfg = types.GenerateContentConfig(system_instruction=HYDE_PROMPT.format(category=category or "clothing"),
                                          temperature=0, max_output_tokens=200)
        r = self.client.models.generate_content(model=self.model, contents=f'Search query: "{query}"', config=cfg)
        text = (r.text or "").strip()
        if not text:
            raise RuntimeError("the model returned an empty description")
        return text


def load_index(folder=DATA):
    folder = Path(folder)
    if not (folder / INDEX).is_file():
        raise FileNotFoundError(f"{folder / INDEX} not found, run prepare.py first")
    d = pd.read_parquet(folder / INDEX)
    for k in ("features", "images"):
        d[k] = d[k].map(json.loads)
    meta = json.loads((folder / META).read_text(encoding="utf-8"))
    return d.to_dict("records"), meta
