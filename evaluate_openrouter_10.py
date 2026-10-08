import os
import sys
import json
import time
import csv
from openai import OpenAI

from evaluate_gemini_extraction import (
    ALLOWED_CATEGORIES,
    CATEGORY_MODELS,
    FEW_SHOT_EXAMPLES,
    BENCHMARK_CSV,
    robust_json_loads,
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Brak zmiennej środowiskowej OPENROUTER_API_KEY!")


MODEL_NAME = "qwen/qwen3.8-27b"
LIMIT = 10

# Klient OpenAI utworzony jednorazowo z włączonym Keep-Alive
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ŚCISŁY ROUTING DO CEREBRAS: BEZ ŻADNYCH WOLNYCH FALLBACKÓW!
EXTRA_BODY = {
    "provider": {
        "order": ["Cerebras"],
        "allow_fallbacks": False
    },
    "reasoning": {
        "effort": "none"
    }
}

KEY_ALIASES = {
    "primary_color": "colors",
    "primary_material": "materials",
    "brand": "brands",
}
REVERSE_ALIASES = {v: k for k, v in KEY_ALIASES.items()}

def call_cerebras_with_retry(fn, max_retries=5, backoff=1.5):
    """Odporne wywołanie z ponawianiem próby w przypadku chwilowego przeciążenia kolejki Cerebras."""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err = str(e)
            if any(k in err for k in ("429", "503", "504", "rate_limit", "overloaded", "busy")):
                wait = backoff * (attempt + 1)
                print(f" [Cerebras chwilowo zajęty, oczekiwanie {wait:.1f}s przed ponowieniem {attempt+1}/{max_retries}]")
                time.sleep(wait)
            else:
                raise e
    return fn()

def norm_val(k, v):
    if v is None:
        return ""
    s = str(v).lower().strip()
    if k in ("brand", "brands"):
        if s.startswith("the "):
            s = s[4:].strip()
        s = s.replace("-", " ").replace("’", "'")
    return s

def compare_attributes(expected: dict, predicted: dict):
    all_keys = set(expected.keys()) | set(predicted.keys())
    tp = 0
    fp = 0
    fn = 0
    for k in all_keys:
        exp_val = expected.get(k)
        pred_val = predicted.get(k)
        if exp_val is None:
            alias = KEY_ALIASES.get(k) or REVERSE_ALIASES.get(k)
            if alias and alias in expected:
                exp_val = expected.get(alias)
        if pred_val is None:
            alias = KEY_ALIASES.get(k) or REVERSE_ALIASES.get(k)
            if alias and alias in predicted:
                pred_val = predicted.get(alias)

        if exp_val is not None and pred_val is not None:
            exp_set = set(norm_val(k, x) for x in exp_val) if isinstance(exp_val, list) else {norm_val(k, exp_val)}
            pred_set = set(norm_val(k, x) for x in pred_val) if isinstance(pred_val, list) else {norm_val(k, pred_val)}
            common = exp_set.intersection(pred_set)
            tp += len(common)
            fp += len(pred_set - common)
            fn += len(exp_set - common)
        elif exp_val is not None and pred_val is None:
            fn += len(exp_val) if isinstance(exp_val, list) else 1
        elif exp_val is None and pred_val is not None:
            fp += len(pred_val) if isinstance(pred_val, list) else 1
    return tp, fp, fn

def step_1_classify(query: str):
    prompt = f"""You are an expert e-commerce fashion taxonomy classifier.
Classify the user shopping query into EXACTLY ONE of the following fashion categories:
{json.dumps(ALLOWED_CATEGORIES, indent=2)}

Rules:
1. If the query clearly matches one category, return its exact name.
2. If the query is about accessories, undergarments, jewelry, bags, hats, socks, belts, or other non-apparel items, return 'None'.

User Query: "{query}"

Return strictly valid JSON format: {{"category": "<one of allowed categories or None>"}}
"""
    t0 = time.time()
    chat = call_cerebras_with_retry(lambda: client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=100,
        extra_body=EXTRA_BODY
    ))
    t1 = time.time()
    duration = (t1 - t0) * 1000

    raw = chat.choices[0].message.content or "{}"
    parsed = robust_json_loads(raw)
    category = parsed.get("category", "None")
    if category not in ALLOWED_CATEGORIES:
        category = "None"
    return category, duration

def step_2_extract(query: str, category: str):
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
2. CRITICAL: DO NOT guess or infer unmentioned default traits. If not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types: return all requested options in the list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if alternative.
     * Set operator to 'AND' if combined multi-color/material.
     * Leave operator null if single option.
4. If a brand name is present, extract normalized official name into 'brands' list.
5. Put any leftover terms into residual_text.
{few_shot_block}
User Query: "{query}"
Category: "{category}"

