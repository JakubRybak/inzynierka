"""
Checks example_queries.yaml against the index: parser + filtering, no ranking.

    python poc/search_ui/check_examples.py               # mock parser, no API calls
    python poc/search_ui/check_examples.py --parser llm  # LLM parser (paid calls)
"""
import argparse
import sys

import yaml

import common
import conditions
import parser_adapter
from server import EXAMPLES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parser", default="mock")
    args = ap.parse_args()

    products, _ = common.load_index()
    products = [conditions.prepare_product(p) for p in products]
    vocabulary = conditions.Vocabulary(products)
    parser = parser_adapter.load_parser(args.parser, vocabulary)
    print(f"Index: {len(products)} products · parser: {parser.name}")
    failures = 0
    for group, queries in yaml.safe_load(EXAMPLES.read_text(encoding="utf-8")).items():
        print(f"\n{group}")
        for x in queries:
            q, empty = (x, False) if isinstance(x, str) else (x["q"], bool(x.get("empty")))
            raw = parser(q)
            problems = []
            if args.parser == "mock" and raw.get("_mock") != "parser_mock.yaml":
                problems.append("missing from parser_mock.yaml")
            try:
                tree, warnings = conditions.prune(parser_adapter.to_condition(raw), vocabulary)
                found = len(conditions.filter_products(tree, products)["candidates"])
            except parser_adapter.OutOfCatalog:
                tree, warnings, found = None, [], None
            problems += warnings
            if found is None:
                problems.append("parser returned no category")
            elif empty and found:
                problems.append(f"expected no results, got {found}")
            elif not empty and not found:
                problems.append("expected results, got none")
            failures += bool(problems)
            print(f"  {'✗' if problems else '✓'} {found if found is not None else '-':>4}  {q}"
                  + (f"\n        {conditions.describe(tree)}" if args.parser != "mock" and tree else "")
                  + "".join(f"\n        ! {p}" for p in problems))
    print(f"\n{'OK' if not failures else f'Problems: {failures}'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
