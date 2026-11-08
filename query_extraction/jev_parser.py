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

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"

CATEGORY_FEW_SHOTS: List[Dict[str, str]] = [
    {"query": "a green jersey T-shirt dress for summer", "answer": "Dresses"},
    {"query": "a ribbed singlet in white", "answer": "Tank tops & Camisoles"},
    {"query": "a black crop top for a party", "answer": "Tank tops & Camisoles"},
    {"query": "a cotton tee with a collar", "answer": "Polos"},
    {"query": "a tee to wear with a leather jacket", "answer": "T-shirts"},
    {"query": "a classic white dress shirt for office", "answer": "Shirts"},
    {"query": "a silk peasant blouse", "answer": "Blouses"},
    {"query": "a fleece crewneck sweatshirt without hood", "answer": "Sweatshirts"},
    {"query": "a grey zip-up hoodie", "answer": "Hoodies & Zipups"},
    {"query": "a cotton half-zip pullover with a hood", "answer": "Hoodies & Zipups"},
    {"query": "a chunky cable-knit wool jumper", "answer": "Knit Sweaters"},
    {"query": "an open-front knit cardigan", "answer": "Cardigans"},
    {"query": "a double-breasted wool peacoat", "answer": "Classic Coats"},
    {"query": "a beige belted gabardine trench", "answer": "Trench Coats"},
    {"query": "a black leather biker jacket", "answer": "Jackets"},
    {"query": "an olive nylon flight bomber", "answer": "Bombers"},
    {"query": "a quilted down gilet", "answer": "Vests"},
    {"query": "tailored high-waisted wool slacks", "answer": "Trousers"},
    {"query": "olive combat pants with utility cargo pockets", "answer": "Cargo Pants"},
    {"query": "grey fleece tapered joggers", "answer": "Sweatpants & Lounge Pants"},
    {"query": "faded bootcut denim jeans", "answer": "Jeans"},
    {"query": "men's linen bermuda shorts", "answer": "Shorts"},
    {"query": "a pleated midi skirt", "answer": "Skirts"},
    {"query": "a long-sleeve snap-crotch bodysuit", "answer": "Bodysuits"},
    {"query": "leather Chelsea ankle boots", "answer": "outside"},
    {"query": "something warm in black under 100 dollars", "answer": "outside"},
    {"query": "a cotton T-shirt or a linen dress", "answer": "outside"},
]

