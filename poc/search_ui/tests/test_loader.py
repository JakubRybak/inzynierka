import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

RECORDS = [
    dict(product_id="101", section="Dresses", category="Dresses", status="ready", exclusion_reasons=[],
         features={"colors": ["Black", "White"], "length": "Midi", "main_composition": {"Wool": 100.0}},
         feature_metadata={"pattern": {"status": "assigned"}}),
    dict(product_id="102", section="Tops", category="T-shirts", status="excluded", exclusion_reasons=["main_composition"],
         features={"gender": "Men"}, feature_metadata={}),
]


class LoadFeatures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        as_json = pd.DataFrame([{k: json.dumps(v) if k in common.JSON_COLUMNS else v for k, v in r.items()} for r in RECORDS])
        as_json.to_parquet(self.d / "f.parquet", index=False)
        as_json.to_csv(self.d / "f.csv", index=False)
        (self.d / "f.jsonl").write_text("".join(json.dumps(r) + "\n" for r in RECORDS), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_three_formats_give_the_same_result(self):
        for ext in ("parquet", "csv", "jsonl"):
            d = common.load_features([self.d / f"f.{ext}"])
            self.assertEqual(d["product_id"].tolist(), ["101", "102"], ext)
            self.assertEqual(d["features"].tolist(), [r["features"] for r in RECORDS], ext)
            self.assertEqual(d["exclusion_reasons"].tolist(), [[], ["main_composition"]], ext)

    def test_duplicates_across_files(self):
        with self.assertRaises(ValueError):
            common.load_features([self.d / "f.parquet", self.d / "f.jsonl"])

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            common.load_features([self.d / "f.xlsx"])


if __name__ == "__main__":
    unittest.main()
