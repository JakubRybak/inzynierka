import os
import sys
import json
import time
import csv
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from google import genai
from google.genai import types

# Domyślny model do testów: Gemini 3.5 Flash Lite (lub przez GEMINI_MODEL)
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
BENCHMARK_CSV = os.environ.get("BENCHMARK_CSV", "fashion_test_benchmark.csv")
LIMIT = int(os.environ.get("LIMIT", "0"))  # 0 oznacza wszystkie 80 zapytań

# ==============================================================================
# 1. DEFINICJA 8 KATEGORII ORAZ DYSKRETNYCH SCHEMATÓW PYDANTIC
# ==============================================================================

ALLOWED_CATEGORIES = [
    "Jackets & Coats",
    "Hoodies & Sweatshirts",
    "Sweaters & Cardigans",
    "Shirts & Blouses",
    "T-Shirts & Tops",
    "Pants & Trousers",
    "Dresses",
    "Footwear"
]

class CategorySelection(BaseModel):
    category: str = Field(description="Selected fashion category from the allowed list, or 'None' if out of scope.")
    confidence: float = Field(default=1.0, description="Confidence score between 0.0 and 1.0.")

# Bazowa klasa z cechami globalnymi dla każdego ubrania (wielowartościowe listy + operatory)
class BaseFashionExtraction(BaseModel):
    department_gender: Optional[Literal["Women", "Men", "Kids", "Unisex"]] = Field(
        default=None, description="Gender / department"
    )
    colors: Optional[List[Literal[
        "Black", "White", "Blue", "Navy", "Grey", "Beige / Cream", "Brown", "Red", "Pink", "Green", "Yellow", "Orange", "Purple", "Multicolor"
    ]]] = Field(default=None, description="List of colors mentioned in the query")
    color_operator: Optional[Literal["AND", "OR"]] = Field(
        default=None, description="'AND' if multi-color item (e.g. black and white). 'OR' if alternative (e.g. black or navy). Leave null if single color."
    )
    pattern: Optional[List[Literal[
        "Solid", "Striped", "Plaid / Checked", "Floral", "Graphic / Print", "Animal Print"
    ]]] = Field(default=None, description="Pattern or print")
    materials: Optional[List[Literal[
        "Cotton", "Denim", "Leather / Faux Leather", "Linen", "Wool", "Fleece", "Silk / Satin", "Synthetic / Polyester", "Corduroy"
    ]]] = Field(default=None, description="List of fabrics / materials mentioned in query")
    material_operator: Optional[Literal["AND", "OR"]] = Field(
        default=None, description="'OR' if alternative (e.g. linen or cotton). 'AND' if blended fabric / lining. Leave null if single material."
    )
    brands: Optional[List[str]] = Field(
        default=None, description="Brand or manufacturer names if explicitly mentioned in query. Leave null if no brand is mentioned."
    )
    residual_text: str = Field(
        default="", description="Any leftover terms: occasions, subjective styles, or unmapped text (do not include brand if captured in brands field)"
    )

# 8 Dedykowanych klas z cechami specyficznymi dla danej kategorii
class JacketsCoatsExtraction(BaseFashionExtraction):
    closure_type: Optional[List[Literal["Zipper", "Buttons", "Belt / Tie", "Snap Buttons", "Pull-over / No Closure"]]] = None
    hood: Optional[Literal["Yes", "No"]] = None
    length: Optional[List[Literal["Short (crop / hip)", "Medium (thigh)", "Long (knee / trench)"]]] = None
    insulation: Optional[List[Literal["Lightweight / Transitional", "Insulated / Winter"]]] = None

class HoodiesSweatshirtsExtraction(BaseFashionExtraction):
    hood: Optional[Literal["Yes", "No"]] = None
    closure_type: Optional[List[Literal["Pullover", "Zip-up"]]] = None
    front_pocket: Optional[Literal["Kangaroo Pocket", "No Pocket"]] = None

class SweatersCardigansExtraction(BaseFashionExtraction):
    neckline: Optional[List[Literal["Turtleneck / High Neck", "Crew Neck / Round", "V-Neck"]]] = None
    closure_type: Optional[List[Literal["Pullover", "Button-up (Cardigan)", "Open Front / No Closure"]]] = None
    knit_style: Optional[List[Literal["Fine Knit", "Chunky / Cable Knit"]]] = None

