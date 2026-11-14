import base64
import io
import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import requests
from PIL import Image

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import jev_reranker as jev  # noqa: E402
import parser_adapter as pa  # noqa: E402
import sentences  # noqa: E402
import server  # noqa: E402
from test_bank import Embedder, ranker, vector  # noqa: E402


def response(body, grades=None):
    grades = grades or {}
    answers = {}
    for label, text in body["state"]["PRODUCTS"].items():
        if isinstance(text, dict):
            text = text["text"]
        pid = text.split(" | ")[0]
        grade = str(grades.get(pid, 1))
        answers[label] = dict(choice=grade, probabilities={str(i): float(str(i) == grade) for i in range(4)})
    return Mock(ok=True, json=lambda: dict(answers=answers, usage=dict(cost=0.0003)))


def decode_photo(part):
    assert part["type"] == "image_url"
    prefix, encoded = part["image_url"]["url"].split(",", 1)
    assert prefix == "data:image/jpeg;base64"
    return Image.open(io.BytesIO(base64.b64decode(encoded)))


class Photos(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_main_photo_keeps_proportions_and_source_file(self):
        Image.new("RGB", (400, 800), "red").save(self.root / "p_id_gridfs_1.png")
        Image.new("RGB", (512, 512), "blue").save(self.root / "p_id_gridfs_2.png")
        original = (self.root / "p_id_gridfs_1.png").read_bytes()
        p = dict(images=["p_id_gridfs_2.png", "p_id_gridfs_1.png"])
        with decode_photo(jev.product_photo(p, self.root)) as im:
            side = jev.MAX_IMAGE_SIZE
            self.assertEqual((im.format, im.mode, im.size), ("JPEG", "RGB", (side, side)))
            self.assertEqual(im.getpixel((side // 12, side // 2)), (255, 255, 255))
            r, g, b = im.getpixel((side // 2, side // 2))
            self.assertGreater(r, 240)
            self.assertLess(g + b, 10)
        self.assertEqual((self.root / "p_id_gridfs_1.png").read_bytes(), original)

    def test_enhanced_photo_is_preferred_at_most_max_size(self):
        enhanced = self.root / "pilot_9922/images_enhanced/p/p_id_gridfs_1.webp"
        enhanced.parent.mkdir(parents=True)
        Image.new("RGB", (1024, 1024), "red").save(enhanced, lossless=True)
        Image.new("RGB", (256, 256), "blue").save(self.root / "p_id_gridfs_1.png")
        original = enhanced.read_bytes()
        for images in (["p_id_gridfs_1.png"], []):
            with self.subTest(images=images):
                p = dict(product_id="p", images=images)
                with decode_photo(jev.product_photo(p, self.root)) as im:
                    self.assertEqual(im.size, (jev.MAX_IMAGE_SIZE, jev.MAX_IMAGE_SIZE))
                    r, g, b = im.getpixel((jev.MAX_IMAGE_SIZE // 2, jev.MAX_IMAGE_SIZE // 2))
                    self.assertGreater(r, 240)
                    self.assertLess(g + b, 10)
        self.assertEqual(enhanced.read_bytes(), original)

    def test_cached_photo_is_read_again_without_the_source(self):
        Image.new("RGB", (256, 256), "green").save(self.root / "q_id_gridfs_1.png")
        p = dict(product_id="q", images=["q_id_gridfs_1.png"])
        cache = self.root / "cache"
        first = jev.product_photo(p, self.root, cache)
        self.assertTrue((cache / "q.jpg").is_file())
        (self.root / "q_id_gridfs_1.png").unlink()
        self.assertEqual(jev.product_photo(p, self.root, cache), first)
        self.assertIsNone(jev.product_photo(p, self.root))
        self.assertEqual(jev.prepare_photos([p], self.root, cache), 0)

    def test_unreadable_enhanced_photo_uses_original_at_minimum_size(self):
        enhanced = self.root / "pilot_9922/images_enhanced/p/p_id_gridfs_1.webp"
        enhanced.parent.mkdir(parents=True)
        enhanced.write_text("broken image")
        Image.new("RGB", (256, 256), "blue").save(self.root / "p_id_gridfs_1.png")
        p = dict(product_id="p", images=["p_id_gridfs_1.png"])
        with decode_photo(jev.product_photo(p, self.root)) as im:
            self.assertEqual(im.size, (280, 280))
            self.assertGreater(im.getpixel((140, 140))[2], 240)

    def test_orientation_and_transparency(self):
        photo = Image.new("RGB", (600, 300), "blue")
        exif = Image.Exif()
        exif[274] = 6  # rotate 90 degrees clockwise
        photo.save(self.root / "rotated.jpg", exif=exif)
        with decode_photo(jev.product_photo(dict(images=["rotated.jpg"]), self.root)) as im:
            self.assertEqual(im.getpixel((20, 256)), (255, 255, 255))
            self.assertGreater(im.getpixel((256, 20))[2], 240)
        Image.new("RGBA", (512, 512), (0, 0, 0, 0)).save(self.root / "alpha.png")
        with decode_photo(jev.product_photo(dict(images=["alpha.png"]), self.root)) as im:
            self.assertEqual(im.getpixel((256, 256)), (255, 255, 255))

    def test_bad_files_fall_back_to_another_photo_or_none(self):
        (self.root / "broken_id_gridfs_1.png").write_text("not an image")
        Image.new("RGB", (256, 256), "blue").save(self.root / "other.webp")
        self.assertIsNone(jev.product_photo(dict(images=[]), self.root))
        self.assertIsNone(jev.product_photo(dict(images=["missing.png", "broken_id_gridfs_1.png"]), self.root))
        with patch("PIL.Image.open") as opened:
            self.assertIsNone(jev.product_photo(dict(images=["../outside.png"]), self.root))
            opened.assert_not_called()
        part = jev.product_photo(dict(images=["broken_id_gridfs_1.png", "other.webp"]), self.root)
        with decode_photo(part) as im:
            self.assertEqual(im.format, "JPEG")
            self.assertGreater(im.getpixel((256, 256))[2], 240)


class Client(unittest.TestCase):
    def test_probabilities_determine_expected_grade(self):
        self.assertAlmostEqual(jev.expected(dict(choice="3", probabilities={"0": 0.3, "3": 0.7})), 2.1)
        self.assertEqual(jev.expected(dict(choice="2")), 2)
        for probabilities in ({"3": -1}, {"3": float("nan")}, {"0": 0}, {"4": 1}):
            with self.subTest(probabilities=probabilities), self.assertRaises(ValueError):
                jev.expected(dict(choice="3", probabilities=probabilities))

    def test_one_call_covers_at_most_30_products_and_reports_cost(self):
        products = [dict(product_id=f"p{i}", name=f"p{i}", brand="Brand", description="A dress", composition="Cotton")
                    for i in range(35)]
        with patch.object(jev.requests, "post", side_effect=lambda *a, **kw: response(kw["json"], {"p29": 3})) as post:
            ids, parts, info = jev.JevReranker(key="test")("cotton dress", "Dresses", products, np.zeros(35))
        post.assert_called_once()
        request = post.call_args.kwargs
        self.assertEqual(len(request["json"]["questions"]), 30)
        self.assertEqual(request["json"]["model"], "typesafe/jev-1.14")
        self.assertEqual(request["timeout"], (3.05, 5.0))
        self.assertFalse(request["allow_redirects"])
        self.assertEqual(set(ids), {f"p{i}" for i in range(30)})
        self.assertEqual(ids[0], "p29")
        self.assertEqual(parts["p29"], dict(grade=3.0, score=3.0))
        self.assertEqual(info["cost_usd"], 0.0003)
        self.assertNotIn("test", json.dumps(info))
        self.assertTrue(all(isinstance(text, str) for text in request["json"]["state"]["PRODUCTS"].values()))
        self.assertNotIn("TypeSafe-Danger-Zone-Images", request["headers"])

    def test_reorders_top_without_promoting_the_tail_and_keeps_ties_stable(self):
        stage = dict(top=["a", "b", "c", "d"], score=[10.0, 9.0, 8.0, 7.0])
        answers = {"a": dict(choice="0"), "b": dict(choice="0"), "c": dict(choice="3"), "d": dict(choice="3")}
        self.assertEqual(jev.rerank(stage, answers, depth=3, blend=0), ["c", "a", "b", "d"])
        self.assertEqual(jev.rerank(stage, answers, depth=3, blend=0.25), ["c", "a", "b", "d"])

    def test_no_call_for_single_candidate(self):
        with patch.object(jev.requests, "post") as post, patch.object(jev, "api_key") as key:
            ids, _, info = jev.JevReranker()("dress", "Dresses", [dict(product_id="a")], [1.0])
        self.assertEqual(ids, ["a"])
        self.assertEqual(info["status"], "skipped")
        post.assert_not_called()
        key.assert_not_called()


class Integration(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.embedder = Embedder()
        bank, products = ranker(Path(tmp.name), self.embedder)
        self.image_dir = Path(tmp.name)
        for p in products:
            p["features"] = dict(colors=["White" if p["product_id"] == "d2" else "Black"])
            p["images"] = [p["product_id"] + ".png"]
            Image.new("RGB", (256, 256), "white" if p["product_id"] == "d2" else "black").save(
                self.image_dir / p["images"][0])
        texts = {s: vector(s) for p in products for s in sentences.split(p)}
        bank.sentences = sentences.Sentences(products, list(texts), np.stack(list(texts.values())))
        T = np.stack([vector(p["description"]) for p in products])
        self.engine = server.SearchEngine(products, T, np.zeros_like(T),
                                         pa.Parser("test", lambda q: dict(category="Dresses", filters=[], residual=[])),
                                         self.embedder, bank=bank, F=T, sentences=bank.sentences,
                                         sentence_weights=dict(description=1.0, sentences=1.0), image_dir=self.image_dir)
        self.addCleanup(self.engine.pool.shutdown)
        self.post = self.enterContext(patch.object(jev.requests, "post", side_effect=self.answer))
        self.key = self.enterContext(patch.object(jev, "api_key", return_value="test"))

    def answer(self, *args, **kwargs):
        return response(kwargs["json"], {"d1": 0, "d2": 3, "d3": 1})

    def test_optional_ranking_reorders_results_and_separates_both_scores(self):
        self.assertIn("sentences_jev", self.engine.rankings)
        base = self.engine.search("dress with lace", "sentences")
        self.post.assert_not_called()
        self.key.assert_not_called()
        out = self.engine.search("dress with lace", "sentences_jev")
        self.assertNotIn("error", out)
        self.assertEqual(out["results"][0]["id"], "d2")
        self.assertEqual({r["id"] for r in out["results"]}, {r["id"] for r in base["results"]})
        original = {r["id"]: r for r in base["results"]}
        for r in out["results"]:
            self.assertEqual(r["score"], original[r["id"]]["score"])
            self.assertEqual(r["parts"], original[r["id"]]["parts"])
            self.assertIn("grade", r["rerank"])
        self.assertIn("rerank_ms", out["timings"])
        self.assertGreaterEqual(out["timings"]["ranking_ms"], out["timings"]["rerank_ms"])
        self.assertEqual(out["rerank"]["status"], "applied")
        json.dumps(out, allow_nan=False)
        self.engine.search("dress with lace", "sentences_jev")
        self.assertEqual(self.post.call_count, 2)

    def hybrid_engine(self):
        e = self.engine
        hybrid = server.SearchEngine(e.products, e.T, e.I, e.parser, self.embedder, bank=e.bank,
                                     image_dir=self.image_dir)
        self.addCleanup(hybrid.pool.shutdown)
        return hybrid

    def test_hybrid_jev_uses_hybrid_scores_without_sentence_assets(self):
        hybrid = self.hybrid_engine()
        self.assertIn("hybrid_jev", hybrid.rankings)
        self.assertNotIn("sentences_jev", hybrid.rankings)
        base = hybrid.search("dress with lace", "hybrid")
        self.post.assert_not_called()
        with patch.object(hybrid.bank, "prefetch", wraps=hybrid.bank.prefetch) as prefetch:
            out = hybrid.search("dress with lace", "hybrid_jev")
        self.assertNotIn("error", out)
        self.assertFalse(prefetch.call_args.kwargs["lean"])
        self.assertEqual(out["rerank"]["base_ranking"], "hybrid")
        self.assertEqual(out["rerank"]["status"], "applied")
        self.assertEqual(out["weights"], base["weights"])
        original = {r["id"]: r for r in base["results"]}
        self.assertEqual({r["id"] for r in out["results"]}, set(original))
        self.assertEqual(out["results"][0]["id"], "d2")
        for r in out["results"]:
            self.assertEqual(r["score"], original[r["id"]]["score"])
            self.assertEqual(r["parts"], original[r["id"]]["parts"])
        self.post.assert_called_once()

    def test_failed_hybrid_jev_falls_back_to_hybrid(self):
        hybrid = self.hybrid_engine()
        base = hybrid.search("lace dress", "hybrid")
        self.post.side_effect = requests.Timeout("timeout")
        out = hybrid.search("lace dress", "hybrid_jev")
        self.assertEqual(out["results"], base["results"])
        self.assertEqual(out["rerank"]["status"], "fallback")
        self.assertEqual(out["rerank"]["base_ranking"], "hybrid")
        self.assertIn("showing the hybrid ranking", out["warnings"][0])

    def test_vision_uses_hybrid_and_pairs_each_text_with_its_own_photo(self):
        hybrid = self.hybrid_engine()
        for pid in ("d1", "d2", "d3"):
            enhanced = self.image_dir / "pilot_9922/images_enhanced" / pid / f"{pid}_id_gridfs_1.webp"
            enhanced.parent.mkdir(parents=True)
            Image.new("RGB", (1024, 1024), "red" if pid == "d2" else "blue").save(enhanced, lossless=True)
        base = hybrid.search("white dress", "hybrid")
        out = hybrid.search("white dress", "hybrid_jev_vision")
        self.assertEqual(out["rerank"]["status"], "applied")
        self.assertEqual(out["rerank"]["base_ranking"], "hybrid")
        self.assertTrue(out["rerank"]["vision"])
        self.assertEqual(out["rerank"]["images"], 3)
        self.assertEqual(out["results"][0]["id"], "d2")
        originals = {p["id"]: p for p in base["results"]}
        for p in out["results"]:
            self.assertEqual(p["parts"], originals[p["id"]]["parts"])
            self.assertTrue(p["rerank"]["image_used"])
        self.post.assert_called_once()
        call = self.post.call_args.kwargs
        self.assertEqual(call["timeout"], (3.05, 15.0))
        self.assertEqual(call["headers"]["TypeSafe-Danger-Zone-Images"], "true")
        for label, product in call["json"]["state"]["PRODUCTS"].items():
            pid = product["text"].split(" | ")[0]
            with decode_photo(product["photo"]) as im:
                self.assertEqual(im.size, (jev.MAX_IMAGE_SIZE, jev.MAX_IMAGE_SIZE))
                expected = (255, 0, 0) if pid == "d2" else (0, 0, 255)
                middle = (jev.MAX_IMAGE_SIZE // 2, jev.MAX_IMAGE_SIZE // 2)
                self.assertLess(sum(abs(a - b) for a, b in zip(im.getpixel(middle), expected)), 10)
            self.assertIn(f"Grade the product {label}.", call["json"]["questions"][label]["instructions"])
        json.dumps(out, allow_nan=False)

    def test_partial_photos_are_reported_and_no_photos_skip_api(self):
        (self.image_dir / "d2.png").unlink()
        out = self.engine.search("white dress", "hybrid_jev_vision")
        self.assertEqual(out["rerank"]["images"], 2)
        self.assertIn("2 of 3", out["warnings"][0])
        self.assertFalse(out["results"][0]["rerank"]["image_used"])
        state = self.post.call_args.kwargs["json"]["state"]["PRODUCTS"]
        self.assertEqual(sum(p["photo"] is None for p in state.values()), 1)
        for pid in ("d1", "d3"):
            (self.image_dir / (pid + ".png")).unlink()
        self.post.reset_mock()
        base = self.engine.search("white dress", "hybrid")
        out = self.engine.search("white dress", "hybrid_jev_vision")
        self.assertEqual(out["rerank"]["status"], "fallback")
        self.assertEqual(out["results"], base["results"])
        self.assertIn("No readable product photos", out["warnings"][0])
        self.post.assert_not_called()

    def test_vision_timeout_preserves_complete_hybrid_order(self):
        base = self.engine.search("lace dress", "hybrid")
        self.post.side_effect = requests.Timeout("timeout")
        out = self.engine.search("lace dress", "hybrid_jev_vision")
        self.assertEqual(out["results"], base["results"])
        self.assertEqual(out["rerank"]["status"], "fallback")
        self.post.assert_called_once()

    def test_filtering_happens_before_jev_and_no_match_skips_it(self):
        def manual(color):
            return dict(category="Dresses", filters=[dict(feature="colors", operator="contains_any", values=[color])])
        for ranking in ("sentences_jev", "hybrid_jev", "hybrid_jev_vision"):
            with self.subTest(ranking=ranking):
                out = self.engine.search("dress", ranking, manual("Black"))
                self.assertEqual({r["id"] for r in out["results"]}, {"d1", "d3"})
                state = self.post.call_args.kwargs["json"]["state"]
                self.assertEqual(len(state["PRODUCTS"]), 2)
                self.post.reset_mock()
                one = self.engine.search("dress", ranking, manual("White"))
                self.assertEqual(one["rerank"]["status"], "skipped")
                empty = self.engine.search("dress", ranking, manual("Red"))
                self.assertEqual(empty["results"], [])
                self.engine.search("", ranking, manual("Black"))
                self.post.assert_not_called()

    def test_results_beyond_the_reranked_prefix_keep_their_order(self):
        scores = np.array([3.0, 2.0, 1.0])
        for ranking in ("sentences_jev", "hybrid_jev", "hybrid_jev_vision"):
            with self.subTest(ranking=ranking):
                with patch.object(jev, "DEPTH", 2), patch.object(self.engine, "rank", return_value=(scores, None, None, None)):
                    out = self.engine.search("dress", ranking)
                self.assertEqual([r["id"] for r in out["results"]], ["d2", "d1", "d3"])
                self.assertIsNone(out["results"][-1]["rerank"])
                self.assertEqual(len(self.post.call_args.kwargs["json"]["questions"]), 2)

    def test_failed_or_incomplete_response_preserves_sentence_order(self):
        base = self.engine.search("lace dress", "sentences")
        original = [r["id"] for r in base["results"]]
        cases = [requests.Timeout("timeout"), Mock(ok=False, status_code=503),
                 Mock(ok=True, json=lambda: dict(answers={})),
                 Mock(ok=True, json=lambda: dict(answers={"P01": dict(choice="wrong")}))]
        for case in cases:
            with self.subTest(case=type(case).__name__):
                self.post.side_effect = case if isinstance(case, Exception) else None
                self.post.return_value = case
                self.post.reset_mock()
                out = self.engine.search("lace dress", "sentences_jev")
                self.assertNotIn("error", out)
                self.assertEqual([r["id"] for r in out["results"]], original)
                self.assertEqual(out["rerank"]["status"], "fallback")
                self.assertTrue(out["warnings"])
                self.assertTrue(all(r["rerank"] is None for r in out["results"]))
                self.post.assert_called_once()

    def test_missing_key_falls_back_without_http(self):
        self.key.side_effect = RuntimeError("Missing OPENROUTER_API_KEY")
        out = self.engine.search("dress", "sentences_jev")
        self.assertEqual(out["rerank"]["status"], "fallback")
        self.post.assert_not_called()

    def test_ranking_requires_sentence_assets(self):
        T = self.engine.T
        basic = server.SearchEngine(self.engine.products, T, np.zeros_like(T), self.engine.parser, self.embedder)
        self.addCleanup(basic.pool.shutdown)
        self.assertNotIn("sentences_jev", basic.rankings)
        self.assertNotIn("hybrid_jev", basic.rankings)
        self.assertNotIn("hybrid_jev_vision", basic.rankings)

    def test_http_menu_and_search_expose_optional_ranking(self):
        srv = server.build_server(self.engine, ".", port=0, ranking="sentences")
        worker = threading.Thread(target=srv.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/api/info") as r:
                info = json.load(r)
            self.assertEqual(info["ranking"], "sentences")
            for ranking, first_stage in server.RERANK_BASES.items():
                with self.subTest(ranking=ranking):
                    self.assertIn(ranking, info["rankings"])
                    with urllib.request.urlopen(base + f"/api/search?q=dress&ranking={ranking}") as r:
                        out = json.load(r)
                    self.assertEqual(out["rerank"]["status"], "applied")
                    self.assertEqual(out["rerank"]["base_ranking"], first_stage)
                    self.assertEqual(out["results"][0]["id"], "d2")
        finally:
            srv.shutdown()
            srv.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
