import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import concepts  # noqa: E402
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402

E = np.eye(4, dtype=np.float32)
VECTORS = {"wedding guest": E[0], "gym": E[1], "for a wedding": E[0] * 0.9 + E[3] * 0.1,
           "with robert lewandowski": E[3]}
RESIDUALS = {"black dress for a wedding": ("Dresses", ["for a wedding"]), "black dress": ("Dresses", []),
             "dress with robert lewandowski": ("Dresses", ["with robert lewandowski"]),
             "t-shirt for a wedding": ("T-shirts", ["for a wedding"]),
             "dress for a wedding and the gym": ("Dresses", ["for a wedding", "gym"])}
WEDDING = {"d1": 9, "d2": 3, "d3": 9, "d4": 0}
GYM = {"d1": 1, "d2": 6, "d3": 4, "d4": 8}


def product(pid, category):
    p = dict(product_id=pid, category=category, section=category, name=pid, brand="Acne Studios", gender="Women",
             features={}, images=[], description="")
    scored = category == "Dresses"
    p.update({"concept__wedding_guest": float(WEDDING[pid]) if scored else np.nan,
              "concept__gym": float(GYM[pid]) if scored else np.nan})
    return p


class Embedder:
    def __init__(self):
        self.texts = []

    def __call__(self, text):
        self.texts.append(text)
        return VECTORS.get(text.removeprefix("task: search result | query: "), E[2])


def engine(misses, combine="geo"):
    products = [product(p, "Dresses") for p in WEDDING] + [product("t1", "T-shirts")]
    T = np.stack([np.array([0, 0, 1, 0.5 * i], np.float32) for i in range(len(products))])
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    embedder = Embedder()
    rows = pd.DataFrame([dict(id="wedding_guest", name="wedding guest", embedding=E[0].tolist()),
                         dict(id="gym", name="gym", embedding=E[1].tolist())])
    ranker = concepts.ConceptRanker(products, rows, dict(categories=["Dresses"]), embedder, threshold=0.5,
                                    combine=combine, misses=misses)
    parser = pa.Parser("test", lambda q: dict(category=RESIDUALS[q][0], filters=[], residual=RESIDUALS[q][1]))
    return server.SearchEngine(products, T, T.copy(), parser, embedder, ranker), embedder


class Build(unittest.TestCase):
    def test_scored_categories_and_stored_names(self):
        index = pd.DataFrame(dict(product_id=["d1", "d2", "t1", "t2", "j1"],
                                  category=["Dresses", "Dresses", "T-shirts", "T-shirts", "Jeans"]))
        scores = pd.DataFrame([dict(product_id=p, concept_id=c, score=5) for p in ["d1", "d2", "t1"]
                               for c in ["gym", "office"]])
        names = pd.DataFrame([dict(id="gym", name="gym", embedding=[1.0, 0.0])])
        calls = []
        out, rows, categories, partial = concepts.build(
            index, [dict(id="gym", name="gym", type="occasion"), dict(id="office", name="office", type="occasion")],
            scores, names, lambda name: calls.append(name) or [0.0, 2.0])
        self.assertEqual((categories, partial), ({"Dresses": ["gym", "office"]}, {}))
        self.assertEqual(calls, ["office"])
        self.assertEqual(rows["embedding"].tolist(), [[1.0, 0.0], [0.0, 1.0]])
        self.assertTrue(np.isnan(out["concept__gym"].iloc[3]))

    def test_a_concept_is_usable_where_every_product_has_it(self):
        index = pd.DataFrame(dict(product_id=["d1", "d2"], category=["Dresses", "Dresses"]))
        scores = pd.DataFrame([dict(product_id=p, concept_id="gym", score=5) for p in ["d1", "d2"]]
                              + [dict(product_id="d1", concept_id="office", score=5)])
        names = pd.DataFrame([dict(id=c, name=c, embedding=[1.0, 0.0]) for c in ("gym", "office")])
        _, _, scored, partial = concepts.build(index, [dict(id="gym", name="gym", type="occasion"),
                                                       dict(id="office", name="office", type="occasion")],
                                               scores, names, None)
        self.assertEqual((scored, partial), ({"Dresses": ["gym"]}, {"Dresses": [1, 2]}))
        self.assertEqual(concepts.scored_concepts(dict(categories=["Dresses"])), {"Dresses": None})


class Ranking(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.misses = Path(self.tmp.name) / "misses.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def ids(self, d):
        return [r["id"] for r in d["results"]]

    def test_concept_scores_order_and_combined_breaks_ties(self):
        e, _ = engine(self.misses)
        self.assertEqual(self.ids(e.search("black dress for a wedding", "combined")), ["d1", "d2", "d3", "d4"])
        d = e.search("black dress for a wedding", "concepts")
        self.assertEqual(self.ids(d), ["d1", "d3", "d2", "d4"])
        self.assertEqual([s["name"] for s in d["concepts"]["selected"]], ["wedding guest"])
        self.assertEqual(d["results"][0]["concepts"], [dict(name="wedding guest", score=9)])
        self.assertIn("concepts_ms", d["timings"])
        self.assertFalse(self.misses.exists())

    def test_two_phrases_geometric_mean(self):
        e, _ = engine(self.misses)
        d = e.search("dress for a wedding and the gym", "concepts")
        self.assertEqual(self.ids(d)[0], "d3")

    def test_empty_residual_falls_back_without_an_embedding(self):
        e, embedder = engine(self.misses)
        d = e.search("black dress", "concepts")
        self.assertEqual((d["concepts"]["fallback"], self.ids(d)), ("empty residual", ["d1", "d2", "d3", "d4"]))
        self.assertEqual(len(embedder.texts), 2)

    def test_no_concept_above_the_threshold_is_logged(self):
        e, _ = engine(self.misses)
        d = e.search("dress with robert lewandowski", "concepts")
        self.assertEqual(d["concepts"]["fallback"], "no concept above the threshold")
        miss = json.loads(self.misses.read_text())
        self.assertEqual(miss["residual"], "with robert lewandowski")

    def test_category_without_scores_uses_combined(self):
        e, _ = engine(self.misses)
        d = e.search("t-shirt for a wedding", "concepts")
        self.assertEqual(d["concepts"]["fallback"], "no concept scores for T-shirts")
        self.assertEqual(self.ids(d), ["t1"])

    def test_product_shows_all_its_scores(self):
        e, _ = engine(self.misses)
        self.assertEqual(e.product("d4")["concepts"][0], dict(name="gym", score=8))
        self.assertEqual(e.product("t1")["concepts"], [])


if __name__ == "__main__":
    unittest.main()
