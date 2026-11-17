"""Generate BiRefNet Lite Matting masks for a FashionGen dataset."""

import argparse
from pathlib import Path
from time import perf_counter

from PIL import Image

from .catalog import select_photos
from .storage import save_mask, valid_mask


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Pilot directory or CSV, Parquet or JSONL with product_id")
    parser.add_argument("output", type=Path, help="Destination for grayscale PNG masks")
    parser.add_argument("--images", type=Path, help="Enhanced image root (default: images_enhanced next to the selection)")
    parser.add_argument("--weights", type=Path, required=True, help="Trusted local BiRefNet Lite Matting checkpoint directory")
    parser.add_argument("--photos", choices=("main", "all"), default="all")
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    parser.add_argument("--force", action="store_true", help="Recompute existing masks")
    args = parser.parse_args()

    try:
        photos = select_photos(args.dataset, args.images, main_only=args.photos == "main")
    except (KeyError, OSError, ValueError) as error:
        parser.error(str(error))

    model = None
    saved = 0
    skipped = 0
    start = perf_counter()
    for index, photo in enumerate(photos, 1):
        destination = args.output / photo.parent.name / f"{photo.stem}.png"
        try:
            with Image.open(photo) as source:
                if not args.force and valid_mask(destination, source.size):
                    skipped += 1
                    continue
                image = source.convert("RGB")
            if model is None:
                from .model import load_model, predict_mask

                model = load_model(args.weights, args.device)
            mask = predict_mask(model, image)
            save_mask(mask, destination)
        except (OSError, RuntimeError, ValueError) as error:
            parser.exit(1, f"Failed on {photo}: {error}\n")
        saved += 1
        print(f"[{index}/{len(photos)}] {destination}", flush=True)

    print(f"Saved {saved} masks, skipped {skipped} in {perf_counter() - start:.1f} s.")


if __name__ == "__main__":
    main()
