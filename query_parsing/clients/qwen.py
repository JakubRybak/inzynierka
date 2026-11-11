"""Qwen feature extraction through the direct Cerebras API."""

from dataclasses import dataclass
import json
import threading
import time
from typing import Any, Dict, List, Optional

import requests

from ..core.catalog import build_cerebras_full_schema, validate_response
from ..core.few_shots import PER_CATEGORY_FEW_SHOTS
from ..core.prompts_loader import (
    load_category_prompt_configs,
    load_feature_definitions_prompt,
    load_full_extraction_prompt,
)
from .credentials import load_api_key

CEREBRAS_ENDPOINT = "https://api.cerebras.ai/v1/chat/completions"
QWEN_MODEL = "qwen-3.8-27b"
TOKEN_COST_USD = (0.30 / 1_000_000, 0.60 / 1_000_000)


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


def build_full_user_message(
    query: str,
    category: str,
    catalog: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> str:
    return load_full_extraction_prompt()["user_template"].format(category=category, query=query)


@dataclass
class LLMCallResult:
    parsed: Dict[str, Any]
    latency_seconds: float
    cost_usd: float
    model: str
    usage: Dict[str, Any]


class QwenClient:
    """Direct Cerebras API client for Qwen 3.8 27B."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or load_api_key("CEREBRAS_API_KEY")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        self.lock = threading.Lock()

    def _post_structured(self, system_prompt: str, user_msg: str, schema: Dict[str, Any]) -> tuple[Dict[str, Any], float, Dict[str, Any]]:
        payload = {
            "model": QWEN_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0,
            "max_completion_tokens": 512,
            "reasoning_effort": "none",
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "query_full_extraction",
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
                        raise RuntimeError(f"Cerebras ({QWEN_MODEL}) HTTP {response.status_code}: {safe_text[:400]}")
                    raw = response.json()
                    break
                except requests.RequestException as e:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    raise RuntimeError(f"Cerebras ({QWEN_MODEL}) network error: {e}") from e

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
            sys_prompt, user_msg, schema
        )
        validated = validate_response(parsed_raw, category, catalog)
        in_rate, out_rate = TOKEN_COST_USD
        cost = usage.get("prompt_tokens", 0) * in_rate + usage.get("completion_tokens", 0) * out_rate
        return LLMCallResult(
            parsed=validated,
            latency_seconds=elapsed,
            cost_usd=cost,
            model=QWEN_MODEL,
            usage=usage,
        )
