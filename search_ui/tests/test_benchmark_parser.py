import csv
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parser_adapter as pa  # noqa: E402

with patch("subprocess.run") as run:
    run.return_value.stdout = ""
    import benchmark_parser as bp  # noqa: E402


def benchmark(*rows):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["query", "expected_output", "language", "source"])
    for query, category, filters, residual in rows:
        w.writerow([query, json.dumps(dict(category=category, filters=filters, residual=residual)), "en", "test"])
    return [("query_extraction/queries/test.csv", out.getvalue())]


def queries(split, n):
    """n query texts of one split."""
    out, i = [], 0
    while len(out) < n:
        q = f"query {i}"
        if bp.split(bp.query_id(q, "Jeans")) == split:
            out.append(q)
        i += 1
    return out


class Benchmark(unittest.TestCase):
    def setUp(self):
        self.dev, self.test = queries("dev", 7), queries("test", 1)
        rows = [(q, "Jeans", [{"feature": "fit", "operator": "in", "values": ["Slim"]}], ["stretch"] if i < 6 else [])
                for i, q in enumerate(self.dev)]
        rows += [(self.test[0], "Jeans", [], []), (self.dev[0], "Jeans", [], ["duplicate"])]
        self.rows = bp.load(benchmark(*rows))
        self.calls = []
        self.parser = bp.BenchmarkParser(self.rows, lambda q: self.calls.append(q) or {"category": None, "filters": []})

    def test_split_is_the_ranking_evaluation_split(self):
        import hashlib
        qid = hashlib.sha256("black jeans|Jeans".encode()).hexdigest()[:12]
        self.assertEqual(bp.query_id("black jeans", "Jeans"), qid)
        self.assertEqual(bp.split(qid), "dev" if int(hashlib.sha256(f"split|{qid}".encode()).hexdigest(), 16) % 2 == 0
                         else "test")

    def test_repeated_query_kept_once(self):
        self.assertEqual(len(self.rows), 8)
        self.assertEqual(next(r for r in self.rows if r["query"] == self.dev[0])["residual"], ["stretch"])

    def test_dev_query_answered_from_the_benchmark(self):
        r = self.parser(self.dev[1].upper() + "!")
        self.assertEqual((r["category"], r["residual"], r["_source"]), ("Jeans", ["stretch"], "benchmark (dev)"))
        self.assertEqual(pa.to_condition(r)["args"][1], {"feature": "fit", "values": ["Slim"]})
        self.assertEqual(self.calls, [])

    def test_test_query_goes_to_the_fallback(self):
        r = self.parser(self.test[0])
        self.assertEqual((self.calls, r["_source"]), ([self.test[0]], "LLM parser (benchmark test query)"))
        self.assertEqual(self.parser("red dress")["_source"], "LLM parser")

    def test_without_fallback_no_category(self):
        self.assertIsNone(bp.BenchmarkParser(self.rows)("red dress")["category"])

    def test_examples_only_dev_and_residual_first(self):
        ex = bp.examples(self.rows)
        self.assertEqual(list(ex), ["Jeans"])
        self.assertEqual(len(ex["Jeans"]), bp.EXAMPLES_PER_CATEGORY)
        self.assertNotIn(self.test[0], ex["Jeans"])
        self.assertNotIn(self.dev[6], ex["Jeans"])


class AroundPrice(unittest.TestCase):
    def test_around_becomes_a_range(self):
        raw = {"category": "Jeans", "filters": [{"feature": "price", "operator": "around", "value": 100}]}
        self.assertEqual(pa.to_condition(raw)["args"][1:], [
            {"feature": "price", "operator": "gte", "value": 80.0},
            {"feature": "price", "operator": "lte", "value": 120.0}])


if __name__ == "__main__":
    unittest.main()
