import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import facets  # noqa: E402
from test_conditions import P  # noqa: E402


class Facets(unittest.TestCase):
    def test_values_and_counts_from_the_parser_schema(self):
        f = facets.load(P)
        self.assertEqual(set(f), {"Dresses", "T-shirts"})
        by_feature = {x["feature"]: x for x in f["Dresses"]}
        self.assertEqual(by_feature["colors"]["kind"], "multi")
        self.assertEqual(by_feature["length"]["kind"], "single")
        self.assertIn(["Black", 1], by_feature["colors"]["values"])
        self.assertIn(["Maxi", 0], by_feature["length"]["values"])
        self.assertEqual(by_feature["brand"]["values"], [["Acne Studios", 1]])
        self.assertEqual(f["Dresses"][-1]["feature"], "brand")


if __name__ == "__main__":
    unittest.main()
