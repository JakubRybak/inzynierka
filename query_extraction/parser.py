"""Public query extraction API and pipeline configuration registry."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

if TYPE_CHECKING:
    from .clients.jev import JevClient
    from .clients.llm import CerebrasClient, VertexGeminiClient

DEFAULT_CONFIG = "full_qwen"
GEMINI_MODEL = "gemini-3.5-flash-lite"
QWEN_MODEL = "qwen-3.8-27b"
GPT_OSS_MODEL = "gpt-oss-120b"

CONFIGS: Dict[str, Dict[str, Any]] = {
    "full_qwen": {
        "name": "full_qwen",
        "aliases": ("2a_qwen", "2a_qwen_3_8_27b", "llm_qwen"),
        "architecture": "full",
        "provider": "cerebras",
        "model": QWEN_MODEL,
        "reasoning_effort": "none",
        "stage_key": "full_qwen",
        "legacy_stage_key": "2a_qwen",
        "required_stages": ("category", "full_qwen"),
        "label": "Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)",
        "stage_description": "Full Extraction (cechy zamknięte + brand + price + residual)",
        "model_description": "`qwen-3.8-27b` (Cerebras, `none`)",
    },
    "full_gpt_oss": {
        "name": "full_gpt_oss",
        "aliases": ("2a_gpt_oss", "2a_gpt_oss_120b", "llm_gpt_oss"),
        "architecture": "full",
        "provider": "cerebras",
        "model": GPT_OSS_MODEL,
        "reasoning_effort": "low",
        "stage_key": "full_gpt_oss",
        "legacy_stage_key": "2a_gpt_oss",
        "required_stages": ("category", "full_gpt_oss"),
        "label": "Full · Jev (Category) → GPT-OSS-120B (Full Extraction)",
        "stage_description": "Full Extraction (cechy zamknięte + brand + price + residual)",
        "model_description": "`gpt-oss-120b` (Cerebras, `low`)",
    },
    "full_gemini": {
        "name": "full_gemini",
        "aliases": ("2a_gemini", "2a_gemini_flash_lite", "llm_gemini"),
        "architecture": "full",
        "provider": "vertex",
        "model": GEMINI_MODEL,
        "reasoning_effort": "none",
        "stage_key": "full_gemini",
        "legacy_stage_key": "2a_gemini",
        "required_stages": ("category", "full_gemini"),
        "label": "Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)",
        "stage_description": "Full Extraction (cechy zamknięte + brand + price + residual)",
        "model_description": "`gemini-3.5-flash-lite` (Vertex AI)",
    },
    "split_qwen": {
        "name": "split_qwen",
        "aliases": ("2b_qwen", "2b_jev_qwen_3_8_27b", "hybrid_qwen"),
        "architecture": "split",
        "provider": "cerebras",
        "model": QWEN_MODEL,
        "reasoning_effort": "none",
        "stage_key": "open_qwen",
        "legacy_stage_key": "2b_qwen_aux",
        "required_stages": ("category", "closed_features", "open_qwen"),
        "label": "Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)",
        "stage_description": "Open Extraction (brand + price + residual po Jev Closed Features)",
        "model_description": "`qwen-3.8-27b` (Cerebras, `none`)",
    },
    "split_gpt_oss": {
        "name": "split_gpt_oss",
        "aliases": ("2b_gpt_oss", "2b_jev_gpt_oss_120b", "hybrid_gpt_oss"),
        "architecture": "split",
        "provider": "cerebras",
        "model": GPT_OSS_MODEL,
        "reasoning_effort": "low",
        "stage_key": "open_gpt_oss",
        "legacy_stage_key": "2b_gpt_oss_aux",
        "required_stages": ("category", "closed_features", "open_gpt_oss"),
        "label": "Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)",
        "stage_description": "Open Extraction (brand + price + residual po Jev Closed Features)",
        "model_description": "`gpt-oss-120b` (Cerebras, `low`)",
    },
}

CONFIG_ALIASES: Dict[str, str] = {}
for _canonical, _spec in CONFIGS.items():
    CONFIG_ALIASES[_canonical] = _canonical
    for _alias in _spec["aliases"]:
        CONFIG_ALIASES[_alias] = _canonical

STAGE_KEY_ALIASES: Dict[str, str] = {
    "jev_category": "category",
    "jev_features": "closed_features",
    "2a_qwen": "full_qwen",
    "2a_gpt_oss": "full_gpt_oss",
    "2a_gemini": "full_gemini",
    "2b_qwen_aux": "open_qwen",
    "2b_gpt_oss_aux": "open_gpt_oss",
}


def normalize_stage_keys(stages: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure canonical stage keys exist in `stages`, migrating any legacy keys in-place."""
    for legacy_key, canon_key in STAGE_KEY_ALIASES.items():
        if legacy_key in stages and canon_key not in stages:
            stages[canon_key] = stages[legacy_key]
        if legacy_key in stages:
            del stages[legacy_key]
    return stages


