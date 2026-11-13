import sys
import tempfile
import unittest
import zlib
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import bank  # noqa: E402
import common  # noqa: E402
import parser_adapter as pa  # noqa: E402
import server  # noqa: E402

BANK = [dict(phrase="for a wedding", kind="occasion", negated=False, english="for a wedding", concepts=["wedding_guest"]),
        dict(phrase="z koronką", kind="detail", negated=False, english="with lace", concepts=[]),
        dict(phrase="plus size", kind="size_or_audience", negated=False, english="plus size", concepts=[])]
DESCRIPTIONS = {"d1": "Midi dress in black lace.", "d2": "Plain jersey dress.", "d3": "Wool dress for a wedding.",
                "j1": "Jeans with lace trims.", "j2": "Jeans for a wedding."}
WEDDING = {"d1": 2.0, "d2": 9.0, "d3": 5.0, "j1": np.nan, "j2": np.nan}


def vector(text):
    """Bag of hashed words, enough to make similarity follow shared words."""
    v = np.zeros(64, np.float32)
    for w in text.removeprefix(common.query_text("")).lower().replace(".", " ").split():
        v[zlib.crc32(w.encode()) % 64] += 1
    return v / (np.linalg.norm(v) + 1e-9)


class Embedder:
    def __init__(self):
        self.texts = []

    def __call__(self, text):
        self.texts.append(text)
        return vector(text)


def products():
    return [dict(product_id=pid, category="Dresses" if pid[0] == "d" else "Jeans", section="x", name=pid,
                 brand="Acne Studios", description=text, features={}, images=[], concept__wedding_guest=WEDDING[pid])
            for pid, text in DESCRIPTIONS.items()]


def ranker(dataset, embedder, rows=BANK, scores=None):
    ps = products() if scores is None else scores
    T = np.stack([vector(p["description"]) for p in ps])
    for split in ("train", "validation"):
        (dataset / f"products_{split}.csv").write_text(
            "product_id,name,description\n" + "".join(f"{p['product_id']},{p['name']},{p['description']}\n" for p in ps),
            encoding="utf-8")
    concept_vectors = np.stack([vector("wedding guest")])
    return bank.BankRanker(ps, T, np.zeros_like(T), dataset, rows, np.stack([vector(r["phrase"]) for r in rows]),
                           embedder, ["Dresses"], ["wedding_guest"], concept_vectors), ps


