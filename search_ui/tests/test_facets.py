import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import facets  # noqa: E402
from test_conditions import P  # noqa: E402


class Facets(unittest.TestCase):
    def test_values_and_counts_from_the_category_schema(self):
        f = facets.load(P)
        self.assertEqual(set(f), {"Dresses", "Jeans", "T-shirts"})
        by_feature = {x["feature"]: x for x in f["Dresses"]}
        self.assertEqual(by_feature["colors"]["kind"], "multi")
        self.assertEqual(by_feature["main_composition"]["kind"], "multi")
        self.assertEqual(by_feature["length"]["kind"], "single")
        self.assertIn(["Black", 1], by_feature["colors"]["values"])
        self.assertIn(["Maxi", 0], by_feature["length"]["values"])
        self.assertEqual(by_feature["price"]["kind"], "number")
        self.assertEqual(by_feature["brand"]["values"], [["Acne Studios", 1]])
        self.assertEqual(f["Dresses"][-1]["feature"], "brand")

    def test_values_the_parser_never_uses_are_left_out(self):
        values = {v for x in facets.load(P)["Dresses"] for v, _ in x["values"]}
        self.assertFalse(values & facets.HIDDEN)

    def test_every_pilot_category_has_a_schema(self):
        self.assertEqual(len(facets.category_schemas()), 22)


if __name__ == "__main__":
    unittest.main()
