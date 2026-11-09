"""Category catalog, feature definitions, structured output schemas, and validation for query extraction."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

from feature_extraction.schema import allowed_values, load_schemas

from .prompts_loader import (
    load_category_prompt_configs,
    load_common_features_prompt,
    load_step1_category_prompt,
)

ROOT = Path(__file__).resolve().parents[2]
LLM_PROMPTS_DIR = ROOT / "feature_extraction" / "llm" / "prompts"

EXCLUDED_FILTER_VALUES = {"Other", "Not Applicable", "Unknown"}
SINGLE_OPERATORS = ["in", "not_in"]
MULTI_OPERATORS = ["contains_any", "contains_all", "contains_none", "equals_set"]
PRICE_OPERATORS = ["lte", "gte", "around"]

CATEGORY_CRITERIA: Dict[str, str] = dict(load_step1_category_prompt()["categories"])
EXTRA_FEATURE_DEFINITIONS: Dict[str, Dict[str, Any]] = dict(
    load_common_features_prompt()["extra_definitions"]
)


def load_query_catalog() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Build the query-extraction catalog for all 22 categories from YAML prompt definitions."""
    schemas, _ = load_schemas()
    common_prompts = json.loads((LLM_PROMPTS_DIR / "common.json").read_text(encoding="utf-8"))
    cat_prompts: Dict[str, Dict[str, Any]] = {}
    for path in sorted((LLM_PROMPTS_DIR / "categories").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cat_prompts[data["category"]] = data["features"]

    common_feat_cfg = load_common_features_prompt()
    value_overrides: Dict[str, Dict[str, str]] = common_feat_cfg.get("value_overrides", {})
    common_notes: Dict[str, str] = common_feat_cfg.get("feature_notes", {})
    per_cat_cfgs = load_category_prompt_configs()

    catalog: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for (_section, category), schema in sorted(schemas.items(), key=lambda item: item[0][1]):
        cat_dict: Dict[str, Dict[str, Any]] = {}
        cat_cfg = per_cat_cfgs.get(category, {})
        cat_notes: Dict[str, str] = cat_cfg.get("feature_notes", {})

        for feature, spec in schema.items():
            values = [v for v in allowed_values(spec) if v not in EXCLUDED_FILTER_VALUES]
            multi = spec["type"] in ("multi_choice", "composition")
            operators = MULTI_OPERATORS if multi else SINGLE_OPERATORS

            if feature in common_prompts:
                prompt_def = common_prompts[feature]
            elif feature in cat_prompts.get(category, {}):
                prompt_def = cat_prompts[category][feature]
            elif feature == "fit" and set(values) == {"Oversized", "Regular"}:
                prompt_def = EXTRA_FEATURE_DEFINITIONS["outerwear_fit"]
            elif feature == "length" and set(values) == {"Mini", "Midi", "Maxi"}:
                prompt_def = EXTRA_FEATURE_DEFINITIONS["skirt_dress_length"]
            else:
                prompt_def = EXTRA_FEATURE_DEFINITIONS[feature]

            val_descriptions = {
                v: prompt_def["values"].get(v, v)
                for v in values
            }
            if feature in value_overrides:
                for over_val, over_desc in value_overrides[feature].items():
                    if over_val in val_descriptions:
                        val_descriptions[over_val] = over_desc

            lines = [prompt_def["instruction"]]
            for v in values:
                lines.append(f"- {v}: {val_descriptions[v]}")

            # Add category-specific or common query extraction notes from YAML
            if feature in cat_notes:
                lines.append(cat_notes[feature])
            elif feature == "insulation" and "insulation" in common_notes:
                lines.append(common_notes["insulation"])
            elif feature == "leg_shape" and "Flared" in values and "leg_shape_flared" in common_notes:
                lines.append(common_notes["leg_shape_flared"])
            elif feature == "neckline" and "High Neck" in values and "neckline_high_neck" in common_notes:
                lines.append(common_notes["neckline_high_neck"])
            elif feature == "colors" and "colors" in common_notes:
                lines.append(common_notes["colors"])

            cat_dict[feature] = {
                "values": values,
                "multi": multi,
                "operators": operators,
                "instruction": prompt_def["instruction"],
                "value_descriptions": val_descriptions,
                "definition": "\n".join(lines),
            }
        catalog[category] = cat_dict
    return catalog


def build_cerebras_full_schema(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Build strict JSON schema (draft-07/OpenAI style) for full Step 2a extraction."""
    branches: List[Dict[str, Any]] = [
        {
            "type": "object",
            "properties": {
                "feature": {"type": "string", "enum": ["price"]},
                "operator": {"type": "string", "enum": PRICE_OPERATORS},
                "value": {"type": "number"},
            },
            "required": ["feature", "operator", "value"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "feature": {"type": "string", "enum": ["brand"]},
                "operator": {"type": "string", "enum": SINGLE_OPERATORS},
                "values": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["feature", "operator", "values"],
            "additionalProperties": False,
        },
    ]
    for feature, spec in catalog[category].items():
        branches.append(
            {
                "type": "object",
                "properties": {
                    "feature": {"type": "string", "enum": [feature]},
                    "operator": {"type": "string", "enum": spec["operators"]},
                    "values": {"type": "array", "items": {"type": "string", "enum": spec["values"]}},
                },
                "required": ["feature", "operator", "values"],
                "additionalProperties": False,
            }
        )
    return {
        "type": "object",
        "properties": {
            "filters": {"type": "array", "items": {"anyOf": branches}},
            "residual": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["filters", "residual"],
        "additionalProperties": False,
    }


def build_vertex_full_schema(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Build Vertex AI responseSchema for full Step 2a extraction."""
    branches: List[Dict[str, Any]] = [
        {
            "type": "OBJECT",
            "properties": {
                "feature": {"type": "STRING", "enum": ["price"]},
                "operator": {"type": "STRING", "enum": PRICE_OPERATORS},
                "value": {"type": "NUMBER", "minimum": 0},
            },
            "required": ["feature", "operator", "value"],
            "propertyOrdering": ["feature", "operator", "value"],
        },
        {
            "type": "OBJECT",
            "properties": {
                "feature": {"type": "STRING", "enum": ["brand"]},
                "operator": {"type": "STRING", "enum": SINGLE_OPERATORS},
                "values": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 1},
            },
            "required": ["feature", "operator", "values"],
            "propertyOrdering": ["feature", "operator", "values"],
        },
    ]
    for feature, spec in catalog[category].items():
        branches.append(
            {
                "type": "OBJECT",
                "properties": {
                    "feature": {"type": "STRING", "enum": [feature]},
                    "operator": {"type": "STRING", "enum": spec["operators"]},
                    "values": {
                        "type": "ARRAY",
                        "items": {"type": "STRING", "enum": spec["values"]},
                        "minItems": 1,
                    },
                },
                "required": ["feature", "operator", "values"],
                "propertyOrdering": ["feature", "operator", "values"],
            }
        )
    return {
        "type": "OBJECT",
        "properties": {
            "filters": {"type": "ARRAY", "items": {"anyOf": branches}},
            "residual": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["filters", "residual"],
        "propertyOrdering": ["filters", "residual"],
    }


def build_cerebras_auxiliary_schema() -> Dict[str, Any]:
    """Build strict JSON schema for Step 2b-2 auxiliary extraction (brand, price, residual only)."""
    return {
        "type": "object",
        "properties": {
            "filters": {
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "enum": ["price"]},
                                "operator": {"type": "string", "enum": PRICE_OPERATORS},
                                "value": {"type": "number"},
                            },
                            "required": ["feature", "operator", "value"],
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "enum": ["brand"]},
                                "operator": {"type": "string", "enum": SINGLE_OPERATORS},
                                "values": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["feature", "operator", "values"],
                            "additionalProperties": False,
                        },
                    ]
                },
            },
            "residual": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["filters", "residual"],
        "additionalProperties": False,
    }


