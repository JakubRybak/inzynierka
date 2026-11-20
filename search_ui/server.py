"""
Search demo: query -> parser -> feature filtering -> ranking -> results with per-stage timings.
Filters can also be set by hand in the page; the parser is then skipped.

    python search_ui/server.py
    python search_ui/server.py --parser mock --ranking hybrid --port 8000

Rankings (README_ranking.md): hybrid, the similarity of the whole query to the description, image and feature text of
the candidates, corrected by the residual phrases with the phrase bank (bank.py); hybrid_jev_vision, the default, in
which Jev 1.14 regrades the first 30 of hybrid from their text and main photo (jev_reranker.py); and
sentences_jev_vision, the same second stage on the sentence ranking (sentences.py). No caching: every query, including
a repeated one, goes through the parser and the embedding API.
"""
import argparse
import html
import json
import re
import sys
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))
import common  # noqa: E402
import concepts  # noqa: E402
import conditions  # noqa: E402
import facets  # noqa: E402
import jev_reranker  # noqa: E402
import parser_adapter  # noqa: E402
from image_processing.background_color import render_webp  # noqa: E402

# the rankings of the page; sentences is computed only as the first stage of sentences_jev_vision. The rankings the
# evaluation compares them with are in experiments/ranking/baselines.py.
RANKINGS = ("hybrid", "hybrid_jev_vision", "sentences_jev_vision")
DEFAULT_RANKING = "hybrid_jev_vision"
RERANK_BASES = dict(hybrid_jev_vision="hybrid", sentences_jev_vision="sentences")
# detail 0.25: chosen on the dev queries of the benchmark (0.25, 0.5 and 1.0 measured); colour 1.0 is not measured
HYBRID = dict(concept=0.5, negation=1.0, colour=1.0, detail=0.25)
COLOUR_IMAGE_WEIGHT = 2.0
# the weights of the sentence ranking, fitted on the judge's grades of the dev queries
SENTENCE_WEIGHTS = common.SEARCH_UI / "ranking_data/sentence_weights.json"
SENTENCE_PARTS = ("description", "sentences", "image", "features", "concept", "phrase")
POSITIVE = {"in", "contains_any", "contains_all", "equals_set", "equals_any_set"}


def asks_colour(filters, routes):
    """A colour filter that requires a colour, or a residual phrase the phrase bank reads as a shade."""
    return any(f.get("feature") == "colors" and f.get("operator") in POSITIVE for f in filters) \
        or any(r["kind"] == "shade" and not r["skipped"] for r in routes)
PAGE = common.SEARCH_UI / "static/index.html"
EXAMPLES = common.SEARCH_UI / "static/example_queries.yaml"
EXAMPLES_SHOWN = 10
IMAGE_PATH = re.compile(r"images/(?:train|validation)/(?P<product>[A-Za-z0-9_-]+)/(?P<stem>[A-Za-z0-9_-]+)\.png")


def load_sentence_weights(path=SENTENCE_WEIGHTS):
    """{part: weight} of the sentence ranking, or None when the file is missing."""
    if not Path(path).exists():
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))["weights"]


def ms(t):
    return round((time.perf_counter() - t) * 1000, 1)


def _text(v):
    # SSENSE data still contains HTML entities, e.g. "Piqu&eacute;"
    return html.unescape(str(v)) if v else ""


def _show_value(v):
    if isinstance(v, dict):
        return ", ".join(f"{m} {s:g}%" for m, s in sorted(v.items(), key=lambda kv: -kv[1]))
    return ", ".join(map(str, v)) if isinstance(v, list) else str(v)


def _show_price(p):
    value = conditions.product_price(p)
    if value is None:
        return ""
    return (f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}") + " USD"


def _z(s, mask):
    if not mask.any():
        return np.zeros_like(s)
    return (s - s[mask].mean()) / (s[mask].std() + 1e-9)


def image_z(s_i, mask):
    """z-scores of the image similarity among the candidates with an image; the others come last."""
    z = _z(s_i, mask)
    z[~mask] = z[mask].min() - 1 if mask.any() else 0
    return z


