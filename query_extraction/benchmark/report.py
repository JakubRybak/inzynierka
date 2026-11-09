"""Generate a dynamic Markdown comparison report from benchmark JSON results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..parser import (
    CONFIGS,
    assemble_stage_prediction,
    resolve_config_list,
    resolve_config_name,
)
from .evaluate import canonicalize_filters, canonicalize_residual

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "results" / "benchmark_30_seed42.json"
DEFAULT_OUTPUT = HERE / "results" / "benchmark_report.md"


def fmt_s(val: float) -> str:
    return f"{val:.3f} s"


def _resolve_active_summaries(
    summaries: Dict[str, Any],
    configs: Optional[Sequence[str]] = None,
) -> List[Tuple[str, Dict[str, Any], Dict[str, Any]]]:
    """Return ordered list of (canonical_name, config_spec, summary_dict) present in `summaries`."""
    by_canonical: Dict[str, Dict[str, Any]] = {}
    for raw_key, summary in summaries.items():
        try:
            canon = resolve_config_name(raw_key)
            by_canonical[canon] = summary
        except ValueError:
            continue

    target_configs = resolve_config_list(configs) if configs else list(CONFIGS.keys())
    active: List[Tuple[str, Dict[str, Any], Dict[str, Any]]] = []
    for canon in target_configs:
        if canon in by_canonical:
            active.append((canon, CONFIGS[canon], by_canonical[canon]))
    return active


def generate_markdown(
    data: Dict[str, Any],
    configs: Optional[Sequence[str]] = None,
) -> str:
    summaries = data.get("summaries", {})
    queries = data.get("queries", [])
    n = len(queries)
    seed = data.get("seed")
    dataset_label = data.get("dataset", "query_extraction/benchmark/queries")

    active = _resolve_active_summaries(summaries, configs=configs)
    if not active:
        raise ValueError("No matching configuration summaries found in benchmark data.")

    first_summary = active[0][2]
    expected_clauses = first_summary["all_clauses"]["tp"] + first_summary["all_clauses"]["fn_missing"]
    expected_closed = first_summary["closed_clauses"]["tp"] + first_summary["closed_clauses"]["fn_missing"]
    expected_aux = first_summary["aux_clauses"]["tp"] + first_summary["aux_clauses"]["fn_missing"]

    best_f1_cfg = max(active, key=lambda item: (item[2]["all_clauses"]["f1_pct"], item[2]["full_query_exact_pct"]))
    best_exact_cfg = max(active, key=lambda item: (item[2]["full_query_exact_pct"], item[2]["all_clauses"]["f1_pct"]))
    fastest_cfg = min(active, key=lambda item: item[2]["latency"]["total_all_queries"]["p50"])
    under_1s_candidates = [
        item for item in active if item[2]["latency"]["total_all_queries"]["p50"] < 1.0
    ]
    best_sub1s_cfg = (
        max(
            under_1s_candidates,
            key=lambda item: (item[2]["full_query_exact_pct"], item[2]["all_clauses"]["f1_pct"]),
        )
        if under_1s_candidates
        else fastest_cfg
    )

    lines: List[str] = [
        f"# Raport benchmarku: Query Extraction (N = {n}, konfiguracje: {len(active)})",
        "",
        "> [!IMPORTANT]",
        "> **Podsumowanie wyników uruchomienia:**",
    ]

    for _, spec, s in active:
        lat = s["latency"]["total_all_queries"]
        c = s["all_clauses"]
        lines.append(
            f"> - **`{spec['name']}` ({spec['label']}):** "
            f"komplet filtrów **{s['complete_filter_set_correct']}/{n} ({s['complete_filter_set_accuracy_pct']}%)**, "
            f"F1 cech **{c['f1_pct']}%** (TP={c['tp']}/{expected_clauses}, FP={c['fp_redundant']}, FN={c['fn_missing']}), "
            f"pełna zgodność zapytania **{s['full_query_exact']}/{n} ({s['full_query_exact_pct']}%)**, "
            f"czas **p50 = {fmt_s(lat['p50'])}**, **p90 = {fmt_s(lat['p90'])}** "
            f"(**{lat['under_1_0s_pct']}% < 1.0 s**)."
        )

    lines.extend([
        ">",
        f"> **Najwyższa jakość ekstrakcji cech:** `{best_f1_cfg[1]['name']}` ({best_f1_cfg[1]['label']}) — "
        f"**{best_f1_cfg[2]['all_clauses']['f1_pct']}% F1 cech** oraz "
        f"**{best_exact_cfg[2]['full_query_exact_pct']}%** pełnej zgodności (`{best_exact_cfg[1]['name']}`).",
        f"> **Rekomendacja < 1.0 s:** `{best_sub1s_cfg[1]['name']}` ({best_sub1s_cfg[1]['label']}) — "
        f"**p50 = {fmt_s(best_sub1s_cfg[2]['latency']['total_all_queries']['p50'])}**, "
        f"najszybszy wariant: `{fastest_cfg[1]['name']}` (**p50 = {fmt_s(fastest_cfg[2]['latency']['total_all_queries']['p50'])}**).",
        "",
        "---",
        "",
        "## Metodologia i konfiguracja testu",
        "",
        f"1. **Zbiór testowy:** `{dataset_label}` — **{n} zapytań**"
        + (f" (losowanie stratyfikowane `--seed {seed}`)." if seed is not None else " (pełny zbiór)."),
        "2. **Prompty i few-shoty per kategoria:** Po klasyfikacji kategorii (`category_classification.yaml`) każdy kolejny etap (`full_extraction.yaml`, `closed_features.yaml`, `open_extraction.yaml`) otrzymuje wyłącznie definicje cech, reguły oraz 5 przykładów *few-shot* należących do tej konkretnej kategorii (`prompts/categories/<category>.yaml`).",
        "3. **Równoważność semantyczna w ewaluacji:** Pojedyncza wartość w `contains_all` i `contains_any` jest traktowana jako równoważna (`contains_all ['Cotton'] == contains_any ['Cotton']`), a nazwy marek (`brand`) są porównywane bezwielkościowo ([evaluate.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/benchmark/evaluate.py)).",
        "4. **Pomiar czasu:** Minimalny thinking (`temperature = 0`), ścisły Structured Output (`responseSchema` / `json_schema`).",
        "",
        "---",
        "",
        "## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)",
        "",
        "Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.",
        "",
        "| Scenariusz | Opis przepływu | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for canon, spec, s in active:
        lat = s["latency"]["total_all_queries"]
        lines.append(
            f"| `{canon}` | **{spec['label']}** | {fmt_s(lat['mean'])} | **{fmt_s(lat['p50'])}** | **{fmt_s(lat['p80'])}** | "
            f"**{fmt_s(lat['p90'])}** | **{fmt_s(lat['p95'])}** | {fmt_s(lat['max'])} | "
            f"{lat['under_0_7s']}/{lat['count']} ({lat['under_0_7s_pct']}%) | "
            f"**{lat['under_1_0s']}/{lat['count']} ({lat['under_1_0s_pct']}%)** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Czas poszczególnych części (Stage-by-Stage Latency Breakdown)",
        "",
        "| Część (Etap) | Model / API | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    s1_lat = first_summary["latency"]["step1_jev_category"]
    lines.append(
        f"| **`category` (Klasyfikacja kategorii)** *(wspólna)* | `typesafe/jev-1.14` (OpenRouter) | {s1_lat['count']} | "
        f"{fmt_s(s1_lat['mean'])} | **{fmt_s(s1_lat['p50'])}** | **{fmt_s(s1_lat['p80'])}** | "
        f"**{fmt_s(s1_lat['p90'])}** | **{fmt_s(s1_lat['p95'])}** | {fmt_s(s1_lat['max'])} |"
    )

    any_split = next((s for _, spec, s in active if spec["architecture"] == "split"), None)
    if any_split is not None:
        s21_lat = any_split["latency"]["step2_1_jev_features"]
        lines.append(
            f"| **`closed_features` (Cechy zamknięte ze schematu)** | `typesafe/jev-1.14` (OpenRouter) | {s21_lat['count']} | "
            f"{fmt_s(s21_lat['mean'])} | **{fmt_s(s21_lat['p50'])}** | **{fmt_s(s21_lat['p80'])}** | "
            f"**{fmt_s(s21_lat['p90'])}** | **{fmt_s(s21_lat['p95'])}** | {fmt_s(s21_lat['max'])} |"
        )

    for _, spec, s in active:
        st_lat = s["latency"]["step2_llm"]
        lines.append(
            f"| **`{spec['stage_key']}` ({spec['stage_description']})** | {spec['model_description']} | {st_lat['count']} | "
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
        "| Scenariusz | Opis przepływu | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for canon, spec, s in active:
        lines.append(
            f"| `{canon}` | **{spec['label']}** | {s['category_correct']}/{n} ({s['category_accuracy_pct']}%) | "
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
        f"W całej próbce {n} zapytań oczekiwanych było łącznie **{expected_clauses} klauzul filtrów** "
        f"({expected_closed} klauzul cech zamkniętych + {expected_aux} klauzul `brand`/`price`).",
        "",
        "| Scenariusz | Opis przepływu | Poprawne filtry (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe / zapytanie | Brakujące cechy (FN) | Brakujące / zapytanie | Precision | Recall | **F1 cech (Accuracy cech)** |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for canon, spec, s in active:
        c = s["all_clauses"]
        lines.append(
            f"| `{canon}` | **{spec['label']}** | {c['tp']} / {expected_clauses} | **{c['fp_redundant']}** | "
            f"{c['redundant_per_query']:.2f} | {c['fn_missing']} | {c['missing_per_query']:.2f} | "
            f"{c['precision_pct']}% | {c['recall_pct']}% | **{c['f1_pct']}%** |"
        )

    lines.extend([
        "",
        "### 3.3. Metryki `residual` oraz koszty API",
        "",
        f"| Scenariusz | Opis przepływu | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt na {n} zapytań (USD) | Średni koszt / 1000 zapytań (USD) |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for canon, spec, s in active:
        rc = s["residual_concepts"]
        cost_1k = s["avg_cost_per_query_usd"] * 1000.0
        lines.append(
            f"| `{canon}` | **{spec['label']}** | **{rc['f1_pct']}%** | {rc['precision_pct']}% | {rc['recall_pct']}% | "
            f"{s['empty_residual_accuracy_pct']}% | ${s['total_cost_usd']:.4f} | **${cost_1k:.2f}** |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Analiza różnic i przypadków błędnych na próbce testowej",
        "",
    ])

    for canon, spec, _ in active:
        lines.append(f"### `{canon}` — {spec['label']}")
        mismatches = []
        for q in queries:
            exp = q["expected"]
            assembled = assemble_stage_prediction(q["stages"], canon)
            pred = assembled["predicted"]
            cat = pred["category"]
            pred_filters = pred["filters"]
            pred_res = pred["residual"]

            exp_f = canonicalize_filters(exp["filters"])
            pred_f = canonicalize_filters(pred_filters)
            exp_r = set(canonicalize_residual(exp["residual"]))
            pred_r = set(canonicalize_residual(pred_res))

            if cat != exp["category"] or exp_f != pred_f or exp_r != pred_r:
                extra_f = sorted(pred_f - exp_f)
                miss_f = sorted(exp_f - pred_f)
                mismatches.append((q["query"], exp["category"], cat, miss_f, extra_f, exp["residual"], pred_res))

        if not mismatches:
            lines.append(f"- Brak błędów ({n}/{n} idealnie zgodne).")
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT, help="Input benchmark JSON file")
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT, help="Output Markdown report file")
    parser.add_argument(
        "--configs",
        nargs="+",
        default=None,
        help="Optional subset of configuration names to include in the report",
    )
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    report_md = generate_markdown(data, configs=args.configs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report_md + "\n", encoding="utf-8")
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
