#!/usr/bin/env python3
"""CLI entry point: builds the interactive HTML comparison report.

Usage:
    python generate_report.py
    python generate_report.py --output custom_report.html
"""

import argparse
import sys
from pathlib import Path

# Add image_processing to sys.path so superres package can be imported directly
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from superres.paths import REPORT_PATH
from superres.report import build_report


def main():
    parser = argparse.ArgumentParser(description="Generate super-resolution comparison report.")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=REPORT_PATH,
        help=f"Target HTML file path (default: {REPORT_PATH.relative_to(HERE)})"
    )
    args = parser.parse_args()

    out_file = build_report(args.output)
    print(f"✓ Report generated: {out_file.resolve()}")


if __name__ == "__main__":
    main()