class SearchEngine:
    def __init__(self, products, T, I, parser, embedder, concept_data=None, bank=None, F=None, weights=HYBRID,
                 attributes=None, sentences=None, sentence_weights=None, image_dir=common.DATASET, reranker=None):
        """concept_data: the concepts (concepts.py); bank: the phrase bank (bank.py), without which hybrid ranks by
        the whole query only (main() does not start the server without it); F: the feature text embeddings;
        attributes: {product_id: {"colours": [...], "details": [...]}} shown with a product; sentences: the sentence
        embeddings (sentences.py) and sentence_weights: {part: weight}, both needed by the sentence ranking;
        reranker: the Jev second stage."""
        self.products = [conditions.prepare_product(p) for p in products]
        self.attributes = attributes or {}
        self.concepts, self.bank, self.F, self.weights = concept_data, bank, F, dict(weights)
        self.sentences, self.sentence_weights = sentences, sentence_weights
        self.reranker = reranker if reranker is not None else \
            jev_reranker.JevReranker(image_dir=image_dir, timeout=15.0, photo_cache=jev_reranker.PHOTO_CACHE
                                     if Path(image_dir).resolve() == common.DATASET.resolve() else None)
        with_sentences = all(x is not None for x in (bank, F, sentences, sentence_weights))
        self.rankings = [r for r in RANKINGS if with_sentences or RERANK_BASES.get(r, r) != "sentences"]
        self.T, self.I = T, I
        self.has_image = np.linalg.norm(I, axis=1) > 0
        self.parser, self.embedder = parser, embedder
        self.vocabulary = conditions.Vocabulary(self.products)
        self.facets = facets.load(self.products)
        self.by_id = {p["product_id"]: p for p in self.products}
        self.position = {p["product_id"]: i for i, p in enumerate(self.products)}
        self.pool = ThreadPoolExecutor(8)
        self.examples = pick_examples(parser.examples, parser, self.products, self.vocabulary) \
            if getattr(parser, "examples", None) else None

    def base_jobs(self, q, routes, jobs, variants, timings, out):
        """The query embeddings of the similarity of the whole query: of the query without its negated phrases when
        it has any (bank.base_query), from variants when started earlier, otherwise jobs."""
        base = self.bank.base_query(q, routes)
        if base is None:
            return jobs
        out["base_query"] = base
        return (variants or {}).get(base) or self.query_vectors(base, timings)

    def rank(self, q, ranking, cand, category, timings, out, jobs=None, prefetched=None, variants=None):
        """-> (score, description similarity, image similarity) of the candidates by hybrid or sentences. jobs: the
        query embeddings, when started earlier; prefetched: phrase embeddings started earlier (bank.prefetch);
        variants: {query without a negated span: its query embeddings}, started earlier (base_jobs)."""
        t = time.perf_counter()
        jobs = jobs or self.query_vectors(q, timings)
        if ranking == "sentences":
            columns, s_t, s_i = self.sentence_columns(jobs, q, cand, category, timings, out, t, prefetched, variants)
            w = self.sentence_weights
            out["_parts"] = {label: w[part] * column for part, label, column in columns if w.get(part)}
            names = dict(sentences="best sentences", concept="concepts of each phrase",
                         phrase="best sentence of each phrase")
            out["formula"] = " + ".join(f"{w[k]:.3g} × {names.get(k, k)}" for k in SENTENCE_PARTS if w.get(k)) \
                + "; a negated phrase counts with a minus"
            return sum(out["_parts"].values(), np.zeros(len(cand))), s_t, s_i
        terms, routes = dict(concept=[], negation=[], colour=[], detail=[]), []
        if self.bank is not None:
            terms, routes = self.bank.adjustments(out["parsed"]["residual"], cand, category, query=q,
                                                  prefetched=prefetched, stats=timings)
            out["bank"] = routes
            jobs = self.base_jobs(q, routes, jobs, variants, timings, out)
        timings["bank_ms"] = ms(t)
        out["image_weight"] = COLOUR_IMAGE_WEIGHT if asks_colour(out["parsed"]["filters"], routes) else 1.0
        parts = out["_parts"] = {}
        base, s_t, s_i = self.query_similarity(jobs, cand, timings, t, image_weight=out["image_weight"], parts=parts)
        columns = {k: iter(v) for k, v in terms.items()}
        for r in routes:
            if r.get("term"):
                sign = -1 if r["term"] == "negation" else 1
                parts[f"{r['term']} · {r['phrase']}"] = sign * self.weights[r["term"]] * next(columns[r["term"]])
        return self.combine(base, terms), s_t, s_i

    def sentence_columns(self, jobs, q, cand, category, timings, out, t, prefetched=None, variants=None):
        """The parts of the sentence ranking before their weights, [(part, label, column over the candidates)]:
        the z-scores of the similarity of the whole query to the description, to the two best sentences, to the
        image and to the feature text; and for every residual phrase its concept scores and its best sentence
        (bank.sentence_terms). -> (columns, description similarity, image similarity)."""
        terms, out["bank"] = self.bank.sentence_terms(out["parsed"]["residual"], cand, category, query=q,
                                                      prefetched=prefetched, stats=timings)
        timings["bank_ms"] = ms(t)
        jobs = self.base_jobs(q, out["bank"], jobs, variants, timings, out)
        v = {k: common.normalize(f.result()) for k, f in jobs.items()}
        timings["embedding_wait_ms"] = ms(t)
        s_t, s_i = self.T[cand] @ v["t"], self.I[cand] @ v["i"]
        everyone = np.ones(len(cand), bool)
        out["image_weight"] = 1.0
        columns = [("description", "description", _z(s_t, everyone)),
                   ("sentences", "sentences", _z(self.sentences.whole(v["t"], cand), everyone)),
                   ("image", "image", image_z(s_i, self.has_image[cand])),
                   ("features", "features", _z(self.F[cand] @ v["t"], everyone))]
        # a sentence term is shown around the mean of the candidates, like the z-scores; the order stays the same
        columns += [("concept", f"{term} · {phrase}", column) if term == "concept" else
                    ("phrase", f"{term} · {phrase}", column - column.mean()) for term, phrase, column in terms]
        return columns, s_t, s_i

    def combine(self, base, terms, weights=None):
        """Hybrid score: the similarity of the whole query plus the concept, colour and detail terms minus the
        negation terms."""
        w = weights or self.weights
        total = base - w["negation"] * sum(terms["negation"], np.zeros(len(base)))
        for kind in ("concept", "colour", "detail"):
            total = total + w.get(kind, 0.0) * sum(terms.get(kind, []), np.zeros(len(base)))
        return total

    def query_vectors(self, q, timings=None):
        """Starts the embeddings of the query: for the descriptions and feature texts (query format) and for the
        images (plain); the jobs never wait on other jobs of the pool. timings gets query_embedding_ms: from the start
        until the last embedding arrived."""
        start = time.perf_counter()
        jobs = dict(t=self.pool.submit(self.embedder, common.query_text(q)), i=self.pool.submit(self.embedder, q))
        if timings is not None:
            for f in jobs.values():
                f.add_done_callback(lambda _: timings.__setitem__(
                    "query_embedding_ms", max(timings.get("query_embedding_ms", 0), ms(start))))
        return jobs

    def query_similarity(self, jobs, cand, timings, t, image_weight=1.0, parts=None):
        """The similarity of the whole query in hybrid: the mean of the z-scores of its similarity to the description,
        the image and, when there are feature embeddings, the feature text, the image counting image_weight times.
        parts: a dict that gets the share of each. -> (score, description similarity, image similarity)."""
        v = {k: common.normalize(f.result()) for k, f in jobs.items()}
        timings["embedding_wait_ms"] = ms(t)
        s_t, s_i = self.T[cand] @ v["t"], self.I[cand] @ v["i"]
        everyone = np.ones(len(cand), bool)
        shares = {"description": _z(s_t, everyone), "image" + (f" ×{image_weight:g}" if image_weight != 1 else ""):
                  image_weight * image_z(s_i, self.has_image[cand])}
        if self.F is not None:
            shares["features"] = _z(self.F[cand] @ v["t"], everyone)
        shares = {k: x / (len(shares) - 1 + image_weight) for k, x in shares.items()}
        if parts is not None:
            parts.update(shares)
        return sum(shares.values()), s_t, s_i

    def search(self, q, ranking="hybrid", manual=None):
        """manual: {"category", "filters", "residual"} in the parser format; when given, the parser is not called."""
        t0 = time.perf_counter()
        timings = {}
        out = dict(query=q, parser=self.parser.name, ranking=ranking, timings=timings,
                   counts=dict(index=len(self.products)), warnings=[])
        base_ranking = RERANK_BASES.get(ranking, ranking)

        def fail(stage, e):
            timings["total_ms"] = ms(t0)
            out["error"] = dict(stage=stage, message=f"{type(e).__name__}: {str(e)[:500]}")
            traceback.print_exc()
            return out

        # the query embeddings do not depend on the parser, so they run while it parses
        jobs = self.query_vectors(q, timings) if q else None
        # so do the embeddings of the spans of the query, which the residual phrases usually are
        prefetched = self.bank.prefetch(q, lean=base_ranking == "sentences") \
            if q and manual is None and self.bank is not None else None
        # and so does the query without each span that could be a negated phrase (base_jobs)
        variants = {v: self.query_vectors(v) for v in self.bank.negation_variants(q)} \
            if q and self.bank is not None else None
        t = time.perf_counter()
        try:
            if manual is None:
                raw = self.parser(q)
                out["raw"] = raw
                out["parser_info"] = parser_adapter.parser_info(raw)
                timings["parsing_ms"] = ms(t)
            else:
                raw = dict(category=manual.get("category"), filters=manual.get("filters") or [],
                           residual=parser_adapter.residual_list(manual.get("residual"))[:10])
                out["parser_info"] = dict(category=raw["category"], residual=raw["residual"], source="manual")
            out["parsed"] = dict(category=raw.get("category"), filters=parser_adapter.expand_price(raw.get("filters") or []),
                                 residual=parser_adapter.residual_list(raw.get("residual")),
                                 source="manual" if manual else "parser")
            tree = parser_adapter.to_condition(raw)
        except parser_adapter.OutOfCatalog as e:
            timings.setdefault("parsing_ms", ms(t))
            timings["total_ms"] = ms(t0)
            out.update(match="out_of_catalog", message=str(e), results=[])
            out["counts"]["candidates"] = 0
            return out
        except Exception as e:
            if manual is None:
                timings.setdefault("parsing_ms", ms(t))
            return fail("parsing" if manual is None else "filters", e)

        t = time.perf_counter()
        tree, out["warnings"] = conditions.canonicalize(tree, self.vocabulary)
        f = conditions.filter_products(tree, self.products)
        timings["filtering_ms"] = ms(t)
        cand = np.array(f["candidates"], dtype=int)
        out.update(tree=tree, condition=conditions.describe(tree), match="full" if len(cand) else "none")
        out["counts"]["candidates"] = len(cand)

        t = time.perf_counter()
        s_t = s_i = None
        rerank_parts = {}
        if len(cand) and q:
            try:
                score, s_t, s_i = self.rank(q, base_ranking, cand, out["parsed"]["category"], timings, out, jobs,
                                            prefetched, variants)
            except Exception as e:
                timings["ranking_ms"] = ms(t)
                return fail("ranking", e)
            order = np.argsort(-score, kind="stable")
            if ranking in RERANK_BASES:
                start = time.perf_counter()
                try:
                    top = order[:jev_reranker.DEPTH]
                    products = [self.products[int(cand[j])] for j in top]
                    ids, rerank_parts, out["rerank"] = self.reranker(q, out["parsed"]["category"], products, score[top])
                    positions = {p["product_id"]: j for p, j in zip(products, top)}
                    if len(ids) != len(top) or set(ids) != set(positions):
                        raise ValueError("Reranker changed the candidate set")
                    if out["rerank"].get("status") == "applied" and out["rerank"]["images"] < len(top):
                        out["warnings"].append(f"Jev vision received photos for {out['rerank']['images']} of "
                                               f"{len(top)} products; the others were evaluated from text only.")
                    order = np.concatenate(([positions[pid] for pid in ids], order[len(top):]))
                except Exception as e:
                    rerank_parts = {}
                    out["rerank"] = dict(status="fallback", count=0)
                    if isinstance(e, jev_reranker.NoProductImages):
                        reason = "No readable product photos for Jev vision."
                    else:
                        reason = "Check OPENROUTER_API_KEY and the connection to OpenRouter, the local photos and Pillow."
                    out["warnings"].append(f"Jev reranking unavailable; showing the {base_ranking} ranking. {reason}")
                out["rerank"]["base_ranking"] = base_ranking
                timings["rerank_ms"] = ms(start)
        else:
            score, order = np.zeros(len(cand)), np.arange(len(cand))
        timings["ranking_ms"] = ms(t)

        columns = self.concept_columns(out)
        parts = out.pop("_parts", None) or {}
        if parts and len(cand):
            out["score_parts"] = [dict(label=k, spread=round(float(np.std(v)), 3)) for k, v in parts.items()]
            out["weights"] = dict(self.weights) if base_ranking == "hybrid" else None
        asked = {n for r in out.get("bank") or [] if r.get("detail") for n in r["detail"]["names"]}
        results = []
        for j in order:
            i = int(cand[j])
            p = self.products[i]
            extra = self.attributes.get(p["product_id"], {})
            results.append(dict(
                id=p["product_id"], name=_text(p["name"]), brand=_text(p.get("brand")), category=p["category"],
                section=p["section"], gender=p.get("gender") or "",
                price=_show_price(p),
                image=f"/images/{p['images'][0]}" if p["images"] else "",
                score=round(float(score[j]), 4),
                rerank=rerank_parts.get(p["product_id"]),
                score_text=None if s_t is None else round(float(s_t[j]), 4),
                score_image=None if s_i is None else round(float(s_i[j]), 4),
                features={k: _show_value(v) for k, v in sorted(p["features"].items())},
                matched=f["matched"].get(i, []),
                concepts=self.concepts.product_scores(i, columns) if columns else [],
                parts={k: round(float(v[j]), 3) for k, v in parts.items()},
                details=[d for d in extra.get("details", []) if d["name"] in asked]))
        out["results"] = results
        timings["total_ms"] = ms(t0)
        return out

    def concept_columns(self, out):
        """Concept columns the ranking used, shown with every result. A phrase can carry concepts it does not use: a
        shade takes those of its nearest bank phrase ("navy" -> "navy formal") but only its colour counts."""
        if not self.concepts:
            return None
        used = dict.fromkeys(c for r in out.get("bank") or [] if r.get("concepts_used") for c in r["concepts"])
        return [self.concepts.ids.index(c) for c in used if c in self.concepts.ids] or None

    def product(self, pid):
        p = self.by_id.get(pid)
        if p is None:
            return None
        return dict(id=pid, name=_text(p["name"]), brand=_text(p.get("brand")), category=p["category"], section=p["section"],
                    gender=p.get("gender") or "", price=_show_price(p), description=_text(p.get("description")),
                    composition=_text(p.get("composition")), season=p.get("season") or "",
                    original_category=f"{p.get('original_section')} / {p.get('original_category')}",
                    status=p.get("status"), images=[f"/images/{z}" for z in p["images"]],
                    features={k: _show_value(v) for k, v in sorted(p["features"].items())},
                    concepts=sorted(self.concepts.product_scores(self.position[pid]), key=lambda c: -c["score"])
                    if self.concepts else [], **self.attributes.get(pid, {}))


