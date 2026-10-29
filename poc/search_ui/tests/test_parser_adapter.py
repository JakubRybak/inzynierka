import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import conditions as c  # noqa: E402
import parser_adapter as pa  # noqa: E402
from test_conditions import P  # noqa: E402


def parsed(category, *filters, residual=""):
    return {"query": "q", "category": category, "residual": residual,
            "filters": [{"feature": f, "operator": op, "values": list(v)} for f, op, v in filters]}


class ToCondition(unittest.TestCase):
    def test_operators(self):
        tree = pa.to_condition(parsed("Jeans",
                                      ("colors", "contains_any", ["Black", "Blue"]),
                                      ("fit", "not_in", ["Slim"]),
                                      ("colors", "contains_all", ["Black", "White"]),
                                      ("main_composition", "equals_set", ["Cotton"]),
                                      ("main_composition", "contains_none", ["Polyester"]),
                                      ("brand", "in", ["Acne Studios"])))
        self.assertEqual(tree["args"], [
            {"feature": "category", "values": ["Jeans"]},
            {"feature": "colors", "values": ["Black", "Blue"]},
            {"op": "not", "arg": {"feature": "fit", "values": ["Slim"]}},
            {"feature": "colors", "values": ["Black", "White"], "match": "all"},
            {"feature": "main_composition", "values": ["Cotton"], "match": "exact"},
            {"op": "not", "arg": {"feature": "main_composition", "values": ["Polyester"]}},
            {"feature": "brand", "values": ["Acne Studios"]}])

    def test_category_only(self):
        self.assertEqual(pa.to_condition(parsed("Dresses", residual="for a wedding")),
                         {"op": "and", "args": [{"feature": "category", "values": ["Dresses"]}]})

    def test_out_of_catalog(self):
        with self.assertRaises(pa.OutOfCatalog):
            pa.to_condition(parsed(None, residual="blue skinny jeans"))

    def test_bad_format(self):
        for bad in [None, ["Jeans"], {"filters": []}, parsed("Jeans", ("fit", "gte", ["Slim"])),
                    parsed("Jeans", ("fit", "in", []))]:
            with self.assertRaises(c.ConditionError, msg=bad):
                pa.to_condition(bad)

    def test_parser_info(self):
        raw = parsed("Dresses", residual="for a wedding") | {"step1_latency_seconds": 0.7, "step2_latency_seconds": 1.1,
                                                             "metadata": {"estimated_cost_usd": 0.002}}
        i = pa.parser_info(raw)
        self.assertEqual((i["category"], i["residual"], i["step2_s"], i["cost_usd"]), ("Dresses", ["for a wedding"], 1.1, 0.002))


class Mock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.yaml = Path(self.tmp.name) / "mock.yaml"
        self.yaml.write_text(textwrap.dedent("""
            "Black Skinny Jeans!":
              category: Jeans
              filters:
                - {feature: fit, operator: not_in, values: [Slim]}
        """), encoding="utf-8")
        self.mock = pa.MockParser(c.Vocabulary(P), self.yaml)

    def tearDown(self):
        self.tmp.cleanup()

    def test_from_yaml(self):
        r = self.mock("black skinny jeans")
        self.assertEqual((r["_mock"], r["category"], r["residual"]), ("parser_mock.yaml", "Jeans", []))
        self.assertEqual(pa.to_condition(r)["args"][1], {"op": "not", "arg": {"feature": "fit", "values": ["Slim"]}})

    def test_yaml_reread_on_every_query(self):
        self.yaml.write_text('"black skinny jeans": {category: Dresses}\n', encoding="utf-8")
        self.assertEqual(self.mock("black skinny jeans")["category"], "Dresses")

    def test_vocabulary(self):
        r = self.mock("black slim jean for men")
        self.assertEqual((r["_mock"], r["category"], r["residual"]), ("vocabulary", "Jeans", ["for"]))
        self.assertIn({"feature": "colors", "operator": "contains_any", "values": ["Black"]}, r["filters"])
        self.assertIn({"feature": "fit", "operator": "in", "values": ["Slim"]}, r["filters"])
        self.assertIn({"feature": "gender", "operator": "in", "values": ["Men"]}, r["filters"])

    def test_no_category_is_out_of_catalog(self):
        with self.assertRaises(pa.OutOfCatalog):
            pa.to_condition(self.mock("blackish slimmer"))


class LoadParser(unittest.TestCase):
    def test_module_function(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_parser_module.py").write_text(
                'NAME = "test"\ndef parse(q):\n    return {"category": q.title(), "filters": []}\n', encoding="utf-8")
            sys.path.insert(0, d)
            try:
                p = pa.load_parser("test_parser_module:parse")
                self.assertEqual(p.name, "test")
                self.assertEqual(pa.to_condition(p("jeans"))["args"], [{"feature": "category", "values": ["Jeans"]}])
            finally:
                sys.path.remove(d)

    def test_bad_spec(self):
        with self.assertRaises(SystemExit):
            pa.load_parser("no_colon")


if __name__ == "__main__":
    unittest.main()
