"""Offline unit tests for query extraction API, catalog, schemas, validators, dataset loader, and reporting."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from query_extraction import (
    CONFIGS,
    QueryExtractor,
    parse_query,
    resolve_config_list,
    resolve_config_name,
)
from query_extraction.benchmark import (
    DEFAULT_INPUT,
    canonicalize_clause,
    canonicalize_filters,
    generate_markdown,
    load_dataset_rows,
    load_queries,
    required_stages_for_configs,
    summarize_latencies,
)
from query_extraction.clients import (
    JevCallResult,
    LLMCallResult,
    build_auxiliary_system_prompt,
    build_full_system_prompt,
    category_payload,
    feature_payload,
    filters_from_answers,
    normalize_query,
)
from query_extraction.core import (
    CATEGORIES_PROMPTS_DIR,
    CATEGORY_CRITERIA,
    CATEGORY_FEW_SHOTS,
    EXCLUDED_FILTER_VALUES,
    PER_CATEGORY_FEW_SHOTS,
    PROMPTS_DIR,
    build_cerebras_auxiliary_schema,
    build_cerebras_full_schema,
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
                    {"feature": "colors", "operator": "contains_any", "values": ["Black"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                ],
                "residual": ["for gym"],
            },
            latency_seconds=0.45,
            cost_usd=0.0002,
            model="fake",
            usage={},
        )

    def extract_auxiliary(
        self, query: str, category: str, jev_filters: list, catalog: dict
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


class QueryExtractionOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_query_catalog()
        cls.groups = load_queries()

    def test_all_22_categories_covered_in_catalog_and_criteria(self) -> None:
        self.assertEqual(len(self.catalog), 22)
        self.assertEqual(len(list(CATEGORIES_PROMPTS_DIR.glob("*.yaml"))), 22)
        self.assertTrue((PROMPTS_DIR / "step1_category.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "common_features.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "step2a_full.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "step2b_jev_features.yaml").exists())
        self.assertTrue((PROMPTS_DIR / "step2b_auxiliary.yaml").exists())
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
                validated = validate_response(shot["output"], cat, self.catalog, auxiliary_only=False)
                self.assertEqual(len(validated["filters"]), len(shot["output"]["filters"]))

            full_prompt = build_full_system_prompt(cat, self.catalog)
            aux_prompt = build_auxiliary_system_prompt(cat, self.catalog)
            jev_payload, _ = feature_payload("test query", cat, self.catalog)
            jev_str = str(jev_payload)

            for shot in shots:
                self.assertIn(shot["query"], full_prompt)
                self.assertIn(shot["query"], aux_prompt)
            for other_cat, other_shots in PER_CATEGORY_FEW_SHOTS.items():
                if other_cat == cat:
                    continue
                for other_shot in other_shots:
                    self.assertNotIn(other_shot["query"], full_prompt)
                    self.assertNotIn(other_shot["query"], aux_prompt)
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
        aux_schema = build_cerebras_auxiliary_schema()
        self.assertEqual(len(aux_schema["properties"]["filters"]["items"]["anyOf"]), 2)

        valid_full = validate_response(
            {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                    {"feature": "price", "operator": "around", "value": 99.5},
                ],
                "residual": ["for running"],
            },
            "T-shirts",
            self.catalog,
        )
        self.assertEqual(valid_full["filters"][0]["operator"], "contains_any")

    def test_jev_payloads_and_answer_conversion(self) -> None:
        cp = category_payload("black tee")
        self.assertEqual(len(cp["questions"]["category"]["criteria"]), 23)
        fp, fmap = feature_payload("all-black cotton tee", "T-shirts", self.catalog)
        fake_answers = {qid: {"choice": "not_specified"} for qid in fp["questions"]}
        for qid, (feat, val) in fmap.items():
            if (feat, val) == ("colors", "Black"):
                fake_answers[qid] = {"choice": "requested"}
        fake_answers["colors_relation"] = {"choice": "EXACT"}
        fake_answers["main_composition_relation"] = {"choice": "ANY"}
        filters = filters_from_answers(fake_answers, "T-shirts", self.catalog, fmap)
        self.assertEqual(filters, [{"feature": "colors", "operator": "equals_set", "values": ["Black"]}])

    def test_evaluation_equivalence_and_metrics(self) -> None:
        c1 = canonicalize_clause({"feature": "colors", "operator": "contains_all", "values": ["Black"]})
        c2 = canonicalize_clause({"feature": "colors", "operator": "contains_any", "values": ["Black"]})
        self.assertEqual(c1, c2)

        b1 = canonicalize_filters([{"feature": "brand", "operator": "in", "values": ["adidas"]}])
        b2 = canonicalize_filters([{"feature": "brand", "operator": "in", "values": ["Adidas"]}])
        self.assertEqual(b1, b2)

        lat = summarize_latencies([0.5, 0.6, 0.8, 1.1])
        self.assertEqual(lat["under_0_7s"], 2)
        self.assertEqual(lat["under_1_0s"], 3)

    def test_config_resolution_and_required_stages(self) -> None:
        self.assertEqual(resolve_config_name("2a_qwen"), "2a_qwen")
        self.assertEqual(resolve_config_name("2a_qwen_3_8_27b"), "2a_qwen")
        self.assertEqual(resolve_config_name("2b_jev_qwen_3_8_27b"), "2b_qwen")
        self.assertEqual(resolve_config_list(["all"]), list(CONFIGS.keys()))
        self.assertEqual(
            resolve_config_list(["2a_qwen,2b_qwen", "2a_qwen_3_8_27b"]),
            ["2a_qwen", "2b_qwen"],
        )
        self.assertEqual(
            required_stages_for_configs(["2a_qwen"]),
            {"jev_category", "2a_qwen"},
        )
        self.assertEqual(
            required_stages_for_configs(["2b_qwen"]),
            {"jev_category", "jev_features", "2b_qwen_aux"},
        )
        with self.assertRaises(ValueError):
            resolve_config_name("unknown_config")

    def test_parse_query_2a_2b_and_outside_category(self) -> None:
        fake_llm = _FakeLLMClient()
        extractor = QueryExtractor(
            catalog=self.catalog,
            jev_client=_FakeJevClient("T-shirts"),
            gemini_client=fake_llm,
            cerebras_clients={"qwen-3.8-27b": fake_llm, "gpt-oss-120b": fake_llm},
        )

        res_2a = parse_query("black nike tee for gym", config="2a_qwen", include_meta=True, extractor=extractor)
        self.assertEqual(res_2a["category"], "T-shirts")
        self.assertEqual(len(res_2a["filters"]), 2)
        self.assertEqual(res_2a["residual"], ["for gym"])
        self.assertEqual(res_2a["_meta"]["config"], "2a_qwen")
        self.assertAlmostEqual(res_2a["_meta"]["total_latency_seconds"], 0.66, places=2)

        res_2b = parse_query("black nike tee for gym", config="2b_qwen", include_meta=True, extractor=extractor)
        self.assertEqual(res_2b["category"], "T-shirts")
        self.assertEqual(
            res_2b["filters"],
            [
                {"feature": "colors", "operator": "contains_any", "values": ["Black"]},
                {"feature": "brand", "operator": "in", "values": ["Nike"]},
            ],
        )
        self.assertEqual(res_2b["_meta"]["config"], "2b_qwen")
        self.assertAlmostEqual(res_2b["_meta"]["total_latency_seconds"], 0.90, places=2)

        outside_extractor = QueryExtractor(
            catalog=self.catalog,
            jev_client=_FakeJevClient("outside"),
        )
        res_out = parse_query("iphone 16 charger", config="2a_qwen", extractor=outside_extractor)
        self.assertEqual(res_out, {"category": None, "filters": [], "residual": []})

    def test_dataset_loader_and_dynamic_report_generation(self) -> None:
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

        if DEFAULT_INPUT.exists():
            data = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
            md_all = generate_markdown(data)
            self.assertIn("`2a_qwen`", md_all)
            self.assertIn("`2b_qwen`", md_all)

            md_subset = generate_markdown(data, configs=["2a_qwen", "2b_qwen"])
            self.assertIn("`2a_qwen`", md_subset)
            self.assertIn("`2b_qwen`", md_subset)
            self.assertNotIn("`2a_gemini`", md_subset)


if __name__ == "__main__":
    unittest.main()
