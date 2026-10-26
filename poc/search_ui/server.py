"""
Search demo: query -> parser -> feature filtering -> embedding ranking -> results with per-stage timings.
Filters can also be set by hand in the page; the parser is then skipped.

    python poc/search_ui/server.py --parser llm
    python poc/search_ui/server.py --parser mock --ranking combined --top 24 --port 8000

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

import common
import conditions
import facets
import parser_adapter

RANKINGS = ("combined", "text", "image", "hyde")
RANK_BY = ("residual", "query")
PAGE = common.HERE / "static" / "index.html"
EXAMPLES = common.HERE / "example_queries.yaml"
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


def _z(s, mask):
    if not mask.any():
        return np.zeros_like(s)
    return (s - s[mask].mean()) / (s[mask].std() + 1e-9)


class SearchEngine:
    def __init__(self, products, T, I, parser, embedder, hyde=None, max_results=480):
        self.products = [conditions.prepare_product(p) for p in products]
        self.T, self.I = T, I
        self.has_image = np.linalg.norm(I, axis=1) > 0
        self.parser, self.embedder, self.hyde, self.max_results = parser, embedder, hyde, max_results
        self.vocabulary = conditions.Vocabulary(self.products)
        self.facets = facets.load(self.products)
        self.by_id = {p["product_id"]: p for p in self.products}
        self.pool = ThreadPoolExecutor(2)

    def rank(self, q, ranking, cand, category, timings, out):
        """-> (score, text similarity, image similarity) for the candidates."""
        if ranking == "hyde":
            t = time.perf_counter()
            out["hyde"] = self.hyde(q, category)
            timings["hyde_ms"] = ms(t)
            t = time.perf_counter()
            s_t = self.T[cand] @ common.normalize(self.embedder(out["hyde"]))
            timings["query_embedding_ms"] = ms(t)
            return s_t, s_t, None
        t = time.perf_counter()
        jobs = {}
        if ranking in ("text", "combined"):
            jobs["t"] = self.pool.submit(self.embedder, common.query_text(q))
        if ranking in ("image", "combined"):
            jobs["i"] = self.pool.submit(self.embedder, q)
        v = {k: common.normalize(f.result()) for k, f in jobs.items()}
        timings["query_embedding_ms"] = ms(t)
        s_t = self.T[cand] @ v["t"] if "t" in v else None
        s_i = self.I[cand] @ v["i"] if "i" in v else None
        if ranking == "text":
            return s_t, s_t, s_i
        mask = self.has_image[cand]
        if ranking == "image":
            return np.where(mask, s_i, -1.0), s_t, s_i
        z_i = _z(s_i, mask)
        z_i[~mask] = z_i[mask].min() - 1 if mask.any() else 0
        return (_z(s_t, np.ones(len(cand), bool)) + z_i) / 2, s_t, s_i

    def search(self, q, ranking="combined", manual=None, rank_by="residual"):
        """
        manual: {"category", "filters", "residual"} in the parser format; when given, the parser is not called.
        rank_by: rank by the residual (falls back to the full query when it is empty) or by the full query.
        """
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
                           residual=manual.get("residual") or "")
                out["parser_info"] = dict(category=raw["category"], residual=raw["residual"], source="manual")
            out["parsed"] = dict(category=raw.get("category"), filters=raw.get("filters") or [],
                                 residual=raw.get("residual") or "", source="manual" if manual else "parser")
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
        tree, out["warnings"] = conditions.prune(tree, self.vocabulary)
        f = conditions.filter_products(tree, self.products)
        timings["filtering_ms"] = ms(t)
        cand = np.array(f["candidates"], dtype=int)
        out.update(tree=tree, condition=conditions.describe(tree), match="full" if len(cand) else "none")
        out["counts"]["candidates"] = len(cand)

        residual = out["parsed"]["residual"].strip()
        text = residual if rank_by == "residual" and residual else q
        out["rank_by"] = "residual" if text and text == residual and rank_by == "residual" else "query"
        out["ranking_text"] = text

        t = time.perf_counter()
        s_t = s_i = None
        if len(cand) and text:
            try:
                score, s_t, s_i = self.rank(text, ranking, cand, out["parsed"]["category"], timings, out)
            except Exception as e:
                timings["ranking_ms"] = ms(t)
                return fail("ranking", e)
            order = np.argsort(-score, kind="stable")
        else:
            score, order = np.zeros(len(cand)), np.arange(len(cand))
        timings["ranking_ms"] = ms(t)

        results = []
        for j in order[: self.max_results]:
            i = int(cand[j])
            p = self.products[i]
            results.append(dict(
                id=p["product_id"], name=_text(p["name"]), brand=_text(p.get("brand")), category=p["category"],
                section=p["section"], gender=p.get("gender") or "",
                price="" if p.get("msrpUSD") in (None, "") or p["msrpUSD"] != p["msrpUSD"] else f"{float(p['msrpUSD']):,.0f} USD",
                image=f"/images/{p['images'][0]}" if p["images"] else "",
                score=round(float(score[j]), 4),
                score_text=None if s_t is None else round(float(s_t[j]), 4),
                score_image=None if s_i is None else round(float(s_i[j]), 4),
                features={k: _show_value(v) for k, v in sorted(p["features"].items())},
                matched=f["matched"].get(i, [])))
        out["results"] = results
        timings["total_ms"] = ms(t0)
        return out

    def product(self, pid):
        p = self.by_id.get(pid)
        if p is None:
            return None
        return dict(id=pid, name=_text(p["name"]), brand=_text(p.get("brand")), category=p["category"], section=p["section"],
                    gender=p.get("gender") or "", description=_text(p.get("description")),
                    composition=_text(p.get("composition")), season=p.get("season") or "",
                    original_category=f"{p.get('original_section')} / {p.get('original_category')}",
                    status=p.get("status"), images=[f"/images/{z}" for z in p["images"]],
                    features={k: _show_value(v) for k, v in sorted(p["features"].items())})


def build_server(engine, image_dir, port=8000, ranking="combined", top=24, examples=EXAMPLES, page=PAGE,
                 rank_by="residual"):
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
                    ex = yaml.safe_load(Path(examples).read_text(encoding="utf-8")) if Path(examples).exists() else {}
                    ex = {k: [x if isinstance(x, str) else x["q"] for x in v or []] for k, v in (ex or {}).items()}
                    return self.send(200, dict(parser=engine.parser.name, ranking=ranking, rankings=RANKINGS, top=top,
                                               rank_by=rank_by,
                                               products=len(engine.products), facets=engine.facets, examples=ex,
                                               categories={k: sum(p["category"] == k for p in engine.products)
                                                           for k in engine.facets}))
                if u.path == "/api/search":
                    q = params.get("q", [""])[0].strip()[:300]
                    r = params.get("ranking", [ranking])[0]
                    by = params.get("rank_by", [rank_by])[0]
                    manual = json.loads(params["filters"][0]) if params.get("filters") else None
                    if (not q and manual is None) or r not in RANKINGS or by not in RANK_BY:
                        return self.send(400, {"error": dict(stage="request", message="empty query or unknown ranking")})
                    return self.send(200, engine.search(q, r, manual, by))
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parser", default="llm", help="llm, mock or module:function")
    ap.add_argument("--ranking", choices=RANKINGS, default="combined")
    ap.add_argument("--rank-by", choices=RANK_BY, default="residual", help="text used for ranking")
    ap.add_argument("--hyde-model", default="gemini-3.5-flash-lite")
    ap.add_argument("--top", type=int, default=24)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--data", type=Path, default=common.DATA)
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
    parser = parser_adapter.load_parser(args.parser, conditions.Vocabulary(products))
    engine = SearchEngine(products, T, I, parser, embedder, common.HydeWriter(args.hyde_model))
    print(f"Parser: {engine.parser.name} · ranking: {args.ranking} by {args.rank_by}")
    srv = build_server(engine, meta["dataset"], args.port, args.ranking, args.top, rank_by=args.rank_by)
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
