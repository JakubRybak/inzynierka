"""YAML prompt and few-shot loader for query_parsing."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
CATEGORIES_PROMPTS_DIR = PROMPTS_DIR / "categories"


def _read_yaml(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


@lru_cache(maxsize=1)
def load_category_classification_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "category_classification.yaml")


@lru_cache(maxsize=1)
def load_feature_definitions_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "feature_definitions.yaml")


@lru_cache(maxsize=1)
def load_full_extraction_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "full_extraction.yaml")


@lru_cache(maxsize=1)
def load_category_prompt_configs() -> Dict[str, Dict[str, Any]]:
    configs: Dict[str, Dict[str, Any]] = {}
    for path in sorted(CATEGORIES_PROMPTS_DIR.glob("*.yaml")):
        doc = _read_yaml(path)
        category = doc["category"]
        configs[category] = doc
    return configs