Return strictly valid JSON matching the schema.
"""
    t0 = time.time()
    chat = call_cerebras_with_retry(lambda: client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=600,
        extra_body=EXTRA_BODY
    ))
    t1 = time.time()
    duration = (t1 - t0) * 1000

    raw = chat.choices[0].message.content or "{}"
    parsed = robust_json_loads(raw)
    residual = parsed.pop("residual_text", "")
    attrs = {k: v for k, v in parsed.items() if v is not None}
    return attrs, residual, duration

def main():
    print("=" * 95)
    print(f"EWALUACJA 10 WIERSZY: ŚCISŁY CEREBRAS ONLY (allow_fallbacks = False)")
    print(f"Model: {MODEL_NAME} | Limit: {LIMIT} zapytań")
    print("=" * 95)

    with open(BENCHMARK_CSV, "r", encoding="utf-8") as f:
        queries = list(csv.DictReader(f))[:LIMIT]

    step1_times = []
    step2_times = []
    total_times = []
    correct_cats = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for idx, row in enumerate(queries, 1):
        q = row["query"]
        exp_cat = row["category"]
        exp_attrs = json.loads(row["expected_attributes"])

        # Odstęp między zapytaniami dla regeneracji token bucket
        if idx > 1:
            time.sleep(0.5)

        # Krok 1: Klasyfikacja
        pred_cat, s1_time = step_1_classify(q)
        step1_times.append(s1_time)
        cat_ok = (pred_cat.lower() == exp_cat.lower())
        if cat_ok:
            correct_cats += 1

        # Krok 2: Ekstrakcja
        s2_time = 0.0
        pred_attrs = {}
        pred_residual = ""
        if pred_cat != "None":
            time.sleep(0.3)  # Drobny pacing między Krokiem 1 a Krokiem 2
            pred_attrs, pred_residual, s2_time = step_2_extract(q, pred_cat)
            step2_times.append(s2_time)

        tot_time = s1_time + s2_time
        total_times.append(tot_time)

        tp, fp, fn = compare_attributes(exp_attrs, pred_attrs)
        total_tp += tp
        total_fp += fp
        total_fn += fn

        status_cat = "✅" if cat_ok else "❌"
        status_attr = "✅" if (fp == 0 and fn == 0) else "⚠️"
        print(f"\n[{idx:02d}/10] Q: \"{q}\"")
        print(f"  {status_cat} Kategoria: '{pred_cat}' (Oczekiwana: '{exp_cat}') | Czas S1: {s1_time:.0f} ms")
        print(f"  {status_attr} Atrybuty:  Czas S2: {s2_time:.0f} ms | RAZEM: {tot_time:.0f} ms ({tot_time/1000:.2f} s) [TP={tp}, FP={fp}, FN={fn}]")
        print(f"      Wyciągnięte: {json.dumps(pred_attrs, ensure_ascii=False)}")
        print(f"      Oczekiwane:  {json.dumps(exp_attrs, ensure_ascii=False)}")

    # Podsumowanie metryk
    precision = (total_tp / (total_tp + total_fp) * 100.0) if (total_tp + total_fp) > 0 else 0.0
    recall = (total_tp / (total_tp + total_fn) * 100.0) if (total_tp + total_fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    avg_s1 = sum(step1_times) / len(step1_times)
    avg_s2 = sum(step2_times) / len(step2_times) if step2_times else 0.0
    avg_tot = sum(total_times) / len(total_times)

    print("\n" + "=" * 95)
    print("PODSUMOWANIE DLA 10 WIERSZY (ŚCISŁY CEREBRAS ONLY):")
    print("=" * 95)
    print(f"Dokładność kategorii (Krok 1) : {correct_cats}/10 ({correct_cats*10:.1f}%)")
    print(f"Atrybuty True Positives (TP)  : {total_tp}")
    print(f"Atrybuty False Positives (FP) : {total_fp}")
    print(f"Atrybuty False Negatives (FN) : {total_fn}")
    print(f"Precyzja (Precision)          : {precision:.1f}%")
    print(f"Czułość (Recall)              : {recall:.1f}%")
    print(f"F1-Score                      : {f1:.1f}%")
    print("-" * 95)
    print(f"Średni czas Krok 1 (Klasyfikacja) : {avg_s1:.1f} ms ({avg_s1/1000:.2f} s)")
    print(f"Średni czas Krok 2 (Ekstrakcja)   : {avg_s2:.1f} ms ({avg_s2/1000:.2f} s)")
    print(f"ŚREDNI CZAS CAŁKOWITY (K1 + K2)   : {avg_tot:.1f} ms ({avg_tot/1000:.2f} s)")
    print("=" * 95)

if __name__ == "__main__":
    main()
