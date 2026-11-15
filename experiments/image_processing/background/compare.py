"""Compare background tinting on the enhanced pilot photos listed in sample.csv.

Pass the pilot image directory, the BiRefNet Lite Matting checkpoint
and U²-Net Lite ONNX weights (u2netp.onnx). The product IDs come from
sample.csv. By default, the script writes report.html and timings.json
next to this script.
"""

import argparse
import csv
import json
from functools import partial
from pathlib import Path
from statistics import mean, median
from time import perf_counter

from PIL import Image, ImageChops

import birefnet
import u2net_lite
from grabcut import grabcut_mask
from report import render_card, write_report

TINT = "#e2e4e8"
DIRECTORY = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-images", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--birefnet-weights", type=Path, required=True)
    parser.add_argument("--birefnet-device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--output", type=Path, default=DIRECTORY / "report.html")
    parser.add_argument("--timings", type=Path, default=DIRECTORY / "timings.json")
    args = parser.parse_args()
    if args.output.resolve() == args.timings.resolve():
        parser.error("--output and --timings must use different paths")
    methods = (
        ("grabcut", "GrabCut", grabcut_mask),
        ("u2net_lite", "U²-Net Lite", partial(u2net_lite.predict_mask, u2net_lite.load_model(args.weights))),
        ("birefnet_lite_matting", "BiRefNet Lite Matting",
         partial(birefnet.predict_mask, birefnet.load_model(args.birefnet_weights, args.birefnet_device))),
    )
    rows = []
    timings = []
    with (DIRECTORY / "sample.csv").open(encoding="utf-8", newline="") as file:
        product_ids = [row["product_id"] for row in csv.DictReader(file)]
    if not product_ids:
        parser.error("sample.csv must contain at least one product ID")
    for product in product_ids:
        path = args.pilot_images / product / f"{product}_id_gridfs_1.webp"
        with Image.open(path) as source:
            image = source.convert("RGB")

        tinted = ImageChops.multiply(image, Image.new("RGB", image.size, TINT))
        record = {"product_id": product}
        variants = []
        for key, label, predict in methods:
            start = perf_counter()
            mask = predict(image)
            record[key] = (perf_counter() - start) * 1000
            variants.append((label, mask, Image.composite(image, tinted, mask)))
        timings.append(record)
        rows.append(render_card(product, image, variants))

    write_report(args.output, rows)

    summary = {}
    for method, _, _ in methods:
        durations = [record[method] for record in timings]
        summary[method] = {
            "mean": mean(durations),
            "median": median(durations),
            "total": sum(durations),
        }
    payload = {
        "unit": "ms",
        "scope": "Mask generation including preprocessing and resizing",
        "birefnet_device": args.birefnet_device,
        "sample_size": len(timings),
        "summary": summary,
        "per_product": timings,
    }
    args.timings.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
