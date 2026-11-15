"""Resolve the enhanced photos selected by the dataset."""

from pathlib import Path

from ..enhancement.catalog import MAIN_POSE, read_product_ids


def select_photos(dataset: Path, images: Path | None, *, main_only: bool) -> list[Path]:
    if dataset.is_dir():
        dataset = dataset / "selection.csv"
    root = images if images is not None else dataset.parent / "images_enhanced"
    if not root.is_dir():
        raise FileNotFoundError(f"Image directory does not exist: {root}")

    selected = []
    missing = []
    for product in read_product_ids(dataset):
        if product in {".", ".."} or Path(product).name != product or "\\" in product:
            raise ValueError(f"Invalid product ID: {product!r}")
        directory = root / product
        if main_only:
            candidates = [directory / f"{product}_{MAIN_POSE}.webp"]
        else:
            candidates = sorted(directory.glob("*.webp"))
        photos = [path for path in candidates if path.is_file()]
        if photos:
            selected.extend(photos)
        else:
            missing.append(product)

    if missing:
        raise FileNotFoundError(
            f"No matching enhanced photos for {len(missing)} products: {', '.join(missing[:10])}"
        )
    return selected
