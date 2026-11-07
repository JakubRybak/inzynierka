"""Check annotated query filters against the product feature schemas."""
import csv
import json
import math
import unittest
from pathlib import Path

from feature_extraction.schema import allowed_values, load_schemas


QUERIES = Path(__file__).resolve().parents[1] / "queries"


class QuerySchemaTests(unittest.TestCase):
    def test_expected_filter_features_and_values_exist_in_schema(self):
        schemas, _ = load_schemas()
        by_category = {category: schema for (_, category), schema in schemas.items()}
        self.assertEqual(len(by_category), len(schemas), "Category names must be unique")
        paths = sorted(QUERIES.rglob("*.csv"))
        self.assertTrue(paths, f"No CSV files found in {QUERIES}")

        for path in paths:
            with self.subTest(file=str(path.relative_to(QUERIES))):
                with path.open(encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    self.assertIn("expected_output", reader.fieldnames or [])
                    has_rows = False
                    for row in reader:
                        has_rows = True
                        with self.subTest(line=reader.line_num, query=row.get("query")):
                            expected = json.loads(row["expected_output"])
                            category = expected["category"]
                            filters = expected["filters"]
                            self.assertIsInstance(filters, list)
                            if category is None:
                                self.assertEqual(filters, [])
                                continue
                            self.assertIn(category, by_category)
                            for clause in filters:
                                with self.subTest(feature=clause.get("feature")):
                                    self.assert_filter_values(clause, by_category[category])
                    self.assertTrue(has_rows, "CSV has no query rows")

    def assert_filter_values(self, clause, schema):
        feature = clause["feature"]
        if feature == "price":
            value = clause.get("value")
            self.assertIn(type(value), (int, float))
            self.assertTrue(math.isfinite(value) and value >= 0, f"Invalid price: {value!r}")
            return

        values = clause.get("values")
        self.assertIsInstance(values, list)
        self.assertTrue(values and all(isinstance(value, str) and value.strip() for value in values))
        if feature == "brand":
            return

        self.assertIn(feature, schema)
        unknown = set(values) - (allowed_values(schema[feature]) - {"Other"})
        self.assertFalse(unknown, f"Unsupported values for {feature}: {sorted(unknown)!r}")


if __name__ == "__main__":
    unittest.main()
