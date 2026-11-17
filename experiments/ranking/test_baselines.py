"""Tests of the rankings of baselines.py, with the small catalogues of the search UI tests (no API calls).

    python -m pytest experiments/ranking/test_baselines.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "search_ui" / "tests")]
import baselines  # noqa: E402
import concepts  # noqa: E402
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402
from test_bank import Embedder, ranker, vector  # noqa: E402
from test_concepts import E, WEDDING, product  # noqa: E402

PHRASES = {"wedding guest": E[0], "gym": E[1], "for a wedding": E[0] * 0.9 + E[3] * 0.1}


def order(score, tie):
    return list(np.lexsort((-tie, -score)) if tie is not None else np.argsort(-score, kind="stable"))


class Concepts(unittest.TestCase):
    def setUp(self):
        products = [product(p, "Dresses") for p in WEDDING] + [product("t1", "T-shirts")]
        rows = pd.DataFrame([dict(id="wedding_guest", name="wedding guest", embedding=E[0].tolist()),
                             dict(id="gym", name="gym", embedding=E[1].tolist())])
        self.texts = []

        def embed(text):
            self.texts.append(text)
            return PHRASES.get(text.removeprefix("task: search result | query: "), E[2])
        self.ranking = baselines.ConceptRanking(concepts.Concepts(products, rows), dict(categories=["Dresses"]), embed,
                                                threshold=0.5)
        self.dresses = np.array([0, 1, 2, 3])
        self.combined = np.array([4.0, 3.0, 2.0, 1.0])  # d1 before d2 before d3 before d4

    def test_concept_scores_order_and_combined_breaks_ties(self):
        score, tie = self.ranking.rank(["for a wedding"], "Dresses", self.dresses, self.combined)
        self.assertEqual(order(score, tie), [0, 2, 1, 3])  # wedding 9, 9, 3, 0

    def test_two_phrases_geometric_mean(self):
        score, _ = self.ranking.rank(["for a wedding", "gym"], "Dresses", self.dresses, self.combined)
        self.assertEqual(int(np.argmax(score)), 2)  # d3: wedding 9, gym 4

    def test_no_phrase_or_no_scores_keeps_combined(self):
        for residual, category in (([], "Dresses"), (["for a wedding"], "T-shirts"), (["robert lewandowski"], "Dresses")):
            with self.subTest(residual=residual, category=category):
                score, tie = self.ranking.rank(residual, category, self.dresses, self.combined)
                self.assertIsNone(tie)
                np.testing.assert_array_equal(score, self.combined)
        self.assertEqual(self.texts, ["task: search result | query: robert lewandowski"])  # nothing else embedded


class Bank(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bank, self.products = ranker(Path(self.tmp.name), Embedder())
        self.dresses = np.array([0, 1, 2])

    def test_a_phrase_without_own_signal_takes_the_whole_query(self):
        whole = np.array([0.1, 0.9, 0.5])
        score, routes = baselines.bank_rank(self.bank, ["harry potter"], self.dresses, "Dresses", None,
                                            lambda routes: whole)
        self.assertEqual(int(np.argmax(score)), 1)
        score, routes = baselines.bank_rank(self.bank, ["for a wedding"], self.dresses, "Dresses", None,
                                            lambda routes: np.array([0.9, 0.1, 0.5]))
        self.assertEqual(int(np.argmax(score)), 1)  # its concept: d2 has the highest wedding score

    def test_known_phrase_uses_its_english_version_and_negation_inverts(self):
        none = lambda routes: np.zeros(3)  # noqa: E731
        score, _ = baselines.bank_rank(self.bank, ["z koronką"], self.dresses, "Dresses", None, none)
        self.assertEqual(int(np.argmax(score)), 0)  # "with lace": d1, in black lace
        score, routes = baselines.bank_rank(self.bank, ["without lace"], self.dresses, "Dresses", None, none)
        self.assertTrue(routes[0]["negated"])
        self.assertEqual(int(np.argmin(score)), 0)

    def test_combined_breaks_equal_concept_scores(self):
        ps = [dict(product_id=pid, category="Dresses", section="Dresses", name=pid, brand="Acne Studios",
                   description=text, features={}, images=[], concept__wedding_guest=score)
              for pid, text, score in [("d1", "red dress", 9.0), ("d2", "blue dress", 9.0), ("d3", "green dress", 2.0)]]
        b, ps = ranker(Path(self.tmp.name), Embedder(), scores=ps)
        T = np.stack([vector(p["description"]) for p in ps])
        engine = server.SearchEngine(ps, T, np.zeros_like(T), pa.Parser("test", lambda q: None),
                                     lambda text: vector("blue"), bank=b)
        self.addCleanup(engine.pool.shutdown)
        v = baselines.query_vectors(engine, "blue dress for a wedding")
        combined = baselines.embedding(engine, v, "combined", self.dresses)
        score, _ = baselines.bank_rank(b, ["for a wedding"], self.dresses, "Dresses", None, lambda routes: combined)
        self.assertEqual(order(score, combined), [1, 0, 2])


class Embedding(unittest.TestCase):
    def test_image_ranking_puts_products_without_an_image_last(self):
        ps = [dict(product_id=pid, category="Dresses", section="Dresses", name=pid, brand="Acne Studios",
                   description="Dress.", features={}, images=[]) for pid in ("a", "b", "c")]
        T = np.eye(3, 4, dtype=np.float32)
        I = np.array([[1, 0, 0, 0], [0, 0, 0, 0], [0.6, 0.8, 0, 0]], np.float32)
        engine = server.SearchEngine(ps, T, I, pa.Parser("test", lambda q: None), lambda text: np.eye(4)[1])
        self.addCleanup(engine.pool.shutdown)
        v = baselines.query_vectors(engine, "dress")
        cand = np.array([0, 1, 2])
        self.assertEqual(int(np.argmin(baselines.embedding(engine, v, "image", cand))), 1)
        self.assertEqual(int(np.argmax(baselines.embedding(engine, v, "text", cand))), 1)


if __name__ == "__main__":
    unittest.main()
