import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import details  # noqa: E402
from test_bank import products, ranker, vector  # noqa: E402

# d1 lace all over, d2 plain, d3 a lace trim; j1 pockets, j2 none
DETAILS = pd.DataFrame([("d1", 0, "lace", "all-over"), ("d3", 0, "lace trim", "small"), ("d3", 1, "pockets", "part"),
                        ("j1", 0, "pockets", "part")], columns=["product_id", "rank", "name", "extent"])
NAMES = ["lace", "lace trim", "pockets"]


def detail_data(ps, vectors=None):
    return details.Details(ps, DETAILS, NAMES, vectors if vectors is not None else
                           np.stack([vector(details.common.query_text(n)) for n in NAMES]))


class Details(unittest.TestCase):
    def setUp(self):
        self.ps = products()
        self.dresses = np.array([0, 1, 2])

    def test_target_takes_the_neighbours_of_the_closest_name(self):
        e = np.eye(8, dtype=np.float32)
        near = lambda sim, base, other: sim * e[base] + np.sqrt(1 - sim ** 2) * e[other]  # noqa: E731
        # "graphic", "bunny graphic" close to it but far from the phrase, "pockets" unrelated
        d = details.Details(self.ps, DETAILS.iloc[:0], ["graphic", "bunny graphic", "pockets"],
                            np.stack([e[0], near(0.85, 0, 1), e[2]]))
        t = d.target(near(0.9, 0, 3))
        self.assertEqual(t["names"], ["graphic", "bunny graphic"])
        self.assertEqual(t["weights"][0], 1.0)
        self.assertTrue(0.5 <= t["weights"][1] < 0.7)
        self.assertIsNone(d.target(near(0.7, 0, 3)))

    def test_score_is_extent_times_weight(self):
        d = detail_data(self.ps)
        s = d.score(dict(columns=[0, 1], weights=[1.0, 0.5]), self.dresses)
        self.assertEqual(s.tolist(), [1.0, 0.0, np.float32(0.2)])

    def test_listed_in_order(self):
        self.assertEqual(detail_data(self.ps).of_product(2), [("lace trim", "small"), ("pockets", "part")])


class BankDetails(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        e = np.eye(64, dtype=np.float32)
        own = {"koronkowa": e[0], "lace": e[0], "lace trim": 0.97 * e[0] + 0.243 * e[1], "pockets": e[2],
               "kieszenie": e[2], "na wesele": e[3]}

        def embed(text):
            return own.get(text.removeprefix(details.common.query_text("")), e[9])
        rows = [dict(phrase="for a wedding", kind="occasion", negated=False, english="for a wedding",
                     concepts=["wedding_guest"])]
        self.r, ps = ranker(Path(self.tmp.name), embed, rows)
        self.r.matrix = np.stack([e[4]])
        self.r.details = detail_data(ps, np.stack([embed(details.common.query_text(n)) for n in NAMES]))
        self.dresses = np.array([0, 1, 2])

    def test_unknown_phrase_gets_detail_names(self):
        score, routes = self.r.rank(["koronkowa"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["kind"]), ("detail name", "detail"))
        self.assertEqual(routes[0]["detail"]["names"], ["lace", "lace trim"])
        self.assertEqual(int(np.argmax(score)), 0)

    def test_hybrid_detail_and_negated_detail(self):
        terms, routes = self.r.adjustments(["koronkowa"], self.dresses, "Dresses")
        self.assertEqual((len(terms["detail"]), routes[0]["term"]), (1, "detail"))
        self.assertEqual(int(np.argmax(terms["detail"][0])), 0)
        terms, routes = self.r.adjustments(["bez kieszenie"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["negated"], routes[0]["term"]), (True, "negation"))
        self.assertEqual(int(np.argmax(terms["negation"][0])), 2)

    def test_no_detail_for_an_unrelated_phrase(self):
        _, routes = self.r.rank(["na wesele"], self.dresses, "Dresses")
        self.assertIsNone(routes[0]["detail"])


if __name__ == "__main__":
    unittest.main()
