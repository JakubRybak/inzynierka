"""API clients and prompt/payload builders for Jev 1.14, Vertex AI Gemini, and Cerebras LLMs."""

from __future__ import annotations

from .jev import (
    JevCallResult,
    JevClient,
    build_closed_features_rules,
    build_jev_rules,
    category_payload,
    closed_features_payload,
    feature_payload,
    filters_from_answers,
    normalize_query,
)
from .llm import (
    GEMINI_MODEL,
    GPT_OSS_MODEL,
    QWEN_MODEL,
    CerebrasClient,
    LLMCallResult,
    VertexGeminiClient,
    build_auxiliary_system_prompt,
    build_auxiliary_user_message,
    build_full_system_prompt,
    build_full_user_message,
    build_open_system_prompt,
    build_open_user_message,
)

__all__ = [
    "CerebrasClient",
    "GEMINI_MODEL",
    "GPT_OSS_MODEL",
    "JevCallResult",
    "JevClient",
    "LLMCallResult",
    "QWEN_MODEL",
    "VertexGeminiClient",
    "build_auxiliary_system_prompt",
    "build_auxiliary_user_message",
    "build_closed_features_rules",
    "build_full_system_prompt",
    "build_full_user_message",
    "build_jev_rules",
    "build_open_system_prompt",
    "build_open_user_message",
    "category_payload",
    "closed_features_payload",
    "feature_payload",
    "filters_from_answers",
    "normalize_query",
]