def validate_response(
    data: Any,
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
    *,
    auxiliary_only: bool = False,
) -> Dict[str, Any]:
    """Validate and normalize structured LLM output."""
    if not isinstance(data, dict) or set(data.keys()) != {"filters", "residual"}:
        raise ValueError(f"Expected root keys {{'filters', 'residual'}}, got {list(data) if isinstance(data, dict) else type(data)}")
    if not isinstance(data["filters"], list):
        raise ValueError("filters must be a list")
    if not isinstance(data["residual"], list) or not all(isinstance(x, str) for x in data["residual"]):
        raise ValueError("residual must be a list of strings")

    cat_spec = catalog[category]
    cleaned_filters: List[Dict[str, Any]] = []
    for clause in data["filters"]:
        if not isinstance(clause, dict):
            raise ValueError("Filter clause must be a dict")
        feat = clause.get("feature")
        op = clause.get("operator")
        if feat == "price":
            val = clause.get("value")
            if (
                set(clause.keys()) != {"feature", "operator", "value"}
                or op not in PRICE_OPERATORS
                or type(val) not in (int, float)
                or not math.isfinite(val)
                or val < 0
            ):
                raise ValueError(f"Invalid price filter: {clause!r}")
            cleaned_filters.append({"feature": "price", "operator": op, "value": int(val) if float(val).is_integer() else float(val)})
        elif feat == "brand":
            vals = clause.get("values")
            if (
                set(clause.keys()) != {"feature", "operator", "values"}
                or op not in SINGLE_OPERATORS
                or not isinstance(vals, list)
                or not vals
                or not all(isinstance(v, str) and v.strip() for v in vals)
            ):
                raise ValueError(f"Invalid brand filter: {clause!r}")
            dedup = list(dict.fromkeys(v.strip() for v in vals))
            cleaned_filters.append({"feature": "brand", "operator": op, "values": dedup})
        else:
            if auxiliary_only:
                raise ValueError(f"Auxiliary parser returned non-auxiliary feature: {feat!r}")
            if feat not in cat_spec:
                raise ValueError(f"Unsupported feature {feat!r} for category {category!r}")
            spec = cat_spec[feat]
            vals = clause.get("values")
            if (
                set(clause.keys()) != {"feature", "operator", "values"}
                or op not in spec["operators"]
                or not isinstance(vals, list)
                or not vals
                or not all(isinstance(v, str) and v in spec["values"] for v in vals)
            ):
                raise ValueError(f"Invalid categorical filter for {category}: {clause!r}")
            dedup = list(dict.fromkeys(vals))
            if op == "contains_all" and len(dedup) == 1:
                op = "contains_any"
            cleaned_filters.append({"feature": feat, "operator": op, "values": dedup})

    cleaned_residual = [item.strip() for item in data["residual"] if item and item.strip()]
    return {"filters": cleaned_filters, "residual": cleaned_residual}