FEATURE_FEW_SHOTS: List[Dict[str, Any]] = [
    {
        "query": "a loose boxy T-shirt",
        "decisions": {"fit": {"Oversized": "requested", "Slim": "not_specified", "Regular": "not_specified"}},
        "note": "An explicit positive fit does not negate other fit values.",
    },
    {
        "query": "a fitted tee, but not relaxed",
        "decisions": {"fit": {"Slim": "requested", "Oversized": "excluded", "Regular": "not_specified"}},
        "note": "Both positive and negative clauses are explicitly stated in the query.",
    },
    {
        "query": "a sleeveless dress",
        "decisions": {
            "sleeve_length": {
                "Sleeveless": "requested",
                "Short Sleeve": "not_specified",
                "Three-Quarter Sleeve": "not_specified",
                "Long Sleeve": "not_specified",
            },
            "gender": {},
            "strap_style": {},
        },
        "note": "Sleeveless names one value; Dress does not imply Women or a strap_style.",
    },
    {
        "query": "all-black tank top",
        "decisions": {"colors": {"Black": "requested"}},
        "relations": {"colors": "EXACT"},
        "note": "'all-black' or 'only black' requires EXACT (equals_set).",
    },
    {
        "query": "green tank top, but not emerald",
        "decisions": {"colors": {"Green": "requested"}},
        "relations": {"colors": "ANY"},
        "note": "Excluding a specific shade ('not emerald') does not exclude the Green color family.",
    },
    {
        "query": "blue or red tanks without yellow",
        "decisions": {"colors": {"Blue": "requested", "Red": "requested", "Yellow": "excluded"}},
        "relations": {"colors": "ANY"},
    },
    {
        "query": "black and yellow tank tops",
        "decisions": {"colors": {"Black": "requested", "Yellow": "requested"}},
        "relations": {"colors": "ALL"},
    },
    {
        "query": "a 100% cotton T-shirt",
        "decisions": {"main_composition": {"Cotton": "requested"}},
        "relations": {"main_composition": "EXACT"},
        "note": "100% material or 'only/pure' material maps to EXACT (equals_set).",
    },
    {
        "query": "a 30% wool sweater with 0% polyester",
        "decisions": {"main_composition": {"Wool": "requested", "Polyester": "excluded"}},
        "relations": {"main_composition": "ANY"},
        "note": "0% excludes the material; a percentage between 0% and 100% requests presence (ANY).",
    },
    {
        "query": "a dress made of wool and silk",
        "decisions": {"main_composition": {"Wool": "requested", "Silk": "requested"}, "gender": {}},
        "relations": {"main_composition": "ALL"},
    },
    {
        "query": "an unlined linen jacket",
        "decisions": {
            "main_composition": {"Linen": "requested"},
            "lining_composition": {"Unlined": "requested"},
        },
        "relations": {"main_composition": "ANY", "lining_composition": "EXACT"},
        "note": "'unlined' sets lining_composition=Unlined with EXACT.",
    },
    {
        "query": "a bomber jacket with a silk lining",
        "decisions": {"lining_composition": {"Silk": "requested", "Unlined": "not_specified"}},
        "relations": {"lining_composition": "ANY"},
        "note": "Explicit silk lining maps to lining_composition=Silk (ANY).",
    },
    {
        "query": "a strapless camisole",
        "decisions": {"strap_style": {"Strapless": "requested", "Standard": "not_specified"}, "strap_width": {}},
        "note": "Do not infer strap_width or Sleeveless from Strapless.",
    },
    {
        "query": "a fitted top with spaghetti straps",
        "decisions": {"fit": {"Slim": "requested"}, "strap_width": {"Spaghetti": "requested"}, "strap_style": {}},
        "note": "Generic straps with a width do not specify Standard strap_style.",
    },
    {
        "query": "an oversized pullover hoodie for men",
        "decisions": {
            "fit": {"Oversized": "requested"},
            "closure_type": {"Pullover": "requested"},
            "hood": {"With Hood": "requested"},
            "gender": {"Men": "requested"},
        },
        "note": "In Hoodies & Zipups, the word 'hoodie' explicitly requests hood=With Hood.",
    },
]

JEV_RULES = (
    "Classify direct textual evidence in CURRENT_QUERY (EN/PL/ES). Never infer unstated values. "
    "A positive value does not exclude other values. Exclusions require explicit negation ('without', 'no', 'not', 'bez', 'sin', '0%'). "
    "Negating a color shade ('not turquoise') does NOT exclude its color family ('Blue'). "
    "Multi-choice/composition relation: conjunction ('and'/'i'/'y', blends) -> ALL; alternatives ('or') or single value or <100% share -> ANY; "
    "'only', 'exclusively', 'pure', '100% <material>', 'all-<color>', or 'unlined' -> EXACT. "
    "Faux/vegan/PU leather is NOT Leather. In outerwear, down/feathers ('down', 'puch', 'plumas') is insulation=Down, not main_composition. "
    "Do not extract brand, price, or residual."
)


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


def feature_examples_json(feature: str) -> str:
    examples = []
    for shot in FEATURE_FEW_SHOTS:
        if feature not in shot["decisions"]:
            continue
        example: Dict[str, Any] = {
            "example_query": shot["query"],
            "value_labels": shot["decisions"][feature],
            "all_unlisted_value_labels": "not_specified",
        }
        if feature in shot.get("relations", {}):
            example["relation"] = shot["relations"][feature]
        if shot.get("note"):
            example["explanation"] = shot["note"]
        examples.append(example)
    return json.dumps(examples, ensure_ascii=False)


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
        examples = feature_examples_json(feature)
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
            scope = "The word 'hoodie'/'hoodies'/'hooded'/'z kapturem'/'con capucha' requests With Hood. "
        elif category == "Hoodies & Zipups" and feature == "closure_type":
            scope = "'zip-up'/'zip up'/'zipper'/'na suwak'/'con cremallera' -> Zip; 'half-zip'/'z krótkim zamkiem' -> Half-Zip; 'pullover' -> Pullover. "
        elif category == "Sweatpants & Lounge Pants" and feature == "leg_shape":
            scope = "'joggers'/'joggery' requests Tapered. "
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
                    + (f"\nExamples: {examples}" if examples != "[]" else "")
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
                    f"How must the positively requested {feature} values be combined in CURRENT_QUERY? Ignore exclusions."
                    + (f"\nExamples: {examples}" if examples != "[]" else "")
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
            "rules": JEV_RULES,
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
