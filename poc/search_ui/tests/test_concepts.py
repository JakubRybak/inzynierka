import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import concepts  # noqa: E402
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402

E = np.eye(4, dtype=np.float32)
VECTORS = {"wedding guest": E[0], "gym": E[1], "for a wedding": E[0] * 0.9 + E[3] * 0.1,
           "with robert lewandowski": E[3], "for a wedding or the gym": E[0] + 0.9 * E[1]}
RESIDUALS = {"black dress for a wedding": ("Dresses", ["for a wedding"]), "black dress": ("Dresses", []),
             "dress with robert lewandowski": ("Dresses", ["with robert lewandowski"]),
             "t-shirt for a wedding": ("T-shirts", ["for a wedding"]),
             "dress for a wedding and the gym": ("Dresses", ["for a wedding", "gym"]),
             "dress for a wedding with robert lewandowski": ("Dresses", ["for a wedding", "with robert lewandowski"]),
             "dress for a wedding or the gym": ("Dresses", ["for a wedding or the gym"])}
SCORES = {"d1": 9, "d2": 3, "d3": 9, "d4": 0}
GYM = {"d1": 1, "d2": 6, "d3": 4, "d4": 8}


def product(pid, category):
    p = dict(product_id=pid, category=category, section=category, name=pid, brand="Acne Studios", gender="Women",
             features={}, images=[], description="")
    if category == "Dresses":
        p.update({"concept__wedding_guest": float(SCORES[pid]), "concept__gym": float(GYM[pid])})
    else:
        p.update({"concept__wedding_guest": np.nan, "concept__gym": np.nan})
    return p


class Embedder:
    def __init__(self):
        self.texts = []

    def __call__(self, text):
        self.texts.append(text)
        return VECTORS.get(text, E[2])


def engine(misses, with_concepts=True, alpha=None, norm="percentile", combine="geo"):
    products = [product(p, "Dresses") for p in SCORES] + [product("t1", "T-shirts")]
    T = np.stack([np.array([0, 0, 1, 0.5 * i], np.float32) for i in range(len(products))])
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    embedder = Embedder()
    rows = pd.DataFrame([dict(id="wedding_guest", name="wedding guest", type="occasion", embedding=E[0].tolist()),
                         dict(id="gym", name="gym", type="occasion", embedding=E[1].tolist())])
    ranker = concepts.ConceptRanker(products, rows, dict(categories=["Dresses"], format="plain"), embedder,
                                    threshold=0.5, combine=combine, norm=norm,
                                    misses=misses) if with_concepts else None
    calls = []
    parser = pa.Parser("test", lambda q: calls.append(q) or dict(category=RESIDUALS[q][0], filters=[],
                                                               residual=RESIDUALS[q][1]))
    e = server.SearchEngine(products, T, T.copy(), parser, embedder, None, ranker, alpha)
    e.parser_calls = calls
    return e, embedder


