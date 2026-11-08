"""Offline unit tests for query extraction catalog, schemas, validators, and evaluation metrics."""

from __future__ import annotations

import unittest

from query_extraction.catalog import (
    CATEGORY_CRITERIA,
    EXCLUDED_FILTER_VALUES,
    build_cerebras_auxiliary_schema,
    build_cerebras_full_schema,
    build_vertex_full_schema,
    load_query_catalog,
    validate_response,
)
from query_extraction.evaluate import (
    canonicalize_clause,
    canonicalize_filters,
    evaluate_predictions,
    summarize_latencies,
)
from query_extraction.few_shots import CATEGORY_FEW_SHOTS, PER_CATEGORY_FEW_SHOTS
from query_extraction.jev_parser import (
    category_payload,
    feature_payload,
    filters_from_answers,
    normalize_query,
)
from query_extraction.llm_parser import (
    build_auxiliary_system_prompt,
    build_full_system_prompt,
)
from query_extraction.sample_queries import load_queries


class QueryExtractionOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_query_catalog()
        cls.groups = load_queries()

    def test_all_22_categories_covered_in_catalog_and_criteria(self) -> None:
        self.assertEqual(len(self.catalog), 22)
        self.assertEqual(set(self.catalog.keys()), set(CATEGORY_CRITERIA.keys()))
        self.assertEqual(set(self.catalog.keys()), set(PER_CATEGORY_FEW_SHOTS.keys()))
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

            # Verify all examples of this category appear in the prompts, and NO examples from other categories appear
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
        # 1-item contains_all normalizes to contains_any
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


if __name__ == "__main__":
    unittest.main()
