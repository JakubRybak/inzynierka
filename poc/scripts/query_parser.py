#!/usr/bin/env python3
"""
Query Parsing Engine for Fashion Search.

Performs two-step semantic query parsing:
  Step 1: Category Classification (T-shirts, Dresses, Tank tops & Camisoles, or null)
  Step 2: Category-Specific Feature Extraction (filters with exact operators and residual text)

Configurable model: defaults to 'gemini-3.5-flash-lite' on Google Cloud Vertex AI.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional, Union

import google.auth
from google.auth.transport.requests import AuthorizedSession, Request

# Paths
ROOT = Path(__file__).resolve().parents[2]
QUERY_PARSING_DIR = ROOT / "poc/query_parsing"
PROMPTS_DIR = QUERY_PARSING_DIR / "prompts"
SCHEMAS_DIR = QUERY_PARSING_DIR / "schemas"

# Default GCP settings
DEFAULT_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "project-3a86f100-1aae-4780-84b")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
DEFAULT_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
DEFAULT_THINKING = os.environ.get("GEMINI_THINKING", "NONE")  # NONE, LOW, MEDIUM, HIGH

# Rates per million tokens for Gemini 3.5 Flash-Lite
INPUT_RATE = 0.30 / 1_000_000
OUTPUT_RATE = 2.50 / 1_000_000

SUPPORTED_CATEGORIES = ("T-shirts", "Dresses", "Tank tops & Camisoles")

CATEGORY_FILE_MAP = {
    "T-shirts": "t-shirts",
    "Dresses": "dresses",
    "Tank tops & Camisoles": "tank-tops-and-camisoles",
}


@dataclass
class FilterClause:
    feature: str
    operator: str
    values: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PriceFilterClause:
    feature: str
    operator: str
    value: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedQuery:
    query: str
    category: Optional[str]
    filters: List[Union[FilterClause, PriceFilterClause]] = field(default_factory=list)
    residual: List[str] = field(default_factory=list)
    step1_latency_seconds: float = 0.0
    step2_latency_seconds: float = 0.0
    total_latency_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "category": self.category,
            "filters": [f.to_dict() for f in self.filters],
            "residual": self.residual,
            "step1_latency_seconds": round(self.step1_latency_seconds, 3),
            "step2_latency_seconds": round(self.step2_latency_seconds, 3),
            "total_latency_seconds": round(self.total_latency_seconds, 3),
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def summary(self) -> str:
        lines = [
            f"Query: \"{self.query}\"",
            f"Category: {self.category or 'None (Out of catalog / unsupported)'}",
        ]
        if self.filters:
            lines.append("Filters:")
            for f in self.filters:
                value = f.value if isinstance(f, PriceFilterClause) else f.values
                lines.append(f"  • {f.feature} {f.operator} {value}")
        else:
            lines.append("Filters: None")
        lines.append(f"Residual: \"{self.residual}\"")
        step2_info = (
            f"{self.step2_latency_seconds:.2f}s" if self.category else "skipped"
        )
        lines.append(
            f"Latency: Total {self.total_latency_seconds:.2f}s "
            f"(Step 1: {self.step1_latency_seconds:.2f}s, Step 2: {step2_info})"
        )
        if self.metadata:
            cost = self.metadata.get("estimated_cost_usd", 0)
            model = self.metadata.get("model", "")
            thinking = self.metadata.get("thinking", "NONE")
            lines.append(f"Model: {model} | Thinking: {thinking} | Est. Cost: ${cost:.6f}")
        return "\n".join(lines)


def _extract_code_blocks(markdown_text: str) -> List[str]:
    """Extract code block contents (fenced with ``` or ```text)."""
    return re.findall(r"```(?:text)?\n(.*?)```", markdown_text, re.DOTALL)


class QueryParser:
    """Two-step fashion shopping query parser using Gemini structured output."""

    def __init__(
        self,
        project: str = DEFAULT_PROJECT,
        model: str = DEFAULT_MODEL,
        location: str = DEFAULT_LOCATION,
        thinking: str = DEFAULT_THINKING,
        timeout: float = 30.0,
    ):
        self.project = project
        self.model = model
        self.location = location
        self.thinking = thinking.upper()
        self.timeout = timeout
        self._session: Optional[AuthorizedSession] = None
        self._load_prompts_and_schemas()

    def _load_prompts_and_schemas(self) -> None:
        """Load and cache prompt templates and JSON schemas."""
        # Step 1: Category extraction
        cat_prompt_path = PROMPTS_DIR / "category.md"
        cat_blocks = _extract_code_blocks(cat_prompt_path.read_text(encoding="utf-8"))
        if not cat_blocks:
            raise ValueError(f"No fenced code blocks found in {cat_prompt_path}")
        self.category_system_instruction = cat_blocks[0].strip()
        self.category_schema = json.loads(
            (SCHEMAS_DIR / "category.json").read_text(encoding="utf-8")
        )

        # Step 2: Category-specific feature prompts & schemas
        self.feature_prompts: Dict[str, str] = {}
        self.feature_schemas: Dict[str, Dict[str, Any]] = {}
        for cat, slug in CATEGORY_FILE_MAP.items():
            prompt_path = PROMPTS_DIR / f"{slug}.md"
            blocks = _extract_code_blocks(prompt_path.read_text(encoding="utf-8"))
            if len(blocks) < 2:
                raise ValueError(f"Expected at least 2 fenced code blocks in {prompt_path}")
            # Block 0 is user-message template, block 1 is system instruction with few-shots
            self.feature_prompts[cat] = blocks[1].strip()
            self.feature_schemas[cat] = json.loads(
                (SCHEMAS_DIR / f"{slug}.json").read_text(encoding="utf-8")
            )

    @property
    def session(self) -> AuthorizedSession:
        """Lazily initialize Google Cloud AuthorizedSession."""
        if self._session is None:
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
                quota_project_id=self.project,
            )
            credentials.refresh(Request())
            self._session = AuthorizedSession(
                credentials.with_quota_project(self.project),
                max_refresh_attempts=1,
            )
        return self._session

    @property
    def endpoint(self) -> str:
        return (
            f"https://aiplatform.googleapis.com/v1/projects/{self.project}/"
            f"locations/{self.location}/publishers/google/models/{self.model}:generateContent"
        )

    def _call_api(
        self, system_instruction: str, user_content: str, response_schema: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
        """Make a structured output generateContent request to Vertex AI."""
        gen_config: Dict[str, Any] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
            "temperature": 0.0,
        }
        if self.thinking and self.thinking != "NONE":
            gen_config["thinkingConfig"] = {"thinkingLevel": self.thinking}

        body = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_content}]}],
            "generationConfig": gen_config,
        }
        start = time.perf_counter()
        resp = self.session.post(self.endpoint, json=body, timeout=self.timeout)
        latency = time.perf_counter() - start

        if not resp.ok:
            raise RuntimeError(
                f"Vertex AI HTTP {resp.status_code} ({resp.reason}): {resp.text[:600]}"
            )

        resp_json = resp.json()
        candidates = resp_json.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned by model")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        if not text.strip():
            raise ValueError("Model returned empty response text")

        parsed = json.loads(text)
        usage = resp_json.get("usageMetadata", {})
        return parsed, usage, latency

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a fashion search query in two sequential steps.

        Args:
            query: The user's input search string.

        Returns:
            ParsedQuery with category, structured filters, residual phrase, and metadata.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            return ParsedQuery(
                query=query,
                category=None,
                filters=[],
                residual=[],
                step1_latency_seconds=0.0,
                step2_latency_seconds=0.0,
                total_latency_seconds=0.0,
                metadata={"error": "Empty query"},
            )

        total_start = time.perf_counter()
        meta: Dict[str, Any] = {
            "model": self.model,
            "project": self.project,
            "location": self.location,
            "thinking": self.thinking,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        # Step 1: Category classification
        step1_res, step1_usage, step1_latency = self._call_api(
            system_instruction=self.category_system_instruction,
            user_content=cleaned_query,
            response_schema=self.category_schema,
        )
        meta["step1"] = {
            "latency_seconds": step1_latency,
            "usage": step1_usage,
            "raw_output": step1_res,
        }

        raw_category = step1_res.get("category")
        if raw_category not in SUPPORTED_CATEGORIES:
            total_latency = time.perf_counter() - total_start
            cost = (
                step1_usage.get("promptTokenCount", 0) * INPUT_RATE
                + step1_usage.get("candidatesTokenCount", 0) * OUTPUT_RATE
            )
            meta["total_latency_seconds"] = total_latency
            meta["estimated_cost_usd"] = cost
            # When category is null, no catalog filters are extracted
            return ParsedQuery(
                query=cleaned_query,
                category=None,
                filters=[],
                residual=[cleaned_query],
                step1_latency_seconds=step1_latency,
                step2_latency_seconds=0.0,
                total_latency_seconds=total_latency,
                metadata=meta,
            )

        selected_category = raw_category

        # Step 2: Feature extraction for selected category
        step2_user_msg = f"Category: {selected_category}\nQuery: {cleaned_query}"
        step2_res, step2_usage, step2_latency = self._call_api(
            system_instruction=self.feature_prompts[selected_category],
            user_content=step2_user_msg,
            response_schema=self.feature_schemas[selected_category],
        )
        meta["step2"] = {
            "latency_seconds": step2_latency,
            "usage": step2_usage,
            "raw_output": step2_res,
        }

        # Local validation & normalization of filters
        validated_filters: List[Union[FilterClause, PriceFilterClause]] = []
        raw_filters = step2_res.get("filters", [])
        for f in raw_filters:
            feat = f.get("feature")
            op = f.get("operator")
            if feat == "price":
                value = f.get("value")
                if (set(f) != {"feature", "operator", "value"}
                        or op not in {"lt", "lte", "gt", "gte", "eq"}
                        or type(value) not in (int, float)
                        or not math.isfinite(value) or value < 0):
                    raise ValueError(f"Invalid price filter: {f!r}")
                validated_filters.append(PriceFilterClause(feature=feat, operator=op, value=value))
                continue
            vals = f.get("values", [])
            if not feat or not op or not vals:
                continue
            # Deduplicate values preserving order
            unique_vals = list(dict.fromkeys(str(v).strip() for v in vals if str(v).strip()))
            if unique_vals:
                validated_filters.append(
                    FilterClause(feature=feat, operator=op, values=unique_vals)
                )

        raw_residual = step2_res.get("residual")
        if not isinstance(raw_residual, list) or any(not isinstance(item, str) or not item.strip() for item in raw_residual):
            raise ValueError("residual must be a list of nonempty strings")
        residual = list(dict.fromkeys(item.strip() for item in raw_residual))

        # Aggregate metrics
        total_latency = time.perf_counter() - total_start
        total_input_tokens = step1_usage.get("promptTokenCount", 0) + step2_usage.get(
            "promptTokenCount", 0
        )
        total_output_tokens = (
            step1_usage.get("candidatesTokenCount", 0)
            + step1_usage.get("thoughtsTokenCount", 0)
            + step2_usage.get("candidatesTokenCount", 0)
            + step2_usage.get("thoughtsTokenCount", 0)
        )
        total_cost = total_input_tokens * INPUT_RATE + total_output_tokens * OUTPUT_RATE

        meta["total_latency_seconds"] = total_latency
        meta["total_tokens"] = {
            "input": total_input_tokens,
            "output": total_output_tokens,
            "total": total_input_tokens + total_output_tokens,
        }
        meta["estimated_cost_usd"] = total_cost

        return ParsedQuery(
            query=cleaned_query,
            category=selected_category,
            filters=validated_filters,
            residual=residual,
            step1_latency_seconds=step1_latency,
            step2_latency_seconds=step2_latency,
            total_latency_seconds=total_latency,
            metadata=meta,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Fashion search query parsing engine using Gemini Vertex AI."
    )
    parser.add_argument("query", nargs="?", help="Shopping query to parse")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model identifier on Vertex AI (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help=f"Google Cloud Project ID (default: {DEFAULT_PROJECT})",
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION,
        help=f"GCP Location (default: {DEFAULT_LOCATION})",
    )
    parser.add_argument(
        "--thinking",
        default=DEFAULT_THINKING,
        choices=["NONE", "LOW", "MEDIUM", "HIGH", "none", "low", "medium", "high"],
        help=f"Thinking level for reasoning (default: {DEFAULT_THINKING})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output raw JSON instead of human-readable summary",
    )
    args = parser.parse_args()

    engine = QueryParser(
        project=args.project,
        model=args.model,
        location=args.location,
        thinking=args.thinking,
    )

    if args.query:
        result = engine.parse(args.query)
        if args.output_json:
            print(result.to_json())
        else:
            print(result.summary())
        return

    # Interactive loop if no query provided
    print(f"Fashion Query Parser Engine [{args.model}]")
    print("Type a query (e.g. 'czarna sukienka na wesele', 'black Nike t-shirt') or 'exit' to quit.\n")
    while True:
        try:
            user_input = input("Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input or user_input.lower() in ("exit", "quit", "q"):
            break
        result = engine.parse(user_input)
        if args.output_json:
            print(result.to_json())
        else:
            print("-" * 50)
            print(result.summary())
            print("-" * 50)


if __name__ == "__main__":
    main()
