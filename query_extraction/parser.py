"""Public query extraction API and pipeline configuration registry."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

if TYPE_CHECKING:
    from .jev_parser import JevClient
    from .llm_parser import CerebrasClient, VertexGeminiClient

DEFAULT_CONFIG = "2a_qwen"
GEMINI_MODEL = "gemini-3.5-flash-lite"
QWEN_MODEL = "qwen-3.8-27b"
GPT_OSS_MODEL = "gpt-oss-120b"

CONFIGS: Dict[str, Dict[str, Any]] = {
    "2a_qwen": {
        "name": "2a_qwen",
        "legacy_key": "2a_qwen_3_8_27b",
        "approach": "2a",
        "provider": "cerebras",
        "model": QWEN_MODEL,
        "reasoning_effort": "none",
        "stage_key": "2a_qwen",
        "required_stages": ("jev_category", "2a_qwen"),
        "label": "2a · Jev Cat → Qwen 3.8 27B (Cerebras)",
        "stage_description": "Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)",
        "model_description": "`qwen-3.8-27b` (Cerebras, `none`)",
    },
    "2a_gpt_oss": {
        "name": "2a_gpt_oss",
        "legacy_key": "2a_gpt_oss_120b",
        "approach": "2a",
        "provider": "cerebras",
        "model": GPT_OSS_MODEL,
        "reasoning_effort": "low",
        "stage_key": "2a_gpt_oss",
        "required_stages": ("jev_category", "2a_gpt_oss"),
        "label": "2a · Jev Cat → GPT-OSS-120B (Cerebras)",
        "stage_description": "Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)",
        "model_description": "`gpt-oss-120b` (Cerebras, `low`)",
    },
    "2a_gemini": {
        "name": "2a_gemini",
        "legacy_key": "2a_gemini_flash_lite",
        "approach": "2a",
        "provider": "vertex",
        "model": GEMINI_MODEL,
        "reasoning_effort": "none",
        "stage_key": "2a_gemini",
        "required_stages": ("jev_category", "2a_gemini"),
        "label": "2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)",
        "stage_description": "Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)",
        "model_description": "`gemini-3.5-flash-lite` (Vertex AI)",
    },
    "2b_qwen": {
        "name": "2b_qwen",
        "legacy_key": "2b_jev_qwen_3_8_27b",
        "approach": "2b",
        "provider": "cerebras",
        "model": QWEN_MODEL,
        "reasoning_effort": "none",
        "stage_key": "2b_qwen_aux",
        "required_stages": ("jev_category", "jev_features", "2b_qwen_aux"),
        "label": "2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)",
        "stage_description": "Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)",
        "model_description": "`qwen-3.8-27b` (Cerebras, `none`)",
    },
    "2b_gpt_oss": {
        "name": "2b_gpt_oss",
        "legacy_key": "2b_jev_gpt_oss_120b",
        "approach": "2b",
        "provider": "cerebras",
        "model": GPT_OSS_MODEL,
        "reasoning_effort": "low",
        "stage_key": "2b_gpt_oss_aux",
        "required_stages": ("jev_category", "jev_features", "2b_gpt_oss_aux"),
        "label": "2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)",
        "stage_description": "Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)",
        "model_description": "`gpt-oss-120b` (Cerebras, `low`)",
    },
}

CONFIG_ALIASES: Dict[str, str] = {}
for _canonical, _spec in CONFIGS.items():
    CONFIG_ALIASES[_canonical] = _canonical
    CONFIG_ALIASES[_spec["legacy_key"]] = _canonical


def resolve_config_name(config: str) -> str:
    """Resolve a configuration name or legacy alias to its canonical key in CONFIGS."""
    key = config.strip()
    if key not in CONFIG_ALIASES:
        valid = ", ".join(sorted(CONFIGS.keys()))
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
    s_cat = stages["jev_category"]
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
    if spec["approach"] == "2a":
        s_llm = stages[stage_key]
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

    s_feat = stages["jev_features"]
    s_aux = stages[stage_key]
    t2_1 = float(s_feat["latency_seconds"])
    c2_1 = float(s_feat["cost_usd"])
    t_aux = float(s_aux["latency_seconds"])
    c_aux = float(s_aux["cost_usd"])
    return {
        "predicted": {
            "category": cat,
            "filters": list(s_feat["filters"]) + list(s_aux["filters"]),
            "residual": list(s_aux["residual"]),
        },
        "step1_latency_seconds": t1,
        "step2_1_latency_seconds": t2_1,
        "step2_llm_latency_seconds": t_aux,
        "total_latency_seconds": round(t1 + t2_1 + t_aux, 4),
        "total_cost_usd": round(c1 + c2_1 + c_aux, 6),
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
            from .catalog import load_query_catalog

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
                from .jev_parser import JevClient

                self._jev_client = JevClient(budget_usd=self.jev_budget_usd)
            return self._jev_client

    def _get_gemini(self) -> VertexGeminiClient:
        with self._lock:
            if self._gemini_client is None:
                from .llm_parser import VertexGeminiClient

                self._gemini_client = VertexGeminiClient()
            return self._gemini_client

    def _get_cerebras(self, spec: Dict[str, Any]) -> CerebrasClient:
        model = spec["model"]
        with self._lock:
            if model not in self._cerebras_clients:
                from .llm_parser import CerebrasClient

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
        from .jev_parser import (
            category_payload,
            feature_payload,
            filters_from_answers,
        )

        canon = resolve_config_name(config)
        spec = CONFIGS[canon]
        jev = self._get_jev()

        cat_res = jev.call(category_payload(query))
        choice = cat_res.answers["category"]["choice"]
        category = None if choice == "outside" else choice

        stages: Dict[str, Any] = {
            "jev_category": {
                "category": category,
                "latency_seconds": round(cat_res.latency_seconds, 4),
                "cost_usd": round(cat_res.cost_usd, 6),
            }
        }

        if category is not None:
            if spec["approach"] == "2a":
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
                fp, fmap = feature_payload(query, category, self.catalog)
                feat_res = jev.call(fp)
                jev_filters = filters_from_answers(feat_res.answers, category, self.catalog, fmap)
                stages["jev_features"] = {
                    "filters": jev_filters,
                    "latency_seconds": round(feat_res.latency_seconds, 4),
                    "cost_usd": round(feat_res.cost_usd, 6),
                }
                aux_res = self._get_cerebras(spec).extract_auxiliary(
                    query, category, jev_filters, self.catalog
                )
                stages[spec["stage_key"]] = {
                    "filters": aux_res.parsed["filters"],
                    "residual": aux_res.parsed["residual"],
                    "latency_seconds": round(aux_res.latency_seconds, 4),
                    "cost_usd": round(aux_res.cost_usd, 6),
                }

        assembled = assemble_stage_prediction(stages, canon)
        result = dict(assembled["predicted"])
        if include_meta:
            result["_meta"] = {
                "config": canon,
                "label": spec["label"],
                "step1_latency_seconds": assembled["step1_latency_seconds"],
                "step2_1_latency_seconds": assembled["step2_1_latency_seconds"],
                "step2_llm_latency_seconds": assembled["step2_llm_latency_seconds"],
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
