import os
import sys
import json
import time
import csv
from groq import Groq
from evaluate_gemini_extraction import (
    ALLOWED_CATEGORIES,
    CATEGORY_MODELS,
    FEW_SHOT_EXAMPLES,
    BENCHMARK_CSV,
    robust_json_loads
)

# Domyślny model Groq
MODEL_NAME = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
LIMIT = int(os.environ.get("LIMIT", "0"))  # 0 oznacza wszystkie 92 zapytania


def step_1_classify_category_groq(client: Groq, query: str) -> str:
    """Krok 1 na Groq: Klasyfikacja kategorii modowej."""
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

Return JSON format: {{"category": "<one of allowed categories or None>"}}
"""
    chat = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    result = robust_json_loads(chat.choices[0].message.content)
    selected = result.get("category", "None")
    return selected if selected in ALLOWED_CATEGORIES else "None"


def step_2_extract_attributes_groq(client: Groq, query: str, category: str) -> dict:
    """Krok 2 na Groq: Ekstrakcja cech z użyciem schematu JSON."""
    model_class = CATEGORY_MODELS[category]
    few_shot = FEW_SHOT_EXAMPLES.get(category)
    schema_json = json.dumps(model_class.model_json_schema(), indent=2)

    few_shot_block = ""
    if few_shot:
        few_shot_block = f"""
Example for this category:
Input Query: "{few_shot['query']}"
Output:
{json.dumps(few_shot['output'], indent=2)}
"""

    prompt = f"""Extract fashion product attributes from the user query into the following JSON schema:
{schema_json}

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

Return strictly valid JSON matching the schema.
"""
    chat = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    result = robust_json_loads(chat.choices[0].message.content)
    residual = result.pop("residual_text", "")
    extracted_attributes = {k: v for k, v in result.items() if v is not None}
    return {
        "extracted_attributes": extracted_attributes,
        "residual_text": residual
    }


def main():
    print("=" * 110)
    print(f" EWALUACJA PIPELINE'U EKSTRAKCJI NA GROQ LPU: {MODEL_NAME}")
    print(f" Zbiór testowy: {BENCHMARK_CSV} (Limit: {LIMIT or 'Wszystkie 92'})")
    print("=" * 110)

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("BŁĄD: Brak zmiennej GROQ_API_KEY!")
        return

    client = Groq(api_key=api_key)

    if not os.path.exists(BENCHMARK_CSV):
        print(f"BŁĄD: Nie znaleziono pliku {BENCHMARK_CSV}!")
        return

    with open(BENCHMARK_CSV, "r", encoding="utf-8") as f:
        all_test_queries = list(csv.DictReader(f))

    test_queries = all_test_queries[:LIMIT] if LIMIT > 0 else all_test_queries
    total_queries = len(test_queries)
    print(f"Załadowano {total_queries} zapytań testowych do ewaluacji.\n")

    category_correct = 0
    cat_by_difficulty = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0
    step1_latencies = []
    step2_latencies = []
    latencies = []

    results = []

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

    for idx, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_cat = test["category"]
        difficulty = test.get("difficulty", "Standard")
        expected_attrs = json.loads(test["expected_attributes"])
        expected_residual = test["expected_residual"]

        # KROK 1: Kategoria
        t0 = time.time()
        try:
            predicted_cat = step_1_classify_category_groq(client, query)
        except Exception as e:
            print(f"  [Błąd Krok 1 Q{idx}]: {e}")
            predicted_cat = "None"
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

        # KROK 2: Cechy
        predicted_attrs = {}
        predicted_residual = ""
        s2_ms = 0.0

        if predicted_cat != "None":
            t2 = time.time()
            try:
                extraction = step_2_extract_attributes_groq(client, query, predicted_cat)
                predicted_attrs = extraction.get("extracted_attributes", {})
                predicted_residual = extraction.get("residual_text", "")
            except Exception as e:
                print(f"  [Błąd Krok 2 Q{idx}]: {e}")
            t3 = time.time()
            s2_ms = (t3 - t2) * 1000
            step2_latencies.append(s2_ms)

        total_ms = s1_ms + s2_ms
        latencies.append(total_ms)

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
        timing_str = f"S1: {s1_ms:.0f}ms | S2: {s2_ms:.0f}ms | Total: {total_ms:.0f}ms" if s2_ms > 0 else f"S1: {s1_ms:.0f}ms"
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

    # Zapis wyników
    if results:
        fieldnames = list(results[0].keys())
        slug = MODEL_NAME.replace("/", "_").replace(".", "_").replace("-", "_")
        csv_file = f"groq_extraction_results_{slug}.csv"
        json_file = f"groq_extraction_results_{slug}.json"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"-> Zapisano pełne wyniki do: {csv_file} oraz {json_file}")

    # Statystyki
    cat_accuracy = (category_correct / total_queries) * 100.0
    precision = (total_tp / (total_tp + total_fp) * 100.0) if (total_tp + total_fp) > 0 else 100.0
    recall = (total_tp / (total_tp + total_fn) * 100.0) if (total_tp + total_fn) > 0 else 100.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    avg_s1 = sum(step1_latencies) / len(step1_latencies) if step1_latencies else 0.0
    avg_s2 = sum(step2_latencies) / len(step2_latencies) if step2_latencies else 0.0
    avg_total = sum(latencies) / len(latencies) if latencies else 0.0

    print("\n" + "=" * 110)
    print(f" PODSUMOWANIE STATYSTYCZNE EWALUACJI NA GROQ ({MODEL_NAME})")
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

    # 12 zapytań Complex_Logic
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

    print("\n" + "=" * 110)


if __name__ == "__main__":
    main()
