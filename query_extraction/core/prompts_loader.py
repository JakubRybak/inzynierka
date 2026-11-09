"""YAML prompt and few-shot loader for query_extraction."""

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
def load_step1_category_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "step1_category.yaml")


@lru_cache(maxsize=1)
def load_common_features_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "common_features.yaml")


@lru_cache(maxsize=1)
def load_step2a_full_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "step2a_full.yaml")


@lru_cache(maxsize=1)
def load_step2b_jev_features_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "step2b_jev_features.yaml")


@lru_cache(maxsize=1)
def load_step2b_auxiliary_prompt() -> Dict[str, Any]:
    return _read_yaml(PROMPTS_DIR / "step2b_auxiliary.yaml")


@lru_cache(maxsize=1)
def load_category_prompt_configs() -> Dict[str, Dict[str, Any]]:
    configs: Dict[str, Dict[str, Any]] = {}
    for path in sorted(CATEGORIES_PROMPTS_DIR.glob("*.yaml")):
        doc = _read_yaml(path)
        category = doc["category"]
        configs[category] = doc
    return configs
