import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import conditions as c  # noqa: E402


def product(pid, category, section, features, gender="Women", brand="Acne Studios"):
    return c.prepare_product(dict(product_id=pid, category=category, section=section, gender=gender, brand=brand,
                                  features=features))


def L(feature, *values):
    return {"feature": feature, "values": list(values)}


P = [
    product("1", "Jeans", "Pants", {"colors": ["Black"], "fit": "Slim", "distressing": "Distressed",
                                   "main_composition": {"Cotton": 98, "Elastane": 2}}),
    product("2", "Jeans", "Pants", {"colors": ["Blue", "White"], "fit": "Skinny",
                                   "main_composition": {"Cotton": 50, "Polyester": 50}}, gender="Men"),
    product("3", "Dresses", "Dresses", {"colors": ["Black"], "length": "Midi", "gender": "Women"}),
    product("4", "T-shirts", "Tops", {"colors": ["White"], "main_composition": {"Polyester": 60, "Cotton": 40}}),
]


class Leaf(unittest.TestCase):
    def test_string(self):
        self.assertTrue(c.matches(L("fit", "Slim"), P[0]))
        self.assertFalse(c.matches(L("fit", "Slim"), P[1]))
        self.assertTrue(c.matches(L("fit", "Regular", "Skinny"), P[1]))

    def test_case_insensitive(self):
        self.assertTrue(c.matches(L("fit", "slim"), P[0]))
        self.assertTrue(c.matches(L("colors", "BLACK"), P[0]))

    def test_color_list_intersection(self):
        self.assertTrue(c.matches(L("colors", "White"), P[1]))
        self.assertTrue(c.matches(L("colors", "Red", "Blue"), P[1]))
        self.assertFalse(c.matches(L("colors", "Black"), P[1]))

    def test_composition_is_a_material_set(self):
        self.assertTrue(c.matches(L("main_composition", "Elastane"), P[0]))
        self.assertTrue(c.matches(L("main_composition", "Cotton"), P[3]))
        self.assertFalse(c.matches(L("main_composition", "Silk"), P[0]))
        self.assertTrue(c.matches({"op": "not", "arg": L("main_composition", "Polyester")}, P[0]))

    def test_match_all_and_exact(self):
        both = {"feature": "colors", "values": ["Blue", "White"], "match": "all"}
        self.assertTrue(c.matches(both, P[1]))
        self.assertFalse(c.matches(both, P[3]))
        only = {"feature": "main_composition", "values": ["Cotton"], "match": "exact"}
        self.assertFalse(c.matches(only, P[0]))
        self.assertTrue(c.matches(only | {"values": ["Cotton", "Elastane"]}, P[0]))
        self.assertFalse(c.matches({"feature": "length", "values": ["Midi"], "match": "all"}, P[0]))

    def test_missing_feature_never_matches(self):
        self.assertFalse(c.matches(L("length", "Midi"), P[0]))
        self.assertTrue(c.matches({"op": "not", "arg": L("length", "Midi")}, P[0]))

    def test_category_and_section(self):
        self.assertTrue(c.matches(L("category", "Jeans"), P[0]))
        self.assertTrue(c.matches(L("category", "Pants"), P[0]))
        self.assertFalse(c.matches(L("category", "Tops"), P[0]))
        self.assertTrue(c.matches(L("category", "tops"), P[3]))

    def test_gender_from_features_or_metadata(self):
        self.assertTrue(c.matches(L("gender", "Men"), P[1]))
        self.assertTrue(c.matches(L("gender", "Women"), P[2]))

    def test_brand_from_metadata(self):
        self.assertTrue(c.matches(L("brand", "acne studios"), P[0]))
        self.assertFalse(c.matches(L("brand", "Nike"), P[0]))


class Nodes(unittest.TestCase):
    def test_and_or_not(self):
        tree = {"op": "and", "args": [
            L("category", "Jeans"),
            {"op": "or", "args": [L("colors", "Black"), L("colors", "Blue")]},
            {"op": "not", "arg": L("distressing", "Distressed")}]}
        self.assertEqual([p["product_id"] for p in P if c.matches(tree, p)], ["2"])

    def test_empty_condition_means_no_filter(self):
        self.assertEqual(c.filter_products(None, P)["candidates"], [0, 1, 2, 3])

    def test_validation(self):
        for bad in [{"op": "xor", "args": [L("fit", "Slim")]}, {"op": "and", "args": []}, {"feature": "fit", "values": []},
                    {"feature": "fit", "values": "Slim"}, {"op": "not", "args": [L("fit", "Slim")]}, ["fit"],
                    {"feature": "fit", "values": ["Slim"], "match": "some"}]:
            with self.assertRaises(c.ConditionError, msg=bad):
                c.validate(bad)
        self.assertIsNone(c.validate(None))

    def test_describe(self):
        tree = {"op": "and", "args": [L("category", "Jeans"),
                                      {"op": "or", "args": [L("colors", "Black"), L("colors", "Blue")]},
                                      {"op": "not", "arg": L("fit", "Slim", "Skinny")}]}
        self.assertEqual(c.describe(tree),
                         "category = Jeans AND (colors = Black OR colors = Blue) AND NOT fit ∈ {Slim, Skinny}")
        self.assertEqual(c.describe({"feature": "colors", "values": ["Black", "White"], "match": "all"}), "colors ⊇ {Black, White}")
        self.assertEqual(c.describe({"feature": "colors", "values": ["Black"], "match": "exact"}), "colors = only {Black}")

    def test_matched_features(self):
        tree = {"op": "and", "args": [L("category", "Jeans"), {"op": "or", "args": [L("colors", "Black"), L("fit", "Regular")]},
                                      {"op": "not", "arg": L("length", "Midi")}]}
        self.assertEqual(c.matched_features(tree, P[0]), ["category", "colors"])


class Prune(unittest.TestCase):
    def test_unknown_feature_and_value(self):
        v = c.Vocabulary(P)
        tree = {"op": "and", "args": [L("category", "jeans"), L("pattern", "Striped"), L("colors", "black", "Neon"),
                                      {"op": "not", "arg": L("fit", "Baggy")}]}
        pruned, warnings = c.prune(tree, v)
        self.assertEqual(pruned, {"op": "and", "args": [L("category", "Jeans"), L("colors", "Black")]})
        self.assertEqual(len(warnings), 3)
        self.assertTrue(any("pattern" in w for w in warnings) and any("Neon" in w for w in warnings))

    def test_everything_unknown_gives_no_condition(self):
        pruned, warnings = c.prune(L("pattern", "Striped"), c.Vocabulary(P))
        self.assertIsNone(pruned)
        self.assertEqual(len(warnings), 1)


class FilterProducts(unittest.TestCase):
    def test_no_product_means_no_results(self):
        tree = {"op": "and", "args": [L("category", "Jeans"), L("colors", "Black"), L("fit", "Skinny")]}
        self.assertEqual(c.filter_products(tree, P)["candidates"], [])

    def test_matching_products_with_matched_features(self):
        f = c.filter_products({"op": "and", "args": [L("category", "Dresses"), L("length", "Midi")]}, P)
        self.assertEqual((f["candidates"], f["matched"]), ([2], {2: ["category", "length"]}))


if __name__ == "__main__":
    unittest.main()
