import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import common  # noqa: E402
import parser_adapter as pa  # noqa: E402
import sentences  # noqa: E402
import server  # noqa: E402
from test_bank import Embedder, products, ranker, vector  # noqa: E402

E = np.eye(8, dtype=np.float32)
# three products: a name and one or two sentences each; the vectors say what a sentence is about
TEXTS = {"Lace Dress": E[0], "Lace trim at hem.": E[0], "Zip closure.": E[1], "Plain Dress": E[2],
         "Wool Dress": E[3], "Two-button placket.": E[4]}
PRODUCTS = [dict(product_id="a", name="Lace Dress", description="Lace trim at hem. Zip closure."),
            dict(product_id="b", name="Plain Dress", description="Zip closure."),
            dict(product_id="c", name="Wool Dress", description="Two-button placket. Zip closure.")]


def data(ps=PRODUCTS, texts=TEXTS):
    return sentences.Sentences(ps, list(texts), np.stack(list(texts.values())))


class Split(unittest.TestCase):
    def test_name_first_then_the_sentences_of_the_description(self):
        p = dict(name="Piqu&eacute; Polo", description="Short sleeve polo in navy. Two-button placket.  Tonal stitching.")
        self.assertEqual(sentences.split(p), ["Piqué Polo", "Short sleeve polo in navy.", "Two-button placket.",
                                              "Tonal stitching."])

    def test_tags_end_a_sentence_and_are_dropped(self):
        p = dict(name="Top", description="Tonal stitching.<br><br>Available exclusively at SSENSE.<br><br>")
        self.assertEqual(sentences.split(p), ["Top", "Tonal stitching.", "Available exclusively at SSENSE."])

    def test_a_product_without_a_description_has_its_name(self):
        self.assertEqual(sentences.split(dict(name="Black Dress", description=None)), ["Black Dress"])


class Scores(unittest.TestCase):
    def setUp(self):
        self.s, self.cand = data(), np.array([0, 1, 2])

    def test_phrase_counts_only_above_its_median_similarity(self):
        lace = self.s.phrase(E[0], self.cand)
        self.assertEqual(lace.tolist(), [1.0, 0.0, 0.0])
        # a phrase equally far from every sentence adds nothing
        self.assertEqual(self.s.phrase(E[7], self.cand).tolist(), [0.0, 0.0, 0.0])

    def test_whole_query_takes_the_mean_of_the_two_best_sentences(self):
        whole = self.s.whole(E[0], self.cand)
        self.assertEqual(whole.tolist(), [1.0, 0.0, 0.0])
        both = self.s.whole((E[3] + E[4]) / np.sqrt(2), self.cand)
        self.assertAlmostEqual(float(both[2]), 1 / np.sqrt(2), places=5)

    def test_a_product_with_one_sentence_uses_it_alone(self):
        s = data([dict(product_id="x", name="Lace Dress", description=""), PRODUCTS[1]])
        self.assertEqual(s.whole(E[0], np.array([0, 1])).tolist(), [1.0, 0.0])

    def test_vectors_are_cut_to_the_first_dimensions(self):
        long = np.zeros(sentences.DIM + 5, np.float32)
        long[0], long[-1] = 1.0, 5.0
        self.assertEqual(sentences.shorten(long).shape, (sentences.DIM,))
        self.assertAlmostEqual(float(sentences.shorten(long)[0]), 1.0)


class Stored(unittest.TestCase):
    def test_only_new_sentences_are_embedded(self):
        calls = []

        def embed(text):
            calls.append(text)
            return TEXTS[text]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(sentences.embed(PRODUCTS[:2], embed, folder), (4, 4))
            self.assertIsNone(sentences.load(PRODUCTS, folder))
            self.assertEqual(sentences.embed(PRODUCTS, embed, folder), (6, 2))
            self.assertEqual(sorted(calls), sorted(TEXTS))
            self.assertEqual(sentences.load(PRODUCTS, folder).rows.shape, (3, 3))


