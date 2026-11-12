"""
Search demo: query -> parser -> feature filtering -> embedding ranking -> results with per-stage timings.
Filters can also be set by hand in the page; the parser is then skipped.

    python search_ui/server.py
    python search_ui/server.py --parser mock --ranking combined --port 8000

Ranking compares the query embedding with the description and main image embeddings of the candidates
(combined, text, image), or uses the concept scores of the products: "concepts" matches every residual phrase with
the concept names by embedding (concepts.py), "bank" labels the phrases with the phrase bank and scores them locally
(bank.py), the combined similarity breaking its ties. Both rank by concepts only in categories where every product has concept scores.
No caching: every query, including a repeated one, goes through the parser and the embedding API.
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
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))
import common  # noqa: E402
import concepts  # noqa: E402
import conditions  # noqa: E402
import facets  # noqa: E402
import parser_adapter  # noqa: E402

RANKINGS = ("combined", "text", "image", "features", "combined_features", "concepts", "bank", "hybrid")
HYBRID = dict(concept=0.5, negation=1.0, colour=1.0)
COLOUR_IMAGE_WEIGHT = 2.0
POSITIVE = {"in", "contains_any", "contains_all", "equals_set"}


def asks_colour(filters, routes):
    """A colour filter that requires a colour, or a residual phrase the phrase bank reads as a shade."""
    return any(f.get("feature") == "colors" and f.get("operator") in POSITIVE for f in filters) \
        or any(r["kind"] == "shade" and not r["skipped"] for r in routes)
PAGE = common.SEARCH_UI / "static/index.html"
EXAMPLES = common.SEARCH_UI / "static/example_queries.yaml"
EXAMPLES_SHOWN = 5
IMAGE_PATH = re.compile(r"images/(?:train|validation)/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.png")


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


class SearchEngine:
    def __init__(self, products, T, I, parser, embedder, concept_ranker=None, bank=None, F=None, weights=HYBRID):
        self.products = [conditions.prepare_product(p) for p in products]
        self.concepts, self.bank, self.F, self.weights = concept_ranker, bank, F, dict(weights)
        needs = dict(concepts=concept_ranker, bank=bank, hybrid=bank, features=F, combined_features=F)
        self.rankings = [r for r in RANKINGS if needs.get(r, True) is not None]
        self.T, self.I = T, I
        self.has_image = np.linalg.norm(I, axis=1) > 0
        self.parser, self.embedder = parser, embedder
        self.vocabulary = conditions.Vocabulary(self.products)
        self.facets = facets.load(self.products)
        self.by_id = {p["product_id"]: p for p in self.products}
        self.position = {p["product_id"]: i for i, p in enumerate(self.products)}
        self.pool = ThreadPoolExecutor(3)
        self.examples = pick_examples(parser.examples, parser, self.products, self.vocabulary) \
            if getattr(parser, "examples", None) else None

    def rank(self, q, ranking, cand, category, timings, out):
        """-> (score, text similarity, image similarity, tie-breaker or None) for the candidates. combined is the
        mean of the z-scores of both similarities; products without an image come last in the image ranking."""
        if ranking == "bank":
            t = time.perf_counter()
            jobs = self.query_vectors(q, "combined")
            whole = {}

            def whole_query(routes):
                if not whole:
                    out["image_weight"] = COLOUR_IMAGE_WEIGHT if asks_colour(out["parsed"]["filters"], routes) else 1.0
                    whole["scores"] = self.embedding_scores(jobs, "combined", cand, timings, t,
                                                            image_weight=out["image_weight"])
                return whole["scores"][0]

            score, out["bank"] = self.bank.rank(out["parsed"]["residual"], cand, category, typicality=False, query=q,
                                                whole_query=whole_query)
            timings["bank_ms"] = ms(t)
            whole_query(out["bank"])
            combined, s_t, s_i, _ = whole["scores"]
            return score, s_t, s_i, combined
        if ranking == "hybrid":
            t = time.perf_counter()
            jobs = self.query_vectors(q, "combined")
            terms, out["bank"] = self.bank.adjustments(out["parsed"]["residual"], cand, category, query=q)
            timings["bank_ms"] = ms(t)
            out["image_weight"] = COLOUR_IMAGE_WEIGHT if asks_colour(out["parsed"]["filters"], out["bank"]) else 1.0
            base, s_t, s_i, _ = self.embedding_scores(jobs, "combined_features" if self.F is not None else "combined",
                                                      cand, timings, t, image_weight=out["image_weight"])
            return self.combine(base, terms), s_t, s_i, None
        if ranking == "concepts":
            job = self.pool.submit(self.concepts.match, out["parsed"]["residual"], category, q)
            combined, s_t, s_i, _ = self.rank(q, "combined", cand, category, timings, out)
            m = out["concepts"] = job.result()
            if not m["selected"]:
                timings["concepts_ms"] = round(m.pop("ms"), 1)
                return combined, s_t, s_i, None
            t = time.perf_counter()
            score = self.concepts.scores(m["selected"], cand)
            timings["concepts_ms"] = round(m.pop("ms") + (time.perf_counter() - t) * 1000, 1)
            return score, s_t, s_i, combined
        t = time.perf_counter()
        return self.embedding_scores(self.query_vectors(q, ranking), ranking, cand, timings, t)

    def combine(self, base, terms, weights=None):
        """Hybrid score: the similarity of the whole query plus the concept and colour terms minus the negation
        terms."""
        w = weights or self.weights
        return base + w["concept"] * sum(terms["concept"], np.zeros(len(base))) \
            + w.get("colour", 0.0) * sum(terms.get("colour", []), np.zeros(len(base))) \
            - w["negation"] * sum(terms["negation"], np.zeros(len(base)))

    def query_vectors(self, q, ranking):
        """Starts the query embeddings a ranking needs; the jobs never wait on other jobs of the pool."""
        jobs = {}
        if ranking in ("text", "combined", "features", "combined_features"):
            jobs["t"] = self.pool.submit(self.embedder, common.query_text(q))
        if ranking in ("image", "combined", "combined_features"):
            jobs["i"] = self.pool.submit(self.embedder, q)
        return jobs

    def embedding_scores(self, jobs, ranking, cand, timings, t, image_weight=1.0):
        """image_weight: how much the image counts against the description (and the features) in combined."""
        v = {k: common.normalize(f.result()) for k, f in jobs.items()}
        timings["query_embedding_ms"] = ms(t)
        s_t = self.T[cand] @ v["t"] if "t" in v else None
        s_i = self.I[cand] @ v["i"] if "i" in v else None
        if ranking == "text":
            return s_t, s_t, s_i, None
        if ranking == "features":
            return self.F[cand] @ v["t"], s_t, s_i, None
        mask = self.has_image[cand]
        if ranking == "image":
            return np.where(mask, s_i, -1.0), s_t, s_i, None
        z_i = _z(s_i, mask)
        z_i[~mask] = z_i[mask].min() - 1 if mask.any() else 0
        everyone = np.ones(len(cand), bool)
        if ranking == "combined_features":
            return (_z(s_t, everyone) + image_weight * z_i + _z(self.F[cand] @ v["t"], everyone)) / (2 + image_weight), \
                s_t, s_i, None
        return (_z(s_t, everyone) + image_weight * z_i) / (1 + image_weight), s_t, s_i, None

    def search(self, q, ranking="combined", manual=None):
        """manual: {"category", "filters", "residual"} in the parser format; when given, the parser is not called."""
        t0 = time.perf_counter()
        timings = {}
        out = dict(query=q, parser=self.parser.name, ranking=ranking, timings=timings,
                   counts=dict(index=len(self.products)), warnings=[])

        def fail(stage, e):
            timings["total_ms"] = ms(t0)
            out["error"] = dict(stage=stage, message=f"{type(e).__name__}: {str(e)[:500]}")
            traceback.print_exc()
            return out

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
        if len(cand) and q:
            try:
                score, s_t, s_i, tie = self.rank(q, ranking, cand, out["parsed"]["category"], timings, out)
            except Exception as e:
                timings["ranking_ms"] = ms(t)
                return fail("ranking", e)
            order = np.lexsort((-tie, -score)) if tie is not None else np.argsort(-score, kind="stable")
        else:
            score, order = np.zeros(len(cand)), np.arange(len(cand))
        timings["ranking_ms"] = ms(t)

        columns = self.concept_columns(out)
        results = []
        for j in order:
            i = int(cand[j])
            p = self.products[i]
            results.append(dict(
                id=p["product_id"], name=_text(p["name"]), brand=_text(p.get("brand")), category=p["category"],
                section=p["section"], gender=p.get("gender") or "",
                price=_show_price(p),
                image=f"/images/{p['images'][0]}" if p["images"] else "",
                score=round(float(score[j]), 4),
                score_text=None if s_t is None else round(float(s_t[j]), 4),
                score_image=None if s_i is None else round(float(s_i[j]), 4),
                features={k: _show_value(v) for k, v in sorted(p["features"].items())},
                matched=f["matched"].get(i, []),
                concepts=self.concepts.product_scores(i, columns) if columns else []))
        out["results"] = results
        timings["total_ms"] = ms(t0)
        return out

    def concept_columns(self, out):
        """Concept columns the ranking used, shown with every result."""
        if not self.concepts:
            return None
        if out.get("concepts"):
            return [s["column"] for s in out["concepts"]["selected"]] or None
        used = dict.fromkeys(c for r in out.get("bank") or [] if not r["skipped"] for c in r["concepts"])
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
                    if self.concepts else [])


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


def build_server(engine, image_dir, port=8000, ranking="combined", examples=EXAMPLES, page=PAGE):
    image_dir = Path(image_dir).resolve()

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
                    path = image_dir / rel
                    if IMAGE_PATH.fullmatch(rel) and path.is_file():
                        return self.send(200, path.read_bytes(), "image/png")
                self.send(404, {"error": dict(stage="request", message="not found")})
            except Exception as e:
                traceback.print_exc()
                self.send(500, {"error": dict(stage="server", message=f"{type(e).__name__}: {str(e)[:500]}")})

        def log_message(self, *a):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def load_product_embeddings(products, meta):
    _, text, image = common.load_embeddings(meta["embeddings"])
    missing = [p["product_id"] for p in products
               if p["product_id"] not in text or (p["images"] and p["product_id"] not in image)]
    if missing:
        sys.exit(f"No embeddings for {len(missing)} indexed products (e.g. {missing[:3]}), rerun prepare.py")
    zero = np.zeros(meta["dim"], np.float32)
    T = common.normalize(np.stack([text[p["product_id"]] for p in products]))
    I = np.stack([image.get(p["product_id"], zero) for p in products])
    return T, np.where(np.linalg.norm(I, axis=1, keepdims=True) > 0, common.normalize(I), 0)


def load_feature_embeddings(products, folder):
    """Embeddings of the feature texts aligned with the products, or None when prepare.py did not build them."""
    path = Path(folder) / common.FEATURE_VECTORS
    if not path.exists():
        return None
    stored = np.load(path)
    if stored["ids"].tolist() != [p["product_id"] for p in products]:
        print("Feature embeddings do not match the index; rerun prepare.py")
        return None
    return stored["vectors"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parser", default="llm", help="llm, mock or module:function")
    ap.add_argument("--ranking", choices=RANKINGS, help="default ranking in the page (hybrid, or combined without the phrase bank)")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--data", type=Path, default=common.DATA)
    ap.add_argument("--concept-threshold", type=float, default=0.72, help="minimum phrase-concept cosine similarity")
    ap.add_argument("--concept-combine", choices=list(concepts.COMBINE), default="geo",
                    help="how the concept scores of the residual phrases are combined")
    ap.add_argument("--no-bank", action="store_true", help="do not load the phrase-bank ranking")
    ap.add_argument("--no-warmup", action="store_true", help="skip the test embedding call at startup")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    t = time.perf_counter()
    products, meta = common.load_index(args.data)
    T, I = load_product_embeddings(products, meta)
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
    ranker = concepts.load(args.data, meta, products, embedder, threshold=args.concept_threshold,
                           combine=args.concept_combine)
    if ranker:
        info = meta["concepts"]
        print(f"Concepts: {len(ranker.ids)}, all used in {', '.join(info['categories']) or 'no category'}"
              + "".join(f"; {c}: {a} of {b} concepts" for c, (a, b) in info.get("partial", {}).items())
              + f" · threshold {ranker.threshold}, {ranker.combine} of phrases")
    bank_ranker = None
    if not args.no_bank:
        t = time.perf_counter()
        vectors = args.data / "bank_embeddings.npz"
        try:
            import bank
            import colours
            rows = bank.load_rows()
            stored = np.load(vectors)
            if stored["phrases"].tolist() != [r["phrase"] for r in rows]:
                raise OSError("the phrase bank changed since prepare.py; rerun it")
            colour_data = colours.load(products, args.data)
            bank_ranker = bank.BankRanker(products, T, I, Path(meta["dataset"]), rows, stored["vectors"], embedder,
                                          concepts.scored_concepts(meta.get("concepts") or {}),
                                          ranker.ids if ranker else (), ranker.E if ranker else None, colour_data)
            print(f"Phrase bank: {len(rows)} phrases · colours: "
                  f"{f'{len(colour_data.names)} names' if colour_data else 'missing, run prepare.py'} · {ms(t):.0f} ms")
        except (ImportError, OSError) as e:
            print(f"Phrase bank ranking unavailable ({type(e).__name__}: {str(e)[:200]}); run prepare.py")
    F = load_feature_embeddings(products, args.data)
    print(f"Feature embeddings: {'loaded' if F is not None else 'missing, run prepare.py'}")
    parser = parser_adapter.load_parser(args.parser, conditions.Vocabulary(products))
    engine = SearchEngine(products, T, I, parser, embedder, ranker, bank_ranker, F)
    args.ranking = args.ranking or ("hybrid" if "hybrid" in engine.rankings else "combined")
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