class ShirtsBlousesExtraction(BaseFashionExtraction):
    collar: Optional[List[Literal["Classic Collar", "Stand Collar / Mandarin", "Collarless"]]] = None
    sleeve_length: Optional[List[Literal["Short Sleeve", "Long Sleeve", "Sleeveless"]]] = None
    closure_type: Optional[List[Literal["Full Button Front", "Partial Button", "Pull-over / No Buttons"]]] = None
    fit: Optional[List[Literal["Slim Fit", "Regular Fit", "Relaxed / Oversized"]]] = None

class TShirtsTopsExtraction(BaseFashionExtraction):
    neckline: Optional[List[Literal["Crew Neck / Round", "V-Neck", "Square Neck"]]] = None
    sleeve_length: Optional[List[Literal["Short Sleeve", "Long Sleeve", "Sleeveless / Tank Top"]]] = None
    closure_type: Optional[List[Literal["Pull-over / No Buttons", "Partial Button (Polo)"]]] = None
    length: Optional[List[Literal["Regular Length", "Crop Top"]]] = None

class PantsTrousersExtraction(BaseFashionExtraction):
    pant_type: Optional[List[Literal["Jeans", "Cargo", "Chinos / Trousers", "Sweatpants / Joggers", "Shorts", "Leggings"]]] = None
    leg_fit: Optional[List[Literal["Skinny", "Slim", "Straight", "Wide Leg", "Flare / Bootcut"]]] = None
    rise: Optional[List[Literal["High Rise", "Mid Rise", "Low Rise"]]] = None
    length: Optional[List[Literal["Full Length", "Cropped / Ankle", "Shorts"]]] = None

class DressesExtraction(BaseFashionExtraction):
    length: Optional[List[Literal["Mini", "Midi", "Maxi"]]] = None
    sleeve_length: Optional[List[Literal["Sleeveless / Straps", "Short Sleeve", "Long Sleeve", "Off-Shoulder"]]] = None
    neckline: Optional[List[Literal["V-Neck", "Round / Crew Neck", "Square Neck"]]] = None
    silhouette: Optional[List[Literal["A-Line / Flared", "Fitted / Bodycon", "Straight / Shift", "Wrap"]]] = None

class FootwearExtraction(BaseFashionExtraction):
    shaft_height: Optional[List[Literal["Low (sneakers / shoes)", "Mid (ankle boot)", "High (knee-high / tall boot)"]]] = None
    fastening: Optional[List[Literal["Lace-up", "Slip-on", "Zipper", "Buckle / Straps"]]] = None
    heel_sole_type: Optional[List[Literal["Flat", "Heeled (Stiletto / Block)", "Platform / Chunky"]]] = None
    toe_style: Optional[List[Literal["Closed Toe", "Open Toe (Sandals)"]]] = None

CATEGORY_MODELS = {
    "Jackets & Coats": JacketsCoatsExtraction,
    "Hoodies & Sweatshirts": HoodiesSweatshirtsExtraction,
    "Sweaters & Cardigans": SweatersCardigansExtraction,
    "Shirts & Blouses": ShirtsBlousesExtraction,
    "T-Shirts & Tops": TShirtsTopsExtraction,
    "Pants & Trousers": PantsTrousersExtraction,
    "Dresses": DressesExtraction,
    "Footwear": FootwearExtraction,
}

# ==============================================================================
# 2. PRZYKŁADY FEW-SHOT DLA FAZY 2 (DEDYKOWANE PER KATEGORIA, ZERO WYCIEKU DANYCH)
# ==============================================================================

