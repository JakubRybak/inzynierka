"""Benchmarking, dataset sampling, evaluation metrics, and Markdown report generation."""

from __future__ import annotations

from .dataset import QUERIES, load_dataset_rows, load_queries, parse_size, sample_queries
from .evaluate import (
    canonicalize_clause,
    canonicalize_filters,
    canonicalize_residual,
    evaluate_predictions,
    summarize_latencies,
)
from .report import DEFAULT_INPUT, DEFAULT_OUTPUT, generate_markdown
from .run import required_stages_for_configs, run_benchmark

__all__ = [
    "DEFAULT_INPUT",
    "DEFAULT_OUTPUT",
    "QUERIES",
    "canonicalize_clause",
    "canonicalize_filters",
    "canonicalize_residual",
    "evaluate_predictions",
    "generate_markdown",
    "load_dataset_rows",
    "load_queries",
    "parse_size",
    "required_stages_for_configs",
    "run_benchmark",
    "sample_queries",
    "summarize_latencies",
]
