"""Jev 1.14 (OpenRouter Decisions API) client and payloads for category_classification and closed_features."""

from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import unicodedata

import requests

from ..core.catalog import CATEGORY_CRITERIA
from ..core.few_shots import (
    CATEGORY_FEW_SHOTS,
    build_jev_feature_examples_json,
)
from ..core.prompts_loader import (
    load_category_classification_prompt,
    load_category_prompt_configs,
    load_closed_features_prompt,
)

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"


def build_closed_features_rules(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
    """Build category-scoped Jev closed-feature extraction rules from YAML configuration."""
    rules_cfg = load_closed_features_prompt()["rules"]
    cat_features = set(catalog[category].keys())
    parts = [
        rules_cfg["intro_template"].format(category=category),
        *rules_cfg["base_rules"],
        rules_cfg["relation_rule_base"],
    ]
    if "lining_composition" in cat_features:
        parts[-1] += rules_cfg["relation_rule_lining_suffix"]
    else:
        parts[-1] += rules_cfg["relation_rule_default_suffix"]
    parts.append(rules_cfg["faux_leather_rule"])
    if "insulation" in cat_features:
        parts.append(rules_cfg["insulation_rule"])
    if "leg_shape" in cat_features:
        parts.append(rules_cfg["leg_shape_rule"])
    parts.append(rules_cfg["closing_rule"])
    return " ".join(parts)


build_jev_rules = build_closed_features_rules


def normalize_query(query: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", query).casefold()))


def load_openrouter_key() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"].strip()
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("Missing OPENROUTER_API_KEY in environment or .env")


def category_payload(query: str) -> Dict[str, Any]:
    step1_cfg = load_category_classification_prompt()
    criteria = dict(CATEGORY_CRITERIA)
    criteria["outside"] = step1_cfg["outside_description"]
    return {
        "model": MODEL,
        "state": {
            "CURRENT_QUERY": query,
            "EXAMPLES_NOT_CURRENT_QUERY": CATEGORY_FEW_SHOTS,
        },
        "questions": {
            "category": {
                "type": "choice",
                "instructions": step1_cfg["instructions"],
                "criteria": criteria,
            }
        },
    }


def closed_features_payload(
    query: str,
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> Tuple[Dict[str, Any], Dict[str, Tuple[str, str]]]:
    jev_cfg = load_closed_features_prompt()
    common_scopes: Dict[str, str] = jev_cfg.get("feature_scopes", {})
    val_q_cfg = jev_cfg["value_question"]
    rel_q_cfg = jev_cfg["relation_question"]
    cat_scopes: Dict[str, str] = load_category_prompt_configs().get(category, {}).get("jev_scopes", {})

    questions: Dict[str, Any] = {}
    mapping: Dict[str, Tuple[str, str]] = {}
    for feature, spec in catalog[category].items():
        examples = build_jev_feature_examples_json(category, feature, catalog)
        scope = cat_scopes.get(feature, common_scopes.get(feature, ""))

        for index, value in enumerate(spec["values"]):
            qid = f"{feature}_{index}"
            mapping[qid] = (feature, value)
            val_desc = spec["value_descriptions"].get(value, value)
            base_instr = val_q_cfg["instructions_template"].format(
                feature=feature,
                value_repr=repr(value),
                val_desc=val_desc,
                category=category,
                scope=scope,
                instruction=spec["instruction"],
            )
            questions[qid] = {
                "type": "choice",
                "instructions": base_instr + (f"\nExamples ({category}): {examples}" if examples != "[]" else ""),
                "criteria": {
                    k: tmpl.format(value=value, feature=feature)
                    for k, tmpl in val_q_cfg["criteria"].items()
                },
            }
        if spec["multi"]:
            rel_instr = rel_q_cfg["instructions_template"].format(feature=feature, category=category)
            questions[f"{feature}_relation"] = {
                "type": "choice",
                "instructions": rel_instr + (f"\nExamples ({category}): {examples}" if examples != "[]" else ""),
                "criteria": dict(rel_q_cfg["criteria"]),
            }
    payload = {
        "model": MODEL,
        "state": {
            "CURRENT_QUERY": query,
            "category": category,
            "rules": build_closed_features_rules(category, catalog),
        },
        "questions": questions,
    }
    return payload, mapping


feature_payload = closed_features_payload


def filters_from_answers(
    answers: Dict[str, Any],
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
    mapping: Dict[str, Tuple[str, str]],
) -> List[Dict[str, Any]]:
    positive: Dict[str, List[str]] = {}
    negative: Dict[str, List[str]] = {}
    for qid, (feature, value) in mapping.items():
        choice = answers[qid]["choice"]
        if choice == "requested":
            positive.setdefault(feature, []).append(value)
        elif choice == "excluded":
            negative.setdefault(feature, []).append(value)

    filters: List[Dict[str, Any]] = []
    for feature, spec in catalog[category].items():
        pos_vals = positive.get(feature, [])
        if pos_vals:
            op = "in"
            if spec["multi"]:
                relation = answers[f"{feature}_relation"]["choice"]
                op = {"ANY": "contains_any", "ALL": "contains_all", "EXACT": "equals_set"}[relation]
                if op == "contains_all" and len(pos_vals) == 1:
                    op = "contains_any"
            filters.append({"feature": feature, "operator": op, "values": pos_vals})
        neg_vals = negative.get(feature, [])
        if neg_vals:
            filters.append(
                {
                    "feature": feature,
                    "operator": "contains_none" if spec["multi"] else "not_in",
                    "values": neg_vals,
                }
            )
    return filters


@dataclass
class JevCallResult:
    answers: Dict[str, Any]
    latency_seconds: float
    cost_usd: float
    usage: Dict[str, Any]


class JevClient:
    """Thread-safe OpenRouter Jev 1.14 client with connection pooling and budget tracking."""

    def __init__(self, api_key: Optional[str] = None, budget_usd: float = 0.50, timeout: float = 30.0):
        self.api_key = api_key or load_openrouter_key()
        self.budget_usd = budget_usd
        self.total_cost_usd = 0.0
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        self.lock = threading.Lock()

    def call(self, payload: Dict[str, Any]) -> JevCallResult:
        with self.lock:
            if self.total_cost_usd >= self.budget_usd:
                raise RuntimeError(f"Jev budget exceeded: ${self.total_cost_usd:.6f} >= ${self.budget_usd:.6f}")
            for attempt in range(3):
                t0 = time.perf_counter()
                try:
                    response = self.session.post(
                        ENDPOINT,
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
                        raise RuntimeError(f"Jev HTTP {response.status_code}: {safe_text[:400]}")
                    data = response.json()
                    break
                except requests.RequestException as e:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    raise RuntimeError(f"Jev network error: {e}") from e

            answers = data.get("answers", {})
            if set(answers.keys()) != set(payload["questions"].keys()):
                raise ValueError("Jev response question IDs do not match requested question IDs")
            for qid, qspec in payload["questions"].items():
                if not isinstance(answers[qid], dict) or answers[qid].get("choice") not in qspec["criteria"]:
                    raise ValueError(f"Jev returned invalid choice for {qid}: {answers.get(qid)!r}")

            usage = data.get("usage", {})
            cost = usage.get("cost", 0.0)
            if not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
                cost = 0.0
            self.total_cost_usd += float(cost)
            return JevCallResult(
                answers=answers,
                latency_seconds=elapsed,
                cost_usd=float(cost),
                usage=usage,
            )

    def warmup(self) -> float:
        """Send a minimal 1-question warmup call to establish the TLS session."""
        payload = {
            "model": MODEL,
            "state": {"CURRENT_QUERY": "black t-shirt"},
            "questions": {
                "warmup": {
                    "type": "choice",
                    "instructions": "Select T-shirts.",
                    "criteria": {"T-shirts": "A T-shirt.", "outside": "Other."},
                }
            },
        }
        res = self.call(payload)
        return res.latency_seconds
