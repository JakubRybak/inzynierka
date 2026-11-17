"""Jev category classification through OpenRouter."""

from dataclasses import dataclass
import math
import threading
import time
from typing import Any, Dict, Optional

import requests

from ..core.catalog import CATEGORY_CRITERIA
from ..core.few_shots import CATEGORY_FEW_SHOTS
from ..core.prompts_loader import load_category_classification_prompt
from .credentials import load_api_key

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.14"


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


@dataclass
class JevCallResult:
    answers: Dict[str, Any]
    latency_seconds: float
    cost_usd: float
    usage: Dict[str, Any]


class JevClient:
    """Thread-safe OpenRouter Jev 1.14 client with connection pooling and budget tracking."""

    def __init__(self, api_key: Optional[str] = None, budget_usd: float = 0.50, timeout: float = 30.0):
        self.api_key = api_key or load_api_key("OPENROUTER_API_KEY")
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
