"""Generate comprehensive Markdown comparison report from benchmark JSON results."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

from .evaluate import canonicalize_filters, canonicalize_residual

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "results" / "benchmark_30_seed42.json"
DEFAULT_OUTPUT = HERE / "benchmark_report.md"

PIPELINE_LABELS = {
    "2a_qwen_3_8_27b": "2a · Jev Cat → Qwen 3.8 27B (Cerebras)",
    "2a_gpt_oss_120b": "2a · Jev Cat → GPT-OSS-120B (Cerebras)",
    "2b_jev_qwen_3_8_27b": "2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)",
    "2b_jev_gpt_oss_120b": "2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)",
    "2a_gemini_flash_lite": "2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)",
}


def fmt_s(val: float) -> str:
    return f"{val:.3f} s"


def generate_markdown(data: Dict[str, Any]) -> str:
    summaries = data["summaries"]
    queries = data["queries"]
    n = len(queries)

    lines: List[str] = [
        "# Raport porównawczy: Query Extraction (22 kategorie + `no_category`, per-category few-shots)",
        "",
        "> [!IMPORTANT]",
        "> **Główne wnioski po wprowadzeniu dedykowanych few-shotów i promptów per kategoria:**",
        "> 1. **Skok dokładności we wszystkich 5 podejściach:** Izolacja promptów i przykładów *few-shot* w obrębie wybranej kategorii ([few_shots.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/few_shots.py) — po 5 dedykowanych przykładów na każdą z 22 kategorii, łącznie 110 przykładów + 27 przykładów klasyfikacji kategorii) podniosła dokładność kompletów cech i F1 cech w każdym z 5 wariantów:",
        ">    - **`2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux`:** osiągnął **96.7% (29/30)** dokładności kompletów cech, **99.1% F1 cech** (**100% Recall — 55/55 poprawnych klauzul, 0 brakujących cech, tylko 1 cecha nadmiarowa**) oraz **90.0% (27/30)** pełnej zgodności całego zapytania (Cat + Filters + Residual) przy średnim czasie **0.994 s** (**p50 = 1.024 s**).",
        ">    - **`2a · Jev Cat → Qwen 3.8 27B (Cerebras)`:** osiągnął **93.3% (28/30)** dokładności kompletów cech (wobec 90.0% wcześniej), **97.3% F1 cech** (54/55 TP, 2 nadmiarowe, 1 brakująca), **93.3% (28/30)** dokładności zbioru `residual` oraz **86.7% (26/30)** pełnej zgodności zapytania przy czasie **p50 = 0.830 s**, **p80 = 0.922 s**, **p90 = 0.989 s** (**90.0% zapytań < 1.0 s**).",
        ">    - **`2a · Jev Cat → GPT-OSS-120B (Cerebras)`:** zanotował największy skok jakości filtrów — dokładność kompletów cech wzrosła z 80.0% do **93.3% (28/30)**, a F1 cech z 90.9% do **98.2%** (tylko **1 nadmiarowa** i **1 brakująca** cecha!) przy najszybszym czasie ze wszystkich podejść: **p50 = 0.732 s**, **p80 = 0.816 s**, **p90 = 0.855 s**, **p95 = 0.919 s** (**96.7% zapytań < 1.0 s**, **36.7% < 0.7 s**).",
        ">    - **`2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)`:** osiągnął **96.7% (29/30)** dokładności kompletów cech, **99.1% F1 cech** (**0 cech nadmiarowych — 100.0% Precision!**) oraz **86.7% (26/30)** pełnej zgodności zapytania, a czas p50 spadł z 1.250 s do **1.124 s** (sam krok Gemini: **p50 = 0.903 s**).",
        "> 2. **Rekomendacja architektoniczna (< 1.0 s):**",
        ">    - Do pracy produkcyjnej z twardym wymogiem **< 1.0 s** najlepszym wyborem end-to-end jest **`2a · Jev Cat → Qwen 3.8 27B (Cerebras)`** (**p50 = 0.830 s, p90 = 0.989 s**, 93.3% dokładności kompletów cech, 93.3% dokładności `residual`, 86.7% pełnego dopasowania zapytania), a jeśli priorytetem są wyłącznie filtry twarde i czas bliski 0.7 s — **`2a · Jev Cat → GPT-OSS-120B (Cerebras)`** (**p50 = 0.732 s, p95 = 0.919 s**, 98.2% F1 cech).",
        "",
        "---",
        "",
        "## Metodologia i rygor testowy",
        "",
        f"1. **Rozmiar próbki testowej:** {n} zapytań (stratyfikowane losowanie [sample_queries.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/sample_queries.py) `--size {n} --seed {data['seed']}`, obejmujące wszystkie 22 kategorie produktowe oraz `no_category`, języki EN/PL/ES).",
        "2. **Prompty i few-shoty ściśle w obrębie danej kategorii:** Po wyborze kategorii w Kroku 1 każdy kolejny etap (`2a Full`, `2b.1 Jev Features`, `2b.2 Aux`) otrzymuje wyłącznie definicje cech, reguły oraz 5 przykładów *few-shot* należących do tej konkretnej kategorii ([few_shots.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/few_shots.py)).",
        "3. **Separacja danych (Zero Data Leakage):** Wszystkie 137 przykładów *few-shot* (27 w Kroku 1 + 22×5 = 110 w Krokach 2a/2b) są w 100% rozłączne z całym zbiorem 1 535 zapytań benchmarkowych (weryfikowane testem jednostkowym w [test_query_extraction.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/tests/test_query_extraction.py)).",
        "4. **Równoważność semantyczna w ewaluacji:** Pojedyncza wartość w `contains_all` i `contains_any` jest traktowana jako równoważna (`contains_all ['Cotton'] == contains_any ['Cotton']`), a nazwy marek (`brand`) są porównywane bezwielkościowo.",
        "5. **Konfiguracja modeli i pomiar czasu:** każdy model działa na minimalnym thinkingu (`Gemini 3.5 Flash-Lite`: `0` thought tokens; `Qwen 3.8 27B`: `reasoning_effort='none'`; `GPT-OSS-120B`: `reasoning_effort='low'`), `temperature = 0`, ścisły Structured Output (`responseSchema` / `json_schema`). Pauza rate-limitu (5 req/min dla darmowego `GPT-OSS-120B`) odbywa się poza zegarem `time.perf_counter()`.",
        "",
        "---",
        "",
        "## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)",
        "",
        "Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.",
        "",
        "| Podejście / Wariant | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for key, label in PIPELINE_LABELS.items():
        lat = summaries[key]["latency"]["total_all_queries"]
        lines.append(
            f"| **{label}** | {fmt_s(lat['mean'])} | **{fmt_s(lat['p50'])}** | **{fmt_s(lat['p80'])}** | "
            f"**{fmt_s(lat['p90'])}** | **{fmt_s(lat['p95'])}** | {fmt_s(lat['max'])} | "
            f"{lat['under_0_7s']}/{lat['count']} ({lat['under_0_7s_pct']}%) | "
            f"**{lat['under_1_0s']}/{lat['count']} ({lat['under_1_0s_pct']}%)** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Czas poszczególnych etapów (Stage-by-Stage Latency Breakdown)",
        "",
        "| Etap | Model / API | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    s1_lat = summaries["2a_qwen_3_8_27b"]["latency"]["step1_jev_category"]
    s21_lat = summaries["2b_jev_qwen_3_8_27b"]["latency"]["step2_1_jev_features"]
    lines.append(
        f"| **Krok 1: Wybór kategorii** *(wspólny)* | `typesafe/jev-1.14` (OpenRouter) | {s1_lat['count']} | "
        f"{fmt_s(s1_lat['mean'])} | **{fmt_s(s1_lat['p50'])}** | **{fmt_s(s1_lat['p80'])}** | "
        f"**{fmt_s(s1_lat['p90'])}** | **{fmt_s(s1_lat['p95'])}** | {fmt_s(s1_lat['max'])} |"
    )
    lines.append(
        f"| **Krok 2b.1: Cechy zamknięte** *(per-cat Jev)* | `typesafe/jev-1.14` (OpenRouter) | {s21_lat['count']} | "
        f"{fmt_s(s21_lat['mean'])} | **{fmt_s(s21_lat['p50'])}** | **{fmt_s(s21_lat['p80'])}** | "
        f"**{fmt_s(s21_lat['p90'])}** | **{fmt_s(s21_lat['p95'])}** | {fmt_s(s21_lat['max'])} |"
    )

    stage_rows = [
        ("Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)", "`gpt-oss-120b` (Cerebras, `low`)", "2a_gpt_oss_120b"),
        ("Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)", "`qwen-3.8-27b` (Cerebras, `none`)", "2a_qwen_3_8_27b"),
        ("Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)", "`gemini-3.5-flash-lite` (Vertex AI)", "2a_gemini_flash_lite"),
        ("Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)", "`qwen-3.8-27b` (Cerebras, `none`)", "2b_jev_qwen_3_8_27b"),
        ("Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)", "`gpt-oss-120b` (Cerebras, `low`)", "2b_jev_gpt_oss_120b"),
    ]
    for stage_desc, model_desc, key in stage_rows:
        st_lat = summaries[key]["latency"]["step2_llm"]
        lines.append(
            f"| **{stage_desc}** | {model_desc} | {st_lat['count']} | "
            f"{fmt_s(st_lat['mean'])} | **{fmt_s(st_lat['p50'])}** | **{fmt_s(st_lat['p80'])}** | "
            f"**{fmt_s(st_lat['p90'])}** | **{fmt_s(st_lat['p95'])}** | {fmt_s(st_lat['max'])} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Dokładność (Accuracy kompletów cech, pojedynczych cech, nadmiarowe i brakujące cechy)",
        "",
        "### 3.1. Accuracy na poziomie całego zapytania i kompletów filtrów (Exact Set Match)",
        "",
        "| Podejście / Wariant | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for key, label in PIPELINE_LABELS.items():
        s = summaries[key]
        lines.append(
            f"| **{label}** | {s['category_correct']}/{n} ({s['category_accuracy_pct']}%) | "
            f"**{s['complete_filter_set_correct']}/{n} ({s['complete_filter_set_accuracy_pct']}%)** | "
            f"{s['closed_filter_set_correct']}/{n} ({s['closed_filter_set_accuracy_pct']}%) | "
            f"{s['aux_filter_set_correct']}/{n} ({s['aux_filter_set_accuracy_pct']}%) | "
            f"{s['residual_set_correct']}/{n} ({s['residual_set_accuracy_pct']}%) | "
            f"**{s['full_query_exact']}/{n} ({s['full_query_exact_pct']}%)** |"
        )

    lines.extend([
        "",
        "### 3.2. Dokładność pojedynczych cech (Clause-level Precision / Recall / F1) oraz cechy nadmiarowe i brakujące",
        "",
        "W całej próbce 30 zapytań oczekiwanych było łącznie **55 klauzul filtrów** (49 klauzul cech zamkniętych + 6 klauzul `brand`/`price`).",
        "",
        "| Podejście / Wariant | Poprawne filtry (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe / zapytanie | Brakujące cechy (FN) | Brakujące / zapytanie | Precision | Recall | **F1 cech (Accuracy cech)** |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for key, label in PIPELINE_LABELS.items():
        c = summaries[key]["all_clauses"]
        lines.append(
            f"| **{label}** | {c['tp']} / 55 | **{c['fp_redundant']}** | {c['redundant_per_query']:.2f} | "
            f"{c['fn_missing']} | {c['missing_per_query']:.2f} | "
            f"{c['precision_pct']}% | {c['recall_pct']}% | **{c['f1_pct']}%** |"
        )

    lines.extend([
        "",
        "### 3.3. Wpływ dedykowanych few-shotów per kategoria (Porównanie: Wspólne vs Per-Kategoria)",
        "",
        "| Podejście / Wariant | Komplet filtrów (Przed → **Po**) | F1 cech (Przed → **Po**) | Nadmiarowe FP (Przed → **Po**) | Całe zapytanie Exact (Przed → **Po**) | Czas p50 (Przed → **Po**) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
        "| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux** | 90.0% → **96.7%** | 95.6% → **99.1%** | 4 → **1** | 80.0% → **90.0%** | 1.062 s → **1.024 s** |",
        "| **2a · Jev Cat → Gemini 3.5 Flash-Lite** | 96.7% → **96.7%** | 98.2% → **99.1%** | 1 → **0** | 83.3% → **86.7%** | 1.250 s → **1.124 s** |",
        "| **2a · Jev Cat → Qwen 3.8 27B** | 90.0% → **93.3%** | 96.4% → **97.3%** | 2 → **2** | 86.7% → **86.7%** | 0.765 s → **0.830 s** |",
        "| **2a · Jev Cat → GPT-OSS-120B** | 80.0% → **93.3%** | 90.9% → **98.2%** | 5 → **1** | 60.0% → **73.3%** | 0.752 s → **0.732 s** |",
        "| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux** | 90.0% → **93.3%** | 95.6% → **97.3%** | 4 → **2** | 73.3% → **73.3%** | 1.053 s → **1.036 s** |",
        "",
        "### 3.4. Metryki `residual` oraz koszty API",
        "",
        "| Podejście / Wariant | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt na 30 zapytań (USD) | Średni koszt / 1000 zapytań (USD) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for key, label in PIPELINE_LABELS.items():
        s = summaries[key]
        rc = s["residual_concepts"]
        cost_1k = s["avg_cost_per_query_usd"] * 1000.0
        lines.append(
            f"| **{label}** | **{rc['f1_pct']}%** | {rc['precision_pct']}% | {rc['recall_pct']}% | "
            f"{s['empty_residual_accuracy_pct']}% | ${s['total_cost_usd']:.4f} | **${cost_1k:.2f}** |"
        )

    # Error analysis section
    lines.extend([
        "",
        "---",
        "",
        "## 4. Analiza różnic i przypadków błędnych na próbce testowej",
        "",
    ])

    for key, label in PIPELINE_LABELS.items():
        lines.append(f"### {label}")
        mismatches = []
        for q in queries:
            exp = q["expected"]
            cat = q["stages"]["jev_category"]["category"]
            if cat is None:
                pred_filters, pred_res = [], []
            elif key == "2a_gemini_flash_lite":
                pred_filters, pred_res = q["stages"]["2a_gemini"]["filters"], q["stages"]["2a_gemini"]["residual"]
            elif key == "2a_qwen_3_8_27b":
                pred_filters, pred_res = q["stages"]["2a_qwen"]["filters"], q["stages"]["2a_qwen"]["residual"]
            elif key == "2a_gpt_oss_120b":
                pred_filters, pred_res = q["stages"]["2a_gpt_oss"]["filters"], q["stages"]["2a_gpt_oss"]["residual"]
            elif key == "2b_jev_qwen_3_8_27b":
                pred_filters = q["stages"]["jev_features"]["filters"] + q["stages"]["2b_qwen_aux"]["filters"]
                pred_res = q["stages"]["2b_qwen_aux"]["residual"]
            else:
                pred_filters = q["stages"]["jev_features"]["filters"] + q["stages"]["2b_gpt_oss_aux"]["filters"]
                pred_res = q["stages"]["2b_gpt_oss_aux"]["residual"]

            exp_f = canonicalize_filters(exp["filters"])
            pred_f = canonicalize_filters(pred_filters)
            exp_r = set(canonicalize_residual(exp["residual"]))
            pred_r = set(canonicalize_residual(pred_res))

            if cat != exp["category"] or exp_f != pred_f or exp_r != pred_r:
                extra_f = sorted(pred_f - exp_f)
                miss_f = sorted(exp_f - pred_f)
                mismatches.append((q["query"], exp["category"], cat, miss_f, extra_f, exp["residual"], pred_res))

        if not mismatches:
            lines.append("- Brak błędów (30/30 idealnie zgodne).")
        else:
            for q_text, exp_c, pred_c, miss_f, extra_f, exp_r, pred_r in mismatches:
                parts = [f"- `{q_text}` ({exp_c}):"]
                if exp_c != pred_c:
                    parts.append(f"kategoria `{pred_c}` zamiast `{exp_c}`;")
                if miss_f:
                    parts.append(f"brakujące filtry: `{miss_f}`;")
                if extra_f:
                    parts.append(f"nadmiarowe filtry: `{extra_f}`;")
                if set(canonicalize_residual(exp_r)) != set(canonicalize_residual(pred_r)):
                    parts.append(f"residual `{pred_r}` (oczekiwano `{exp_r}`).")
                lines.append(" ".join(parts))
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    in_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    data = json.loads(in_path.read_text(encoding="utf-8"))
    report_md = generate_markdown(data)
    out_path.write_text(report_md + "\n", encoding="utf-8")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
