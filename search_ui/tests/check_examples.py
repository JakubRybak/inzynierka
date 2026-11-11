"""
Checks static/example_queries.yaml against the index: parser + filtering, no ranking.

    python search_ui/tests/check_examples.py                                  # mock parser, no API calls
    python search_ui/tests/check_examples.py --parser benchmark_parser:parse  # the benchmark dev examples

Groups that are not an indexed category, and categories the parser does not support, expect no category.
"""
import argparse
from pathlib import Path
import sys

import yaml

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "core")]
import common  # noqa: E402
import conditions  # noqa: E402
import parser_adapter  # noqa: E402
from server import EXAMPLES, pick_examples  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parser", default="mock")
    args = ap.parse_args()

    products, _ = common.load_index()
    products = [conditions.prepare_product(p) for p in products]
    vocabulary = conditions.Vocabulary(products)
    parser = parser_adapter.load_parser(args.parser, vocabulary)
    indexed = {p["category"] for p in products}
    print(f"Index: {len(products)} products · parser: {parser.name}")
    failures = 0
    shown = pick_examples(parser.examples, parser, products, vocabulary) if parser.examples else \
        yaml.safe_load(EXAMPLES.read_text(encoding="utf-8"))
    for group, queries in shown.items():
        print(f"\n{group}")
        for x in queries:
            q, empty = (x, False) if isinstance(x, str) else (x["q"], bool(x.get("empty")))
            raw = parser(q)
            problems = []
            try:
                tree, warnings = conditions.canonicalize(parser_adapter.to_condition(raw), vocabulary)
                found = len(conditions.filter_products(tree, products)["candidates"])
            except parser_adapter.OutOfCatalog:
                tree, warnings, found = None, [], None
            problems += warnings
            if found is None:
                # a group named after an indexed category expects one, unless the parser does not support it
                if group in indexed and group in (parser.categories or [group]):
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