class Ranking(unittest.TestCase):
    """The sentence terms of the phrase bank and the sentence ranking of the search engine."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.embedder = Embedder()
        self.ranker, self.products = ranker(Path(self.tmp.name), self.embedder)
        texts = {s: vector(s) for p in self.products for s in sentences.split(p)}
        self.ranker.sentences = sentences.Sentences(self.products, list(texts), np.stack(list(texts.values())))
        self.dresses = np.array([0, 1, 2])

    def test_a_bank_phrase_uses_its_stored_embedding(self):
        terms, routes = self.ranker.sentence_terms(["for a wedding"], self.dresses, "Dresses")
        self.assertEqual(self.embedder.texts, [])
        self.assertEqual([t[0] for t in terms], ["concept", "sentence"])
        self.assertEqual(int(np.argmax(terms[0][2])), 1)  # d2 has the highest wedding score
        self.assertEqual(int(np.argmax(terms[1][2])), 2)  # d3 says "for a wedding"
        self.assertTrue(routes[0]["sentence"] and routes[0]["concepts_used"])

    def test_an_unknown_phrase_is_embedded_and_matched_with_sentences(self):
        terms, routes = self.ranker.sentence_terms(["lace"], self.dresses, "Dresses")
        self.assertEqual(self.embedder.texts, [common.query_text("lace")])
        self.assertEqual([t[0] for t in terms], ["sentence"])
        self.assertEqual(int(np.argmax(terms[0][2])), 0)

    def test_a_known_phrase_is_matched_with_its_english_version(self):
        terms, routes = self.ranker.sentence_terms(["z koronką"], self.dresses, "Dresses")
        self.assertEqual(routes[0]["sentence_text"], "with lace")
        self.assertIn(common.query_text("with lace"), self.embedder.texts)
        self.assertEqual(int(np.argmax(terms[0][2])), 0)  # d1, in black lace

    def test_a_negated_phrase_counts_with_a_minus_and_without_its_negation(self):
        terms, routes = self.ranker.sentence_terms(["without lace"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["negated"])
        self.assertIn(common.query_text("lace"), self.embedder.texts)
        self.assertEqual(int(np.argmin(terms[0][2])), 0)
        self.assertLessEqual(float(terms[0][2].max()), 0.0)

    def test_a_size_phrase_adds_nothing(self):
        terms, routes = self.ranker.sentence_terms(["plus size"], self.dresses, "Dresses")
        self.assertEqual((terms, routes[0]["skipped"]), ([], True))

    def test_lean_prefetch_leaves_out_spans_of_the_bank(self):
        pre = self.ranker.prefetch("dress for a wedding with lace", lean=True)
        self.assertNotIn(common.query_text("for a wedding"), pre)
        self.assertIn(common.query_text("lace"), pre)
        for f in pre.values():
            f.result()

    def engine(self, weights):
        T = np.stack([vector(p["description"]) for p in self.products])
        parser = pa.Parser("test", lambda q: dict(category="Dresses", filters=[], residual=["lace"]))
        return server.SearchEngine(self.products, T, np.zeros_like(T), parser, self.embedder, bank=self.ranker, F=T,
                                   sentences=self.ranker.sentences, sentence_weights=weights)

    def test_search_orders_by_the_weighted_parts(self):
        weights = dict(description=0.0, sentences=0.0, image=0.0, features=0.0, concept=1.0, phrase=1.0)
        d = self.engine(weights).search("dress with lace", "sentences")
        self.assertEqual(d["results"][0]["id"], "d1")
        self.assertEqual([x["label"] for x in d["score_parts"]], ["sentence · lace"])
        self.assertIn("phrase", d["formula"])

    def test_the_whole_query_leaves_out_a_negated_phrase(self):
        T = np.stack([vector(p["description"]) for p in self.products])
        parser = pa.Parser("test", lambda q: dict(category="Dresses", filters=[], residual=["without lace"]))
        e = server.SearchEngine(self.products, T, np.zeros_like(T), parser, self.embedder, bank=self.ranker, F=T,
                                sentences=self.ranker.sentences, sentence_weights=dict(description=1.0))
        self.addCleanup(e.pool.shutdown)
        self.assertEqual(e.search("dress without lace", "sentences")["base_query"], "dress")

    def test_ranking_is_offered_only_with_sentences_and_weights(self):
        self.assertNotIn("sentences_jev_vision", self.engine(None).rankings)
        self.assertIn("sentences_jev_vision", self.engine(dict(description=1.0)).rankings)


if __name__ == "__main__":
    unittest.main()
