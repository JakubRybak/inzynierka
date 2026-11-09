"""Configurable benchmark runner for query extraction pipelines (full_* and split_*)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ..clients.jev import (
    JevClient,
    category_payload,
    closed_features_payload,
    filters_from_answers,
    normalize_query,
)
from ..clients.llm import (
    GPT_OSS_MODEL,
    QWEN_MODEL,
    CerebrasClient,
    VertexGeminiClient,
)
from ..core.catalog import load_query_catalog
from ..core.few_shots import CATEGORY_FEW_SHOTS, PER_CATEGORY_FEW_SHOTS
from ..parser import (
    CONFIGS,
    assemble_stage_prediction,
    normalize_stage_keys,
    resolve_config_list,
    resolve_config_name,
)
from .dataset import QUERIES, load_dataset_rows, parse_size
from .evaluate import evaluate_predictions
from .report import DEFAULT_OUTPUT as DEFAULT_REPORT_OUTPUT, generate_markdown

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"


def assert_no_data_leakage(sample_rows: Sequence[Dict[str, Any]]) -> None:
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


def required_stages_for_configs(selected_configs: Sequence[str]) -> Set[str]:
    """Return the set of stage keys required to evaluate `selected_configs`."""
    stages: Set[str] = set()
    for cfg in resolve_config_list(selected_configs):
        stages.update(CONFIGS[cfg]["required_stages"])
    return stages


def run_benchmark(
    *,
    configs: Optional[Sequence[str]] = None,
    dataset_path: Optional[Path] = None,
    size: Optional[int] = 30,
    seed: int = 42,
    categories: Optional[Sequence[str]] = None,
    budget_usd: float = 0.15,
    output_path: Path = RESULTS_DIR / "benchmark_30_seed42.json",
    report_output_path: Optional[Path] = DEFAULT_REPORT_OUTPUT,
    fresh: bool = False,
) -> Tuple[Dict[str, Any], str]:
    """Run benchmark on `configs` over the selected test dataset and generate a Markdown report."""
    selected_configs = resolve_config_list(configs)
    needed_stages = required_stages_for_configs(selected_configs)

    catalog = load_query_catalog()
    target_dataset = (dataset_path or QUERIES).resolve()
    sample_rows = load_dataset_rows(
        dataset_path=target_dataset,
        size=size,
        seed=seed,
        categories=categories,
    )
    assert_no_data_leakage(sample_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        dataset_rel = str(target_dataset.relative_to(HERE.parents[1]))
    except ValueError:
        dataset_rel = str(target_dataset)

    state: Optional[Dict[str, Any]] = None
    if output_path.exists() and not fresh:
        loaded = json.loads(output_path.read_text(encoding="utf-8"))
        loaded_queries = loaded.get("queries", [])
        if [q["query"] for q in loaded_queries] == [r["query"] for r in sample_rows]:
            for q in loaded_queries:
                normalize_stage_keys(q.get("stages", {}))
            state = loaded
            state["dataset"] = dataset_rel
            state["selected_configs"] = selected_configs
            print(f"Resuming from existing checkpoint: {output_path}", flush=True)
        else:
            print(
                f"Existing file {output_path} has a different query set; initializing new state.",
                flush=True,
            )

    if state is None:
        state = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "dataset": dataset_rel,
            "sample_size": len(sample_rows),
            "seed": seed if size is not None else None,
            "selected_configs": selected_configs,
            "queries": [
                {
                    "index": idx,
                    "query": row["query"],
                    "language": row["language"],
                    "source": row["source"],
                    "expected": row["expected"],
                    "stages": {},
                }
                for idx, row in enumerate(sample_rows)
            ],
            "summaries": {},
        }

    def save_state() -> None:
        output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    queries = state["queries"]

    # 1. Jev Stage: category & closed_features (only if a split_* config is selected)
    run_closed_features = "closed_features" in needed_stages
    needs_jev = any(
        "category" not in q["stages"]
        or (
            run_closed_features
            and q["stages"]["category"]["category"] is not None
            and "closed_features" not in q["stages"]
        )
        for q in queries
    )
    if needs_jev:
        jev = JevClient(budget_usd=budget_usd)
        w = jev.warmup()
        print(f"[Jev 1.14] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            if "category" not in q["stages"]:
                res = jev.call(category_payload(q["query"]))
                choice = res.answers["category"]["choice"]
                cat = None if choice == "outside" else choice
                q["stages"]["category"] = {
                    "category": cat,
                    "latency_seconds": round(res.latency_seconds, 4),
                    "cost_usd": round(res.cost_usd, 6),
                }
                save_state()
            cat = q["stages"]["category"]["category"]
            if run_closed_features and cat is not None and "closed_features" not in q["stages"]:
                fp, fmap = closed_features_payload(q["query"], cat, catalog)
                f_res = jev.call(fp)
                closed_filters = filters_from_answers(f_res.answers, cat, catalog, fmap)
                q["stages"]["closed_features"] = {
                    "filters": closed_filters,
                    "latency_seconds": round(f_res.latency_seconds, 4),
                    "cost_usd": round(f_res.cost_usd, 6),
                }
                save_state()
            print(
                f"  [Jev] {q['index']+1}/{len(queries)} cat={cat} "
                f"t_cat={q['stages']['category']['latency_seconds']:.3f}s "
                f"t_closed={q['stages'].get('closed_features', {}).get('latency_seconds', 0.0):.3f}s | {q['query']}",
                flush=True,
            )

    # 2. Full Extraction: Gemini 3.5 Flash-Lite (Vertex AI)
    if "full_gemini" in needed_stages and any(
        q["stages"]["category"]["category"] is not None and "full_gemini" not in q["stages"]
        for q in queries
    ):
        gemini = VertexGeminiClient()
        w = gemini.warmup(catalog)
        print(f"[full_gemini · Gemini 3.5 Flash-Lite] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["category"]["category"]
            if cat is None or "full_gemini" in q["stages"]:
                continue
            res = gemini.extract_full(q["query"], cat, catalog)
            q["stages"]["full_gemini"] = {
                "filters": res.parsed["filters"],
                "residual": res.parsed["residual"],
                "latency_seconds": round(res.latency_seconds, 4),
                "cost_usd": round(res.cost_usd, 6),
            }
            save_state()
            print(
                f"  [full_gemini] {q['index']+1}/{len(queries)} t={res.latency_seconds:.3f}s | {q['query']}",
                flush=True,
            )

    # 3. Full & Split Open Extraction: Qwen 3.8 27B (Cerebras, thinking=none)
    run_full_qwen = "full_qwen" in needed_stages
    run_open_qwen = "open_qwen" in needed_stages
    needs_qwen = (run_full_qwen or run_open_qwen) and any(
        q["stages"]["category"]["category"] is not None
        and (
            (run_full_qwen and "full_qwen" not in q["stages"])
            or (run_open_qwen and "open_qwen" not in q["stages"])
        )
        for q in queries
    )
    if needs_qwen:
        qwen = CerebrasClient(model=QWEN_MODEL, reasoning_effort="none")
        w = qwen.warmup_full(catalog)
        print(f"[Qwen 3.8 27B · Cerebras] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["category"]["category"]
            if cat is None:
                continue
            if run_full_qwen and "full_qwen" not in q["stages"]:
                res_full = qwen.extract_full(q["query"], cat, catalog)
                q["stages"]["full_qwen"] = {
                    "filters": res_full.parsed["filters"],
                    "residual": res_full.parsed["residual"],
                    "latency_seconds": round(res_full.latency_seconds, 4),
                    "cost_usd": round(res_full.cost_usd, 6),
                }
                save_state()
            if run_open_qwen and "open_qwen" not in q["stages"]:
                closed_filters = q["stages"]["closed_features"]["filters"]
                res_open = qwen.extract_open(q["query"], cat, closed_filters, catalog)
                q["stages"]["open_qwen"] = {
                    "filters": res_open.parsed["filters"],
                    "residual": res_open.parsed["residual"],
                    "latency_seconds": round(res_open.latency_seconds, 4),
                    "cost_usd": round(res_open.cost_usd, 6),
                }
                save_state()
            msg_parts = [f"  [Qwen 3.8 27B] {q['index']+1}/{len(queries)}"]
            if run_full_qwen:
                msg_parts.append(f"full={q['stages']['full_qwen']['latency_seconds']:.3f}s")
            if run_open_qwen:
                msg_parts.append(f"open={q['stages']['open_qwen']['latency_seconds']:.3f}s")
            msg_parts.append(f"| {q['query']}")
            print(" ".join(msg_parts), flush=True)

    # 4. Full & Split Open Extraction: GPT-OSS-120B (Cerebras, thinking=low)
    run_full_gpt = "full_gpt_oss" in needed_stages
    run_open_gpt = "open_gpt_oss" in needed_stages
    needs_gpt = (run_full_gpt or run_open_gpt) and any(
        q["stages"]["category"]["category"] is not None
        and (
            (run_full_gpt and "full_gpt_oss" not in q["stages"])
            or (run_open_gpt and "open_gpt_oss" not in q["stages"])
        )
        for q in queries
    )
    if needs_gpt:
        gpt = CerebrasClient(model=GPT_OSS_MODEL, reasoning_effort="low")
        w = gpt.warmup_full(catalog)
        print(f"[GPT-OSS-120B · Cerebras] Warmup completed in {w:.3f}s", flush=True)
        for q in queries:
            cat = q["stages"]["category"]["category"]
            if cat is None:
                continue
            if run_full_gpt and "full_gpt_oss" not in q["stages"]:
                res_full = gpt.extract_full(q["query"], cat, catalog)
                q["stages"]["full_gpt_oss"] = {
                    "filters": res_full.parsed["filters"],
                    "residual": res_full.parsed["residual"],
                    "latency_seconds": round(res_full.latency_seconds, 4),
                    "cost_usd": round(res_full.cost_usd, 6),
                }
                save_state()
            if run_open_gpt and "open_gpt_oss" not in q["stages"]:
                closed_filters = q["stages"]["closed_features"]["filters"]
                res_open = gpt.extract_open(q["query"], cat, closed_filters, catalog)
                q["stages"]["open_gpt_oss"] = {
                    "filters": res_open.parsed["filters"],
                    "residual": res_open.parsed["residual"],
                    "latency_seconds": round(res_open.latency_seconds, 4),
                    "cost_usd": round(res_open.cost_usd, 6),
                }
                save_state()
            msg_parts = [f"  [GPT-OSS-120B] {q['index']+1}/{len(queries)}"]
            if run_full_gpt:
                msg_parts.append(f"full={q['stages']['full_gpt_oss']['latency_seconds']:.3f}s")
            if run_open_gpt:
                msg_parts.append(f"open={q['stages']['open_gpt_oss']['latency_seconds']:.3f}s")
            msg_parts.append(f"| {q['query']}")
            print(" ".join(msg_parts), flush=True)

    # 5. Assemble end-to-end predictions and evaluate selected configurations
    clean_summaries: Dict[str, Any] = {}
    for raw_k, val in state.get("summaries", {}).items():
        try:
            clean_summaries[resolve_config_name(raw_k)] = val
        except ValueError:
            pass

    for canon in selected_configs:
        cases: List[Dict[str, Any]] = []
        for q in queries:
            assembled = assemble_stage_prediction(q["stages"], canon)
            cases.append(
                {
                    "query": q["query"],
                    "expected": q["expected"],
                    "predicted": assembled["predicted"],
                    "step1_latency_seconds": assembled["step1_latency_seconds"],
                    "step2_1_latency_seconds": assembled["step2_1_latency_seconds"],
                    "step2_llm_latency_seconds": assembled["step2_llm_latency_seconds"],
                    "total_latency_seconds": assembled["total_latency_seconds"],
                    "total_cost_usd": assembled["total_cost_usd"],
                }
            )
        clean_summaries[canon] = evaluate_predictions(cases)

    state["summaries"] = clean_summaries
    save_state()

    report_md = generate_markdown(state, configs=selected_configs)
    if report_output_path is not None:
        report_output_path.parent.mkdir(parents=True, exist_ok=True)
        report_output_path.write_text(report_md + "\n", encoding="utf-8")
        print(f"Markdown report written to {report_output_path}", flush=True)

    return state, report_md


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["all"],
        help=(
            "Configurations to benchmark (default: all). "
            f"Choices: {', '.join(CONFIGS.keys())} (or aliases)"
        ),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=QUERIES,
        help="Path to test dataset directory or .csv/.jsonl/.json file (default: query_extraction/benchmark/queries)",
    )
    parser.add_argument(
        "--size",
        type=parse_size,
        default=30,
        help="Stratified sample size or 'all' (default: 30)",
    )
    parser.add_argument(
        "--all-queries",
        action="store_true",
        help="Run all queries from --dataset without sampling (equivalent to --size all)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling (default: 42)")
    parser.add_argument(
        "--category",
        action="append",
        default=None,
        help="Restrict benchmark to specific category(ies). Can be repeated.",
    )
    parser.add_argument("--budget-usd", type=float, default=0.15, help="Max Jev budget in USD (default: 0.15)")
    parser.add_argument(
        "--output",
        "--json-output",
        dest="output",
        type=Path,
        default=RESULTS_DIR / "benchmark_30_seed42.json",
        help="Path to output JSON checkpoint/results file",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=DEFAULT_REPORT_OUTPUT,
        help="Path to output Markdown report file (default: query_extraction/benchmark/results/benchmark_report.md)",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore existing checkpoint and run selected stages fresh",
    )
    args = parser.parse_args()

    effective_size = None if args.all_queries else args.size
    run_benchmark(
        configs=args.configs,
        dataset_path=args.dataset,
        size=effective_size,
        seed=args.seed,
        categories=args.category,
        budget_usd=args.budget_usd,
        output_path=args.output,
        report_output_path=args.report_output,
        fresh=args.fresh,
    )


if __name__ == "__main__":
    main()
