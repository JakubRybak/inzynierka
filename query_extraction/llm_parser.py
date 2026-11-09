"""LLM clients (Vertex AI Gemini 3.5 Flash-Lite & Cerebras Qwen 3.8 27B / GPT-OSS-120B) and prompt builders."""

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

from .catalog import (
    build_cerebras_auxiliary_schema,
    build_cerebras_full_schema,
    build_vertex_full_schema,
    validate_response,
)
from .few_shots import PER_CATEGORY_FEW_SHOTS

ROOT = Path(__file__).resolve().parents[1]
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
    """Return narrow sub-style residual rules strictly applicable to the given category."""
    rules: List[str] = [
        "   - Specific pattern sub-styles that map to a broader pattern filter stay in residual: e.g. 'leopard print' (maps to pattern=Animal Print AND stays in residual).",
    ]
    if "neckline" in cat_features and "High Neck" in cat_features["neckline"]["values"]:
        rules.append(
            "   - Specific high-neck styles ('turtleneck', 'mock neck', 'funnel neck') map to neckline=High Neck AND stay in residual."
        )
    if category == "Shirts":
        rules.append(
            "   - In Shirts: 'dress shirt' puts 'dress' in residual; 'button-down', 'button-up', 'oxford', 'flannel' stay in residual."
        )
    if category == "Classic Coats":
        rules.append(
            "   - In Classic Coats: 'pea coat' / 'peacoat' maps to coat_style=Standard AND stays in residual."
        )
    if "insulation" in cat_features:
        rules.append(
            "   - In Jackets & Coats: 'goose down' maps to insulation=Down AND stays in residual; 'quilted' / 'puffer' without stating down or synthetic stays in residual."
        )
    if "leg_shape" in cat_features and "Flared" in cat_features["leg_shape"]["values"]:
        rules.append(
            "   - 'bootcut' and 'bell bottom' map to leg_shape=Flared AND stay in residual."
        )
    if category == "Sweatpants & Lounge Pants":
        rules.append(
            "   - In Sweatpants & Lounge Pants: 'joggers' / 'joggery' maps to leg_shape=Tapered AND stays in residual."
        )
    if category == "Shorts":
        rules.append(
            "   - In Shorts: specific sports ('running', 'volleyball', 'gym', 'compression') map to shorts_type=Athletic AND stay in residual."
        )
    if category == "Skirts":
        rules.append(
            "   - In Skirts: 'pencil' maps to skirt_silhouette=Fitted AND stays in residual."
        )
    return rules


