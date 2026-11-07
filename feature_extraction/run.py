"""Run keyword extraction and prepare or execute missing-feature inference."""
import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature_extraction.pipeline import run
from feature_extraction.settings import load_settings
from feature_extraction.schema import load_schemas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--run-name', required=True)
    parser.add_argument('--stage', choices=['keywords', 'llm', 'all'], default='all')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--mode', choices=['online', 'batch'], default='online')
    parser.add_argument('--batch-size', type=int, help='Maximum requests per batch; omit for one job')
    parser.add_argument('--all-categories', action='store_true',
                        help='Use all supported categories; requires --all-products')
    parser.add_argument('--all-products', action='store_true', help='Process all configured categories instead of the saved sample')
    parser.add_argument('--execute', action='store_true', help='Authorize paid inference; default only prepares prompts')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    if args.batch_size is not None and (args.mode != 'batch' or args.batch_size < 1):
        parser.error('--batch-size must be positive and requires --mode batch')
    if args.mode == 'batch' and args.stage == 'keywords':
        parser.error('--mode batch requires the LLM stage')
    if args.all_categories and not args.all_products:
        parser.error('--all-categories requires --all-products')
    settings = load_settings(args.config)
    if args.all_products:
        settings['selection'] = None
    if args.all_categories:
        schemas, _ = load_schemas()
        settings['categories'] = sorted({category for _, category in schemas})
    summary = run(settings, args.run_name, args.stage, args.execute, args.limit,
                  mode=args.mode, batch_size=args.batch_size)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
