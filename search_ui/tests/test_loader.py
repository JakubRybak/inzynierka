import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import pandas as pd

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import common  # noqa: E402
import numpy as np
from server import load_feature_embeddings

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

    def test_existing_index_excludes_products_and_aligns_embeddings(self):
        records = [
            dict(product_id="342903", category="Blouses", features="{}", images="[]"),
            dict(product_id="101", category="Dresses", features="{}", images="[]"),
        ]
        pd.DataFrame(records).to_parquet(self.d / common.INDEX)
        (self.d / common.META).write_text(json.dumps({"products": 2, "categories": {"Blouses": 1, "Dresses": 1}}))
        np.savez(self.d / common.FEATURE_VECTORS, ids=["342903", "101"], vectors=[[1., 0.], [0., 1.]])
        products, meta = common.load_index(self.d)
        self.assertEqual([p["product_id"] for p in products], ["101"])
        self.assertEqual(meta["products"], 1)
        self.assertEqual(meta["categories"], {"Dresses": 1})
        np.testing.assert_array_equal(load_feature_embeddings(products, self.d), [[0., 1.]])

    def test_index_paths_are_kept_relative_to_the_repository(self):
        self.assertEqual(common.repo_relative(common.DATASET), "data/processed/fashiongen")
        self.assertEqual(common.repo_relative(self.d), str(self.d.resolve()))
        pd.DataFrame([dict(product_id="101", category="Dresses", features="{}", images="[]")]).to_parquet(
            self.d / common.INDEX)
        (self.d / common.META).write_text(json.dumps(dict(dataset="data/processed/fashiongen", embeddings="/elsewhere",
                                                          concepts=dict(yaml="search_ui/ranking_data/concepts.yaml"))))
        _, meta = common.load_index(self.d)
        self.assertEqual(meta["dataset"], str(common.DATASET))
        self.assertEqual(meta["embeddings"], "/elsewhere")
        self.assertEqual(meta["concepts"]["yaml"], str(common.SEARCH_UI / "ranking_data/concepts.yaml"))

    def test_exclusions_accept_numeric_product_ids(self):
        products = pd.DataFrame({"product_id": [342903, 101]})
        self.assertEqual(common.exclude_products(products)["product_id"].tolist(), [101])


if __name__ == "__main__":
    unittest.main()
