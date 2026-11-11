"""Core domain definitions: category/feature catalog, JSON schemas, validators, and YAML prompt loaders."""

from __future__ import annotations

from .catalog import (
    CATEGORY_CRITERIA,
    EXCLUDED_FILTER_VALUES,
    build_cerebras_auxiliary_schema,
    build_cerebras_full_schema,
    build_cerebras_open_schema,
    build_vertex_full_schema,
    load_query_catalog,
    validate_response,
)
from .few_shots import (
    CATEGORY_FEW_SHOTS,
    PER_CATEGORY_FEW_SHOTS,
    build_jev_feature_examples_json,
)
from .prompts_loader import (
    CATEGORIES_PROMPTS_DIR,
    PROMPTS_DIR,
    load_category_classification_prompt,
    load_category_prompt_configs,
    load_closed_features_prompt,
    load_feature_definitions_prompt,
    load_full_extraction_prompt,
    load_open_extraction_prompt,
)

__all__ = [
    "CATEGORIES_PROMPTS_DIR",
    "CATEGORY_CRITERIA",
    "CATEGORY_FEW_SHOTS",
    "EXCLUDED_FILTER_VALUES",
    "PER_CATEGORY_FEW_SHOTS",
    "PROMPTS_DIR",
    "build_cerebras_auxiliary_schema",
    "build_cerebras_full_schema",
    "build_cerebras_open_schema",
    "build_jev_feature_examples_json",
    "build_vertex_full_schema",
    "load_category_classification_prompt",
    "load_category_prompt_configs",
    "load_closed_features_prompt",
    "load_feature_definitions_prompt",
    "load_full_extraction_prompt",
    "load_open_extraction_prompt",
    "load_query_catalog",
    "validate_response",
]
