"""Offline unit tests for query parsing API, catalog, schemas, validators, dataset loader, and reporting."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from experiments.query_parsing import (
    CONFIGS,
    QueryParser,
    QueryExtractor,
    parse_query,
    resolve_config_list,
    resolve_config_name,
)
from experiments.query_parsing.benchmark import (
    canonicalize_clause,
    canonicalize_filters,
    load_dataset_rows,
    load_queries,
    required_stages_for_configs,
    summarize_latencies,
)
from experiments.query_parsing.clients import (
    JevCallResult,
    LLMCallResult,
    build_full_system_prompt,
    build_open_system_prompt,
    category_payload,
    closed_features_payload,
    filters_from_answers,
    normalize_query,
)
from experiments.query_parsing.core import (
    CATEGORIES_PROMPTS_DIR,
    CATEGORY_CRITERIA,
    CATEGORY_FEW_SHOTS,
    EXCLUDED_FILTER_VALUES,
    PER_CATEGORY_FEW_SHOTS,
    PROMPTS_DIR,
    build_cerebras_full_schema,
    build_cerebras_open_schema,
    build_vertex_full_schema,
    load_category_prompt_configs,
    load_query_catalog,
    validate_response,
)


class _FakeJevClient:
    def __init__(self, category_choice: str = "T-shirts") -> None:
        self.category_choice = category_choice
        self.calls = 0

    def call(self, payload: dict) -> JevCallResult:
        self.calls += 1
        if "category" in payload["questions"]:
            return JevCallResult(
                answers={"category": {"choice": self.category_choice}},
                latency_seconds=0.21,
                cost_usd=0.00012,
                usage={},
            )
        answers = {qid: {"choice": "not_specified"} for qid in payload["questions"]}
        for qid, qspec in payload["questions"].items():
            if qid.endswith("_relation"):
                answers[qid] = {"choice": "ANY"}
            elif "'Black'" in qspec.get("instructions", ""):
                answers[qid] = {"choice": "requested"}
        return JevCallResult(
            answers=answers,
            latency_seconds=0.31,
            cost_usd=0.00045,
            usage={},
        )


class _FakeLLMClient:
    def extract_full(self, query: str, category: str, catalog: dict) -> LLMCallResult:
        return LLMCallResult(
            parsed={
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                ],
                "residual": ["for gym"],
            },
            latency_seconds=0.45,
            cost_usd=0.0002,
            model="fake",
            usage={},
        )

    def extract_open(
        self, query: str, category: str, closed_filters: list, catalog: dict
    ) -> LLMCallResult:
        return LLMCallResult(
            parsed={
                "filters": [{"feature": "brand", "operator": "in", "values": ["Nike"]}],
                "residual": ["for gym"],
            },
            latency_seconds=0.38,
            cost_usd=0.00015,
            model="fake",
            usage={},
        )


class QueryParsingOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_query_catalog()
        cls.groups = load_queries()

    def test_all_22_categories_covered_in_catalog_and_criteria(self) -> None:
        self.assertEqual(len(self.catalog), 22)
        self.assertEqual(len(list(CATEGORIES_PROMPTS_DIR.glob("*.yaml"))), 22)
        self.assertTrue((PROMPTS_DIR / "category_classification.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "feature_definitions.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "full_extraction.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "closed_features.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "open_extraction.yaml").exists())
        self.assertEqual(set(self.catalog.keys()), set(CATEGORY_CRITERIA.keys()))
        self.assertEqual(set(self.catalog.keys()), set(PER_CATEGORY_FEW_SHOTS.keys()))
        self.assertEqual(set(self.catalog.keys()), set(load_category_prompt_configs().keys()))
        for cat, features in self.catalog.items():
            for feat, spec in features.items():
                self.assertTrue(spec["values"], f"Empty values for {cat}.{feat}")
                self.assertFalse(set(spec["values"]) & EXCLUDED_FILTER_VALUES)

    def test_per_category_few_shots_schema_validity_and_category_isolation(self) -> None:
        for cat, shots in PER_CATEGORY_FEW_SHOTS.items():
            self.assertGreaterEqual(len(shots), 5, f"Category {cat} should have at least 5 few-shots")
            for shot in shots:
                validated = validate_response(shot["output"], cat, self.catalog, open_only=False)
                self.assertEqual(len(validated["filters"]), len(shot["output"]["filters"]))

            full_prompt = build_full_system_prompt(cat, self.catalog)
            open_prompt = build_open_system_prompt(cat, self.catalog)
            jev_payload, _ = closed_features_payload("test query", cat, self.catalog)
            jev_str = str(jev_payload)

            for shot in shots:
                self.assertIn(shot["query"], full_prompt)
                self.assertIn(shot["query"], open_prompt)
            for other_cat, other_shots in PER_CATEGORY_FEW_SHOTS.items():
                if other_cat == cat:
                    continue
                for other_shot in other_shots:
                    self.assertNotIn(other_shot["query"], full_prompt)
                    self.assertNotIn(other_shot["query"], open_prompt)
                    self.assertNotIn(other_shot["query"], jev_str)

    def test_zero_overlap_between_few_shots_and_all_benchmark_queries(self) -> None:
        all_bench = {
            normalize_query(row["query"])
            for rows in self.groups.values()
            for row in rows
        }
        for shot in CATEGORY_FEW_SHOTS:
            self.assertNotIn(
                normalize_query(shot["query"]),
                all_bench,
                f"Category few-shot overlaps with benchmark: {shot['query']}",
            )
        for cat, shots in PER_CATEGORY_FEW_SHOTS.items():
            for shot in shots:
                self.assertNotIn(
                    normalize_query(shot["query"]),
                    all_bench,
                    f"Per-category few-shot ({cat}) overlaps with benchmark: {shot['query']}",
                )

    def test_schemas_and_validation(self) -> None:
        for cat in self.catalog:
            c_schema = build_cerebras_full_schema(cat, self.catalog)
            v_schema = build_vertex_full_schema(cat, self.catalog)
            self.assertEqual(c_schema["type"], "object")
            self.assertEqual(v_schema["type"], "OBJECT")
        open_schema = build_cerebras_open_schema()
        self.assertEqual(len(open_schema["properties"]["filters"]["items"]["anyOf"]), 2)

        valid_full = validate_response(
            {
                "filters": [
                    {"feature": "colors", "operator": "equals_any_set", "values": ["Black"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                    {"feature": "price", "operator": "around", "value": 99.5},
                ],
                "residual": ["for running"],
            },
            "T-shirts",
            self.catalog,
        )
        self.assertEqual(valid_full["filters"][0]["operator"], "equals_set")

    def test_jev_payloads_and_answer_conversion(self) -> None:
        cp = category_payload("black tee")
        self.assertEqual(len(cp["questions"]["category"]["criteria"]), 23)
        fp, fmap = closed_features_payload("all-black cotton tee", "T-shirts", self.catalog)
        fake_answers = {qid: {"choice": "not_specified"} for qid in fp["questions"]}
        for qid, (feat, val) in fmap.items():
            if (feat, val) == ("colors", "Black"):
                fake_answers[qid] = {"choice": "requested"}
        fake_answers["colors_relation"] = {"choice": "EXACT"}
        fake_answers["main_composition_relation"] = {"choice": "ANY"}
        filters = filters_from_answers(fake_answers, "T-shirts", self.catalog, fmap)
        self.assertEqual(filters, [{"feature": "colors", "operator": "equals_set", "values": ["Black"]}])

    def test_evaluation_equivalence_and_metrics(self) -> None:
        c1 = canonicalize_clause({"feature": "colors", "operator": "equals_any_set", "values": ["Black"]})
        c2 = canonicalize_clause({"feature": "colors", "operator": "equals_set", "values": ["Black"]})
        self.assertEqual(c1, c2)

        colors = {"feature": "colors", "values": ["Black", "White"]}
        together = canonicalize_clause(dict(colors, operator="equals_set"))
        alternatives = canonicalize_clause(dict(colors, operator="equals_any_set"))
        self.assertNotEqual(together, alternatives)
        self.assertNotEqual(alternatives, canonicalize_clause(dict(colors, operator="contains_any")))

        b1 = canonicalize_filters([{"feature": "brand", "operator": "in", "values": ["adidas"]}])
        b2 = canonicalize_filters([{"feature": "brand", "operator": "in", "values": ["Adidas"]}])
        self.assertEqual(b1, b2)

        lat = summarize_latencies([0.5, 0.6, 0.8, 1.1])
        self.assertEqual(lat["under_0_7s"], 2)
        self.assertEqual(lat["under_1_0s"], 3)

    def test_config_resolution_and_required_stages(self) -> None:
        self.assertEqual(resolve_config_name("full_qwen"), "full_qwen")
        self.assertEqual(resolve_config_name("split_qwen"), "split_qwen")
        self.assertEqual(resolve_config_list(["all"]), list(CONFIGS.keys()))
        self.assertEqual(
            resolve_config_list(["full_qwen,split_qwen", "split_gpt_oss"]),
            ["full_qwen", "split_qwen", "split_gpt_oss"],
        )
        self.assertEqual(
            required_stages_for_configs(["full_qwen"]),
            {"category", "full_qwen"},
        )
        self.assertEqual(
            required_stages_for_configs(["split_qwen"]),
            {"category", "closed_features", "open_qwen"},
        )
        with self.assertRaises(ValueError):
            resolve_config_name("unknown_config")

    def test_parse_query_full_split_and_outside_category(self) -> None:
        fake_llm = _FakeLLMClient()
        parser_inst = QueryParser(
            catalog=self.catalog,
            jev_client=_FakeJevClient("T-shirts"),
            gemini_client=fake_llm,
            cerebras_clients={"qwen-3.8-27b": fake_llm, "gpt-oss-120b": fake_llm},
        )

        res_full = parse_query("black nike tee for gym", config="full_qwen", include_meta=True, parser=parser_inst)
        self.assertEqual(res_full["category"], "T-shirts")
        self.assertEqual(len(res_full["filters"]), 2)
        self.assertEqual(res_full["residual"], ["for gym"])
        self.assertEqual(res_full["_meta"]["config"], "full_qwen")
        self.assertAlmostEqual(res_full["_meta"]["total_latency_seconds"], 0.66, places=2)

        res_split = parse_query("black nike tee for gym", config="split_qwen", include_meta=True, extractor=parser_inst)
        self.assertEqual(res_split["category"], "T-shirts")
        self.assertEqual(
            res_split["filters"],
            [
                {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                {"feature": "brand", "operator": "in", "values": ["Nike"]},
            ],
        )
        self.assertEqual(res_split["_meta"]["config"], "split_qwen")
        self.assertAlmostEqual(res_split["_meta"]["total_latency_seconds"], 0.90, places=2)

        outside_parser = QueryParser(
            catalog=self.catalog,
            jev_client=_FakeJevClient("outside"),
        )
        res_out = parse_query("iphone 16 charger", config="full_qwen", parser=outside_parser)
        self.assertEqual(res_out, {"category": None, "filters": [], "residual": []})

    def test_dataset_loader(self) -> None:
        rows_30 = load_dataset_rows(size=30, seed=42)
        self.assertEqual(len(rows_30), 30)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_json = Path(tmpdir) / "custom_test.json"
            tmp_json.write_text(
                json.dumps(rows_30[:5], ensure_ascii=False),
                encoding="utf-8",
            )
            loaded_custom = load_dataset_rows(dataset_path=tmp_json, size=None)
            self.assertEqual(len(loaded_custom), 5)


if __name__ == "__main__":
    unittest.main()
