"""LLM clients (Vertex AI Gemini 3.5 Flash-Lite & Cerebras Qwen 3.8 27B / GPT-OSS-120B) and YAML prompt builders."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional

import google.auth
from google.auth.transport.requests import AuthorizedSession, Request
import requests

from ..core.catalog import (
    build_cerebras_full_schema,
    build_cerebras_open_schema,
    build_vertex_full_schema,
    validate_response,
)
from ..core.few_shots import PER_CATEGORY_FEW_SHOTS
from ..core.prompts_loader import (
    load_category_prompt_configs,
    load_feature_definitions_prompt,
    load_full_extraction_prompt,
    load_open_extraction_prompt,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "project-3a86f100-1aae-4780-84b")
DEFAULT_GCP_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
GEMINI_MODEL = "gemini-3.5-flash-lite"

CEREBRAS_ENDPOINT = "https://api.cerebras.ai/v1/chat/completions"
QWEN_MODEL = "qwen-3.8-27b"
GPT_OSS_MODEL = "gpt-oss-120b"

# Pricing per 1M tokens (USD)
PRICING = {
    "gemini-3.5-flash-lite": (0.30 / 1_000_000, 2.50 / 1_000_000),
    "qwen-3.8-27b": (0.30 / 1_000_000, 0.60 / 1_000_000),
    "gpt-oss-120b": (0.25 / 1_000_000, 0.69 / 1_000_000),
}


def _category_narrow_substyle_rules(category: str, cat_features: Dict[str, Dict[str, Any]]) -> List[str]:
    """Return narrow sub-style residual rules strictly applicable to `category` from YAML."""
    sub_cfg = load_feature_definitions_prompt()["substyle_rules"]
    cat_sub_rules = load_category_prompt_configs().get(category, {}).get("substyle_rules", [])

    rules: List[str] = list(sub_cfg.get("always", []))
    by_feat = sub_cfg.get("by_feature_value", [])

    for cond in by_feat:
        feat = cond["feature"]
        val = cond["value"]
        if feat == "neckline" and feat in cat_features and (val is None or val in cat_features[feat]["values"]):
            rules.append(cond["rule"])

    if category in ("Shirts", "Classic Coats"):
        rules.extend(cat_sub_rules)

    for cond in by_feat:
        feat = cond["feature"]
        val = cond["value"]
        if feat != "neckline" and feat in cat_features and (val is None or val in cat_features[feat]["values"]):
            rules.append(cond["rule"])

    if category not in ("Shirts", "Classic Coats"):
        rules.extend(cat_sub_rules)

    return rules


def build_full_system_prompt(
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Build a full_extraction system prompt strictly scoped to `category` from YAML."""
    full_cfg = load_full_extraction_prompt()
    cat_spec = catalog[category]
    single_feats = [f for f, s in cat_spec.items() if not s["multi"]]
    multi_feats = [f for f, s in cat_spec.items() if s["multi"]]

    defs = []
    for feature, spec in cat_spec.items():
        op_kind = "multi-choice / composition" if spec["multi"] else "single-choice"
        defs.append(f"### {feature} ({op_kind}; operators: {', '.join(spec['operators'])})\n{spec['definition']}")
    defs_text = "\n\n".join(defs)

    equals_set_examples = full_cfg["equals_set_base"]
    if "lining_composition" in cat_spec:
        equals_set_examples += full_cfg["equals_set_lining_suffix"]

    substyle_lines = "\n".join(_category_narrow_substyle_rules(category, cat_spec))
    shots = PER_CATEGORY_FEW_SHOTS[category]
    examples_text = "\n".join(
        f"Category: {category}\nQuery: {ex['query']}\nOutput: {json.dumps(ex['output'], ensure_ascii=False)}\n"
        for ex in shots
    )

    return full_cfg["system_template"].format(
        category=category,
        category_upper=category.upper(),
        single_feats=", ".join(single_feats),
        multi_feats=", ".join(multi_feats),
        equals_set_examples=equals_set_examples,
        substyle_lines=substyle_lines,
        defs_text=defs_text,
        examples_text=examples_text,
    )


