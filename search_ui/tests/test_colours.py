import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import bank  # noqa: E402
import colours  # noqa: E402
from test_bank import Embedder, products, ranker, vector  # noqa: E402

# d1 light pink, d2 dark pink with a little black, d3 burgundy; the jeans are blue
COLOURS = [("d1", 0, "light pink", "Pink", "#FFB6C1", 1.0), ("d2", 0, "dark pink", "Pink", "#9C526D", 0.8),
           ("d2", 1, "black", "Black", "#1A1A1A", 0.2), ("d3", 0, "burgundy", "Red", "#6B222A", 1.0),
           ("j1", 0, "blue", "Blue", "#3B64AA", 1.0), ("j2", 0, "light blue", "Blue", "#A8C2E0", 1.0)]
NAMES = pd.DataFrame([("light pink", "#FFB6C1", "Pink"), ("dark pink", "#9C526D", "Pink"), ("burgundy", "#6B222A", "Red"),
                      ("blue", "#3B64AA", "Blue")], columns=["name", "hex", "family"])


def colour_data(ps):
    frame = pd.DataFrame(COLOURS, columns=["product_id", "rank", "name", "family", "hex", "share"])
    return colours.Colours(ps, frame, NAMES, np.stack([vector(common_text(n)) for n in NAMES["name"]]))


def common_text(name):
    return colours.common.query_text(name)


class Colours(unittest.TestCase):
    def setUp(self):
        self.ps = products()
        self.c = colour_data(self.ps)
        self.dresses = np.array([0, 1, 2])

    def test_closest_colour_first(self):
        s = self.c.score(dict(hex="#FFB6C1"), self.dresses)
        self.assertEqual(list(np.argsort(-s)), [0, 1, 2])
        s = self.c.score(dict(hex="#6B222A"), self.dresses)
        self.assertEqual(int(np.argmax(s)), 2)

    def test_lightness_only(self):
        light = self.c.score(dict(lightness="light", family="Pink"), self.dresses)
        dark = self.c.score(dict(lightness="dark", family="Pink"), self.dresses)
        self.assertEqual(int(np.argmax(light)), 0)
        self.assertEqual(int(np.argmax(dark)), 2)

    def test_target_exact_and_nearest(self):
        self.assertEqual(self.c.target("burgundy")["hex"], "#6B222A")
        self.assertEqual(self.c.target("dark  pink dress", vector(common_text("dark pink")))["name"], "dark pink")
        self.assertIsNone(self.c.target("with pockets", vector(common_text("with pockets"))))


class BankColours(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        rows = [dict(phrase="light pink", kind="shade", negated=False, english="light pink", concepts=[],
                     hex="#FFB6C1", family="Pink", lightness="light"),
                dict(phrase="for a wedding", kind="occasion", negated=False, english="for a wedding",
                     concepts=["wedding_guest"])]
        self.r, ps = ranker(Path(self.tmp.name), Embedder(), rows)
        self.r.colours = colour_data(ps)
        self.dresses = np.array([0, 1, 2])

    def test_lightness_word_takes_the_colour_after_it(self):
        score, routes = self.r.rank(["light"], self.dresses, "Dresses", query="light pink dress")
        self.assertEqual(routes[0]["colour"]["hex"], "#FFB6C1")
        self.assertEqual(int(np.argmax(score)), 0)

    def test_unknown_colour_name_and_negation(self):
        score, routes = self.r.rank(["burgundy"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["kind"]), ("colour name", "shade"))
        self.assertEqual(int(np.argmax(score)), 2)
        score, routes = self.r.rank(["not burgundy"], self.dresses, "Dresses")
        self.assertTrue(routes[0]["negated"])
        self.assertEqual(int(np.argmin(score)), 2)

    def test_hybrid_colour_term(self):
        terms, _ = self.r.adjustments(["light"], self.dresses, "Dresses", query="light pink dress")
        self.assertEqual(len(terms["colour"]), 1)
        self.assertEqual(int(np.argmax(terms["colour"][0])), 0)

    def test_nearest_shade_takes_its_own_colour(self):
        e = np.eye(64, dtype=np.float32)
        own = {"ciemnozielona": 0.9 * e[0] + 0.436 * e[1], "dark green": 0.8 * e[0] + 0.6 * e[1], "dark pink": e[5],
               "burgundy": e[6], "light pink": e[7], "blue": e[8], "ciemnoszary": e[0]}

        def embed(text):
            return own.get(text.removeprefix(colours.common.query_text("")), e[9])
        rows = [dict(phrase="ciemnoszary", kind="shade", negated=False, english="ciemnoszary", concepts=[],
                     hex="#36454F", family="Grey", lightness="dark")]
        r, ps = ranker(Path(self.tmp.name), embed, rows)
        r.matrix = np.stack([own["ciemnoszary"]])
        names = pd.concat([NAMES, pd.DataFrame([("dark green", "#1F3D2B", "Green")], columns=NAMES.columns)])
        r.colours = colours.Colours(ps, pd.DataFrame(COLOURS, columns=["product_id", "rank", "name", "family", "hex",
                                                                         "share"]), names,
                                    np.stack([embed(colours.common.query_text(n)) for n in names["name"]]))
        _, routes = r.rank(["ciemnozielona"], self.dresses, "Dresses")
        self.assertEqual((routes[0]["match"], routes[0]["neighbour"]), ("nearest", "ciemnoszary"))
        self.assertEqual(routes[0]["colour"]["name"], "dark green")

    def test_no_colours_keeps_text_signals(self):
        self.r.colours = None
        _, routes = self.r.rank(["burgundy"], self.dresses, "Dresses")
        self.assertIsNone(routes[0]["colour"])


if __name__ == "__main__":
    unittest.main()
