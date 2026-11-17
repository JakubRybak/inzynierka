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

    def test_bank_occasion_uses_its_concept_scores(self):
        terms, routes = self.ranker.adjustments(["For a  wedding"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["concepts"], routes[0]["term"]),
                         ("exact", ["wedding_guest"], "concept"))
        self.assertEqual(int(np.argmax(terms["concept"][0])), 1)  # d2 has the highest wedding score

    def test_occasion_without_scores_adds_nothing(self):
        terms, routes = self.ranker.adjustments(["for a wedding"], self.jeans, "Jeans")
        self.assertEqual((routes[0]["concepts"], routes[0]["concepts_unavailable"], routes[0]["term"]),
                         ([], ["wedding_guest"], None))
        self.assertFalse(any(terms.values()))

    def test_known_phrase_uses_its_english_version_and_a_negation_is_subtracted(self):
        _, routes = self.ranker.adjustments(["z koronką"], self.dresses, "Dresses")
        self.assertEqual(routes[0]["english"], "with lace")
        terms, routes = self.ranker.adjustments(["without lace"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["negated"], routes[0]["term"]), (True, "negation"))
        self.assertEqual(int(np.argmax(terms["negation"][0])), 0)  # d1, in black lace, loses the most

    def test_unknown_phrase_takes_a_concept_by_name(self):
        _, routes = self.ranker.adjustments(["wedding guest outfit"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["concepts"], routes[0]["term"]),
                         ("concept", ["wedding_guest"], "concept"))
        _, routes = self.ranker.adjustments(["with pockets"], self.dresses, "Dresses")
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
        _, routes = self.ranker.adjustments(["not in this lifetime tour"], self.dresses, "Dresses")
        self.assertFalse(routes[0]["negated"])
        _, routes = self.ranker.adjustments(["no lace"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["negated"])

    def test_a_negation_is_read_from_the_phrase_unless_the_bank_knows_it(self):
        rows = BANK + [dict(phrase="no me importa", kind="other", negated=False, english="i don't care", concepts=[])]
        r, _ = ranker(Path(self.tmp.name), Embedder(), rows)
        _, routes = r.adjustments(["no me importa", "not for a wedding"], self.dresses, "Dresses")
        self.assertEqual([x["negated"] for x in routes], [False, True])
        self.assertEqual((routes[1]["bare"], routes[1]["match"], routes[1]["concepts"]),
                         ("for a wedding", "exact", ["wedding_guest"]))

    def test_only_concepts_scored_in_the_category_are_used(self):
        r = bank.BankRanker(self.products, self.ranker.T, self.ranker.I, Path(self.tmp.name), BANK, self.ranker.matrix,
                            self.embedder, {"Dresses": []}, ["wedding_guest"], np.stack([vector("wedding guest")]))
        _, routes = r.adjustments(["for a wedding"], self.dresses, "Dresses")
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

    def test_size_phrase_is_skipped(self):
        terms, routes = self.ranker.adjustments(["plus size"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["skipped"], routes[0]["term"]), (True, None))
        self.assertFalse(any(terms.values()))

    def test_embed_bank_embeds_only_new_phrases(self):
        folder, embedder = Path(self.tmp.name), Embedder()
        vectors, new = bank.embed_bank(BANK[:2], embedder, folder)
        self.assertEqual((vectors.shape[0], new), (2, 2))
        vectors, new = bank.embed_bank(BANK, embedder, folder)
        self.assertEqual((vectors.shape[0], new, len(embedder.texts)), (3, 1, 3))


class ColourWeight(unittest.TestCase):
    def test_colour_makes_the_image_count_twice_in_the_hybrid_base(self):
        from concurrent.futures import Future
        ps = [dict(product_id=pid, category="Dresses", section="Dresses", name=pid, brand="Acne Studios",
                   description="Dress.", features={}, images=[]) for pid in ("text", "image")]
        T = np.array([[1, 0], [0, 1]], np.float32)
        I = np.array([[0, 1], [1, 0]], np.float32)
        e = server.SearchEngine(ps, T, I, pa.Parser("test", lambda q: None), lambda text: np.ones(2))
        self.addCleanup(e.pool.shutdown)
        jobs = {}
        for k, v in (("t", [1, 0.2]), ("i", [1, 0.1])):
            jobs[k] = Future()
            jobs[k].set_result(np.array(v, np.float32))
        cand = np.array([0, 1])
        plain = e.query_similarity(jobs, cand, {}, 0)[0]
        colour = e.query_similarity(jobs, cand, {}, 0, image_weight=2.0)[0]
        self.assertEqual(int(np.argmax(colour)), 1)
        self.assertLess(colour[0], plain[0])

    def test_colour_is_asked_by_a_colour_filter_or_a_shade_phrase(self):
        self.assertTrue(server.asks_colour([{"feature": "colors", "operator": "contains_any", "values": ["Pink"]}], []))
        self.assertTrue(server.asks_colour([{"feature": "colors", "operator": "equals_any_set", "values": ["Pink", "Red"]}], []))
        self.assertFalse(server.asks_colour([{"feature": "colors", "operator": "contains_none", "values": ["Red"]}], []))
        self.assertTrue(server.asks_colour([], [dict(kind="shade", skipped=False)]))
        self.assertFalse(server.asks_colour([], [dict(kind="detail", skipped=False)]))


class NegationInTheBase(unittest.TestCase):
    """The similarity of the whole query leaves out its negated phrases."""

    def test_query_without_phrases(self):
        self.assertEqual(bank.without_phrases("Sukienka, bez pufiastych rekawow!", ["bez pufiastych rekawow"]),
                         "Sukienka")
        self.assertEqual(bank.without_phrases("dress WITHOUT lace for work", ["without lace"]), "dress for work")
        self.assertIsNone(bank.without_phrases("dress without lace", ["no pockets"]))
        self.assertIsNone(bank.without_phrases("dress without laces", ["without lace"]))
        self.assertIsNone(bank.without_phrases("without lace", ["without lace"]))

    def test_variants_leave_out_the_spans_after_a_negation_word(self):
        self.assertEqual(bank.negation_variants("sukienka bez pufiastych rekawow"), ["sukienka rekawow", "sukienka"])
        self.assertEqual(bank.negation_variants("black dress with lace"), [])

    def test_hybrid_compares_the_query_without_the_negated_phrase(self):
        query, base = "black midi dress for work without lace", "black midi dress for work"
        with tempfile.TemporaryDirectory() as tmp:
            embedder = Embedder()
            r, ps = ranker(Path(tmp), embedder)
            parser = pa.Parser("test", lambda q: dict(category="Dresses", filters=[],
                                                      residual=["without lace"] if "without" in q else []))
            T = np.stack([vector(p["description"]) for p in ps])
            e = server.SearchEngine(ps, T, np.zeros_like(T), parser, embedder, bank=r)
            self.addCleanup(e.pool.shutdown)
            d = e.search(query, "hybrid")
            plain = e.search("black midi dress", "hybrid")
        self.assertEqual(d["base_query"], base)
        self.assertEqual(embedder.texts.count(common.query_text(base)), 1)  # started with the parser, not again
        position = {p["product_id"]: i for i, p in enumerate(ps)}
        for x in d["results"]:
            self.assertAlmostEqual(x["score_text"], float(T[position[x["id"]]] @ vector(base)), places=3)
        self.assertNotIn("base_query", plain)


if __name__ == "__main__":
    unittest.main()
