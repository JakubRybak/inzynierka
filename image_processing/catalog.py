"""Read product selections and resolve photos using the FashionGen manifests."""

import csv
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "data" / "processed" / "fashiongen"
MAIN_POSE = "id_gridfs_1"


def read_product_ids(path: Path) -> list[str]:
    def ids(rows):
        for row in rows:
            if not isinstance(row, dict) or "product_id" not in row:
                raise ValueError("Input must contain a product_id column")
            yield row["product_id"]

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        from pyarrow import parquet

        with parquet.ParquetFile(path) as parquet_file:
            if "product_id" not in parquet_file.schema_arrow.names:
                raise ValueError("Input must contain a product_id column")
            values = [
                value
                for batch in parquet_file.iter_batches(columns=["product_id"])
                for value in batch.column(0).to_pylist()
            ]
    else:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            if suffix == ".csv":
                reader = csv.DictReader(handle)
                if "product_id" not in (reader.fieldnames or ()):
                    raise ValueError("Input must contain a product_id column")
                values = list(ids(reader))
            elif suffix == ".jsonl":
                values = list(ids(json.loads(line) for line in handle if line.strip()))
            else:
                raise ValueError("Input format must be CSV, Parquet or JSONL")

    if any(isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).strip()
           for value in values):
        raise ValueError("product_id must be a non-empty string or integer")
    if not values:
        raise ValueError("Input contains no product IDs")
    return list(dict.fromkeys(str(value).strip() for value in values))


def select_images(product_ids: list[str], catalog: Path, *, all_images: bool) -> list[Path]:
    selected: dict[str, dict[str, Path]] = {product_id: {} for product_id in product_ids}
    for split in ("train", "validation"):
        with (catalog / f"images_{split}.csv").open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                images = selected.get(row["product_id"])
                pose = row["pose"]
                if images is None or (not all_images and pose != MAIN_POSE):
                    continue
                relative = Path(row["image_path"])
                if not row["image_path"] or relative.is_absolute() or ".." in relative.parts:
                    raise ValueError(f"Invalid image path for product {row['product_id']}: {row['image_path']!r}")
                if images.setdefault(pose, relative) != relative:
                    raise ValueError(f"Ambiguous image for product {row['product_id']}, pose {pose}")

    missing = [product_id for product_id, images in selected.items() if not images]
    if missing:
        selection = "images" if all_images else "main images"
        raise ValueError(f"No {selection} for {len(missing)} products: {', '.join(missing[:10])}")
    paths = [images[pose] for images in selected.values() for pose in sorted(images)]
    missing_files = [path for path in paths if not (catalog / path).is_file()]
    if missing_files:
        raise FileNotFoundError(f"{len(missing_files)} source images missing, first: {catalog / missing_files[0]}")
    return paths
