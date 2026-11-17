"""Batch enhancement of FashionGen photos selected by product ID."""

import argparse
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from PIL import Image

from .catalog import CATALOG, read_product_ids, select_images
from .weights import DEFAULT_WEIGHTS_DIR

WEBP_QUALITY = 90


def is_valid_output(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            if image.format != "WEBP":
                return False
            image.load()
        return True
    except OSError:
        return False


def save_image(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            image.save(handle, format="WEBP", quality=WEBP_QUALITY)
            handle.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV, Parquet or JSONL with a product_id column")
    parser.add_argument("output", type=Path, help="Directory for the enhanced WebP images")
    parser.add_argument("--photos", choices=("main", "all"), default="main", help="Photo selection (default: main)")
    parser.add_argument("--weights-dir", type=Path, default=DEFAULT_WEIGHTS_DIR, help="Directory with cached model weights")
    parser.add_argument("--device", choices=("auto", "mps", "cuda", "cpu"), default="auto")
    parser.add_argument("--force", action="store_true", help="Reprocess existing WebP images")
    args = parser.parse_args()

    try:
        product_ids = read_product_ids(args.input)
        paths = select_images(product_ids, CATALOG, all_images=args.photos == "all")
    except (KeyError, OSError, ValueError) as exc:
        parser.error(str(exc))

    pending = [
        (CATALOG / path, args.output / path.with_suffix(".webp"))
        for path in paths
        if args.force or not is_valid_output(args.output / path.with_suffix(".webp"))
    ]
    print(f"{len(product_ids)} products, {len(paths)} photos, {len(paths) - len(pending)} already saved.", flush=True)
    if not pending:
        return

    import torch

    from .model import Dat2Gfpgan

    device = args.device
    if device == "auto":
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    start = perf_counter()
    model = Dat2Gfpgan(torch.device(device), args.weights_dir)
    for index, (source, destination) in enumerate(pending, 1):
        with Image.open(source) as image:
            result = model.upscale(image.convert("RGB"))
        save_image(result, destination)
        print(f"[{index}/{len(pending)}] {destination}", flush=True)
    print(f"Saved {len(pending)} images on {device} in {perf_counter() - start:.1f} s.")


if __name__ == "__main__":
    main()
