"""Run the query parser from the command line."""

import argparse
import json

from . import parse_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract filters and residual concepts from a shopping query.")
    parser.add_argument("query", help="Shopping query")
    parser.add_argument("--meta", action="store_true", help="Include latency and estimated cost")
    args = parser.parse_args()
    print(json.dumps(parse_query(args.query, include_meta=args.meta), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
