"""Two-step LLM query parser adapter using query_extraction (default: full_qwen) for search_ui.

Supports all 22 categories, catalog attribute validation, open brand/price extraction,
and residual concepts for vector ranking.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from query_extraction import DEFAULT_CONFIG, get_default_extractor, parse_query
from query_extraction.core.catalog import load_query_catalog

CATALOG = load_query_catalog()
CATEGORIES = list(CATALOG.keys())
NAME = f"QueryExtractor ({DEFAULT_CONFIG} · Jev + Qwen 3.8 27B)"

# Priming TLS session on import / server startup
try:
    _extractor = get_default_extractor()
    _extractor.warmup([DEFAULT_CONFIG])
except Exception as e:
    print(f"Parser warmup warning ({type(e).__name__}): {e}")


def parse(query: str) -> Dict[str, Any]:
    """Parse query using query_extraction default config (full_qwen)."""
    raw = parse_query(query, config=DEFAULT_CONFIG, include_meta=True)
    meta = raw.get("_meta", {})
    return {
        "query": query,
        "category": raw.get("category"),
        "filters": list(raw.get("filters", [])),
        "residual": list(raw.get("residual", [])),
        "step1_latency_seconds": meta.get("category_latency_seconds", 0.0),
        "step2_latency_seconds": meta.get("llm_latency_seconds", 0.0),
        "total_latency_seconds": meta.get("total_latency_seconds", 0.0),
        "metadata": {
            "model": meta.get("label", "Qwen 3.8 27B (Cerebras)"),
            "estimated_cost_usd": meta.get("total_cost_usd", 0.0),
            "config": meta.get("config", DEFAULT_CONFIG),
        },
        "_source": f"QueryExtractor ({DEFAULT_CONFIG})",
    }