def resolve_config_name(config: str) -> str:
    """Resolve a configuration name or alias to its canonical key in CONFIGS."""
    key = config.strip()
    if key not in CONFIG_ALIASES:
        valid = ", ".join(CONFIGS.keys())
        raise ValueError(f"Unknown configuration {config!r}. Available configurations: {valid}")
    return CONFIG_ALIASES[key]


def resolve_config_list(configs: Optional[Sequence[str]] = None) -> List[str]:
    """Resolve a sequence of configuration names (or ['all'] / None) into an ordered deduplicated list."""
    if not configs or any(c.strip().lower() == "all" for c in configs):
        return list(CONFIGS.keys())
    resolved: List[str] = []
    for item in configs:
        for part in item.split(","):
            part = part.strip()
            if not part:
                continue
            canon = resolve_config_name(part)
            if canon not in resolved:
                resolved.append(canon)
    return resolved


def assemble_stage_prediction(stages: Dict[str, Any], config: str) -> Dict[str, Any]:
    """Assemble predicted output and stage latencies/costs for a single query from recorded stages."""
    canon = resolve_config_name(config)
    spec = CONFIGS[canon]
    s_cat = stages.get("category") or stages["jev_category"]
    cat = s_cat["category"]
    t1 = float(s_cat["latency_seconds"])
    c1 = float(s_cat["cost_usd"])

    if cat is None:
        return {
            "predicted": {"category": None, "filters": [], "residual": []},
            "step1_latency_seconds": t1,
            "step2_1_latency_seconds": 0.0,
            "step2_llm_latency_seconds": 0.0,
            "total_latency_seconds": round(t1, 4),
            "total_cost_usd": round(c1, 6),
        }

    stage_key = spec["stage_key"]
    s_llm = stages.get(stage_key) or stages[spec["legacy_stage_key"]]
    if spec["architecture"] == "full":
        t_llm = float(s_llm["latency_seconds"])
        c_llm = float(s_llm["cost_usd"])
        return {
            "predicted": {
                "category": cat,
                "filters": list(s_llm["filters"]),
                "residual": list(s_llm["residual"]),
            },
            "step1_latency_seconds": t1,
            "step2_1_latency_seconds": 0.0,
            "step2_llm_latency_seconds": t_llm,
            "total_latency_seconds": round(t1 + t_llm, 4),
            "total_cost_usd": round(c1 + c_llm, 6),
        }

    s_feat = stages.get("closed_features") or stages["jev_features"]
    t2_1 = float(s_feat["latency_seconds"])
    c2_1 = float(s_feat["cost_usd"])
    t_open = float(s_llm["latency_seconds"])
    c_open = float(s_llm["cost_usd"])
    return {
        "predicted": {
            "category": cat,
            "filters": list(s_feat["filters"]) + list(s_llm["filters"]),
            "residual": list(s_llm["residual"]),
        },
        "step1_latency_seconds": t1,
        "step2_1_latency_seconds": t2_1,
        "step2_llm_latency_seconds": t_open,
        "total_latency_seconds": round(t1 + t2_1 + t_open, 4),
        "total_cost_usd": round(c1 + c2_1 + c_open, 6),
    }