class Bank(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.embedder = Embedder()
        self.ranker, self.products = ranker(Path(self.tmp.name), self.embedder)
        self.dresses, self.jeans = np.array([0, 1, 2]), np.array([3, 4])

    def tearDown(self):
        self.tmp.cleanup()

    def order(self, residual, cand, category):
        score, routes = self.ranker.rank(residual, cand, category)
        return [self.products[i]["product_id"] for i in cand[np.argsort(-score, kind="stable")]], routes

    def test_prefetched_spans_save_calls_after_parsing(self):
        query = "black dress with pockets"
        pre = self.ranker.prefetch(query)
        self.assertIn(common.query_text("with pockets"), pre)
        self.assertNotIn(common.query_text("with"), pre)
        for f in pre.values():
            f.result()
        calls, stats = len(self.embedder.texts), {}
        self.ranker.adjustments(["with pockets"], self.dresses, "Dresses", query=query, prefetched=pre, stats=stats)
        self.assertEqual(len(self.embedder.texts), calls)
        self.assertEqual(stats, dict(phrase_embeddings_early=1, phrase_embeddings_late=0))
        stats = {}
        self.ranker.adjustments(["deep pockets"], self.dresses, "Dresses", query=query, prefetched=pre, stats=stats)
        self.assertEqual(stats, dict(phrase_embeddings_early=0, phrase_embeddings_late=1))

    def test_bank_occasion_uses_only_concepts_in_a_scored_category(self):
        order, routes = self.order(["For a  wedding"], self.dresses, "Dresses")
        self.assertEqual(order, ["d2", "d3", "d1"])
        self.assertEqual((routes[0]["match"], routes[0]["concepts"], routes[0]["text_signals"]),
                         ("exact", ["wedding_guest"], False))

    def test_occasion_falls_back_to_text_without_scores(self):
        order, routes = self.order(["for a wedding"], self.jeans, "Jeans")
        self.assertEqual(order, ["j2", "j1"])
        self.assertEqual((routes[0]["concepts"], routes[0]["concepts_unavailable"], routes[0]["text_signals"]),
                         ([], ["wedding_guest"], True))

    def test_known_phrase_uses_its_english_version_and_negation_inverts(self):
        self.assertEqual(self.order(["z koronką"], self.dresses, "Dresses")[0][0], "d1")
        self.assertIn("with lace", self.embedder.texts)
        order, routes = self.order(["without lace"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["negated"])
        self.assertEqual(order[-1], "d1")

    def test_unknown_phrase_takes_a_concept_by_name(self):
        _, routes = self.order(["wedding guest outfit"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["concepts"], routes[0]["text_signals"]),
                         ("concept", ["wedding_guest"], True))
        _, routes = self.order(["with pockets"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["concepts"]), ("none", []))

    def test_a_lightness_word_before_a_colour_is_a_shade(self):
        rows = BANK + [dict(phrase="light", kind="season", negated=False, english="light", concepts=["wedding_guest"])]
        r = bank.BankRanker(self.products, self.ranker.T, self.ranker.I, Path(self.tmp.name), rows,
                            np.stack([vector(x["phrase"]) for x in rows]), self.embedder, ["Dresses"], ["wedding_guest"],
                            np.stack([vector("wedding guest")]))
        _, routes = r.adjustments(["light"], self.dresses, "Dresses", query="Light  pink dress")
        self.assertEqual((routes[0]["kind"], routes[0]["concepts"], routes[0]["match"]), ("shade", [], "colour"))
        _, routes = r.adjustments(["light"], self.dresses, "Dresses", query="light jacket for spring")
        self.assertEqual(routes[0]["concepts"], ["wedding_guest"])

    def test_a_long_phrase_after_not_is_a_slogan(self):
        _, routes = self.order(["not in this lifetime tour"], self.dresses, "Dresses")
        self.assertFalse(routes[0]["negated"])
        _, routes = self.order(["no lace"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["negated"])

    def test_only_concepts_scored_in_the_category_are_used(self):
        r = bank.BankRanker(self.products, self.ranker.T, self.ranker.I, Path(self.tmp.name), BANK, self.ranker.matrix,
                            self.embedder, {"Dresses": []}, ["wedding_guest"], np.stack([vector("wedding guest")]))
        _, routes = r.rank(["for a wedding"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["concepts"], routes[0]["concepts_unavailable"]), ([], ["wedding_guest"]))

    def test_a_shade_is_judged_mainly_from_the_image(self):
        self.assertEqual(self.ranker.image_weight(dict(kind="shade")), 2.0)
        self.assertEqual(self.ranker.image_weight(dict(kind="detail")), 1.0)
        I = np.stack([vector("red"), vector("pink"), vector("blue")])
        r = bank.BankRanker(self.products[:3], np.stack([vector("pink dress"), vector("red dress"), vector("blue dress")]),
                            I, Path(self.tmp.name), BANK, np.stack([vector(x["phrase"]) for x in BANK]), self.embedder)
        vectors = r.embed(["pink"])
        plain, image = r.text_score("pink", self.dresses, vectors), r.text_score("pink", self.dresses, vectors, 2.0)
        self.assertGreater(image[1] - image[0], plain[1] - plain[0])

    def test_a_phrase_without_own_signal_takes_the_whole_query(self):
        whole = np.array([0.1, 0.9, 0.5])
        score, routes = self.ranker.rank(["harry potter"], self.dresses, "Dresses", typicality=False,
                                         whole_query=lambda routes: whole)
        self.assertTrue(routes[0]["whole_query"])
        self.assertEqual(int(np.argmax(score)), 1)
        score, routes = self.ranker.rank(["for a wedding"], self.dresses, "Dresses", typicality=False,
                                         whole_query=lambda routes: whole)
        self.assertNotIn("whole_query", routes[0])
        self.assertEqual(int(np.argmax(score)), 1)

    def test_size_phrase_is_skipped_and_typicality_orders(self):
        score, routes = self.ranker.rank(["plus size"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["skipped"])
        np.testing.assert_allclose(score, self.ranker.rank([], self.dresses, "Dresses")[0])

    def test_embed_bank_embeds_only_new_phrases(self):
        folder, embedder = Path(self.tmp.name), Embedder()
        vectors, new = bank.embed_bank(BANK[:2], embedder, folder)
        self.assertEqual((vectors.shape[0], new), (2, 2))
        vectors, new = bank.embed_bank(BANK, embedder, folder)
        self.assertEqual((vectors.shape[0], new, len(embedder.texts)), (3, 1, 3))


class TiesInSearch(unittest.TestCase):
    """In the search engine the combined similarity of the query orders candidates with equal concept scores."""

    def test_combined_breaks_equal_concept_scores(self):
        ps = [dict(product_id=pid, category="Dresses", section="Dresses", name=pid, brand="Acne Studios",
                   description=text, features={}, images=[], concept__wedding_guest=score)
              for pid, text, score in [("d1", "red dress", 9.0), ("d2", "blue dress", 9.0), ("d3", "green dress", 2.0)]]
        with tempfile.TemporaryDirectory() as tmp:
            r, ps = ranker(Path(tmp), Embedder(), scores=ps)
            parser = pa.Parser("test", lambda q: dict(category="Dresses", filters=[], residual=["for a wedding"]))
            T = np.stack([vector(p["description"]) for p in ps])
            e = server.SearchEngine(ps, T, np.zeros_like(T), parser, lambda text: vector("blue"), bank=r)
            d = e.search("blue dress for a wedding", "bank")
        self.assertEqual([x["id"] for x in d["results"]], ["d2", "d1", "d3"])
        self.assertIn("query_embedding_ms", d["timings"])


class ColourWeight(unittest.TestCase):
    def test_colour_makes_the_image_count_twice_in_the_hybrid_base(self):
        from concurrent.futures import Future
        ps = [dict(product_id=pid, category="Dresses", section="Dresses", name=pid, brand="Acne Studios",
                   description="Dress.", features={}, images=[]) for pid in ("text", "image")]
        T = np.array([[1, 0], [0, 1]], np.float32)
        I = np.array([[0, 1], [1, 0]], np.float32)
        e = server.SearchEngine(ps, T, I, pa.Parser("test", lambda q: None), lambda text: np.ones(2))
        jobs = {}
        for k, v in (("t", [1, 0.2]), ("i", [1, 0.1])):
            jobs[k] = Future()
            jobs[k].set_result(np.array(v, np.float32))
        cand = np.array([0, 1])
        plain = e.embedding_scores(jobs, "combined", cand, {}, 0)[0]
        colour = e.embedding_scores(jobs, "combined", cand, {}, 0, image_weight=2.0)[0]
        self.assertEqual(int(np.argmax(colour)), 1)
        self.assertLess(colour[0], plain[0])

    def test_colour_is_asked_by_a_colour_filter_or_a_shade_phrase(self):
        self.assertTrue(server.asks_colour([{"feature": "colors", "operator": "contains_any", "values": ["Pink"]}], []))
        self.assertFalse(server.asks_colour([{"feature": "colors", "operator": "contains_none", "values": ["Red"]}], []))
        self.assertTrue(server.asks_colour([], [dict(kind="shade", skipped=False)]))
        self.assertFalse(server.asks_colour([], [dict(kind="detail", skipped=False)]))


if __name__ == "__main__":
    unittest.main()
