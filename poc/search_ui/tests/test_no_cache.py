import json
import re
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402
from test_conditions import P  # noqa: E402


class Counter:
    def __init__(self, f):
        self.f, self.n = f, 0

    def __call__(self, *a):
        self.n += 1
        return self.f(*a)


def fake_parse(q):
    if "shoes" in q:
        return {"category": None, "filters": []}
    return {"category": "Dresses" if "dress" in q else "Jeans", "filters": []}


def engine(parser=None):
    products = [dict(p, name=f"Product {p['product_id']}", images=[f"images/train/{p['product_id']}/x.png"]) for p in P]
    rng = np.random.default_rng(0)
    T = rng.normal(size=(len(products), 8)).astype(np.float32)
    I = rng.normal(size=(len(products), 8)).astype(np.float32)
    parser = parser or pa.Parser("test", Counter(fake_parse))
    embedder = Counter(lambda text: rng.normal(size=8).astype(np.float32))
    hyde = Counter(lambda q, category: f"Imaginary {category} matching {q}.")
    e = server.SearchEngine(products, T / np.linalg.norm(T, axis=1, keepdims=True),
                            I / np.linalg.norm(I, axis=1, keepdims=True), parser, embedder, hyde)
    return e, embedder


class RepeatedQuery(unittest.TestCase):
    def test_parser_and_api_called_every_time(self):
        e, embedder = engine()
        a = e.search("black jeans", "combined")
        b = e.search("black jeans", "combined")
        self.assertEqual(e.parser.function.n, 2)
        self.assertEqual(embedder.n, 4)
        self.assertEqual(a["counts"]["candidates"], 2)
        self.assertIn("query_embedding_ms", b["timings"])

    def test_out_of_catalog_skips_ranking(self):
        e, embedder = engine()
        d = e.search("red shoes")
        self.assertEqual((d["match"], d["results"], embedder.n), ("out_of_catalog", [], 0))
        self.assertIn("parsing_ms", d["timings"])
        self.assertNotIn("filtering_ms", d["timings"])

    def test_hyde_called_every_time(self):
        e, embedder = engine()
        a = e.search("black dress", "hyde")
        e.search("black dress", "hyde")
        self.assertEqual((e.hyde.n, embedder.n), (2, 2))
        self.assertEqual(a["hyde"], "Imaginary Dresses matching black dress.")
        self.assertIn("hyde_ms", a["timings"])

    def test_manual_filters_skip_the_parser(self):
        e, embedder = engine()
        manual = {"category": "Jeans", "filters": [{"feature": "fit", "operator": "in", "values": ["Slim"]}]}
        d = e.search("", "combined", manual)
        self.assertEqual((e.parser.function.n, embedder.n, d["counts"]["candidates"]), (0, 0, 1))
        self.assertEqual(d["parsed"]["source"], "manual")
        self.assertNotIn("parsing_ms", d["timings"])
        e.search("slim jeans", "combined", manual)
        self.assertEqual((e.parser.function.n, embedder.n), (0, 2))

    def test_no_match_gives_no_results(self):
        e, _ = engine()
        d = e.search("", "combined", {"category": "Dresses", "filters": [{"feature": "colors", "operator": "contains_any",
                                                                         "values": ["White"]}]})
        self.assertEqual((d["match"], d["results"]), ("none", []))

    def test_ranking_uses_the_full_query(self):
        calls = []
        e, embedder = engine(pa.Parser("test", lambda q: {"category": "Dresses", "filters": [], "residual": "for a wedding"}))
        embedder.f = lambda text: calls.append(text) or np.ones(8, np.float32)
        e.search("black dress for a wedding", "text")
        self.assertEqual(calls, ["task: search result | query: black dress for a wedding"])

    def test_text_ranking_one_call(self):
        e, embedder = engine()
        e.search("jeans", "text")
        self.assertEqual(embedder.n, 1)

    def test_parser_error_is_reported_with_timings(self):
        def broken(q):
            raise RuntimeError("parser is down")
        e, _ = engine(pa.Parser("broken", broken))
        d = e.search("anything")
        self.assertEqual(d["error"]["stage"], "parsing")
        self.assertIn("parser is down", d["error"]["message"])
        self.assertIn("parsing_ms", d["timings"])

    def test_no_cache_code_in_sources(self):
        for path in HERE.glob("*.py"):
            self.assertIsNone(re.search(r"lru_cache|functools\.cache|@cache\b", path.read_text(encoding="utf-8")), path.name)


class HttpHeaders(unittest.TestCase):
    def test_no_store_on_every_response(self):
        e, _ = engine()
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "images/train/1").mkdir(parents=True)
            (Path(d) / "images/train/1/x.png").write_bytes(b"\x89PNG")
            srv = server.build_server(e, d, port=0)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            base = f"http://127.0.0.1:{srv.server_address[1]}"
            try:
                for path in ("/", "/api/info", "/api/search?q=jeans", "/api/product?id=1", "/images/images/train/1/x.png"):
                    with urllib.request.urlopen(base + path) as r:
                        self.assertEqual(r.headers["Cache-Control"], "no-store", path)
                with urllib.request.urlopen(base + "/api/search?q=jeans") as r:
                    self.assertEqual(json.loads(r.read())["counts"]["candidates"], 2)
                with self.assertRaises(urllib.error.HTTPError) as err:
                    urllib.request.urlopen(base + "/images/../../etc/passwd")
                self.assertEqual(err.exception.headers["Cache-Control"], "no-store")
            finally:
                srv.shutdown()
                srv.server_close()


if __name__ == "__main__":
    unittest.main()