def pick_examples(pool, parser, products, vocabulary, n=EXAMPLES_SHOWN):
    """The first n queries of every group that find at least one product or get no category on purpose. The pool
    comes from the parser module and is parsed here, so it must not need API calls."""
    out = {}
    for group, queries in pool.items():
        keep = []
        for q in queries:
            try:
                tree, _ = conditions.canonicalize(parser_adapter.to_condition(parser(q)), vocabulary)
            except parser_adapter.OutOfCatalog:
                keep.append(q)
            else:
                if conditions.filter_products(tree, products)["candidates"]:
                    keep.append(q)
            if len(keep) == n:
                break
        out[group] = keep
    return out


def build_server(engine, image_dir, port=8000, ranking=DEFAULT_RANKING, examples=EXAMPLES, page=PAGE):
    image_dir = Path(image_dir).resolve()
    pilot_dirs = tuple(dict.fromkeys((image_dir / common.PILOT.name, common.PILOT)))
    excluded_ids = common.excluded_product_ids()

    class Handler(BaseHTTPRequestHandler):
        def send(self, code, body, content_type="application/json; charset=utf-8"):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            params = parse_qs(u.query)
            try:
                if u.path == "/":
                    return self.send(200, Path(page).read_bytes(), "text/html; charset=utf-8")
                if u.path == "/api/info":
                    ex = engine.examples or (yaml.safe_load(Path(examples).read_text(encoding="utf-8"))
                                             if Path(examples).exists() else {})
                    ex = {k: [x if isinstance(x, str) else x["q"] for x in v or []] for k, v in (ex or {}).items()}
                    return self.send(200, dict(parser=engine.parser.name, ranking=ranking, rankings=engine.rankings,
                                               parser_categories=engine.parser.categories,
                                               products=len(engine.products), facets=engine.facets, examples=ex,
                                               categories={k: sum(p["category"] == k for p in engine.products)
                                                           for k in engine.facets}))
                if u.path == "/api/search":
                    q = params.get("q", [""])[0].strip()[:300]
                    r = params.get("ranking", [ranking])[0]
                    manual = json.loads(params["filters"][0]) if params.get("filters") else None
                    if (not q and manual is None) or r not in engine.rankings:
                        return self.send(400, {"error": dict(stage="request", message="empty query or unknown ranking")})
                    return self.send(200, engine.search(q, r, manual))
                if u.path == "/api/product":
                    p = engine.product(params.get("id", [""])[0])
                    return self.send(200, p) if p else self.send(404, {"error": dict(stage="product", message="no such product")})
                if u.path.startswith("/images/"):
                    rel = u.path[len("/images/"):]
                    match = IMAGE_PATH.fullmatch(rel)
                    if match:
                        if match["product"] in excluded_ids:
                            return self.send(404, {"error": dict(stage="product", message="no such product")})
                        photo = Path(match["product"]) / match["stem"]
                        for pilot in pilot_dirs:
                            enhanced = pilot / "images_enhanced" / photo.with_suffix(".webp")
                            if not enhanced.is_file():
                                continue
                            mask = pilot / "image_masks" / photo.with_suffix(".png")
                            if mask.is_file():
                                return self.send(200, render_webp(enhanced, mask), "image/webp")
                            return self.send(200, enhanced.read_bytes(), "image/webp")
                        original = image_dir / rel
                        if original.is_file():
                            return self.send(200, original.read_bytes(), "image/png")
                self.send(404, {"error": dict(stage="request", message="not found")})
            except Exception as e:
                traceback.print_exc()
                self.send(500, {"error": dict(stage="server", message=f"{type(e).__name__}: {str(e)[:500]}")})

        def log_message(self, *a):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def load_product_embeddings(products, meta, enhanced=True):
    """Description and photo embeddings of the products; with enhanced, the photo embeddings of the 1024 px front
    photos (offline/image_embeddings.py, embeddings/image_enhanced.parquet of the pilot) replace the original ones
    where they exist."""
    _, text, image = common.load_embeddings(meta["embeddings"])
    path = common.ENHANCED_IMAGE_EMBEDDINGS
    if enhanced and path.exists():
        stored = pd.read_parquet(path, columns=["product_id", "embedding"])
        image = dict(image) | {pid: np.asarray(v, np.float32) for pid, v in zip(stored["product_id"], stored["embedding"])}
        print(f"Photo embeddings: {len(stored)} from the 1024 px photos")
    missing = [p["product_id"] for p in products
               if p["product_id"] not in text or (p["images"] and p["product_id"] not in image)]
    if missing:
        sys.exit(f"No embeddings for {len(missing)} indexed products (e.g. {missing[:3]}), rerun prepare.py")
    zero = np.zeros(meta["dim"], np.float32)
    T = common.normalize(np.stack([text[p["product_id"]] for p in products]))
    I = np.stack([image.get(p["product_id"], zero) for p in products])
    return T, np.where(np.linalg.norm(I, axis=1, keepdims=True) > 0, common.normalize(I), 0)