class Selection(unittest.TestCase):
    def test_threshold_k_and_softmax(self):
        chosen, w = concepts.select(np.array([0.2, 0.8, 0.7, 0.75, 0.6]), threshold=0.65, k=2, temperature=0.1)
        self.assertEqual(chosen, [1, 3])
        self.assertAlmostEqual(w.sum(), 1.0)
        self.assertGreater(w[0], w[1])

    def test_nothing_above_the_threshold(self):
        chosen, w = concepts.select(np.array([0.3, 0.4]), threshold=0.5, k=3, temperature=0.1)
        self.assertEqual((chosen, len(w)), ([], 0))

    def test_percentiles_within_category(self):
        raw = np.array([[9, 1], [3, 1], [9, 1], [0, 1], [np.nan, np.nan], [5, 2]])
        pct = concepts.percentiles(raw, ["D", "D", "D", "D", "T", "T"])
        np.testing.assert_allclose(pct[:4, 0], [0.875, 0.5, 0.875, 0.25])
        np.testing.assert_allclose(pct[:4, 1], [0.625] * 4)
        self.assertTrue(np.isnan(pct[4]).all())
        self.assertEqual(pct[5, 0], 1.0)


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
        self.assertEqual([s["name"] for s in d["concepts"]["phrases"][0]["sims"]], ["wedding guest", "gym"])
        self.assertEqual(d["results"][0]["concepts"], [dict(name="wedding guest", score=9)])
        self.assertIn("concepts_ms", d["timings"])
        self.assertFalse(self.misses.exists())

    def test_empty_residual_falls_back_without_an_embedding(self):
        e, embedder = engine(self.misses)
        d = e.search("black dress", "concepts")
        self.assertEqual((d["concepts"]["fallback"], d["concepts"]["selected"]), ("empty residual", []))
        self.assertEqual(self.ids(d), ["d1", "d2", "d3", "d4"])
        self.assertEqual(len(embedder.texts), 2)

    def test_no_concept_above_the_threshold_is_logged(self):
        e, _ = engine(self.misses)
        d = e.search("dress with robert lewandowski", "concepts")
        self.assertEqual(d["concepts"]["fallback"], "no concept above the threshold")
        self.assertEqual(self.ids(d), ["d1", "d2", "d3", "d4"])
        miss = json.loads(self.misses.read_text())
        self.assertEqual((miss["query"], miss["residual"]), ("dress with robert lewandowski", "with robert lewandowski"))
        self.assertEqual(len(miss["top"]), 2)

    def test_category_without_scores(self):
        e, embedder = engine(self.misses)
        d = e.search("t-shirt for a wedding", "concepts")
        self.assertEqual(d["concepts"]["fallback"], "no concept scores for T-shirts")
        self.assertNotIn("for a wedding", embedder.texts)
        self.assertFalse(self.misses.exists())

    def test_residual_embedded_on_every_query(self):
        e, embedder = engine(self.misses)
        e.search("black dress for a wedding", "concepts")
        e.search("black dress for a wedding", "concepts")
        self.assertEqual(embedder.texts.count("for a wedding"), 2)

    def test_manual_filters_keep_the_residual(self):
        e, _ = engine(self.misses)
        d = e.search("black dress for a wedding", "concepts",
                     {"category": "Dresses", "filters": [], "residual": ["for a wedding"]})
        self.assertEqual((e.parser_calls, self.ids(d)), ([], ["d1", "d3", "d2", "d4"]))

    def test_alpha_mixes_with_combined(self):
        e, _ = engine(self.misses, alpha=0.0)
        self.assertEqual(self.ids(e.search("black dress for a wedding", "concepts")), ["d1", "d2", "d3", "d4"])

    def test_raw_norm_uses_the_scores_directly(self):
        e, _ = engine(self.misses, norm="raw")
        d = e.search("black dress for a wedding", "concepts")
        self.assertEqual((self.ids(d), d["results"][0]["score"]), (["d1", "d3", "d2", "d4"], 0.9))

    def test_phrases_are_matched_separately_and_combined(self):
        e, embedder = engine(self.misses, norm="raw")
        d = e.search("dress for a wedding and the gym", "concepts")
        self.assertEqual([[s["name"] for s in p["selected"]] for p in d["concepts"]["phrases"]],
                         [["wedding guest"], ["gym"]])
        self.assertEqual(self.ids(d), ["d3", "d2", "d1", "d4"])
        self.assertAlmostEqual(d["results"][0]["score"], 0.6)
        self.assertEqual(d["results"][0]["concepts"], [dict(name="wedding guest", score=9), dict(name="gym", score=4)])
        self.assertIn("for a wedding", embedder.texts)
        self.assertIn("gym", embedder.texts)
        e, _ = engine(self.misses, norm="raw", combine="mean")
        self.assertEqual(self.ids(e.search("dress for a wedding and the gym", "concepts")), ["d3", "d1", "d2", "d4"])

    def test_one_concept_per_phrase(self):
        e, _ = engine(self.misses)
        sims = e.search("dress for a wedding or the gym", "concepts")["concepts"]["phrases"][0]["sims"]
        self.assertGreater(sims[1]["sim"], 0.5)
        d = e.search("dress for a wedding or the gym", "concepts")
        self.assertEqual([s["name"] for s in d["concepts"]["selected"]], ["wedding guest"])

    def test_phrase_without_a_concept_is_skipped_and_logged(self):
        e, _ = engine(self.misses, norm="raw")
        d = e.search("dress for a wedding with robert lewandowski", "concepts")
        self.assertEqual(self.ids(d), ["d1", "d3", "d2", "d4"])
        self.assertEqual(d["concepts"]["phrases"][1]["fallback"], "no concept above the threshold")
        self.assertNotIn("fallback", d["concepts"])
        self.assertEqual(json.loads(self.misses.read_text())["residual"], "with robert lewandowski")

    def test_product_panel_lists_all_scores(self):
        e, _ = engine(self.misses)
        self.assertEqual(e.product("d1")["concepts"], [dict(name="wedding guest", score=9), dict(name="gym", score=1)])
        self.assertEqual(e.product("t1")["concepts"], [])

    def test_ranking_offered_only_with_concepts(self):
        self.assertIn("concepts", engine(self.misses)[0].rankings)
        self.assertNotIn("concepts", engine(self.misses, with_concepts=False)[0].rankings)


class Build(unittest.TestCase):
    LIST = [dict(id="a", name="A", type="style"), dict(id="b", name="B", type="style")]
    INDEX = pd.DataFrame(dict(product_id=["1", "2", "3"], category=["Dresses", "Dresses", "T-shirts"]))
    SCORES = pd.DataFrame(dict(product_id=["1", "1", "2", "2"], concept_id=["a", "b", "a", "b"], score=[5, 7, 1, 2]))

    def test_columns_and_scored_categories(self):
        names = []
        index, rows, categories = concepts.build(self.INDEX, self.LIST, self.SCORES,
                                                 lambda name: names.append(name) or np.array([3.0, 4.0]))
        self.assertEqual(categories, ["Dresses"])
        self.assertEqual(index["concept__a"].tolist()[:2], [5.0, 1.0])
        self.assertTrue(np.isnan(index["concept__b"].iloc[2]))
        self.assertEqual(names, ["A", "B"])
        np.testing.assert_allclose(rows["embedding"][0], [0.6, 0.8])

    def test_refuses_a_gap_in_a_scored_category(self):
        with self.assertRaises(ValueError):
            concepts.build(self.INDEX, self.LIST, self.SCORES.iloc[:3], lambda name: np.ones(2))

    def test_server_refuses_a_changed_concept_list(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "concepts.yaml"
            path.write_text("- {id: a, name: A, type: style}\n")
            meta = dict(concepts=dict(yaml=str(path), yaml_sha256=concepts.file_hash(path), scores=str(path),
                                      scores_sha256="", format="plain", categories=[]))
            path.write_text("- {id: b, name: B, type: style}\n")
            with self.assertRaises(SystemExit):
                concepts.load(d, meta, [], None, threshold=0.5)
        self.assertIsNone(concepts.load(".", {}, [], None, threshold=0.5))


if __name__ == "__main__":
    unittest.main()
