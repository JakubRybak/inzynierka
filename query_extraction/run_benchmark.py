"""End-to-end benchmark runner comparing all 5 query extraction pipelines (2a and 2b)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List

from .catalog import load_query_catalog
from .evaluate import evaluate_predictions
from .few_shots import CATEGORY_FEW_SHOTS, PER_CATEGORY_FEW_SHOTS
from .jev_parser import (
    JevClient,
    category_payload,
    feature_payload,
    filters_from_answers,
    normalize_query,
)
from .llm_parser import (
    GEMINI_MODEL,
    GPT_OSS_MODEL,
    QWEN_MODEL,
    CerebrasClient,
    VertexGeminiClient,
)
from .sample_queries import load_queries, sample_queries

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"


def assert_no_data_leakage(sample_rows: List[Dict[str, str]]) -> None:
    few_shot_queries = {normalize_query(item["query"]) for item in CATEGORY_FEW_SHOTS}
    for cat_shots in PER_CATEGORY_FEW_SHOTS.values():
        for item in cat_shots:
            few_shot_queries.add(normalize_query(item["query"]))
    overlaps = [
        row["query"]
        for row in sample_rows
        if normalize_query(row["query"]) in few_shot_queries
    ]
    if overlaps:
        raise ValueError(f"Data leakage detected! Test queries overlap with few-shots: {overlaps}")


def run_smoke_test() -> None:
    catalog = load_query_catalog()
    jev = JevClient(budget_usd=0.05)
    gemini = VertexGeminiClient()
    qwen = CerebrasClient(model=QWEN_MODEL, reasoning_effort="none")
    gpt = CerebrasClient(model=GPT_OSS_MODEL, reasoning_effort="low", min_interval_seconds=12.5)

    print("Warming up clients...", flush=True)
    print(f"  Jev warmup:    {jev.warmup():.3f}s", flush=True)
    print(f"  Gemini warmup: {gemini.warmup(catalog):.3f}s", flush=True)
    print(f"  Qwen warmup:   {qwen.warmup_full(catalog):.3f}s", flush=True)
    print(f"  GPT warmup:    {gpt.warmup_full(catalog):.3f}s", flush=True)

    q = "navy wool overcoat with buttons under $250 for winter"
    cat_res = jev.call(category_payload(q))
    cat = cat_res.answers["category"]["choice"]
    cat = None if cat == "outside" else cat
    print(f"\nSmoke Query: {q}", flush=True)
    print(f"Step 1 Jev Category: {cat} ({cat_res.latency_seconds:.3f}s, ${cat_res.cost_usd:.6f})", flush=True)

    fp, fmap = feature_payload(q, cat, catalog)
    feat_res = jev.call(fp)
    jev_filters = filters_from_answers(feat_res.answers, cat, catalog, fmap)
    print(f"Step 2b-1 Jev Features ({feat_res.latency_seconds:.3f}s, ${feat_res.cost_usd:.6f}): {jev_filters}", flush=True)

    g_res = gemini.extract_full(q, cat, catalog)
    print(f"2a Gemini Full ({g_res.latency_seconds:.3f}s): {g_res.parsed}", flush=True)

    qw_full = qwen.extract_full(q, cat, catalog)
    print(f"2a Qwen Full ({qw_full.latency_seconds:.3f}s): {qw_full.parsed}", flush=True)

    qw_aux = qwen.extract_auxiliary(q, cat, jev_filters, catalog)
    print(f"2b Qwen Aux ({qw_aux.latency_seconds:.3f}s): {qw_aux.parsed}", flush=True)

    gpt_full = gpt.extract_full(q, cat, catalog)
    print(f"2a GPT Full ({gpt_full.latency_seconds:.3f}s): {gpt_full.parsed}", flush=True)

    gpt_aux = gpt.extract_auxiliary(q, cat, jev_filters, catalog)
    print(f"2b GPT Aux ({gpt_aux.latency_seconds:.3f}s): {gpt_aux.parsed}", flush=True)


def run_benchmark(size: int, seed: int, budget_usd: float, output_path: Path, fresh: bool = False) -> Dict[str, Any]:
    catalog = load_query_catalog()
    groups = load_queries()
    sample_rows = sample_queries(groups, size, seed)
    assert_no_data_leakage(sample_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not fresh:
        state = json.loads(output_path.read_text(encoding="utf-8"))
        print(f"Resuming from existing checkpoint: {output_path}", flush=True)
    else:
        state = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample_size": size,
            "seed": seed,
            "queries": [
                {
                    "index": idx,
                    "query": row["query"],
                    "language": row["language"],
                    "source": row["source"],
                    "expected": json.loads(row["expected_output"]),
                    "stages": {},
                }
                for idx, row in enumerate(sample_rows)
            ],
            "summaries": {},
        }

    def save_state() -> None:
        output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    queries = state["queries"]

    # 1. Jev Stage 1 (Category) & Stage 2b-1 (Closed-Vocabulary Features)
    needs_jev = any(
        "jev_category" not in q["stages"]
        or (q["stages"]["jev_category"]["category"] is not None and "jev_features" not in q["stages"])
        for q in queries
    )
    if needs_jev:
        jev = JevClient(budget_usd=budget_usd)
        w = jev.warmup()
        print(f"[Jev 1.14] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            if "jev_category" not in q["stages"]:
                res = jev.call(category_payload(q["query"]))
                choice = res.answers["category"]["choice"]
                cat = None if choice == "outside" else choice
                q["stages"]["jev_category"] = {
                    "category": cat,
                    "latency_seconds": round(res.latency_seconds, 4),
                    "cost_usd": round(res.cost_usd, 6),
                }
                save_state()
            cat = q["stages"]["jev_category"]["category"]
            if cat is not None and "jev_features" not in q["stages"]:
                fp, fmap = feature_payload(q["query"], cat, catalog)
                f_res = jev.call(fp)
                j_filters = filters_from_answers(f_res.answers, cat, catalog, fmap)
                q["stages"]["jev_features"] = {
                    "filters": j_filters,
                    "latency_seconds": round(f_res.latency_seconds, 4),
                    "cost_usd": round(f_res.cost_usd, 6),
                }
                save_state()
            print(
                f"  [Jev] {q['index']+1}/{len(queries)} cat={cat} "
                f"t_cat={q['stages']['jev_category']['latency_seconds']:.3f}s "
                f"t_feat={q['stages'].get('jev_features', {}).get('latency_seconds', 0.0):.3f}s | {q['query']}",
                flush=True,
            )

    # 2. Variant 2a: Gemini 3.5 Flash-Lite (Vertex AI)
    if any(q["stages"]["jev_category"]["category"] is not None and "2a_gemini" not in q["stages"] for q in queries):
        gemini = VertexGeminiClient()
        w = gemini.warmup(catalog)
        print(f"[2a Gemini 3.5 Flash-Lite] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["jev_category"]["category"]
            if cat is None or "2a_gemini" in q["stages"]:
                continue
            res = gemini.extract_full(q["query"], cat, catalog)
            q["stages"]["2a_gemini"] = {
                "filters": res.parsed["filters"],
                "residual": res.parsed["residual"],
                "latency_seconds": round(res.latency_seconds, 4),
                "cost_usd": round(res.cost_usd, 6),
            }
            save_state()
            print(
                f"  [2a Gemini] {q['index']+1}/{len(queries)} t={res.latency_seconds:.3f}s | {q['query']}",
                flush=True,
            )

    # 3. Variant 2a & 2b: Qwen 3.8 27B (Cerebras, thinking=none)
    needs_qwen = any(
        q["stages"]["jev_category"]["category"] is not None
        and ("2a_qwen" not in q["stages"] or "2b_qwen_aux" not in q["stages"])
        for q in queries
    )
    if needs_qwen:
        qwen = CerebrasClient(model=QWEN_MODEL, reasoning_effort="none")
        w = qwen.warmup_full(catalog)
        print(f"[Qwen 3.8 27B · Cerebras] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["jev_category"]["category"]
            if cat is None:
                continue
            if "2a_qwen" not in q["stages"]:
                res_full = qwen.extract_full(q["query"], cat, catalog)
                q["stages"]["2a_qwen"] = {
                    "filters": res_full.parsed["filters"],
                    "residual": res_full.parsed["residual"],
                    "latency_seconds": round(res_full.latency_seconds, 4),
                    "cost_usd": round(res_full.cost_usd, 6),
                }
                save_state()
            if "2b_qwen_aux" not in q["stages"]:
                j_filters = q["stages"]["jev_features"]["filters"]
                res_aux = qwen.extract_auxiliary(q["query"], cat, j_filters, catalog)
                q["stages"]["2b_qwen_aux"] = {
                    "filters": res_aux.parsed["filters"],
                    "residual": res_aux.parsed["residual"],
                    "latency_seconds": round(res_aux.latency_seconds, 4),
                    "cost_usd": round(res_aux.cost_usd, 6),
                }
                save_state()
            print(
                f"  [Qwen 3.8 27B] {q['index']+1}/{len(queries)} "
                f"2a={q['stages']['2a_qwen']['latency_seconds']:.3f}s "
                f"2b_aux={q['stages']['2b_qwen_aux']['latency_seconds']:.3f}s | {q['query']}",
                flush=True,
            )

    # 4. Variant 2a & 2b: GPT-OSS-120B (Cerebras, thinking=low, 5 req/min rate limit paced outside timer)
    needs_gpt = any(
        q["stages"]["jev_category"]["category"] is not None
        and ("2a_gpt_oss" not in q["stages"] or "2b_gpt_oss_aux" not in q["stages"])
        for q in queries
    )
    if needs_gpt:
        gpt = CerebrasClient(model=GPT_OSS_MODEL, reasoning_effort="low", min_interval_seconds=12.2)
        w = gpt.warmup_full(catalog)
        print(f"[GPT-OSS-120B · Cerebras] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["jev_category"]["category"]
            if cat is None:
                continue
            if "2a_gpt_oss" not in q["stages"]:
                res_full = gpt.extract_full(q["query"], cat, catalog)
                q["stages"]["2a_gpt_oss"] = {
                    "filters": res_full.parsed["filters"],
                    "residual": res_full.parsed["residual"],
                    "latency_seconds": round(res_full.latency_seconds, 4),
                    "cost_usd": round(res_full.cost_usd, 6),
                }
                save_state()
            if "2b_gpt_oss_aux" not in q["stages"]:
                j_filters = q["stages"]["jev_features"]["filters"]
                res_aux = gpt.extract_auxiliary(q["query"], cat, j_filters, catalog)
                q["stages"]["2b_gpt_oss_aux"] = {
                    "filters": res_aux.parsed["filters"],
                    "residual": res_aux.parsed["residual"],
                    "latency_seconds": round(res_aux.latency_seconds, 4),
                    "cost_usd": round(res_aux.cost_usd, 6),
                }
                save_state()
            print(
                f"  [GPT-OSS-120B] {q['index']+1}/{len(queries)} "
                f"2a={q['stages']['2a_gpt_oss']['latency_seconds']:.3f}s "
                f"2b_aux={q['stages']['2b_gpt_oss_aux']['latency_seconds']:.3f}s | {q['query']}",
                flush=True,
            )

    # 5. Assemble end-to-end predictions and evaluate all 5 pipelines
    pipelines = {
        "2a_gemini_flash_lite": ("2a", "2a_gemini"),
        "2a_qwen_3_8_27b": ("2a", "2a_qwen"),
        "2a_gpt_oss_120b": ("2a", "2a_gpt_oss"),
        "2b_jev_qwen_3_8_27b": ("2b", "2b_qwen_aux"),
        "2b_jev_gpt_oss_120b": ("2b", "2b_gpt_oss_aux"),
    }

    summaries: Dict[str, Any] = {}
    for name, (kind, stage_key) in pipelines.items():
        cases: List[Dict[str, Any]] = []
        for q in queries:
            s_cat = q["stages"]["jev_category"]
            cat = s_cat["category"]
            t1 = s_cat["latency_seconds"]
            c1 = s_cat["cost_usd"]

            if cat is None:
                cases.append(
                    {
                        "query": q["query"],
                        "expected": q["expected"],
                        "predicted": {"category": None, "filters": [], "residual": []},
                        "step1_latency_seconds": t1,
                        "step2_1_latency_seconds": 0.0,
                        "step2_llm_latency_seconds": 0.0,
                        "total_latency_seconds": t1,
                        "total_cost_usd": c1,
                    }
                )
            elif kind == "2a":
                s_llm = q["stages"][stage_key]
                t_llm = s_llm["latency_seconds"]
                c_llm = s_llm["cost_usd"]
                cases.append(
                    {
                        "query": q["query"],
                        "expected": q["expected"],
                        "predicted": {
                            "category": cat,
                            "filters": s_llm["filters"],
                            "residual": s_llm["residual"],
                        },
                        "step1_latency_seconds": t1,
                        "step2_1_latency_seconds": 0.0,
                        "step2_llm_latency_seconds": t_llm,
                        "total_latency_seconds": round(t1 + t_llm, 4),
                        "total_cost_usd": round(c1 + c_llm, 6),
                    }
                )
            else:
                s_feat = q["stages"]["jev_features"]
                s_aux = q["stages"][stage_key]
                t2_1 = s_feat["latency_seconds"]
                c2_1 = s_feat["cost_usd"]
                t_aux = s_aux["latency_seconds"]
                c_aux = s_aux["cost_usd"]
                cases.append(
                    {
                        "query": q["query"],
                        "expected": q["expected"],
                        "predicted": {
                            "category": cat,
                            "filters": s_feat["filters"] + s_aux["filters"],
                            "residual": s_aux["residual"],
                        },
                        "step1_latency_seconds": t1,
                        "step2_1_latency_seconds": t2_1,
                        "step2_llm_latency_seconds": t_aux,
                        "total_latency_seconds": round(t1 + t2_1 + t_aux, 4),
                        "total_cost_usd": round(c1 + c2_1 + c_aux, 6),
                    }
                )
        summaries[name] = evaluate_predictions(cases)

    state["summaries"] = summaries
    save_state()
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true", help="Run 1-query smoke test across all 5 pipelines")
    parser.add_argument("--size", type=int, default=30, help="Stratified sample size (default: 30)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--budget-usd", type=float, default=0.15, help="Max Jev budget in USD (default: 0.15)")
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "benchmark_30_seed42.json",
        help="Path to output JSON file",
    )
    parser.add_argument("--fresh", action="store_true", help="Ignore existing checkpoint and run all stages fresh")
    args = parser.parse_args()

    if args.smoke_test:
        run_smoke_test()
        return

    run_benchmark(args.size, args.seed, args.budget_usd, args.output, fresh=args.fresh)


if __name__ == "__main__":
    main()
