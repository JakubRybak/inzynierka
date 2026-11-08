"""Category catalog, feature definitions, structured output schemas, and validation for query extraction."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

from feature_extraction.schema import allowed_values, load_schemas

ROOT = Path(__file__).resolve().parents[1]
LLM_PROMPTS_DIR = ROOT / "feature_extraction" / "llm" / "prompts"

EXCLUDED_FILTER_VALUES = {"Other", "Not Applicable", "Unknown"}
SINGLE_OPERATORS = ["in", "not_in"]
MULTI_OPERATORS = ["contains_any", "contains_all", "contains_none", "equals_set"]
PRICE_OPERATORS = ["lte", "gte", "around"]

CATEGORY_CRITERIA: Dict[str, str] = {
    "T-shirts": (
        "T-shirt, tee, tee shirt, koszulka, t-shirt, camiseta. Includes long-sleeve, short-sleeve, "
        "and sleeveless tees. Excludes collared tees/polos (Polos) and T-shirt dresses (Dresses)."
    ),
    "Polos": (
        "Polo shirt, polo, koszulka polo, polo shirt, or a collared tee (e.g. 'tee with a collar', 'collar tee')."
    ),
    "Tank tops & Camisoles": (
        "Tank top, camisole, cami, singlet, sleeveless strap top, top na ramiączkach, or generic 'top' / "
        "'crop top' / 'black top' when no more specific supported garment category is named."
    ),
    "Bodysuits": (
        "Bodysuit, body suit, one-piece top/leotard with snap crotch, body (Polish/Spanish garment)."
    ),
    "Shirts": (
        "Shirt, dress shirt, button-down shirt, button-up shirt, oxford shirt, flannel shirt, koszula, camisa. "
        "Excludes T-shirts (T-shirts), polo shirts (Polos), sweatshirts (Sweatshirts), and shirt dresses (Dresses)."
    ),
    "Blouses": (
        "Blouse, dressy blouse, peasant blouse, tunic blouse, bluzka, blusa."
    ),
    "Knit Sweaters": (
        "Sweater, knit sweater, pullover sweater, jumper, turtleneck sweater, mock-neck sweater, jersey, "
        "sweter, suéter. Excludes sweatshirts (Sweatshirts), hoodies/zip-ups (Hoodies & Zipups), "
        "cardigans (Cardigans), and sweater dresses (Dresses)."
    ),
    "Sweatshirts": (
        "Sweatshirt, crewneck sweatshirt, fleece sweatshirt without zip, bluza (when not a hoodie or zip-up), "
        "sudadera (without zip or hood-first 'hoodie' designation)."
    ),
    "Hoodies & Zipups": (
        "Hoodie, hooded sweatshirt, zip-up sweatshirt, zip-up hoodie, half-zip or quarter-zip pullover/sweatshirt, "
        "bluza z kapturem, bluza na suwak / rozpinana, bluza z krótkim zamkiem, sudadera con capucha / con cremallera."
    ),
    "Cardigans": (
        "Cardigan, button-front or open-front knit sweater, kardigan, rozpinany sweter, cárdigan."
    ),
    "Classic Coats": (
        "Coat, classic coat, overcoat, topcoat, peacoat, pea coat, parka, duffle coat, wool coat, winter coat, "
        "fur coat, down coat, płaszcz, parka, abrigo. Excludes trench coats (Trench Coats) and jackets (Jackets)."
    ),
    "Trench Coats": (
        "Trench coat, trench, gabardine trench, mac trench, trencz, gabardina."
    ),
    "Jackets": (
        "Jacket, denim/jean jacket, leather jacket, biker/moto jacket, windbreaker, puffer jacket, quilted jacket, "
        "field jacket, blazer/sport jacket, kurtka, chaqueta, cazadora. Excludes bomber jackets (Bombers) and vests (Vests)."
    ),
    "Bombers": (
        "Bomber jacket, bomber, flight jacket, varsity/letterman bomber, bomberka, cazadora bomber."
    ),
    "Vests": (
        "Vest, gilet, sleeveless jacket, bodywarmer, down vest, quilted vest, waistcoat, kamizelka, chaleco."
    ),
    "Trousers": (
        "Trousers, pants, dress pants, slacks, chinos, tailored pants, wide-leg pants, leather pants, "
        "spodnie (garniturowe/materiałowe/ogólne), pantalones. Excludes cargo pants (Cargo Pants), "
        "sweatpants/joggers (Sweatpants & Lounge Pants), jeans (Jeans), and shorts (Shorts)."
    ),
    "Cargo Pants": (
        "Cargo pants, cargo trousers, combat pants with utility cargo pockets, bojówki, pantalones cargo."
    ),
    "Sweatpants & Lounge Pants": (
        "Sweatpants, sweat pants, joggers, track pants, lounge pants, athletic fleece pants, "
        "spodnie dresowe, dresy, joggery, pantalones de chándal."
    ),
    "Jeans": (
        "Jeans, denim pants, dżinsy, jeansy, vaqueros."
    ),
    "Shorts": (
        "Shorts, denim shorts, cargo shorts, athletic/running/volleyball/gym shorts, sweatshorts, tailored shorts, "
        "bermuda shorts, szorty, krótkie spodenki, pantalones cortos."
    ),
    "Skirts": (
        "Skirt, mini/midi/maxi skirt, pleated skirt, wrap skirt, A-line skirt, spódnica, falda."
    ),
    "Dresses": (
        "Dress, gown, sundress, maxi/midi/mini dress, slip dress, shirt dress, T-shirt dress, sweater dress, "
        "sweatshirt dress, wrap dress, sukienka, vestido."
    ),
}

EXTRA_FEATURE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "gender": {
        "instruction": (
            "Explicitly requested target gender only. Do not infer Women from dresses, skirts, blouses, "
            "or camisoles. Do not map 'unisex', 'boys', 'girls', or 'kids' to Men or Women (keep those in residual)."
        ),
        "values": {
            "Men": "Explicitly for men (men, men's, mens, man, male, męski, męskie, hombre).",
            "Women": "Explicitly for women (women, women's, womens, woman, female, ladies, damski, damska, damskie, mujer).",
        },
    },
    "main_composition": {
        "instruction": (
            "Main garment fabric composition. '100% X' or 'only X' or 'pure X' uses equals_set ['X']. "
            "'0% X' or 'without X' / 'no X' / 'bez X' uses contains_none ['X']. Any share between 0% and 100% "
            "(e.g. '30% wool') or an unqualified material mention ('cotton', 'wool blend') uses contains_any. "
            "Two required materials ('cotton and elastane') use contains_all; alternatives ('cotton or linen') use contains_any. "
            "Do NOT map faux/vegan/PU/patent leather to Leather (keep 'faux leather' in residual). "
            "In Jackets & Coats, 'down' / 'puch' / 'plumas' refers to insulation=Down, not main_composition=Down."
        ),
        "values": {
            "Cotton": "Cotton, bawełna, algodón (excluding brand names like Cotton Citizen).",
            "Polyester": "Polyester, poliester, poliéster.",
            "Acrylic": "Acrylic, modacrylic, akryl, acrílico.",
            "Wool": "Wool, merino, lambswool, mohair, alpaca, angora, camel, wełna, lana.",
            "Viscose": "Viscose, rayon, cupro, modal, lyocell, tencel, bamboo, wiskoza, viscosa.",
            "Elastane": "Elastane, spandex, lycra, elastan, elastano (note: generic word 'stretch' alone stays in residual).",
            "Nylon": "Nylon, polyamide, poliamid, nailon.",
            "Silk": "Silk, jedwab, seda.",
            "Leather": "Real leather, genuine leather, suede, nubuck, lambskin, calfskin, skóra, cuero (NOT faux/vegan/patent leather).",
            "Cashmere": "Cashmere, kaszmir, cachemira.",
            "Linen": "Linen, flax, hemp, ramie, len, lniany, lino.",
            "Down": "Down/feathers as main composition (rare outside fill; in outerwear use insulation=Down instead).",
            "Fur": "Real fur, shearling fur exterior, pelo/futro (faux fur stays in residual unless main_composition Fur is explicitly meant).",
        },
    },
    "lining_composition": {
        "instruction": (
            "Lining material or unlined state for Jackets & Coats ONLY when lining is explicitly mentioned. "
            "'unlined' / 'bez podszewki' / 'sin forro' -> equals_set ['Unlined']. "
            "'with lining' / 'lined' / 'with inner warming lining' (without naming a supported lining material) -> contains_none ['Unlined']. "
            "'with silk lining' -> contains_any ['Silk']. 'with 100% silk lining' -> equals_set ['Silk']. "
            "'with cotton and viscose lining' -> contains_all ['Cotton', 'Viscose']. "
            "Note: 'fleece-lined' and 'shearling-lined' map to insulation (Fleece Lined / Shearling Lined), NOT lining_composition."
        ),
        "values": {
            "Cotton": "Cotton lining.",
            "Polyester": "Polyester lining.",
            "Acrylic": "Acrylic lining.",
            "Wool": "Wool lining.",
            "Viscose": "Viscose, cupro, rayon, acetate, modal, or lyocell lining.",
            "Elastane": "Elastane/spandex lining.",
            "Nylon": "Nylon or polyamide lining.",
            "Silk": "Silk lining.",
            "Leather": "Leather lining.",
            "Cashmere": "Cashmere lining.",
            "Linen": "Linen lining.",
            "Down": "Down lining.",
            "Fur": "Fur lining.",
            "Unlined": "Explicitly unlined (equals_set ['Unlined']), or negated when a lining is required (contains_none ['Unlined']).",
        },
    },
    "outerwear_fit": {
        "instruction": (
            "Intended fit for Jackets & Coats. Only Oversized and Regular exist in schema. "
            "Note: 'slim-fitting' or 'fitted' on a jacket/coat is NOT in schema and goes to residual."
        ),
        "values": {
            "Oversized": "Oversized, loose, boxy, relaxed fit (luźny, oversize, holgado).",
            "Regular": "Explicitly regular, standard, or classic fit (only when fit itself is described as regularfit/standard fit).",
        },
    },
    "skirt_dress_length": {
        "instruction": (
            "Skirt or dress hemline length. Do not confuse sleeve length with garment length."
        ),
        "values": {
            "Mini": "Mini, short skirt/dress ending above the knee (mini, krótka, corta/corto).",
            "Midi": "Midi, knee-length or calf-length skirt/dress (midi, do kolan, do połowy łydki).",
            "Maxi": "Maxi, long, ankle-length or floor-length skirt/dress or gown (maxi, długa, largo/larga).",
        },
    },
}


def load_query_catalog() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Build the query-extraction catalog for all 22 categories."""
    schemas, _ = load_schemas()
    common_prompts = json.loads((LLM_PROMPTS_DIR / "common.json").read_text(encoding="utf-8"))
    cat_prompts: Dict[str, Dict[str, Any]] = {}
    for path in sorted((LLM_PROMPTS_DIR / "categories").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cat_prompts[data["category"]] = data["features"]

    catalog: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for (_section, category), schema in sorted(schemas.items(), key=lambda item: item[0][1]):
        cat_dict: Dict[str, Dict[str, Any]] = {}
        for feature, spec in schema.items():
            values = [v for v in allowed_values(spec) if v not in EXCLUDED_FILTER_VALUES]
            multi = spec["type"] in ("multi_choice", "composition")
            operators = MULTI_OPERATORS if multi else SINGLE_OPERATORS

            if feature in common_prompts:
                prompt_def = common_prompts[feature]
            elif feature in cat_prompts.get(category, {}):
                prompt_def = cat_prompts[category][feature]
            elif feature == "fit" and set(values) == {"Oversized", "Regular"}:
                prompt_def = EXTRA_FEATURE_DEFINITIONS["outerwear_fit"]
            elif feature == "length" and set(values) == {"Mini", "Midi", "Maxi"}:
                prompt_def = EXTRA_FEATURE_DEFINITIONS["skirt_dress_length"]
            else:
                prompt_def = EXTRA_FEATURE_DEFINITIONS[feature]

            val_descriptions = {
                v: prompt_def["values"].get(v, v)
                for v in values
            }
            lines = [prompt_def["instruction"]]
            for v in values:
                lines.append(f"- {v}: {val_descriptions[v]}")

            # Add category-specific query extraction notes
            if category == "Hoodies & Zipups" and feature == "hood":
                lines.append(
                    "IMPORTANT: In Hoodies & Zipups, the word 'hoodie' / 'hoodies' / 'hooded' / 'z kapturem' / 'con capucha' "
                    "explicitly sets hood = With Hood. 'without a hood' / 'bez kaptura' sets hood = Without Hood. "
                    "A 'zip-up' or 'half-zip' without mentioning hoodie/hood leaves hood unspecified."
                )
            elif category == "Hoodies & Zipups" and feature == "closure_type":
                lines.append(
                    "IMPORTANT: 'zip-up' / 'zip up' / 'zipper' / 'na suwak' / 'con cremallera' -> Zip; "
                    "'half-zip' / 'quarter-zip' / 'z krótkim zamkiem' -> Half-Zip; 'pullover' -> Pullover."
                )
            elif category == "Classic Coats" and feature == "coat_style":
                lines.append(
                    "IMPORTANT: 'classic coat', 'overcoat', 'topcoat', 'pea coat', 'peacoat', 'chesterfield', 'car coat' "
                    "map to Standard (and specific sub-styles like 'pea coat'/'peacoat' also stay in residual). "
                    "'parka' maps to Parka. A generic 'coat' / 'płaszcz' / 'abrigo' alone does NOT set coat_style."
                )
            elif feature == "insulation":
                lines.append(
                    "IMPORTANT: 'down' / 'down-filled' / 'goose down' / 'puchowa' / 'plumas' maps to Down "
                    "(keep specific 'goose down' in residual). 'synthetic padding' / 'synthetic insulation' / "
                    "'synthetically padded' maps to Synthetic Padding (note: 'quilted' / 'puffer' / 'acolchado' "
                    "alone without stating down or synthetic stays in residual). 'shearling-lined' -> Shearling Lined; "
                    "'fleece-lined' -> Fleece Lined; 'uninsulated' / 'unpadded' -> Uninsulated."
                )
            elif category == "Sweatpants & Lounge Pants" and feature == "leg_shape":
                lines.append(
                    "IMPORTANT: 'joggers' / 'joggery' maps to leg_shape = Tapered AND keeps 'joggers' in residual."
                )
            elif feature == "leg_shape" and "Flared" in values:
                lines.append(
                    "IMPORTANT: 'bootcut' and 'bell bottom' map to leg_shape = Flared AND keep 'bootcut' / 'bell bottom' in residual."
                )
            elif feature == "neckline" and "High Neck" in values:
                lines.append(
                    "IMPORTANT: 'turtleneck', 'mock neck', 'funnel neck', 'golf', 'półgolf' map to neckline = High Neck "
                    "AND keep specific 'turtleneck' / 'mock neck' in residual."
                )
            elif category == "Shorts" and feature == "shorts_type":
                lines.append(
                    "IMPORTANT: Sport/running/volleyball/gym/compression/athletic shorts map to shorts_type = Athletic "
                    "AND keep the specific sport or 'compression' in residual (note: 'golf shorts' does not map to Athletic)."
                )
            elif feature == "colors":
                lines.append(
                    "IMPORTANT: Named color shades (e.g. 'navy', 'turquoise', 'burgundy', 'maroon', 'olive', 'khaki', "
                    "'emerald', 'coral', 'fuchsia', 'hot pink', 'lavender', 'lilac', 'mustard', 'rust', 'charcoal', "
                    "'heather grey', 'forest green', 'off-white', 'cream', 'ivory', 'camel', 'azul marino', 'azul celeste', "
                    "'jasnoniebieski', 'granatowy', 'bordowy') map to their parent color family in filters AND MUST ALSO "
                    "be kept in residual! However, an excluded shade ('not turquoise') stays ONLY in residual ('not turquoise') "
                    "with NO color family exclusion filter. 'all-black' / 'only black' uses equals_set ['Black']."
                )

            cat_dict[feature] = {
                "values": values,
                "multi": multi,
                "operators": operators,
                "instruction": prompt_def["instruction"],
                "value_descriptions": val_descriptions,
                "definition": "\n".join(lines),
            }
        catalog[category] = cat_dict
    return catalog


def build_cerebras_full_schema(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Build strict JSON schema (draft-07/OpenAI style) for full Step 2a extraction."""
    branches: List[Dict[str, Any]] = [
        {
            "type": "object",
            "properties": {
                "feature": {"type": "string", "enum": ["price"]},
                "operator": {"type": "string", "enum": PRICE_OPERATORS},
                "value": {"type": "number"},
            },
            "required": ["feature", "operator", "value"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "feature": {"type": "string", "enum": ["brand"]},
                "operator": {"type": "string", "enum": SINGLE_OPERATORS},
                "values": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["feature", "operator", "values"],
            "additionalProperties": False,
        },
    ]
    for feature, spec in catalog[category].items():
        branches.append(
            {
                "type": "object",
                "properties": {
                    "feature": {"type": "string", "enum": [feature]},
                    "operator": {"type": "string", "enum": spec["operators"]},
                    "values": {"type": "array", "items": {"type": "string", "enum": spec["values"]}},
                },
                "required": ["feature", "operator", "values"],
                "additionalProperties": False,
            }
        )
    return {
        "type": "object",
        "properties": {
            "filters": {"type": "array", "items": {"anyOf": branches}},
            "residual": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["filters", "residual"],
        "additionalProperties": False,
    }


def build_vertex_full_schema(category: str, catalog: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Build Vertex AI responseSchema for full Step 2a extraction."""
    branches: List[Dict[str, Any]] = [
        {
            "type": "OBJECT",
            "properties": {
                "feature": {"type": "STRING", "enum": ["price"]},
                "operator": {"type": "STRING", "enum": PRICE_OPERATORS},
                "value": {"type": "NUMBER", "minimum": 0},
            },
            "required": ["feature", "operator", "value"],
            "propertyOrdering": ["feature", "operator", "value"],
        },
        {
            "type": "OBJECT",
            "properties": {
                "feature": {"type": "STRING", "enum": ["brand"]},
                "operator": {"type": "STRING", "enum": SINGLE_OPERATORS},
                "values": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 1},
            },
            "required": ["feature", "operator", "values"],
            "propertyOrdering": ["feature", "operator", "values"],
        },
    ]
    for feature, spec in catalog[category].items():
        branches.append(
            {
                "type": "OBJECT",
                "properties": {
                    "feature": {"type": "STRING", "enum": [feature]},
                    "operator": {"type": "STRING", "enum": spec["operators"]},
                    "values": {
                        "type": "ARRAY",
                        "items": {"type": "STRING", "enum": spec["values"]},
                        "minItems": 1,
                    },
                },
                "required": ["feature", "operator", "values"],
                "propertyOrdering": ["feature", "operator", "values"],
            }
        )
    return {
        "type": "OBJECT",
        "properties": {
            "filters": {"type": "ARRAY", "items": {"anyOf": branches}},
            "residual": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["filters", "residual"],
        "propertyOrdering": ["filters", "residual"],
    }


def build_cerebras_auxiliary_schema() -> Dict[str, Any]:
    """Build strict JSON schema for Step 2b-2 auxiliary extraction (brand, price, residual only)."""
    return {
        "type": "object",
        "properties": {
            "filters": {
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "enum": ["price"]},
                                "operator": {"type": "string", "enum": PRICE_OPERATORS},
                                "value": {"type": "number"},
                            },
                            "required": ["feature", "operator", "value"],
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "enum": ["brand"]},
                                "operator": {"type": "string", "enum": SINGLE_OPERATORS},
                                "values": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["feature", "operator", "values"],
                            "additionalProperties": False,
                        },
                    ]
                },
            },
            "residual": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["filters", "residual"],
        "additionalProperties": False,
    }


