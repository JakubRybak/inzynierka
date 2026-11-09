"""Query extraction package: structured category, filter, and residual extraction from search queries."""

from __future__ import annotations

from .parser import (
    CONFIG_ALIASES,
    CONFIGS,
    DEFAULT_CONFIG,
    QueryExtractor,
    assemble_stage_prediction,
    get_default_extractor,
    parse_query,
    resolve_config_list,
    resolve_config_name,
)

__all__ = [
    "CONFIG_ALIASES",
    "CONFIGS",
    "DEFAULT_CONFIG",
    "QueryExtractor",
    "assemble_stage_prediction",
    "get_default_extractor",
    "parse_query",
    "resolve_config_list",
    "resolve_config_name",
]
