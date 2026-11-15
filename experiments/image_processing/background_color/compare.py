"""Compare background shades on FashionGen pilot photos using existing masks."""

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median
from time import perf_counter

from PIL import Image

from composite import tint_background
from report import render_row, write_report

DIRECTORY = Path(__file__).resolve().parent
PILOT = DIRECTORY.parents[2] / "data/processed/fashiongen/pilot_9922"
SHADES = ("#F4F3F7", "#F2F2F2", "#E8E8E8", "#E2E4E8", "#D4D4D4")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, default=DIRECTORY / "sample.csv")
    parser.add_argument("--images", type=Path, default=PILOT / "images_enhanced")
    parser.add_argument("--masks", type=Path, default=PILOT / "image_masks")
    parser.add_argument("--output", type=Path, default=DIRECTORY / "report.html")
    parser.add_argument("--timings", type=Path, default=DIRECTORY / "timings.json")
    args = parser.parse_args()
    if args.output.resolve() == args.timings.resolve():
        parser.error("--output and --timings must use different paths")

    run_start = perf_counter()

    with args.sample.open(encoding="utf-8-sig", newline="") as file:
        product_ids = [row["product_id"] for row in csv.DictReader(file)]
    if not product_ids:
        parser.error("The sample must contain at least one product ID")

    rows = []
    records = []
    for product in product_ids:
        stem = f"{product}_id_gridfs_1"
        start = perf_counter()
        with Image.open(args.images / product / f"{stem}.webp") as source:
            image = source.convert("RGB")
        with Image.open(args.masks / product / f"{stem}.png") as source:
            if source.mode != "L" or source.size != image.size:
                raise ValueError(f"Mask for {product} must be grayscale and match the photo size")
            mask = source.copy()
        read_ms = (perf_counter() - start) * 1000

        variants = [("Oryginał", image)]
        tint_ms = {}
        for shade in SHADES:
            start = perf_counter()
            result = tint_background(image, mask, shade)
            tint_ms[shade] = (perf_counter() - start) * 1000
            variants.append((shade, result))

        start = perf_counter()
        rows.append(render_row(product, variants))
        records.append({
            "product_id": product,
            "read_ms": read_ms,
            "tint_ms": tint_ms,
            "render_ms": (perf_counter() - start) * 1000,
        })

    start = perf_counter()
    write_report(args.output, rows, 1 + len(SHADES))
    report_write_ms = (perf_counter() - start) * 1000
    elapsed_ms = (perf_counter() - run_start) * 1000

    summary = {}
    for shade in SHADES:
        durations = [record["tint_ms"][shade] for record in records]
        summary[shade] = {
            "mean_ms": mean(durations),
            "median_ms": median(durations),
            "total_ms": sum(durations),
        }

    payload = {
        "sample_size": len(records),
        "summary_by_shade": summary,
        "read_total_ms": sum(record["read_ms"] for record in records),
        "render_total_ms": sum(record["render_ms"] for record in records),
        "report_write_ms": report_write_ms,
        "elapsed_ms": elapsed_ms,
        "per_product": records,
    }
    args.timings.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
