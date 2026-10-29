"""
Step E: threshold and text format for matching the parser residual with the concept names.

For every case in threshold_cases.yaml and both formats in poc/search_ui/concepts.py (plain, query) the residual and
the concept names are embedded with gemini-embedding-2. A concept is chosen as in the search: among the k most
similar and with similarity >= the threshold. For each threshold:
  TP – a positive case whose most similar chosen concept is acceptable;
  FP – a negative case with any chosen concept, or a positive one whose most similar chosen concept is not acceptable;
  precision = TP / (TP + FP), recall = TP / positive cases.
The report (data/threshold_report.md) gives top-1 accuracy, the threshold with the best F1 and every case.

    python poc/concepts/check_threshold.py            # number of calls only
    python poc/concepts/check_threshold.py --execute  # paid: (concepts + cases) x 2 embedding calls
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "search_ui"))
import common  # noqa: E402
import concepts  # noqa: E402

CASES = HERE / "threshold_cases.yaml"
REPORT = HERE / "data/threshold_report.md"
MODEL, DIM = "gemini-embedding-2", 3072
GRID = np.round(np.arange(0.30, 0.96, 0.01), 2)


def load_cases(ids):
    d = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    positive = {str(r): list(v) for r, v in d["positive"].items()}
    unknown = {c for v in positive.values() for c in v} - set(ids)
    if unknown:
        raise SystemExit(f"{CASES.name}: unknown concepts {sorted(unknown)}")
    return positive, [str(r) for r in d["negative"]]


def similarities(names, residuals, fmt, workers):
    text = concepts.FORMATS[fmt]
    embedder = common.QueryEmbedder(MODEL, DIM)
    with ThreadPoolExecutor(workers) as pool:
        v = common.normalize(np.stack(list(pool.map(embedder, [text(x) for x in names + residuals]))))
    return v[len(names):] @ v[:len(names)].T


def verdict(sims, expected, threshold, k):
    """'ok', 'wrong', 'fallback' (positive with nothing chosen), 'rejected' or 'false' (negative)."""
    chosen, _ = concepts.select(sims, threshold, k, 1.0)
    if not expected:
        return "false" if chosen else "rejected"
    if not chosen:
        return "fallback"
    return "ok" if chosen[0] in expected else "wrong"


def metrics(sims, expected, threshold, k):
    v = [verdict(s, e, threshold, k) for s, e in zip(sims, expected)]
    tp, fp = v.count("ok"), v.count("wrong") + v.count("false")
    positives = sum(bool(e) for e in expected)
    precision, recall = tp / max(tp + fp, 1), tp / max(positives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return dict(threshold=float(threshold), f1=f1, precision=precision, recall=recall, verdicts=v,
                rejected=v.count("rejected"), negatives=len(expected) - positives)


def best(sims, expected, k):
    results = [metrics(sims, expected, t, k) for t in GRID]
    top = max(r["f1"] for r in results)
    plateau = [r for r in results if r["f1"] >= top - 1e-9]
    return results, plateau[len(plateau) // 2]


def report(sims_by_format, residuals, expected, ids, names, k):
    lines = ["# Concept threshold", "",
             f"`check_threshold.py`, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, {MODEL}, k = {k}, "
             f"{sum(bool(e) for e in expected)} positive and {sum(not e for e in expected)} negative cases "
             f"from `{CASES.name}`. Threshold = middle of the best-F1 range.", "",
             "| format | top-1 accuracy | threshold | best-F1 range | F1 | precision | recall | negatives rejected |",
             "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |"]
    chosen = {}
    for fmt, sims in sims_by_format.items():
        results, b = best(sims, expected, k)
        plateau = [r["threshold"] for r in results if r["f1"] >= b["f1"] - 1e-9]
        top1 = np.mean([int(np.argmax(s)) in e for s, e in zip(sims, expected) if e])
        chosen[fmt] = (b, top1)
        lines.append(f"| {fmt} | {top1:.0%} | {b['threshold']:.2f} | {plateau[0]:.2f}–{plateau[-1]:.2f} | {b['f1']:.2f} "
                     f"| {b['precision']:.2f} | {b['recall']:.2f} | {b['rejected']}/{b['negatives']} |")
    for fmt, sims in sims_by_format.items():
        pos_best = [max(s[j] for j in e) for s, e in zip(sims, expected) if e]
        neg_max = [s.max() for s, e in zip(sims, expected) if not e]
        lines += ["", f"## {fmt}", "",
                  f"Similarity of the best acceptable concept, positive cases: min {min(pos_best):.2f}, median "
                  f"{np.median(pos_best):.2f}. Highest similarity, negative cases: median {np.median(neg_max):.2f}, "
                  f"max {max(neg_max):.2f}.", "",
                  f"At threshold {chosen[fmt][0]['threshold']:.2f}:", "",
                  "| residual | acceptable | three most similar | result |", "| --- | --- | --- | --- |"]
        for r, e, s, v in zip(residuals, expected, sims, chosen[fmt][0]["verdicts"]):
            top = ", ".join(f"{names[j]} {s[j]:.2f}" for j in np.argsort(-s)[:3])
            lines.append(f"| {r} | {', '.join(ids[j] for j in e) or '–'} | {top} | {v} |")
    return "\n".join(lines) + "\n", chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="make the embedding calls")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    concept_list = concepts.load_list()
    ids, names = [c["id"] for c in concept_list], [c["name"] for c in concept_list]
    positive, negative = load_cases(ids)
    residuals = list(positive) + negative
    expected = [{ids.index(c) for c in positive[r]} for r in positive] + [set() for _ in negative]
    calls = (len(names) + len(residuals)) * len(concepts.FORMATS)
    print(f"{len(names)} concepts, {len(positive)} positive and {len(negative)} negative cases: {calls} embedding calls")
    if not args.execute:
        print("add --execute to make them")
        return None
    sims = {fmt: similarities(names, residuals, fmt, args.workers) for fmt in concepts.FORMATS}
    text, chosen = report(sims, residuals, expected, ids, names, args.k)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(text, encoding="utf-8")
    for fmt, (b, top1) in chosen.items():
        print(f"{fmt:6s} top-1 {top1:.0%}  threshold {b['threshold']:.2f}  F1 {b['f1']:.2f}  precision "
              f"{b['precision']:.2f}  recall {b['recall']:.2f}  negatives rejected {b['rejected']}/{b['negatives']}")
    print(f"-> {REPORT.relative_to(HERE.parents[1])}")
    return dict(sims=sims, residuals=residuals, expected=expected, ids=ids, chosen=chosen)


if __name__ == "__main__":
    main()
