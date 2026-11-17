"""Few-shot examples for category classification and per-category feature extraction, loaded from YAML."""

from __future__ import annotations

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