class QueryExtractor:
    """Reusable, thread-safe query extractor supporting all 5 pipeline configurations."""

    def __init__(
        self,
        *,
        catalog: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
        jev_budget_usd: float = 0.50,
        jev_client: Optional[JevClient] = None,
        gemini_client: Optional[VertexGeminiClient] = None,
        cerebras_clients: Optional[Dict[str, CerebrasClient]] = None,
    ) -> None:
        if catalog is None:
            from .core.catalog import load_query_catalog

            catalog = load_query_catalog()
        self.catalog = catalog
        self.jev_budget_usd = jev_budget_usd
        self._jev_client = jev_client
        self._gemini_client = gemini_client
        self._cerebras_clients: Dict[str, CerebrasClient] = dict(cerebras_clients or {})
        self._lock = threading.Lock()

    def _get_jev(self) -> JevClient:
        with self._lock:
            if self._jev_client is None:
                from .clients.jev import JevClient

                self._jev_client = JevClient(budget_usd=self.jev_budget_usd)
            return self._jev_client

    def _get_gemini(self) -> VertexGeminiClient:
        with self._lock:
            if self._gemini_client is None:
                from .clients.llm import VertexGeminiClient

                self._gemini_client = VertexGeminiClient()
            return self._gemini_client

    def _get_cerebras(self, spec: Dict[str, Any]) -> CerebrasClient:
        model = spec["model"]
        with self._lock:
            if model not in self._cerebras_clients:
                from .clients.llm import CerebrasClient

                self._cerebras_clients[model] = CerebrasClient(
                    model=model,
                    reasoning_effort=spec["reasoning_effort"],
                )
            return self._cerebras_clients[model]

    def warmup(self, configs: Optional[Sequence[str]] = None) -> Dict[str, float]:
        """Warm up network connections for the specified configurations."""
        resolved = resolve_config_list(configs)
        timings: Dict[str, float] = {}
        timings["jev"] = self._get_jev().warmup()
        for cfg_name in resolved:
            spec = CONFIGS[cfg_name]
            if spec["provider"] == "vertex" and "gemini" not in timings:
                timings["gemini"] = self._get_gemini().warmup(self.catalog)
            elif spec["provider"] == "cerebras":
                model = spec["model"]
                if model not in timings:
                    timings[model] = self._get_cerebras(spec).warmup_full(self.catalog)
        return timings

    def parse(
        self,
        query: str,
        config: str = DEFAULT_CONFIG,
        *,
        include_meta: bool = False,
    ) -> Dict[str, Any]:
        """Extract category, filters, and residual concepts from a user query using `config`."""
        from .clients.jev import (
            category_payload,
            closed_features_payload,
            filters_from_answers,
        )

        canon = resolve_config_name(config)
        spec = CONFIGS[canon]
        jev = self._get_jev()

        cat_res = jev.call(category_payload(query))
        choice = cat_res.answers["category"]["choice"]
        category = None if choice == "outside" else choice

        stages: Dict[str, Any] = {
            "category": {
                "category": category,
                "latency_seconds": round(cat_res.latency_seconds, 4),
                "cost_usd": round(cat_res.cost_usd, 6),
            }
        }

        if category is not None:
            if spec["architecture"] == "full":
                if spec["provider"] == "vertex":
                    llm_res = self._get_gemini().extract_full(query, category, self.catalog)
                else:
                    llm_res = self._get_cerebras(spec).extract_full(query, category, self.catalog)
                stages[spec["stage_key"]] = {
                    "filters": llm_res.parsed["filters"],
                    "residual": llm_res.parsed["residual"],
                    "latency_seconds": round(llm_res.latency_seconds, 4),
                    "cost_usd": round(llm_res.cost_usd, 6),
                }
            else:
                fp, fmap = closed_features_payload(query, category, self.catalog)
                feat_res = jev.call(fp)
                closed_filters = filters_from_answers(feat_res.answers, category, self.catalog, fmap)
                stages["closed_features"] = {
                    "filters": closed_filters,
                    "latency_seconds": round(feat_res.latency_seconds, 4),
                    "cost_usd": round(feat_res.cost_usd, 6),
                }
                open_res = self._get_cerebras(spec).extract_open(
                    query, category, closed_filters, self.catalog
                )
                stages[spec["stage_key"]] = {
                    "filters": open_res.parsed["filters"],
                    "residual": open_res.parsed["residual"],
                    "latency_seconds": round(open_res.latency_seconds, 4),
                    "cost_usd": round(open_res.cost_usd, 6),
                }

        assembled = assemble_stage_prediction(stages, canon)
        result = dict(assembled["predicted"])
        if include_meta:
            result["_meta"] = {
                "config": canon,
                "label": spec["label"],
                "category_latency_seconds": assembled["step1_latency_seconds"],
                "closed_features_latency_seconds": assembled["step2_1_latency_seconds"],
                "llm_latency_seconds": assembled["step2_llm_latency_seconds"],
                "total_latency_seconds": assembled["total_latency_seconds"],
                "total_cost_usd": assembled["total_cost_usd"],
            }
        return result


_DEFAULT_EXTRACTOR: Optional[QueryExtractor] = None
_DEFAULT_LOCK = threading.Lock()


def get_default_extractor() -> QueryExtractor:
    """Return the lazily initialized singleton QueryExtractor."""
    global _DEFAULT_EXTRACTOR
    with _DEFAULT_LOCK:
        if _DEFAULT_EXTRACTOR is None:
            _DEFAULT_EXTRACTOR = QueryExtractor()
        return _DEFAULT_EXTRACTOR


def parse_query(
    query: str,
    config: str = DEFAULT_CONFIG,
    *,
    include_meta: bool = False,
    extractor: Optional[QueryExtractor] = None,
) -> Dict[str, Any]:
    """Extract category, filters, and residual from `query` using the specified `config`."""
    active_extractor = extractor if extractor is not None else get_default_extractor()
    return active_extractor.parse(query, config=config, include_meta=include_meta)
