"""Evaluation metrics (latency percentiles, filter accuracy, redundant/missing filters, residual F1) for query extraction."""

from __future__ import annotations

import math
import re
import statistics
from typing import Any, Dict, List, Set, Tuple
import unicodedata


def normalize_text(text: str) -> str:
    """Case-insensitive, punctuation-normalized string representation."""
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def canonicalize_clause(clause: Dict[str, Any]) -> Tuple[Any, ...]:
    """Canonical representation of a filter clause for semantic equivalence."""
    feat = clause["feature"]
    op = clause["operator"]
    if feat == "price":
        val = float(clause["value"])
        return ("price", op, round(val, 4))
    vals = clause["values"]
    if feat == "brand":
        norm_vals = tuple(sorted({normalize_text(v) for v in vals}))
        return ("brand", op, norm_vals)
    dedup = tuple(sorted(set(vals)))
    # A 1-element contains_all is semantically identical to a 1-element contains_any.
    if op == "contains_all" and len(dedup) == 1:
        op = "contains_any"
    return (feat, op, dedup)


def canonicalize_filters(
    filters: List[Dict[str, Any]],
    *,
    mode: str = "all",
) -> Set[Tuple[Any, ...]]:
    """Return canonical set of filter clauses ('all', 'closed', or 'aux')."""
    result: Set[Tuple[Any, ...]] = set()
    for c in filters:
        feat = c["feature"]
        if mode == "closed" and feat in ("brand", "price"):
            continue
        if mode == "aux" and feat not in ("brand", "price"):
            continue
        result.add(canonicalize_clause(c))
    return result


def canonicalize_residual(residual: List[str]) -> List[str]:
    """Normalize residual concept strings while preserving order and removing empty items."""
    out: List[str] = []
    for item in residual:
        norm = normalize_text(item)
        if norm and norm not in out:
            out.append(norm)
    return out


