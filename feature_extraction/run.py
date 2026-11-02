"""Run keyword extraction and prepare or execute missing-feature inference."""
import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature_extraction.pipeline import run
from feature_extraction.settings import load_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--run-name', required=True)
    parser.add_argument('--stage', choices=['keywords', 'llm', 'all'], default='all')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--all-products', action='store_true', help='Process all configured categories instead of the saved sample')
    parser.add_argument('--execute', action='store_true', help='Authorize paid inference; default only prepares prompts')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    settings = load_settings(args.config)
    if args.all_products:
        settings['selection'] = None
    summary = run(settings, args.run_name, args.stage, args.execute, args.limit)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
