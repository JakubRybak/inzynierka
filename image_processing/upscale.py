#!/usr/bin/env python3
"""CLI entry point: 4x super-resolution batch runner for fashion catalog images.

Usage:
    python upscale.py                     # run all methods on missing images
    python upscale.py dat2_gfpgan         # run only the top-performing hybrid method
    python upscale.py dat2 aurasr sd_x4   # run selected methods
    python upscale.py --list              # list available upscaling methods
    python upscale.py --force             # recompute already existing outputs
    python upscale.py --report            # regenerate HTML report after upscaling
"""

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from superres.paths import list_sample_images
from superres.report import build_report
from superres.upscaling import METHOD_IDS, create_upscaler, run_upscaler
from superres.upscaling.device import get_device


def main():
    parser = argparse.ArgumentParser(description="Run 4x super-resolution on fashion product photos.")
    parser.add_argument(
        "methods",
        nargs="*",
        metavar="METHOD",
        help=f"Methods to run ({', '.join(METHOD_IDS)}). Default: all methods.",
    )
    parser.add_argument("--list", action="store_true", help="List all available method IDs and exit.")
    parser.add_argument("--force", action="store_true", help="Re-upscale images even if output exists.")
    parser.add_argument("--report", action="store_true", help="Regenerate HTML comparison report after running.")
    args = parser.parse_args()

    if args.list:
        print("Available upscaling methods:")
        for mid in METHOD_IDS:
            u = create_upscaler(mid)
            print(f"  • {mid:15s} – {u.name}")
        return

    chosen_ids = args.methods if args.methods else METHOD_IDS
    for mid in chosen_ids:
        if mid not in METHOD_IDS:
            sys.exit(f"Error: Unknown method '{mid}'. Valid choices: {', '.join(METHOD_IDS)}")

    images = list_sample_images()
    if not images:
        sys.exit(f"Error: No sample images found in data/sample_images/")

    device = get_device()
    print("==================================================")
    print(f"🚀 Super-Resolution Runner")
    print(f"Device: {device}")
    print(f"Input images: {len(images)}")
    print(f"Methods: {', '.join(chosen_ids)}")
    print("==================================================")

    total_start = time.perf_counter()
    stats_list = []

    for mid in chosen_ids:
        upscaler = create_upscaler(mid)
        print(f"\n▶ [{mid}] {upscaler.name}")

        t0 = time.perf_counter()
        upscaler.load(device)
        load_time = time.perf_counter() - t0
        if load_time > 0.05:
            print(f"  Model loaded in {load_time:.2f}s")

        stats = run_upscaler(upscaler, images, force=args.force)
        stats_list.append(stats)
        print(stats.summary())

    total_elapsed = time.perf_counter() - total_start
    print(f"\n✓ Completed in {total_elapsed:.1f}s")

    if args.report:
        print("\nRegenerating HTML comparison report...")
        out_file = build_report()
        print(f"✓ Report updated: {out_file.resolve()}")


if __name__ == "__main__":
    main()