def validate_response(
    data: Any,
    category: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
    *,
    auxiliary_only: bool = False,
) -> Dict[str, Any]:
    """Validate and normalize structured LLM output."""
    if not isinstance(data, dict) or set(data.keys()) != {"filters", "residual"}:
        raise ValueError(f"Expected root keys {{'filters', 'residual'}}, got {list(data) if isinstance(data, dict) else type(data)}")
    if not isinstance(data["filters"], list):
        raise ValueError("filters must be a list")
    if not isinstance(data["residual"], list) or not all(isinstance(x, str) for x in data["residual"]):
        raise ValueError("residual must be a list of strings")

    cat_spec = catalog[category]
    cleaned_filters: List[Dict[str, Any]] = []
    for clause in data["filters"]:
        if not isinstance(clause, dict):
            raise ValueError("Filter clause must be a dict")
        feat = clause.get("feature")
        op = clause.get("operator")
        if feat == "price":
            val = clause.get("value")
            if (
                set(clause.keys()) != {"feature", "operator", "value"}
                or op not in PRICE_OPERATORS
                or type(val) not in (int, float)
                or not math.isfinite(val)
                or val < 0
            ):
                raise ValueError(f"Invalid price filter: {clause!r}")
            cleaned_filters.append({"feature": "price", "operator": op, "value": int(val) if float(val).is_integer() else float(val)})
        elif feat == "brand":
            vals = clause.get("values")
            if (
                set(clause.keys()) != {"feature", "operator", "values"}
                or op not in SINGLE_OPERATORS
                or not isinstance(vals, list)
                or not vals
                or not all(isinstance(v, str) and v.strip() for v in vals)
            ):
                raise ValueError(f"Invalid brand filter: {clause!r}")
            dedup = list(dict.fromkeys(v.strip() for v in vals))
            cleaned_filters.append({"feature": "brand", "operator": op, "values": dedup})
        else:
            if auxiliary_only:
                raise ValueError(f"Auxiliary parser returned non-auxiliary feature: {feat!r}")
            if feat not in cat_spec:
                raise ValueError(f"Unsupported feature {feat!r} for category {category!r}")
            spec = cat_spec[feat]
            vals = clause.get("values")
            if (
                set(clause.keys()) != {"feature", "operator", "values"}
                or op not in spec["operators"]
                or not isinstance(vals, list)
                or not vals
                or not all(isinstance(v, str) and v in spec["values"] for v in vals)
            ):
                raise ValueError(f"Invalid categorical filter for {category}: {clause!r}")
            dedup = list(dict.fromkeys(vals))
            if op == "contains_all" and len(dedup) == 1:
                op = "contains_any"
            cleaned_filters.append({"feature": feat, "operator": op, "values": dedup})

    cleaned_residual = [ item.strip() for item in data["residual"] if item and item.strip() ]
    return {"filters": cleaned_filters, "residual": cleaned_residual}
