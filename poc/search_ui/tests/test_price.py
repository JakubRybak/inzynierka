"""Price boundary, parser serialization and search integration regressions (offline)."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "search_ui"))
sys.path.insert(0, str(ROOT / "scripts"))
import conditions
import parser_adapter
import server
from query_parser import QueryParser


def price(op, value):
    return {"feature": "price", "operator": op, "value": value}


def products():
    return [dict(product_id=str(i), category="T-shirts", section="Tops", name=f"Tee {i}",
                 images=[], features={"colors": ["Black" if i != 2 else "White"]}, msrpUSD=value)
            for i, value in enumerate([99.5, 100, 200, 200.01, 0, None, "", "bad", float("nan"), float("inf")])]


class PriceTests(unittest.TestCase):
    def setUp(self):
        self.products = [conditions.prepare_product(p) for p in products()]

    def test_numeric_boundaries_and_unknown_prices(self):
        for op, expected in [("lt", [0, 1]), ("lte", [0, 1, 2]), ("gt", [3]),
                             ("gte", [2, 3]), ("eq", [2])]:
            with self.subTest(op=op):
                self.assertEqual(conditions.filter_products(price(op, 200), self.products)["candidates"], expected)
        self.assertEqual(conditions.filter_products(None, self.products)["candidates"], list(range(10)))
        self.assertEqual(conditions.filter_products(price("eq", 0), self.products)["candidates"], [])

    def test_range_and_price_not_pruned(self):
        raw = {"category": "T-shirts", "filters": [price("gte", 100), price("lt", 200)]}
        tree, warnings = conditions.prune(parser_adapter.to_condition(raw), conditions.Vocabulary(self.products))
        self.assertFalse(warnings)
        self.assertEqual(conditions.filter_products(tree, self.products)["candidates"], [1])
        self.assertIn("price < 200", conditions.describe(tree))
        # An index with no known prices must not discard the condition and return everything.
        empty_prices = self.products[4:]
        tree, _ = conditions.prune(tree, conditions.Vocabulary(empty_prices))
        self.assertEqual(conditions.filter_products(tree, empty_prices)["candidates"], [])

    def test_invalid_price_rejected(self):
        invalid = [price("lt", v) for v in ["200", True, None, -1, float("nan"), float("inf")]]
        invalid += [price("contains_any", 200), price("lt", 200) | {"values": ["200"]}]
        for f in invalid:
            with self.subTest(f=f), self.assertRaises(conditions.ConditionError):
                parser_adapter.to_condition({"category": "T-shirts", "filters": [f]})

    def test_parser_to_search_and_manual_filters(self):
        parser = QueryParser()
        filters = [{"feature": "colors", "operator": "contains_any", "values": ["Black"]}, price("lte", 100)]
        with patch.object(parser, "_call_api", side_effect=[
                ({"category": "T-shirts"}, {}, 0), ({"filters": filters, "residual": ""}, {}, 0)]):
            parsed = parser.parse("black tee up to 100 euros")
        self.assertEqual(parsed.to_dict()["filters"], filters)
        self.assertIn("price lte 100", parsed.summary())
        vectors = np.ones((len(self.products), 4))
        engine = server.SearchEngine(copy.deepcopy(self.products), vectors, vectors,
                                     parser_adapter.Parser("test", lambda q: parsed.to_dict()),
                                     lambda q: np.ones(4))
        self.addCleanup(engine.pool.shutdown)
        result = engine.search("black tee up to 100 euros")
        self.assertNotIn("error", result)
        self.assertEqual([p["id"] for p in result["results"]], ["0", "1"])
        self.assertEqual(result["results"][0]["price"], "99.50 USD")
        self.assertIn("price", result["results"][0]["matched"])
        self.assertEqual(engine.product("0")["price"], "99.50 USD")
        numeric = next(f for f in engine.facets["T-shirts"] if f["feature"] == "price")
        self.assertEqual(numeric["kind"], "number")
        self.assertEqual(set(numeric["operators"]), {"lt", "lte", "gt", "gte", "eq"})
        manual = {"category": "T-shirts", "filters": [price("gte", 100), price("lt", 200)]}
        result = engine.search("", manual=manual)
        self.assertEqual([p["id"] for p in result["results"]], ["1"])
        self.assertEqual(result["parsed"]["filters"], manual["filters"])

    def test_parser_does_not_silently_drop_invalid_price(self):
        parser = QueryParser()
        with patch.object(parser, "_call_api", side_effect=[
                ({"category": "T-shirts"}, {}, 0),
                ({"filters": [price("lt", "200")], "residual": ""}, {}, 0)]):
            with self.assertRaises(ValueError):
                parser.parse("tee under 200")


if __name__ == "__main__":
    unittest.main()