FEW_SHOT_EXAMPLES = {
    "Jackets & Coats": {
        "query": "men's vintage brown leather bomber jacket with zipper",
        "output": {
            "department_gender": "Men",
            "colors": ["Brown"],
            "color_operator": None,
            "materials": ["Leather / Faux Leather"],
            "material_operator": None,
            "closure_type": ["Zipper"],
            "hood": None,
            "length": None,
            "insulation": None,
            "pattern": None,
            "brands": None,
            "residual_text": "vintage bomber"
        }
    },
    "Hoodies & Sweatshirts": {
        "query": "women's oversized grey fleece hoodie with kangaroo pocket",
        "output": {
            "department_gender": "Women",
            "colors": ["Grey"],
            "color_operator": None,
            "materials": ["Fleece"],
            "material_operator": None,
            "hood": "Yes",
            "front_pocket": "Kangaroo Pocket",
            "closure_type": None,
            "pattern": None,
            "brands": None,
            "residual_text": "oversized"
        }
    },
    "Sweaters & Cardigans": {
        "query": "chunky cable knit turtleneck sweater for women in beige",
        "output": {
            "department_gender": "Women",
            "colors": ["Beige / Cream"],
            "color_operator": None,
            "neckline": ["Turtleneck / High Neck"],
            "knit_style": ["Chunky / Cable Knit"],
            "closure_type": None,
            "materials": None,
            "material_operator": None,
            "pattern": None,
            "brands": None,
            "residual_text": ""
        }
    },
    "Shirts & Blouses": {
        "query": "men's blue and white striped short sleeve slim fit button down shirt",
        "output": {
            "department_gender": "Men",
            "colors": ["Blue", "White"],
            "color_operator": "AND",
            "pattern": ["Striped"],
            "sleeve_length": ["Short Sleeve"],
            "collar": ["Classic Collar"],
            "closure_type": ["Full Button Front"],
            "fit": ["Slim Fit"],
            "materials": None,
            "material_operator": None,
            "brands": None,
            "residual_text": ""
        }
    },
    "T-Shirts & Tops": {
        "query": "women's black ribbed crop tank top v neck",
        "output": {
            "department_gender": "Women",
            "colors": ["Black"],
            "color_operator": None,
            "neckline": ["V-Neck"],
            "sleeve_length": ["Sleeveless / Tank Top"],
            "length": ["Crop Top"],
            "closure_type": ["Pull-over / No Buttons"],
            "pattern": None,
            "materials": None,
            "material_operator": None,
            "brands": None,
            "residual_text": "ribbed"
        }
    },
    "Pants & Trousers": {
        "query": "women's high rise beige linen or cotton flare pants",
        "output": {
            "department_gender": "Women",
            "colors": ["Beige / Cream"],
            "color_operator": None,
            "pant_type": ["Chinos / Trousers"],
            "materials": ["Linen", "Cotton"],
            "material_operator": "OR",
            "leg_fit": ["Flare / Bootcut"],
            "rise": ["High Rise"],
            "length": None,
            "pattern": None,
            "brands": None,
            "residual_text": ""
        }
    },
    "Dresses": {
        "query": "women's red floral midi wrap dress short sleeve",
        "output": {
            "department_gender": "Women",
            "colors": ["Red"],
            "color_operator": None,
            "pattern": ["Floral"],
            "length": ["Midi"],
            "sleeve_length": ["Short Sleeve"],
            "silhouette": ["Wrap"],
            "neckline": None,
            "materials": None,
            "material_operator": None,
            "brands": None,
            "residual_text": ""
        }
    },
    "Footwear": {
        "query": "men's white adidas low top lace up running sneakers",
        "output": {
            "brands": ["Adidas"],
            "department_gender": "Men",
            "colors": ["White"],
            "color_operator": None,
            "shaft_height": ["Low (sneakers / shoes)"],
            "fastening": ["Lace-up"],
            "heel_sole_type": None,
            "toe_style": None,
            "pattern": None,
            "materials": None,
            "material_operator": None,
            "residual_text": "running sneakers"
        }
    }
}

# ==============================================================================
# 3. FUNKCJE WYWOŁUJĄCE GEMINI (KROK 1 I KROK 2)
# ==============================================================================

