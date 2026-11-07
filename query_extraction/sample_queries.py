"""Write a reproducible, category-stratified sample of the query benchmark."""

import argparse
import csv
import json
import random
import sys
from pathlib import Path


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


def load_queries():
    groups = {}
    paths = sorted(path for folder in QUERY_FOLDERS for path in (QUERIES / folder).glob("*_queries.csv"))
    for path in paths:
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                category = json.loads(row["expected_output"])["category"]
                group = NO_CATEGORY if category is None else category
                groups.setdefault(group, []).append(row)
    return groups


def parse_size(value):
    if value == "all":
        return None
    try:
        size = int(value)
        if size > 0:
            return size
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("size must be a positive integer or 'all'")


def sample_queries(groups, size, seed):
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


def main():
    groups = load_queries()
    parser = argparse.ArgumentParser(
        description="Write a stratified query benchmark sample as CSV.",
        epilog="Save generated samples outside query_extraction/queries/.",
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

    writer = csv.DictWriter(sys.stdout, FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sample_queries(groups, size, args.seed))


if __name__ == "__main__":
    main()