def percentile(values: List[float], p: float) -> float:
    """Compute linear-interpolated percentile (0 <= p <= 100)."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def summarize_latencies(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "min": 0.0,
            "p50": 0.0,
            "p80": 0.0,
            "p90": 0.0,
            "p95": 0.0,
            "max": 0.0,
            "under_0_7s": 0,
            "under_0_7s_pct": 0.0,
            "under_1_0s": 0,
            "under_1_0s_pct": 0.0,
        }
    n = len(values)
    u07 = sum(1 for v in values if v < 0.7)
    u10 = sum(1 for v in values if v < 1.0)
    return {
        "count": n,
        "mean": round(statistics.mean(values), 4),
        "min": round(min(values), 4),
        "p50": round(percentile(values, 50), 4),
        "p80": round(percentile(values, 80), 4),
        "p90": round(percentile(values, 90), 4),
        "p95": round(percentile(values, 95), 4),
        "max": round(max(values), 4),
        "under_0_7s": u07,
        "under_0_7s_pct": round(100.0 * u07 / n, 1),
        "under_1_0s": u10,
        "under_1_0s_pct": round(100.0 * u10 / n, 1),
    }


def evaluate_predictions(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute comprehensive accuracy, redundancy, residual, and latency metrics over evaluated cases."""
    n = len(cases)
    cat_correct = 0
    all_filters_exact = 0
    closed_filters_exact = 0
    aux_filters_exact = 0
    residual_exact = 0
    residual_set_exact = 0
    empty_residual_total = 0
    empty_residual_correct = 0
    full_query_exact = 0

    tp_all = fp_all = fn_all = 0
    tp_closed = fp_closed = fn_closed = 0
    tp_aux = fp_aux = fn_aux = 0
    res_tp = res_fp = res_fn = 0

    for row in cases:
        exp = row["expected"]
        pred = row["predicted"]

        c_ok = pred["category"] == exp["category"]
        cat_correct += int(c_ok)

        exp_all = canonicalize_filters(exp["filters"], mode="all")
        pred_all = canonicalize_filters(pred["filters"], mode="all")
        f_all_ok = c_ok and (pred_all == exp_all)
        all_filters_exact += int(f_all_ok)

        exp_closed = canonicalize_filters(exp["filters"], mode="closed")
        pred_closed = canonicalize_filters(pred["filters"], mode="closed")
        f_closed_ok = c_ok and (pred_closed == exp_closed)
        closed_filters_exact += int(f_closed_ok)

        exp_aux = canonicalize_filters(exp["filters"], mode="aux")
        pred_aux = canonicalize_filters(pred["filters"], mode="aux")
        f_aux_ok = c_ok and (pred_aux == exp_aux)
        aux_filters_exact += int(f_aux_ok)

        tp_all += len(exp_all & pred_all)
        fp_all += len(pred_all - exp_all)
        fn_all += len(exp_all - pred_all)

        tp_closed += len(exp_closed & pred_closed)
        fp_closed += len(pred_closed - exp_closed)
        fn_closed += len(exp_closed - pred_closed)

        tp_aux += len(exp_aux & pred_aux)
        fp_aux += len(pred_aux - exp_aux)
        fn_aux += len(exp_aux - pred_aux)

        exp_res = canonicalize_residual(exp["residual"])
        pred_res = canonicalize_residual(pred["residual"])
        r_exact = c_ok and (pred_res == exp_res)
        r_set_exact = c_ok and (set(pred_res) == set(exp_res))
        residual_exact += int(r_exact)
        residual_set_exact += int(r_set_exact)

        if not exp_res:
            empty_residual_total += 1
            if not pred_res:
                empty_residual_correct += 1

        res_tp += len(set(exp_res) & set(pred_res))
        res_fp += len(set(pred_res) - set(exp_res))
        res_fn += len(set(exp_res) - set(pred_res))

        if c_ok and f_all_ok and r_set_exact:
            full_query_exact += 1

    def prf(tp: int, fp: int, fn: int) -> Dict[str, Any]:
        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        return {
            "tp": tp,
            "fp_redundant": fp,
            "fn_missing": fn,
            "redundant_per_query": round(fp / n, 3) if n else 0.0,
            "missing_per_query": round(fn / n, 3) if n else 0.0,
            "precision_pct": round(100.0 * prec, 1),
            "recall_pct": round(100.0 * rec, 1),
            "f1_pct": round(100.0 * f1, 1),
        }

    total_latencies = [r["total_latency_seconds"] for r in cases]
    supported_latencies = [r["total_latency_seconds"] for r in cases if r["predicted"]["category"] is not None]
    step1_latencies = [r["step1_latency_seconds"] for r in cases]
    step2_1_latencies = [r["step2_1_latency_seconds"] for r in cases if r.get("step2_1_latency_seconds", 0.0) > 0]
    step2_llm_latencies = [r["step2_llm_latency_seconds"] for r in cases if r.get("step2_llm_latency_seconds", 0.0) > 0]

    total_cost = sum(r.get("total_cost_usd", 0.0) for r in cases)

    return {
        "num_queries": n,
        "category_accuracy_pct": round(100.0 * cat_correct / n, 1) if n else 0.0,
        "category_correct": cat_correct,
        "complete_filter_set_accuracy_pct": round(100.0 * all_filters_exact / n, 1) if n else 0.0,
        "complete_filter_set_correct": all_filters_exact,
        "closed_filter_set_accuracy_pct": round(100.0 * closed_filters_exact / n, 1) if n else 0.0,
        "closed_filter_set_correct": closed_filters_exact,
        "aux_filter_set_accuracy_pct": round(100.0 * aux_filters_exact / n, 1) if n else 0.0,
        "aux_filter_set_correct": aux_filters_exact,
        "all_clauses": prf(tp_all, fp_all, fn_all),
        "closed_clauses": prf(tp_closed, fp_closed, fn_closed),
        "aux_clauses": prf(tp_aux, fp_aux, fn_aux),
        "residual_exact_order_pct": round(100.0 * residual_exact / n, 1) if n else 0.0,
        "residual_set_accuracy_pct": round(100.0 * residual_set_exact / n, 1) if n else 0.0,
        "residual_set_correct": residual_set_exact,
        "empty_residual_accuracy_pct": (
            round(100.0 * empty_residual_correct / empty_residual_total, 1) if empty_residual_total else 0.0
        ),
        "residual_concepts": prf(res_tp, res_fp, res_fn),
        "full_query_exact_pct": round(100.0 * full_query_exact / n, 1) if n else 0.0,
        "full_query_exact": full_query_exact,
        "total_cost_usd": round(total_cost, 6),
        "avg_cost_per_query_usd": round(total_cost / n, 6) if n else 0.0,
        "latency": {
            "total_all_queries": summarize_latencies(total_latencies),
            "total_supported_queries": summarize_latencies(supported_latencies),
            "step1_jev_category": summarize_latencies(step1_latencies),
            "step2_1_jev_features": summarize_latencies(step2_1_latencies),
            "step2_llm": summarize_latencies(step2_llm_latencies),
        },
    }