def product_attributes():
    """{product_id: {"colours": [...], "details": [...]}} from the files of ranking_data/ that exist."""
    import colours
    import details
    out = {}
    if colours.PRODUCTS.exists():
        for r in pd.read_parquet(colours.PRODUCTS).sort_values(["product_id", "rank"]).itertuples():
            out.setdefault(r.product_id, {}).setdefault("colours", []).append(
                dict(name=r.name, hex=r.hex, family=r.family, share=round(float(r.share), 2)))
    if details.PRODUCTS.exists():
        for r in pd.read_parquet(details.PRODUCTS).sort_values(["product_id", "rank"]).itertuples():
            out.setdefault(r.product_id, {}).setdefault("details", []).append(dict(name=r.name, extent=r.extent))
    return out


def load_feature_embeddings(products, folder):
    """Embeddings of the feature texts aligned with the products, or None when prepare.py did not build them."""
    path = Path(folder) / common.FEATURE_VECTORS
    if not path.exists():
        return None
    stored = np.load(path)
    positions = {str(product): i for i, product in enumerate(stored["ids"])}
    if any(p["product_id"] not in positions for p in products):
        print("Feature embeddings do not match the index; rerun prepare.py")
        return None
    return stored["vectors"][[positions[p["product_id"]] for p in products]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parser", default="llm", help="llm, mock or module:function")
    ap.add_argument("--ranking", choices=RANKINGS,
                    help=f"default ranking in the page ({DEFAULT_RANKING})")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--data", type=Path, default=common.DATA)
    ap.add_argument("--no-warmup", action="store_true", help="skip the test embedding call at startup")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--original-images", action="store_true",
                    help="use the embeddings of the original 256 px photos instead of the 1024 px ones")
    args = ap.parse_args()

    t = time.perf_counter()
    products, meta = common.load_index(args.data)
    T, I = load_product_embeddings(products, meta, enhanced=not args.original_images)
    print(f"Index: {len(products)} products ({', '.join(f'{k} {v}' for k, v in meta['categories'].items())}) "
          f"· embeddings {meta['model']}, {meta['dim']} dims · {ms(t):.0f} ms")
    embedder = common.QueryEmbedder(meta["model"], meta["dim"])
    if not args.no_warmup:
        t = time.perf_counter()
        try:
            embedder(common.query_text("warm-up"))
            print(f"Embedding API warm-up: {ms(t):.0f} ms")
        except Exception as e:
            print(f"Embedding API warm-up failed ({type(e).__name__}): check the network and GCP credentials")
    concept_data = concepts.load(args.data, meta, products)
    if concept_data:
        info = meta["concepts"]
        print(f"Concepts: {len(concept_data.ids)}, all used in {', '.join(info['categories']) or 'no category'}"
              + "".join(f"; {c}: {a} of {b} concepts" for c, (a, b) in info.get("partial", {}).items()))
    bank_ranker = sentence_data = None
    t = time.perf_counter()
    try:
        import bank
        import colours
        import details
        import sentences
        rows = bank.load_rows()
        stored = np.load(args.data / bank.VECTORS)
        if stored["phrases"].tolist() != [r["phrase"] for r in rows]:
            raise OSError("the phrase bank changed since prepare.py; rerun it")
        colour_data, detail_data = colours.load(products, args.data), details.load(products, args.data)
        sentence_data = sentences.load(products, args.data)
        bank_ranker = bank.BankRanker(products, T, I, Path(meta["dataset"]), rows, stored["vectors"], embedder,
                                      concepts.scored_concepts(meta.get("concepts") or {}),
                                      concept_data.ids if concept_data else (),
                                      concept_data.E if concept_data else None, colour_data, detail_data, sentence_data)
        print(f"Phrase bank: {len(rows)} phrases · colours: "
              f"{f'{len(colour_data.names)} names' if colour_data else 'missing, run prepare.py'} · details: "
              f"{f'{len(detail_data.names)} names' if detail_data else 'missing, run prepare.py'} · sentences: "
              f"{f'{len(sentence_data.E)}' if sentence_data else 'missing, run prepare.py'} · {ms(t):.0f} ms")
    except (ImportError, OSError) as e:
        sys.exit(f"No phrase bank ({type(e).__name__}: {str(e)[:200]}). Every ranking needs it: run "
                 "python search_ui/prepare.py and start the server again.")
    F = load_feature_embeddings(products, args.data)
    print(f"Feature embeddings: {'loaded' if F is not None else 'missing, run prepare.py'}")
    parser = parser_adapter.load_parser(args.parser, conditions.Vocabulary(products))
    engine = SearchEngine(products, T, I, parser, embedder, concept_data, bank_ranker, F,
                          attributes=product_attributes(), sentences=sentence_data,
                          sentence_weights=load_sentence_weights(), image_dir=meta["dataset"])
    args.ranking = args.ranking or DEFAULT_RANKING
    if args.ranking not in engine.rankings:
        sys.exit(f"--ranking {args.ranking} is not available; available: {', '.join(engine.rankings)}")
    print(f"Parser: {engine.parser.name} · ranking: {args.ranking}")
    srv = build_server(engine, meta["dataset"], args.port, args.ranking)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"\nReady: {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