def step_1_classify_category(client: genai.Client, query: str) -> str:
    """Prompt 1: Wybór jednej z 8 kategorii lub 'None'."""
    prompt = f"""You are an expert e-commerce fashion taxonomy classifier.
Classify the user shopping query into EXACTLY ONE of the following fashion categories:
{json.dumps(ALLOWED_CATEGORIES, indent=2)}

Rules:
1. If the query clearly matches one category, return its exact name.
2. If the query is about accessories, undergarments, jewelry, bags, hats, socks, belts, or other non-apparel items, return 'None'.
3. Disambiguation Guide for Borderline Cases:
   - "track jacket" / athletic zip-up -> "Hoodies & Sweatshirts"
   - "polo shirt" / golf polo -> "T-Shirts & Tops"
   - "cardigan" / knit sweater -> "Sweaters & Cardigans"
   - "t-shirt dress" / "shirt dress" -> "Dresses"
   - "windbreaker" / "fleece jacket" -> "Jackets & Coats"
   - "shorts" (e.g. "mens shorts", "denim shorts") -> "Pants & Trousers"
   - "belts", "hats", "socks", "wallets" -> "None"

User Query: "{query}"
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CategorySelection,
            temperature=0.0
        )
    )
    result = json.loads(response.text)
    selected = result.get("category", "None")
    return selected if selected in ALLOWED_CATEGORIES else "None"


def step_2_extract_attributes(client: genai.Client, query: str, category: str) -> Dict[str, Any]:
    """Prompt 2: Wyciągnięcie cech z Guided Decoding i 1-Shot demonstration."""
    model_class = CATEGORY_MODELS[category]
    few_shot = FEW_SHOT_EXAMPLES.get(category)

    few_shot_block = ""
    if few_shot:
        few_shot_block = f"""
Example for this category:
Input Query: "{few_shot['query']}"
Output:
{json.dumps(few_shot['output'], indent=2)}
"""

    prompt = f"""Extract fashion product attributes from the user query into the schema.

Important Rules:
1. Extract attributes that are explicitly stated in the query.
2. CRITICAL: DO NOT guess or infer unmentioned default traits (e.g. do not assume sneakers are flat, do not assume coats are wool or unhooded). If an attribute is not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types (e.g. 'midi or maxi', 'straight or wide leg', 'slip-on or lace-up'): return all requested options in the corresponding list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if the user is open to either alternative (e.g. 'linen or cotton', 'black or navy').
     * Set operator to 'AND' if the single item combines multiple values (e.g. 'black and white', 'cotton polyester blend').
     * If only one color or material is mentioned, leave the operator null.
4. If a brand or company name is present in the query, extract its normalized official name into 'brands' list. If no brand is present, leave 'brands' null.
5. Put any leftover terms (occasions, subjective styles, or unmapped words) into residual_text. Do not put the brand name into residual_text if captured in 'brands'.
{few_shot_block}
User Query: "{query}"
Category: "{category}"
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=model_class,
            temperature=0.0
        )
    )
    result = json.loads(response.text)
    residual = result.pop("residual_text", "")
    extracted_attributes = {k: v for k, v in result.items() if v is not None}
    return {
        "extracted_attributes": extracted_attributes,
        "residual_text": residual
    }


# ==============================================================================
# 4. GŁÓWNA PĘTLA EWALUACYJNA
# ==============================================================================

