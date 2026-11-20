import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import concepts  # noqa: E402
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402

E = np.eye(4, dtype=np.float32)
WEDDING = {"d1": 9, "d2": 3, "d3": 9, "d4": 0}
GYM = {"d1": 1, "d2": 6, "d3": 4, "d4": 8}


def product(pid, category):
    p = dict(product_id=pid, category=category, section=category, name=pid, brand="Acne Studios", gender="Women",
             features={}, images=[], description="")
    scored = category == "Dresses"
    p.update({"concept__wedding_guest": float(WEDDING[pid]) if scored else np.nan,
              "concept__gym": float(GYM[pid]) if scored else np.nan})
    return p


def engine():
    products = [product(p, "Dresses") for p in WEDDING] + [product("t1", "T-shirts")]
    T = np.eye(len(products), 4, dtype=np.float32)
    rows = pd.DataFrame([dict(id="wedding_guest", name="wedding guest", embedding=E[0].tolist()),
                         dict(id="gym", name="gym", embedding=E[1].tolist())])
    return server.SearchEngine(products, T, T.copy(), pa.Parser("test", lambda q: None), lambda text: E[2],
                               concepts.Concepts(products, rows))


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


class Scores(unittest.TestCase):
    def test_product_shows_all_its_scores(self):
        e = engine()
        self.addCleanup(e.pool.shutdown)
        self.assertEqual(e.product("d4")["concepts"][0], dict(name="gym", score=8))
        self.assertEqual(e.product("t1")["concepts"], [])

    def test_results_show_only_the_concepts_the_ranking_used(self):
        e = engine()
        self.addCleanup(e.pool.shutdown)
        shade = dict(skipped=False, concepts=["wedding_guest"])
        occasion = dict(skipped=False, concepts=["gym"], concepts_used=True)
        self.assertEqual(e.concept_columns(dict(bank=[shade, occasion])), [e.concepts.ids.index("gym")])
        self.assertIsNone(e.concept_columns(dict(bank=[shade])))


if __name__ == "__main__":
    unittest.main()
