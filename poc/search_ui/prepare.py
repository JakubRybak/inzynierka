"""
Builds the search index: extracted features + product metadata + images -> data/index.parquet.
Product embeddings are the precomputed ones in poc/feature_extraction/embeddings.

    python poc/search_ui/prepare.py --features poc/feature_extraction/results/products.parquet --status ready
"""
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

import common


def build_index(features, dataset, limit=None, statuses=None):
    f = features[features["status"].isin(statuses) if statuses else features["status"] != "excluded"].copy()
    meta = pd.concat([pd.read_csv(dataset / f"products_{s}.csv", dtype={"product_id": str}).assign(split=s)
                      for s in ("train", "validation")], ignore_index=True)
    images = pd.concat([pd.read_csv(dataset / f"images_{s}.csv", dtype={"product_id": str})
                        for s in ("train", "validation")], ignore_index=True)
    image_paths = images.groupby("product_id", sort=False)["image_path"].agg(list)
    d = f[["product_id", "section", "category", "status", "features"]].merge(
        meta.drop(columns=["section", "category"]), on="product_id", how="left", validate="one_to_one")
    no_meta = d["name"].isna()
    if no_meta.any():
        raise ValueError(f"{no_meta.sum()} products have no metadata, e.g. {d.loc[no_meta, 'product_id'].head(3).tolist()}")
    d["images"] = d["product_id"].map(image_paths).map(lambda z: z if isinstance(z, list) else [])
    if limit:
        per_category = math.ceil(limit / d["category"].nunique())
        d = d.groupby("category", group_keys=False).head(per_category).head(limit)
    return d.sort_values(["category", "product_id"]).reset_index(drop=True), len(features) - len(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--features", nargs="+", required=True, type=Path, help=".csv, .parquet or .jsonl")
    ap.add_argument("--status", nargs="+", help="keep only these statuses, e.g. ready (default: all but excluded)")
    ap.add_argument("--limit", type=int, help="only N products, split evenly across categories")
    ap.add_argument("--dataset", type=Path, default=common.DATASET)
    ap.add_argument("--embeddings", type=Path, default=common.EMBEDDINGS)
    ap.add_argument("--output", type=Path, default=common.DATA)
    args = ap.parse_args()

    dataset = args.dataset.resolve()
    features = common.load_features(args.features)
    d, skipped = build_index(features, dataset, args.limit, args.status)
    print(f"Features file: {len(features)} products, skipped by status: {skipped}, indexed: {len(d)}")
    print("  " + ", ".join(f"{k} {v}" for k, v in d["category"].value_counts().items()))

    manifest, text, image = common.load_embeddings(args.embeddings)
    missing = [r.product_id for r in d.itertuples() if r.product_id not in text or (r.images and r.product_id not in image)]
    if missing:
        sys.exit(f"No embeddings for {len(missing)} indexed products, e.g. {missing[:3]}")
    print(f"Embeddings: {manifest['model']}, {manifest['output_dimensionality']} dims, all indexed products covered")

    args.output.mkdir(parents=True, exist_ok=True)
    d.assign(features=d["features"].map(lambda f: json.dumps(f, ensure_ascii=False, sort_keys=True)),
             images=d["images"].map(json.dumps)).to_parquet(args.output / common.INDEX, index=False)
    meta = dict(created=datetime.now().isoformat(timespec="seconds"), features=[str(p.resolve()) for p in args.features],
                dataset=str(dataset), embeddings=str(args.embeddings.resolve()), model=manifest["model"],
                dim=manifest["output_dimensionality"], products=len(d), limit=args.limit,
                categories=d["category"].value_counts().to_dict())
    (args.output / common.META).write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Saved {args.output / common.INDEX}")


if __name__ == "__main__":
    main()