def main():
    print("=" * 110)
    print(f" EWALUACJA PIPELINE'U EKSTRAKCJI: {MODEL_NAME}")
    print(f" Zbiór testowy: {BENCHMARK_CSV} (Limit: {LIMIT or 'Wszystkie'})")
    print("=" * 110)

    # Inicjalizacja Vertex AI
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or "project-3a86f100-1aae-4780-84b"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us")

    try:
        if project_id or not os.environ.get("GEMINI_API_KEY"):
            print(f"Logowanie: Google Cloud Vertex AI (Projekt: {project_id}, Region: {location})...\n")
            client = genai.Client(vertexai=True, project=project_id, location=location)
        else:
            client = genai.Client()
    except Exception as e:
        print(f"Błąd inicjalizacji klienta Google GenAI: {e}")
        return

    # Wczytanie zapytań z pliku CSV
    if not os.path.exists(BENCHMARK_CSV):
        print(f"BŁĄD: Nie znaleziono pliku {BENCHMARK_CSV}!")
        return

    with open(BENCHMARK_CSV, "r", encoding="utf-8") as f:
        all_test_queries = list(csv.DictReader(f))

    if LIMIT > 0:
        test_queries = all_test_queries[:LIMIT]
    else:
        test_queries = all_test_queries

    total_queries = len(test_queries)
    print(f"Załadowano {total_queries} zapytań testowych do ewaluacji.\n")

    # Zmienne statystyczne
    category_correct = 0
    cat_by_difficulty = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0
    step1_latencies = []
    step2_latencies = []
    latencies = []

    results = []

    for idx, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_cat = test["category"]
        difficulty = test.get("difficulty", "Standard")
        expected_attrs = json.loads(test["expected_attributes"])
        expected_residual = test["expected_residual"]

        # KROK 1: Kategoria
        t0 = time.time()
        predicted_cat = step_1_classify_category(client, query)
        t1 = time.time()
        s1_ms = (t1 - t0) * 1000
        step1_latencies.append(s1_ms)

        cat_ok = (predicted_cat.lower() == expected_cat.lower())

        if cat_ok:
            category_correct += 1

        cat_by_difficulty.setdefault(difficulty, {"correct": 0, "total": 0})
        cat_by_difficulty[difficulty]["total"] += 1
        if cat_ok:
            cat_by_difficulty[difficulty]["correct"] += 1

        # KROK 2: Cechy (tylko gdy kategoria != None)
        predicted_attrs = {}
        predicted_residual = ""
        s2_ms = 0.0

        if predicted_cat != "None":
            t2 = time.time()
            extraction = step_2_extract_attributes(client, query, predicted_cat)
            t3 = time.time()
            s2_ms = (t3 - t2) * 1000
            step2_latencies.append(s2_ms)
            predicted_attrs = extraction.get("extracted_attributes", {})
            predicted_residual = extraction.get("residual_text", "")

        total_ms = s1_ms + s2_ms
        latencies.append(total_ms)

        KEY_ALIASES = {
            "primary_color": "colors",
            "primary_material": "materials",
            "brand": "brands",
        }
        REVERSE_ALIASES = {v: k for k, v in KEY_ALIASES.items()}

        def norm_val(k, v):
            if v is None:
                return ""
            s = str(v).lower().strip()
            if k in ("brand", "brands"):
                if s.startswith("the "):
                    s = s[4:]
                return s.replace("-", " ").replace("'", "").replace("raw", "").strip()
            return s

        def attr_matches(k, v_pred, v_exp):
            if isinstance(v_pred, list) and isinstance(v_exp, str):
                return any(norm_val(k, item) == norm_val(k, v_exp) for item in v_pred)
            if isinstance(v_exp, list) and isinstance(v_pred, str):
                return any(norm_val(k, v_pred) == norm_val(k, item) for item in v_exp)
            if isinstance(v_pred, list) and isinstance(v_exp, list):
                return any(norm_val(k, x) in [norm_val(k, y) for y in v_exp] for x in v_pred)
            return norm_val(k, v_pred) == norm_val(k, v_exp)

        tp = 0
        fp = 0
        fn = 0

        for k_pred, v_pred in predicted_attrs.items():
            if k_pred in ("color_operator", "material_operator"):
                if k_pred in expected_attrs:
                    if str(v_pred).upper() == str(expected_attrs[k_pred]).upper():
                        tp += 1
                    else:
                        fp += 1
                else:
                    fp += 1
                continue
            canonical_exp = k_pred if k_pred in expected_attrs else REVERSE_ALIASES.get(k_pred, k_pred)
            if canonical_exp in expected_attrs and attr_matches(k_pred, v_pred, expected_attrs[canonical_exp]):
                tp += 1
            else:
                fp += 1

        for k_exp, v_exp in expected_attrs.items():
            if k_exp in ("color_operator", "material_operator"):
                pred_op = predicted_attrs.get(k_exp)
                if not pred_op or str(pred_op).upper() != str(v_exp).upper():
                    fn += 1
                continue
            canonical_pred = k_exp if k_exp in predicted_attrs else KEY_ALIASES.get(k_exp, k_exp)
            pred_val = predicted_attrs.get(canonical_pred, predicted_attrs.get(k_exp))
            if pred_val is None or not attr_matches(k_exp, pred_val, v_exp):
                fn += 1

        total_tp += tp
        total_fp += fp
        total_fn += fn

        status_icon = "✅" if cat_ok else "❌"
        timing_str = f"S1: {s1_ms:.0f}ms | S2: {s2_ms:.0f}ms | Total: {total_ms:.0f}ms" if s2_ms > 0 else f"S1: {s1_ms:.0f}ms (S2 pominięty)"
        print(f"[{idx:2d}/{total_queries:2d}] {status_icon} Kat: [{predicted_cat:20s}] (Oczek: [{expected_cat:20s}]) | Q: \"{query}\" ({timing_str})")

        results.append({
            "idx": idx,
            "query_id": test.get("query_id", ""),
            "query": query,
            "expected_cat": expected_cat,
            "pred_cat": predicted_cat,
            "cat_ok": cat_ok,
            "difficulty": difficulty,
            "expected_attrs": expected_attrs,
            "pred_attrs": predicted_attrs,
            "pred_residual": predicted_residual,
            "expected_residual": expected_residual,
            "s1_ms": s1_ms, "s2_ms": s2_ms, "total_ms": total_ms,
            "tp": tp, "fp": fp, "fn": fn
        })

    # Zapis wyników do plików CSV i JSON
    if results:
        fieldnames = list(results[0].keys())
        with open("gemini_extraction_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        with open("gemini_extraction_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("-> Zapisano pełne wyniki do: gemini_extraction_results.csv oraz gemini_extraction_results.json")

    # ==============================================================================
    # 5. RAPORT STATYSTYCZNY
    # ==============================================================================
    cat_accuracy = (category_correct / total_queries) * 100.0

    precision = (total_tp / (total_tp + total_fp) * 100.0) if (total_tp + total_fp) > 0 else 100.0
    recall = (total_tp / (total_tp + total_fn) * 100.0) if (total_tp + total_fn) > 0 else 100.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    
    avg_s1 = sum(step1_latencies) / len(step1_latencies) if step1_latencies else 0.0
    avg_s2 = sum(step2_latencies) / len(step2_latencies) if step2_latencies else 0.0
    avg_total = sum(latencies) / len(latencies) if latencies else 0.0

    print("\n" + "=" * 110)
    print(" PODSUMOWANIE STATYSTYCZNE EWALUACJI (CAŁOŚĆ: 92 ZAPYTANIA)")
    print("=" * 110)
    print(f"Model: {MODEL_NAME}")
    print(f"Liczba zapytań: {total_queries}")
    print(f"CZAS ODPOWIEDZI (LATENCY BREAKDOWN):")
    print(f"  - Krok 1 (Klasyfikacja Kategorii)    : średnio {avg_s1:.1f} ms")
    print(f"  - Krok 2 (Ekstrakcja Cech)           : średnio {avg_s2:.1f} ms")
    print(f"  - Całkowity czas (Krok 1 + Krok 2)   : średnio {avg_total:.1f} ms (~{avg_total/1000:.2f} s / query)\n")

    print(f"DOKŁADNOŚĆ KATEGORII (Krok 1): {category_correct}/{total_queries} ({cat_accuracy:.1f}%)")
    print("  Rozbicie na poziom trudności:")
    for diff, data in sorted(cat_by_difficulty.items()):
        acc = (data['correct'] / data['total']) * 100.0 if data['total'] > 0 else 0.0
        print(f"    - {diff:18s}: {data['correct']:2d}/{data['total']:2d} ({acc:.1f}%)")

    print(f"\nMETRYKI EKSTRAKCJI CECH (Krok 2):")
    print(f"  - True Positives (Poprawne cechy)    : {total_tp}")
    print(f"  - False Positives (Cechy nadmiarowe) : {total_fp}")
    print(f"  - False Negatives (Cechy pominięte)  : {total_fn}")
    print(f"  - Precision (Precyzja)               : {precision:.1f}%")
    print(f"  - Recall (Czułość)                   : {recall:.1f}%")
    print(f"  - F1-Score                           : {f1:.1f}%")

    # --------------------------------------------------------------------------
    # Statystyki dedykowane dla 12 zapytań Complex_Logic (AND / OR)
    # --------------------------------------------------------------------------
    complex_ids = ["72705", "5631", "5676", "52479", "111109", "67459", "80142", "17315", "86257", "51216", "47180", "87316"]
    complex_res = [r for r in results if r["query_id"] in complex_ids or r["difficulty"] == "Complex_Logic"]
    if complex_res:
        c_total = len(complex_res)
        c_cat_ok = sum(1 for r in complex_res if r["cat_ok"])
        c_tp = sum(r["tp"] for r in complex_res)
        c_fp = sum(r["fp"] for r in complex_res)
        c_fn = sum(r["fn"] for r in complex_res)
        c_prec = (c_tp / (c_tp + c_fp) * 100.0) if (c_tp + c_fp) > 0 else 100.0
        c_rec = (c_tp / (c_tp + c_fn) * 100.0) if (c_tp + c_fn) > 0 else 100.0
        c_f1 = (2 * c_prec * c_rec / (c_prec + c_rec)) if (c_prec + c_rec) > 0 else 0.0

        print("\n" + "=" * 110)
        print(f" STATYSTYKI STRICTE DLA {c_total} NOWYCH ZAPYTAŃ Z LOGIKĄ AND / OR (Complex_Logic)")
        print("=" * 110)
        print(f"  - Dokładność kategorii (Krok 1)      : {c_cat_ok}/{c_total} ({c_cat_ok/c_total*100.0:.1f}%)")
        print(f"  - True Positives (Poprawne cechy)    : {c_tp}")
        print(f"  - False Positives (Cechy nadmiarowe) : {c_fp}")
        print(f"  - False Negatives (Cechy pominięte)  : {c_fn}")
        print(f"  - Precision (Precyzja)               : {c_prec:.1f}%")
        print(f"  - Recall (Czułość)                   : {c_rec:.1f}%")
        print(f"  - F1-Score                           : {c_f1:.1f}%")

        # Sprawdzenie operatorów boolowskich
        op_tests = 0
        op_correct = 0
        for r in complex_res:
            for op_key in ("color_operator", "material_operator"):
                if op_key in r["expected_attrs"]:
                    op_tests += 1
                    exp_val = str(r["expected_attrs"][op_key]).upper()
                    pred_val = str(r["pred_attrs"].get(op_key, "")).upper()
                    if exp_val == pred_val:
                        op_correct += 1

        if op_tests > 0:
            print(f"  - Skuteczność operatorów (AND/OR)    : {op_correct}/{op_tests} ({op_correct/op_tests*100.0:.1f}%)")

        print("\n  SZCZEGÓŁOWY WYKAZ TYCH 12 ZAPYTAŃ:")
        for r in complex_res:
            cat_flag = "✅" if r["cat_ok"] else "❌"
            attr_flag = "✅" if (r["fp"] == 0 and r["fn"] == 0) else "⚠️"
            print(f"    [{r['query_id']}] {cat_flag} Kat: {r['pred_cat']:18s} | {attr_flag} Q: \"{r['query']}\"")
            print(f"         Oczekiwane: {json.dumps(r['expected_attrs'])}")
            print(f"         Wyciągnięte: {json.dumps(r['pred_attrs'])}")

    print("\n" + "=" * 110)
    print(" PRZYKŁADY BŁĘDÓW LUB ROZBIEŻNOŚCI (JEŚLI WYSTĄPIŁY):")
    print("=" * 110)
    discrepancies = [r for r in results if not r["cat_ok"] or r["fp"] > 0 or r["fn"] > 0]
    if not discrepancies:
        print("Brak jakichkolwiek błędów! 100% idealna zgodność z wzorcem.")
    else:
        for r in discrepancies[:12]:
            print(f"\n[Zapytanie {r['idx']}]: \"{r['query']}\" ({r['difficulty']})")
            if not r["cat_ok"]:
                print(f"  ❌ Błąd kategorii: Oczekiwana=[{r['expected_cat']}] vs Otrzymana=[{r['pred_cat']}]")
            if r["fp"] > 0 or r["fn"] > 0:
                print(f"  Oczekiwane cechy : {json.dumps(r['expected_attrs'])}")
                print(f"  Wyciągnięte cechy: {json.dumps(r['pred_attrs'])}")
                print(f"  Resztka modelu   : \"{r['pred_residual']}\"")

    print("\n" + "=" * 110)

if __name__ == "__main__":
    main()