def build_full_system_prompt(
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Build a Step 2a full-extraction system prompt strictly scoped to the given category."""
    cat_spec = catalog[category]
    single_feats = [f for f, s in cat_spec.items() if not s["multi"]]
    multi_feats = [f for f, s in cat_spec.items() if s["multi"]]

    defs = []
    for feature, spec in cat_spec.items():
        op_kind = "multi-choice / composition" if spec["multi"] else "single-choice"
        defs.append(f"### {feature} ({op_kind}; operators: {', '.join(spec['operators'])})\n{spec['definition']}")
    defs_text = "\n\n".join(defs)

    equals_set_examples = "'only', 'exclusively', 'pure', '100% <material>' ('100% cotton' -> equals_set ['Cotton']), or 'all-<color>' ('all-black' -> equals_set ['Black'])"
    if "lining_composition" in cat_spec:
        equals_set_examples += ", or 'unlined' (lining_composition equals_set ['Unlined'])"

    substyle_lines = "\n".join(_category_narrow_substyle_rules(category, cat_spec))
    shots = PER_CATEGORY_FEW_SHOTS[category]
    examples_text = "\n".join(
        f"Category: {category}\nQuery: {ex['query']}\nOutput: {json.dumps(ex['output'], ensure_ascii=False)}\n"
        for ex in shots
    )

    return (
        f"You convert a shopping query (in English, Polish, or Spanish) for the ALREADY selected category '{category}' "
        f"into hard catalog filters for '{category}' and a list of residual ranking concepts.\n"
        f"The category '{category}' is fixed. Use ONLY the features and exact allowed values defined for '{category}'.\n\n"
        "OUTPUT FORMAT\n"
        "Return JSON with exactly 'filters' and 'residual'.\n"
        "- Categorical filters: {\"feature\": \"<feature>\", \"operator\": \"<op>\", \"values\": [\"<label>\", ...]}\n"
        "- Price filters: {\"feature\": \"price\", \"operator\": \"lte\" | \"gte\" | \"around\", \"value\": <number>}\n"
        "- Residual: [\"<concept 1>\", ...] (empty array [] when no residual concepts remain).\n\n"
        f"FILTER RULES FOR {category.upper()}\n"
        "1. Extract only requirements explicitly expressed in the query. Never infer unmentioned features from the garment category or from another feature.\n"
        f"2. Single-choice features ({', '.join(single_feats)}) and 'brand' use 'in' (positive, OR for multiple values) and 'not_in' (explicit exclusions).\n"
        f"3. Multi-choice / composition features ({', '.join(multi_feats)}) use:\n"
        "   - 'contains_any': single requested value, OR alternatives ('white or black', 'cotton or linen'), or material percentage between 0% and 100% ('30% wool').\n"
        "   - 'contains_all': conjunctions requiring all listed values together ('black and white', 'cotton and elastane').\n"
        "   - 'contains_none': explicit exclusions ('without polyester', 'no red', '0% wool').\n"
        f"   - 'equals_set': exact set required via {equals_set_examples}.\n"
        "4. Positive and negative clauses on the same feature are separate filter objects combined with AND.\n"
        "5. Brand: use conventional brand capitalization (e.g. 'Nike', 'Adidas', 'Calvin Klein', 'Levi\\'s', 'Under Armour', 'ASICS'). "
        "'Off-White' in 'by Off-White' is a brand; 'off-white' as a color is a shade (White + residual 'off-white').\n"
        "6. Price: preserve decimal numbers, ignore currency symbols/names without conversion:\n"
        "   - up to / under / below / less than / at most / do / <= X -> 'lte'\n"
        "   - at least / over / above / more than / minimum / od / >= X -> 'gte'\n"
        "   - between X and Y / from X to Y -> two clauses: 'gte' X and 'lte' Y\n"
        "   - around X / approximately X / za około X -> 'around'\n"
        "   Never treat sizes ('2x', '34 x 28', '20'), pack counts, model numbers ('501'), or material percentages as prices.\n\n"
        f"RESIDUAL RULES FOR {category.upper()}\n"
        "1. Residual is a list of strings (one string per independent concept, in query order, preserving the query's language).\n"
        f"2. Omit the '{category}' garment category noun, and omit requirements fully captured by filters (basic colors, materials, percentages, brands, prices, currencies, genders, fits, lengths).\n"
        "3. KEEP in residual any specific sub-concept that is narrower than the assigned catalog filter bucket:\n"
        "   - Specific color shades map to their color family filter AND stay in residual: 'turquoise' (Blue), 'navy' / 'navy blue' / "
        "'azul marino' / 'granatowy' (Blue), 'azul celeste' / 'jasnoniebieski' (Blue), 'burgundy' / 'maroon' / 'bordowy' (Red), "
        "'olive' / 'forest green' / 'khaki' / 'emerald' (Green), 'hot pink' / 'fuchsia' / 'coral' (Pink), 'heather grey' / 'charcoal' (Grey), "
        "'off-white' / 'cream' / 'ivory' (White), 'camel' (Brown), 'mustard' (Yellow), 'lavender' / 'lilac' (Purple). "
        "(Basic color words like 'blue', 'black', 'white', 'red', 'green', 'grey', 'pink', 'brown', 'yellow', 'purple', 'orange', 'beige' do NOT go to residual.)\n"
        "   - Excluded shade ('not turquoise', 'not emerald') stays in residual with NO color filter.\n"
        f"{substyle_lines}\n"
        "4. Keep unsupported attributes in residual: sizes ('2x', '3xl', '34 x 28', 'tall', 'plus', 'big and tall'), target age ('boys', 'girls', 'kids', 'unisex'), "
        "fabric/construction details ('soft', 'lace', 'faux leather', 'stretch', 'with pockets', 'quilted', 'ribbed', 'fleece'), occasions ('for hiking', 'for work', 'for summer'), "
        "and graphics/themes ('star wars', 'nirvana', 'vintage', 'boho').\n\n"
        f"SUPPORTED FEATURES AND DEFINITIONS FOR {category.upper()}\n"
        f"{defs_text}\n\n"
        f"FEW-SHOT EXAMPLES (Category: {category})\n"
        f"{examples_text}"
    )


def build_auxiliary_system_prompt(
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Build a Step 2b.2 auxiliary system prompt strictly scoped to the given category."""
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

    return (
        f"You are Step 2.2 of a two-stage shopping query parser for the ALREADY selected category '{category}'. "
        f"Step 2.1 (a closed-vocabulary classifier) already extracted the catalog feature filters for '{category}'.\n"
        "Your task is ONLY to extract:\n"
        "1. 'filters': explicitly requested 'brand' ('in', 'not_in') and numeric 'price' ('lte', 'gte', 'around') filters.\n"
        f"2. 'residual': a list of independent concepts (in query order, in the query's language) not fully represented by '{category}', brand, price, or '{category}' closed-vocabulary catalog filters.\n\n"
        f"CLOSED-VOCABULARY FEATURES FOR {category.upper()} (handled in Step 2.1)\n"
        f"{json.dumps(vocab, ensure_ascii=False)}\n\n"
        "BRAND & PRICE RULES\n"
        "- Brand: {\"feature\": \"brand\", \"operator\": \"in\" | \"not_in\", \"values\": [\"<Brand>\"]}. Use conventional capitalization "
        "(e.g. 'Nike', 'Adidas', 'Calvin Klein', 'Levi\\'s', 'Under Armour', 'ASICS', 'Champion').\n"
        "- Price: {\"feature\": \"price\", \"operator\": \"lte\" | \"gte\" | \"around\", \"value\": <number>}.\n"
        "  * up to / under / below / less than / at most / do / <= X -> 'lte'\n"
        "  * at least / over / above / more than / minimum / od / >= X -> 'gte'\n"
        "  * between X and Y / from X to Y -> two clauses: 'gte' X and 'lte' Y\n"
        "  * around X / approximately X / za około X -> 'around'\n"
        "  Ignore currency symbols/names without conversion. Never treat sizes ('2x', '34 x 28', '20'), model numbers ('501'), "
        "or material percentages ('100%', '0%') as prices.\n\n"
        f"RESIDUAL RULES FOR {category.upper()}\n"
        "- Return an array of strings, one per independent concept, in query order, preserving the original language.\n"
        f"- Omit the '{category}' garment category noun, extracted brands, extracted prices/currencies, material percentages, and attributes "
        f"fully captured by '{category}' closed-vocabulary filters.\n"
        "- IMPORTANT — KEEP narrow sub-concepts in residual even when their parent bucket was extracted in Step 2.1:\n"
        "  * Named color shades MUST stay in residual: 'turquoise', 'navy', 'navy blue', 'azul marino', 'granatowy', 'azul celeste', "
        "'jasnoniebieski', 'burgundy', 'maroon', 'bordowy', 'olive', 'forest green', 'khaki', 'emerald', 'hot pink', 'fuchsia', "
        "'coral', 'heather grey', 'charcoal', 'off-white', 'cream', 'ivory', 'camel', 'mustard', 'lavender', 'lilac'. "
        "(Basic color names like 'black', 'white', 'blue', 'red', 'green', 'grey', 'pink', 'brown', 'yellow', 'purple', 'orange', 'beige' are NOT shades and must be omitted.)\n"
        "  * Excluded shades ('not turquoise', 'not emerald') stay in residual.\n"
        f"{substyle_lines}\n"
        "- Keep all unsupported concepts in residual: sizes ('2x', '3xl', '34 x 28', 'tall', 'plus', 'big and tall'), age/group "
        "('boys', 'girls', 'kids', 'unisex'), fabric/construction details ('soft', 'lace', 'faux leather', 'stretch', 'with pockets', "
        "'quilted', 'ribbed', 'fleece'), occasions ('for hiking', 'for work', 'for summer'), and graphics/themes ('star wars', 'nirvana', 'vintage', 'boho').\n\n"
        f"FEW-SHOT EXAMPLES (Category: {category})\n"
        f"{examples_text}"
    )


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
    return f"Category: {category}\nQuery: {query}"


def build_auxiliary_user_message(
    query: str,
    category: str,
    jev_filters: List[Dict[str, Any]],
    catalog: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> str:
    return (
        f"Category: {category}\n"
        f"Already Extracted Catalog Filters: {json.dumps(jev_filters, ensure_ascii=False)}\n"
        f"Query: {query}"
    )


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
            t0 = time.perf_counter()
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=(10.0, self.timeout),
                allow_redirects=False,
            )
            elapsed = time.perf_counter() - t0
            if not response.ok:
                raise RuntimeError(f"Vertex AI HTTP {response.status_code}: {response.text[:400]}")
            raw = response.json()

        candidates = raw.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Vertex AI returned no candidates: {raw}")
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        parsed_raw = json.loads(text)
        validated = validate_response(parsed_raw, category, catalog, auxiliary_only=False)

        usage = raw.get("usageMetadata", {})
        in_rate, out_rate = PRICING[self.model]
        prompt_tokens = usage.get("promptTokenCount", 0)
        out_tokens = usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)
        cost = prompt_tokens * in_rate + out_tokens * out_rate
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
                response = self.session.post(
                    CEREBRAS_ENDPOINT,
                    json=payload,
                    timeout=(10.0, self.timeout),
                    allow_redirects=False,
                )
                elapsed = time.perf_counter() - t0

                if response.status_code == 429 and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if not response.ok:
                    safe_text = response.text.replace(self.api_key, "[REDACTED]")
                    raise RuntimeError(f"Cerebras ({self.model}) HTTP {response.status_code}: {safe_text[:400]}")
                raw = response.json()
                break

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
        validated = validate_response(parsed_raw, category, catalog, auxiliary_only=False)
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

    def extract_auxiliary(
        self,
        query: str,
        category: str,
        jev_filters: List[Dict[str, Any]],
        catalog: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> LLMCallResult:
        schema = build_cerebras_auxiliary_schema()
        sys_prompt = build_auxiliary_system_prompt(category, catalog)
        user_msg = build_auxiliary_user_message(query, category, jev_filters, catalog)
        parsed_raw, elapsed, usage = self._post_structured(
            sys_prompt, user_msg, "query_auxiliary_extraction", schema
        )
        validated = validate_response(parsed_raw, category, catalog, auxiliary_only=True)
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

    def warmup_full(self, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> float:
        res = self.extract_full("black t-shirt", "T-shirts", catalog)
        return res.latency_seconds

    def warmup_auxiliary(self, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> float:
        res = self.extract_auxiliary(
            "black t-shirt",
            "T-shirts",
            [{"feature": "colors", "operator": "contains_any", "values": ["Black"]}],
            catalog,
        )
        return res.latency_seconds
