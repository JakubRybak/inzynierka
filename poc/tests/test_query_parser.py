"""Offline tests for query parser prompts, schemas and dataclass validation."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
QUERY_PARSING_DIR = ROOT / "poc/query_parsing"
PROMPTS_DIR = QUERY_PARSING_DIR / "prompts"
SCHEMAS_DIR = QUERY_PARSING_DIR / "schemas"

sys_path = str(ROOT / "poc/scripts")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from query_parser import QueryParser, FilterClause, ParsedQuery, _extract_code_blocks


class QueryParserOfflineTests(unittest.TestCase):
    def test_prompt_extraction_code_blocks(self):
        cat_text = (PROMPTS_DIR / "category.md").read_text(encoding="utf-8")
        cat_blocks = _extract_code_blocks(cat_text)
        self.assertEqual(len(cat_blocks), 1)
        self.assertIn("FEW-SHOT EXAMPLES", cat_blocks[0])

        for cat_file in ["t-shirts.md", "dresses.md", "tank-tops-and-camisoles.md"]:
            text = (PROMPTS_DIR / cat_file).read_text(encoding="utf-8")
            blocks = _extract_code_blocks(text)
            self.assertEqual(len(blocks), 2, f"Expected 2 code blocks in {cat_file}")
            self.assertIn("Category:", blocks[0])
            self.assertIn("Query:", blocks[0])
            self.assertIn("FEW-SHOT EXAMPLES", blocks[1])

    def test_schema_validity(self):
        for schema_file in ["category.json", "t-shirts.json", "dresses.json", "tank-tops-and-camisoles.json"]:
            path = SCHEMAS_DIR / schema_file
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("type", data)
            self.assertIn("properties", data)

    def test_dataclass_methods(self):
        f1 = FilterClause(feature="brand", operator="in", values=["Nike"])
        f2 = FilterClause(feature="colors", operator="contains_any", values=["Black"])
        parsed = ParsedQuery(
            query="black Nike t-shirt for running",
            category="T-shirts",
            filters=[f1, f2],
            residual="for running",
            step1_latency_seconds=0.72,
            step2_latency_seconds=0.81,
            total_latency_seconds=1.53,
            metadata={"model": "gemini-3.5-flash-lite", "estimated_cost_usd": 0.0018}
        )
        self.assertEqual(parsed.step1_latency_seconds, 0.72)
        self.assertEqual(parsed.step2_latency_seconds, 0.81)
        self.assertEqual(parsed.total_latency_seconds, 1.53)

        d = parsed.to_dict()
        self.assertEqual(d["category"], "T-shirts")
        self.assertEqual(len(d["filters"]), 2)
        self.assertEqual(d["filters"][0]["feature"], "brand")
        self.assertEqual(d["filters"][1]["feature"], "colors")
        self.assertEqual(d["step1_latency_seconds"], 0.72)
        self.assertEqual(d["step2_latency_seconds"], 0.81)
        self.assertEqual(d["total_latency_seconds"], 1.53)
        self.assertEqual(d["residual"], "for running")

        summary = parsed.summary()
        self.assertIn("brand in ['Nike']", summary)
        self.assertIn("Step 1: 0.72s, Step 2: 0.81s", summary)


if __name__ == "__main__":
    unittest.main()
