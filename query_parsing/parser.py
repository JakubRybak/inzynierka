"""Parse shopping queries with Jev for the category and Qwen for the filters."""

from __future__ import annotations

from functools import lru_cache
from threading import Lock
from typing import Any

from .clients.jev import JevClient, category_payload
from .clients.qwen import QwenClient
from .core.catalog import load_query_catalog


class QueryParser:
    def __init__(
        self,
        *,
        jev_client: JevClient | None = None,
        qwen_client: QwenClient | None = None,
        jev_budget_usd: float = 0.50,
    ) -> None:
        self.catalog = load_query_catalog()
        self._jev = jev_client
        self._qwen = qwen_client
        self._jev_budget_usd = jev_budget_usd
        self._lock = Lock()

    def parse(self, query: str, *, include_meta: bool = False) -> dict[str, Any]:
        """Return the category, filters and residual concepts in a shopping query."""
        with self._lock:
            if self._jev is None:
                self._jev = JevClient(budget_usd=self._jev_budget_usd)
            jev = self._jev

        classification = jev.call(category_payload(query))
        choice = classification.answers["category"]["choice"]
        category = None if choice == "outside" else choice
        result: dict[str, Any] = {"category": category, "filters": [], "residual": []}
        qwen_latency = qwen_cost = 0.0

        if category is not None:
            with self._lock:
                if self._qwen is None:
                    self._qwen = QwenClient()
                qwen = self._qwen
            extraction = qwen.extract_full(query, category, self.catalog)
            result.update(extraction.parsed)
            qwen_latency = round(extraction.latency_seconds, 4)
            qwen_cost = round(extraction.cost_usd, 6)

        if include_meta:
            category_latency = round(classification.latency_seconds, 4)
            category_cost = round(classification.cost_usd, 6)
            result["_meta"] = {
                "config": "full_qwen",
                "label": "Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)",
                "category_latency_seconds": category_latency,
                "closed_features_latency_seconds": 0.0,
                "llm_latency_seconds": qwen_latency,
                "total_latency_seconds": round(category_latency + qwen_latency, 4),
                "total_cost_usd": round(category_cost + qwen_cost, 6),
            }
        return result


@lru_cache(maxsize=1)
def _default_parser() -> QueryParser:
    return QueryParser()


def parse_query(query: str, *, include_meta: bool = False) -> dict[str, Any]:
    return _default_parser().parse(query, include_meta=include_meta)
