"""Write or load a reproducible, category-stratified sample of the query benchmark."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


QUERIES = Path(__file__).resolve().parent / "queries"
QUERY_FOLDERS = (
    "dress",
    "jackets-and-coats",
    "no_category",
    "pants",
    "shirts-and-blouses",
    "shorts",
    "skirts",
    "sweaters",
    "tops",
)
FIELDS = ("query", "expected_output", "language", "source")
NO_CATEGORY = "no_category"


def _normalize_dataset_row(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a row from CSV, JSON, or JSONL into standard benchmark format."""
    if "query" not in raw:
        raise ValueError(f"Dataset row is missing 'query' field: {raw!r}")
    if "expected" in raw and isinstance(raw["expected"], dict):
        expected = raw["expected"]
        expected_output_str = json.dumps(expected, ensure_ascii=False)
    elif "expected_output" in raw:
        val = raw["expected_output"]
        if isinstance(val, dict):
            expected = val
            expected_output_str = json.dumps(expected, ensure_ascii=False)
        else:
            expected = json.loads(val)
            expected_output_str = val
    else:
        raise ValueError(f"Dataset row must contain 'expected_output' or 'expected': {raw!r}")

    return {
        "query": str(raw["query"]),
        "expected_output": expected_output_str,
        "expected": expected,
        "language": str(raw.get("language", "en")),
        "source": str(raw.get("source", "custom")),
    }


def load_queries(dataset_dir: Path = QUERIES) -> Dict[str, List[Dict[str, str]]]:
    groups: Dict[str, List[Dict[str, str]]] = {}
    standard_paths = [
        path
        for folder in QUERY_FOLDERS
        if (dataset_dir / folder).is_dir()
        for path in (dataset_dir / folder).glob("*_queries.csv")
    ]
    paths = sorted(standard_paths) if standard_paths else sorted(dataset_dir.rglob("*.csv"))
    for path in paths:
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                category = json.loads(row["expected_output"])["category"]
                group = NO_CATEGORY if category is None else category
                groups.setdefault(group, []).append(row)
    return groups


def load_dataset_rows(
    dataset_path: Optional[Path] = None,
    size: Optional[int] = 30,
    seed: int = 42,
    categories: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """Load benchmark queries from a directory of CSVs or a single .csv/.json/.jsonl file.

    If `size` is None, returns all matching rows without sampling.
    If `size` is an int, returns a category-stratified sample of `size` rows using `seed`.
    """
    target = (dataset_path or QUERIES).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {target}")

    rows: List[Dict[str, Any]] = []
    if target.is_dir():
        groups_raw = load_queries(target)
        for cat_rows in groups_raw.values():
            for r in cat_rows:
                rows.append(_normalize_dataset_row(r))
    elif target.suffix.lower() == ".csv":
        with target.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows.append(_normalize_dataset_row(r))
    elif target.suffix.lower() == ".jsonl":
        with target.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(_normalize_dataset_row(json.loads(line)))
    elif target.suffix.lower() == ".json":
        payload = json.loads(target.read_text(encoding="utf-8"))
        items = payload["queries"] if isinstance(payload, dict) and "queries" in payload else payload
        if not isinstance(items, list):
            raise ValueError(f"Unsupported JSON dataset format in {target}")
        for r in items:
            rows.append(_normalize_dataset_row(r))
    else:
        raise ValueError(f"Unsupported dataset file extension: {target.suffix} (expected directory, .csv, .jsonl, or .json)")

    if categories:
        allowed = set(categories)
        rows = [
            r for r in rows
            if (NO_CATEGORY if r["expected"]["category"] is None else r["expected"]["category"]) in allowed
        ]

    if not rows:
        raise ValueError(f"No benchmark queries found in {target}")

    if size is None or size == len(rows):
        return rows
    if size > len(rows):
        raise ValueError(f"Requested sample size {size}, but dataset {target} only contains {len(rows)} queries")

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        cat = r["expected"]["category"]
        group = NO_CATEGORY if cat is None else cat
        groups.setdefault(group, []).append(r)

    return sample_queries(groups, size, seed)


def parse_size(value: str) -> Optional[int]:
    if value == "all":
        return None
    try:
        size = int(value)
        if size > 0:
            return size
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("size must be a positive integer or 'all'")


def sample_queries(groups: Dict[str, List[Dict[str, Any]]], size: int, seed: int) -> List[Dict[str, Any]]:
    total = sum(map(len, groups.values()))
    if size == total:
        return [row for rows in groups.values() for row in rows]

    rng = random.Random(seed)
    categories = sorted(groups)
    rng.shuffle(categories)
    if NO_CATEGORY in groups:
        categories.remove(NO_CATEGORY)
        categories.insert(0, NO_CATEGORY)

    selected = categories[:size]
    quotas = dict.fromkeys(selected, 1)
    remaining = size - len(selected)
    if remaining:
        # Allocate the remaining slots proportionally to the unused rows.
        capacity = total - len(selected)
        shares = {
            category: divmod(remaining * (len(groups[category]) - 1), capacity)
            for category in selected
        }
        for category, (whole, _) in shares.items():
            quotas[category] += whole
        leftover = size - sum(quotas.values())
        by_remainder = sorted(selected, key=lambda category: shares[category][1], reverse=True)
        for category in by_remainder[:leftover]:
            quotas[category] += 1

    rows = [
        row
        for category, quota in quotas.items()
        for row in rng.sample(groups[category], quota)
    ]
    rng.shuffle(rows)
    return rows


def main() -> None:
    groups = load_queries()
    parser = argparse.ArgumentParser(
        description="Write a stratified query benchmark sample as CSV.",
        epilog="Save generated samples outside query_parsing/queries/.",
    )
    parser.add_argument("--size", type=parse_size, required=True, help="Number of queries or 'all'")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(groups),
        help="Restrict to a category. Repeat to select multiple categories. Defaults to all.",
    )
    args = parser.parse_args()

    if args.category:
        groups = {category: rows for category, rows in groups.items() if category in args.category}
    total = sum(map(len, groups.values()))
    if not total:
        parser.error("no benchmark queries found")
    size = total if args.size is None else args.size
    if size > total:
        parser.error(f"requested {size} queries, but only {total} are available in the selection")

    writer = csv.DictWriter(sys.stdout, FIELDS, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(sample_queries(groups, size, args.seed))


if __name__ == "__main__":
    main()