def build_open_system_prompt(
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Build an open_extraction system prompt (brand, price, residual) strictly scoped to `category` from YAML."""
    open_cfg = load_open_extraction_prompt()
    cat_spec = catalog[category]
    vocab = {feat: spec["values"] for feat, spec in cat_spec.items()}
    substyle_lines = "\n".join(_category_narrow_substyle_rules(category, cat_spec))
    shots = PER_CATEGORY_FEW_SHOTS[category]
    examples_text = "\n".join(
        f"Category: {category}\n"
        f"Already Extracted Catalog Filters: {json.dumps([f for f in ex['output']['filters'] if f['feature'] not in ('brand', 'price')], ensure_ascii=False)}\n"
        f"Query: {ex['query']}\n"
        f"Output: {json.dumps({'filters': [f for f in ex['output']['filters'] if f['feature'] in ('brand', 'price')], 'residual': ex['output']['residual']}, ensure_ascii=False)}\n"
        for ex in shots
    )

    return open_cfg["system_template"].format(
        category=category,
        category_upper=category.upper(),
        vocab_json=json.dumps(vocab, ensure_ascii=False),
        substyle_lines=substyle_lines,
        examples_text=examples_text,
    )


build_auxiliary_system_prompt = build_open_system_prompt


def load_cerebras_key() -> str:
    if os.environ.get("CEREBRAS_API_KEY"):
        return os.environ["CEREBRAS_API_KEY"].strip()
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("CEREBRAS_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("Missing CEREBRAS_API_KEY in environment or .env")


def build_full_user_message(
    query: str,
    category: str,
    catalog: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> str:
    return load_full_extraction_prompt()["user_template"].format(category=category, query=query)


def build_open_user_message(
    query: str,
    category: str,
    closed_filters: List[Dict[str, Any]],
    catalog: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> str:
    return load_open_extraction_prompt()["user_template"].format(
        category=category,
        jev_filters_json=json.dumps(closed_filters, ensure_ascii=False),
        query=query,
    )


build_auxiliary_user_message = build_open_user_message


@dataclass
class LLMCallResult:
    parsed: Dict[str, Any]
    latency_seconds: float
    cost_usd: float
    model: str
    usage: Dict[str, Any]


class VertexGeminiClient:
    """Vertex AI client for gemini-3.5-flash-lite with structured output and minimal thinking."""

    def __init__(
        self,
        project: str = DEFAULT_GCP_PROJECT,
        location: str = DEFAULT_GCP_LOCATION,
        model: str = GEMINI_MODEL,
        timeout: float = 30.0,
    ):
        self.project = project
        self.location = location
        self.model = model
        self.timeout = timeout
        self._session: Optional[AuthorizedSession] = None
        self.lock = threading.Lock()
        self.total_cost_usd = 0.0

    @property
    def session(self) -> AuthorizedSession:
        if self._session is None:
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
                quota_project_id=self.project,
            )
            credentials.refresh(Request())
            self._session = AuthorizedSession(
                credentials.with_quota_project(self.project),
                max_refresh_attempts=2,
            )
        return self._session

    @property
    def endpoint(self) -> str:
        return (
            f"https://aiplatform.googleapis.com/v1/projects/{self.project}/"
            f"locations/{self.location}/publishers/google/models/{self.model}:generateContent"
        )

    def extract_full(
        self,
        query: str,
        category: str,
        catalog: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> LLMCallResult:
        schema = build_vertex_full_schema(category, catalog)
        sys_prompt = build_full_system_prompt(category, catalog)
        user_msg = build_full_user_message(query, category, catalog)
        payload = {
            "systemInstruction": {"parts": [{"text": sys_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "temperature": 0.0,
                "maxOutputTokens": 512,
            },
        }
        with self.lock:
            for attempt in range(3):
                t0 = time.perf_counter()
                try:
                    response = self.session.post(
                        self.endpoint,
                        json=payload,
                        timeout=(10.0, self.timeout),
                        allow_redirects=False,
                    )
                    elapsed = time.perf_counter() - t0
                    if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    if not response.ok:
                        raise RuntimeError(f"Vertex Gemini HTTP {response.status_code}: {response.text[:400]}")
                    raw = response.json()
                    break
                except requests.RequestException as e:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    raise RuntimeError(f"Vertex Gemini network error: {e}") from e

        candidates = raw.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Vertex Gemini returned no candidates: {raw}")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if not part.get("thought"))
        parsed_raw = json.loads(text)
        validated = validate_response(parsed_raw, category, catalog, open_only=False)

        usage = raw.get("usageMetadata", {})
        in_tok = usage.get("promptTokenCount", 0)
        out_tok = usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)
        in_rate, out_rate = PRICING.get(self.model, (0.0, 0.0))
        cost = in_tok * in_rate + out_tok * out_rate
        self.total_cost_usd += cost

        return LLMCallResult(
            parsed=validated,
            latency_seconds=elapsed,
            cost_usd=cost,
            model=self.model,
            usage=usage,
        )

    def warmup(self, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> float:
        res = self.extract_full("black t-shirt", "T-shirts", catalog)
        return res.latency_seconds


class CerebrasClient:
    """Direct Cerebras API client supporting Qwen 3.8 27B and GPT-OSS-120B."""

    def __init__(
        self,
        model: str,
        reasoning_effort: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.api_key = api_key or load_cerebras_key()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        self.lock = threading.Lock()
        self.total_cost_usd = 0.0

    def _post_structured(self, system_prompt: str, user_msg: str, schema_name: str, schema: Dict[str, Any]) -> tuple[Dict[str, Any], float, Dict[str, Any]]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0,
            "max_completion_tokens": 512,
            "reasoning_effort": self.reasoning_effort,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
        }
        with self.lock:
            for attempt in range(3):
                t0 = time.perf_counter()
                try:
                    response = self.session.post(
                        CEREBRAS_ENDPOINT,
                        json=payload,
                        timeout=(10.0, self.timeout),
                        allow_redirects=False,
                    )
                    elapsed = time.perf_counter() - t0

                    if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    if not response.ok:
                        safe_text = response.text.replace(self.api_key, "[REDACTED]")
                        raise RuntimeError(f"Cerebras ({self.model}) HTTP {response.status_code}: {safe_text[:400]}")
                    raw = response.json()
                    break
                except requests.RequestException as e:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    raise RuntimeError(f"Cerebras ({self.model}) network error: {e}") from e

        content = raw["choices"][0]["message"]["content"]
        parsed_raw = json.loads(content)
        usage = raw.get("usage", {})
        return parsed_raw, elapsed, usage

    def extract_full(
        self,
        query: str,
        category: str,
        catalog: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> LLMCallResult:
        schema = build_cerebras_full_schema(category, catalog)
        sys_prompt = build_full_system_prompt(category, catalog)
        user_msg = build_full_user_message(query, category, catalog)
        parsed_raw, elapsed, usage = self._post_structured(
            sys_prompt, user_msg, "query_full_extraction", schema
        )
        validated = validate_response(parsed_raw, category, catalog, open_only=False)
        in_rate, out_rate = PRICING.get(self.model, (0.0, 0.0))
        cost = usage.get("prompt_tokens", 0) * in_rate + usage.get("completion_tokens", 0) * out_rate
        self.total_cost_usd += cost
        return LLMCallResult(
            parsed=validated,
            latency_seconds=elapsed,
            cost_usd=cost,
            model=self.model,
            usage=usage,
        )

    def extract_open(
        self,
        query: str,
        category: str,
        closed_filters: List[Dict[str, Any]],
        catalog: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> LLMCallResult:
        schema = build_cerebras_open_schema()
        sys_prompt = build_open_system_prompt(category, catalog)
        user_msg = build_open_user_message(query, category, closed_filters, catalog)
        parsed_raw, elapsed, usage = self._post_structured(
            sys_prompt, user_msg, "query_open_extraction", schema
        )
        validated = validate_response(parsed_raw, category, catalog, open_only=True)
        in_rate, out_rate = PRICING.get(self.model, (0.0, 0.0))
        cost = usage.get("prompt_tokens", 0) * in_rate + usage.get("completion_tokens", 0) * out_rate
        self.total_cost_usd += cost
        return LLMCallResult(
            parsed=validated,
            latency_seconds=elapsed,
            cost_usd=cost,
            model=self.model,
            usage=usage,
        )

    extract_auxiliary = extract_open

    def warmup_full(self, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> float:
        res = self.extract_full("black t-shirt", "T-shirts", catalog)
        return res.latency_seconds

    def warmup_open(self, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> float:
        res = self.extract_open(
            "black t-shirt",
            "T-shirts",
            [{"feature": "colors", "operator": "contains_any", "values": ["Black"]}],
            catalog,
        )
        return res.latency_seconds

    warmup_auxiliary = warmup_open
