"""Few-shot examples for category classification and per-category feature extraction, loaded from YAML."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .prompts_loader import (
    load_category_classification_prompt,
    load_category_prompt_configs,
)

CATEGORY_FEW_SHOTS: List[Dict[str, Any]] = load_category_classification_prompt()["few_shots"]

PER_CATEGORY_FEW_SHOTS: Dict[str, List[Dict[str, Any]]] = {
    category: doc["few_shots"]
    for category, doc in load_category_prompt_configs().items()
}


def build_jev_feature_examples_json(
    category: str,
    feature: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Return compact JSON string of few-shot examples from `category` that mention `feature`."""
    shots = PER_CATEGORY_FEW_SHOTS.get(category, [])
    relevant: List[Dict[str, Any]] = []
    for item in shots:
        matching_clauses = [
            clause for clause in item["output"]["filters"] if clause["feature"] == feature
        ]
        if matching_clauses:
            relevant.append(
                {
                    "query": item["query"],
                    feature: matching_clauses,
                }
            )
    return json.dumps(relevant, ensure_ascii=False)
