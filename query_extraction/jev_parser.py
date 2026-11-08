"""Jev 1.14 (OpenRouter Decisions API) client and payloads for Step 1 (category) and Step 2b-1 (features)."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import unicodedata

import requests

from .catalog import CATEGORY_CRITERIA, load_query_catalog
from .few_shots import (
    CATEGORY_FEW_SHOTS,
    PER_CATEGORY_FEW_SHOTS,
    build_jev_feature_examples_json,
)

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"


def build_jev_rules(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
    """Build category-scoped Jev extraction rules."""
    cat_features = set(catalog[category].keys())
    parts = [
        f"Classify direct textual evidence in CURRENT_QUERY (EN/PL/ES) for category {category}. Never infer unstated values.",
        "A positive value does NOT exclude other values (e.g. requesting 'With Hood' leaves 'Without Hood' as not_specified, NEVER excluded).",
        "Exclusions require explicit negation ('without', 'no', 'not', 'bez', 'sin', '0%') targeting that specific value.",
        "Negating a color shade ('not turquoise', 'not emerald') does NOT exclude its color family.",
        "Multi-choice/composition relation: conjunction ('and'/'i'/'y', blends) -> ALL; alternatives ('or') or single value or <100% share -> ANY; 'only', 'exclusively', 'pure', '100% <material>', 'all-<color>'",
    ]
    if "lining_composition" in cat_features:
        parts[-1] += ", or 'unlined' -> EXACT."
    else:
        parts[-1] += " -> EXACT."
    parts.append("Faux/vegan/PU leather is NOT Leather.")
    if "insulation" in cat_features:
        parts.append("Down/feathers ('down', 'puch', 'plumas') is insulation=Down, not main_composition.")
    if "leg_shape" in cat_features:
        parts.append("Do NOT map 'skinny', 'slim fit', or 'elasticized waistband' ('z gumką w pasie') to leg_shape=Tapered.")
    parts.append("Do not extract brand, price, or residual.")
    return " ".join(parts)


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
    criteria = dict(CATEGORY_CRITERIA)
    criteria["outside"] = (
        "No supported garment category is requested (e.g. shoes, sneakers, boots, bags, belts, hats, scarves, "
        "socks, jewelry, bras, swimsuits, pajamas, full two-piece suits, replacement parts/accessories, "
        "queries with no garment type like 'something black under $50', or alternative categories like 't-shirt or dress')."
    )
    return {
        "model": MODEL,
        "state": {
            "CURRENT_QUERY": query,
            "EXAMPLES_NOT_CURRENT_QUERY": CATEGORY_FEW_SHOTS,
        },
        "questions": {
            "category": {
                "type": "choice",
                "instructions": (
                    "Select the single product category that the user wants to buy in CURRENT_QUERY across English, "
                    "Polish, and Spanish. Classify the target garment being bought, NOT clothing mentioned only as "
                    "styling context (e.g. 't-shirt to wear with jeans' -> T-shirts; 'belt to wear with jeans' -> outside; "
                    "'buttons for a wool coat' -> outside). A 'T-shirt dress', 'shirt dress', 'sweater dress', or "
                    "'sweatshirt dress' is Dresses. A generic 'top' or 'crop top' without a more specific category is "
                    "Tank tops & Camisoles. A collared tee ('tee with a collar') is Polos. A 'dress shirt' is Shirts. "
                    "If no supported category or multiple alternative categories ('t-shirt or dress') are requested, "
                    "choose outside."
                ),
                "criteria": criteria,
            }
        },
    }


def feature_payload(
    query: str,
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> Tuple[Dict[str, Any], Dict[str, Tuple[str, str]]]:
    questions: Dict[str, Any] = {}
    mapping: Dict[str, Tuple[str, str]] = {}
    for feature, spec in catalog[category].items():
        examples = build_jev_feature_examples_json(category, feature, catalog)
        scope = ""
        if feature == "strap_style":
            scope = (
                "Generic 'top', 'tank', 'camisole', 'straps', 'na ramiączkach', strap width, or fit are NOT "
                "evidence of Standard strap_style. Standard requires an explicit ordinary/standard strap description. "
            )
        elif feature == "lining_composition":
            scope = (
                "Only mark a lining_composition value when the query explicitly mentions a lining or unlined state "
                "('lining', 'lined', 'unlined', 'podszewka', 'bez podszewki', 'forro', 'sin forro'). Outer shell "
                "materials belong to main_composition, and 'fleece-lined'/'shearling-lined' belong to insulation. "
            )
        elif feature == "coat_style":
            scope = (
                "A bare 'coat', 'płaszcz', or 'abrigo' does NOT request Standard coat_style; Standard requires "
                "'classic coat', 'overcoat', 'topcoat', 'pea coat', 'peacoat', 'chesterfield', or 'car coat'. "
            )
        elif feature == "insulation":
            scope = (
                "'quilted', 'puffer', or 'acolchado' alone without stating down/feathers or synthetic padding "
                "does NOT specify Synthetic Padding or Down; leave insulation not_specified in that case. "
            )
        elif category == "Hoodies & Zipups" and feature == "hood":
            scope = (
                "The word 'hoodie'/'hoodies'/'hooded'/'z kapturem'/'con capucha' requests With Hood "
                "(and leaves Without Hood as not_specified, NEVER excluded). "
            )
        elif category == "Hoodies & Zipups" and feature == "closure_type":
            scope = "'zip-up'/'zip up'/'zipper'/'na suwak'/'con cremallera' -> Zip; 'half-zip'/'z krótkim zamkiem' -> Half-Zip; 'pullover' -> Pullover. "
        elif category == "Sweatpants & Lounge Pants" and feature == "leg_shape":
            scope = "'joggers'/'joggery' requests Tapered. "
        elif feature == "leg_shape":
            scope = "Do NOT map 'skinny', 'slim fit', or 'elasticized waistband' ('z gumką w pasie') to Tapered. "
        elif category == "Shorts" and feature == "shorts_type":
            scope = "Running/volleyball/gym/compression/athletic shorts request Athletic. "

        for index, value in enumerate(spec["values"]):
            qid = f"{feature}_{index}"
            mapping[qid] = (feature, value)
            val_desc = spec["value_descriptions"].get(value, value)
            questions[qid] = {
                "type": "choice",
                "instructions": (
                    f"Classify direct mention and polarity of {feature}={value!r} ({val_desc}) in CURRENT_QUERY for {category}. "
                    f"Another positive value does NOT exclude this value. {scope}{spec['instruction']}"
                    + (f"\nExamples ({category}): {examples}" if examples != "[]" else "")
                ),
                "criteria": {
                    "not_specified": f"CURRENT_QUERY does not directly request or negate {value} for {feature}.",
                    "requested": f"CURRENT_QUERY directly requests {value} (or a synonym/shade) for {feature}.",
                    "excluded": f"CURRENT_QUERY explicitly negates {value} ('without', 'no', 'not', 'bez', 'sin', '0%') for {feature}.",
                },
            }
        if spec["multi"]:
            questions[f"{feature}_relation"] = {
                "type": "choice",
                "instructions": (
                    f"How must the positively requested {feature} values be combined in CURRENT_QUERY for {category}? Ignore exclusions."
                    + (f"\nExamples ({category}): {examples}" if examples != "[]" else "")
                ),
                "criteria": {
                    "ANY": "Alternatives ('or'), or a single value without 'only'/'100%'/'all-'/'unlined', or <100% material share, or none requested.",
                    "ALL": "Multiple requested values that must all occur together ('and', blends, multi-color, combined closures).",
                    "EXACT": "Explicit 'only', 'exclusively', 'pure', '100% <material>', 'all-<color>' ('all-black'), or 'unlined'.",
                },
            }
    payload = {
        "model": MODEL,
        "state": {
            "CURRENT_QUERY": query,
            "category": category,
            "rules": build_jev_rules(category, catalog),
        },
        "questions": questions,
    }
    return payload, mapping


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
            t0 = time.perf_counter()
            response = self.session.post(
                ENDPOINT,
                json=payload,
                timeout=(10.0, self.timeout),
                allow_redirects=False,
            )
            elapsed = time.perf_counter() - t0
            if not response.ok:
                safe_text = response.text.replace(self.api_key, "[REDACTED]")
                raise RuntimeError(f"Jev HTTP {response.status_code}: {safe_text[:400]}")
            data = response.json()

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
