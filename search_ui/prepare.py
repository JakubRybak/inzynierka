"""
Builds the search index: extracted features + product metadata + images -> data/index.parquet.
Product embeddings are the precomputed description and main image embeddings of the pilot. When
ranking_data/concept_scores.parquet exists, its concept scores become concept__<id> columns and the concept names with
their embeddings go to data/concepts.parquet (names from ranking_data/concept_names.parquet; a new name costs one
embedding call). The phrases of ranking_data/phrase_bank.jsonl are embedded into data/bank_embeddings.npz for the bank
ranking (one call per phrase not embedded there yet; under $0.01 for the whole bank), and the colour names of
ranking_data/color_names.parquet into data/color_embeddings.npz, and the detail names of
ranking_data/product_details.parquet into data/detail_embeddings.npz. The extracted features of
every product are written as a short text (feature_text.py) and embedded into data/feature_embeddings.npz (one call
per product whose text is new; about $0.07 for the pilot).

    python search_ui/prepare.py
    python search_ui/prepare.py --features data/processed/fashiongen/pilot_9922/products.parquet --status ready
    python search_ui/prepare.py --no-concepts
"""
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))
import bank  # noqa: E402
import colours  # noqa: E402
import common  # noqa: E402
import concepts  # noqa: E402
import details  # noqa: E402
import feature_text  # noqa: E402


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
    ap.add_argument("--features", nargs="+", default=[common.FEATURES], type=Path, help=".csv, .parquet or .jsonl")
    ap.add_argument("--status", nargs="+", default=["ready"], help="keep only these statuses (default: ready)")
    ap.add_argument("--limit", type=int, help="only N products, split evenly across categories")
    ap.add_argument("--dataset", type=Path, default=common.DATASET)
    ap.add_argument("--embeddings", type=Path, default=common.EMBEDDINGS)
    ap.add_argument("--output", type=Path, default=common.DATA)
    ap.add_argument("--concept-scores", type=Path, default=concepts.SCORES)
    ap.add_argument("--no-concepts", action="store_true", help="build the index without concept scores")
    ap.add_argument("--no-bank", action="store_true", help="do not embed the phrase bank")
    ap.add_argument("--no-feature-embeddings", action="store_true", help="do not embed the feature texts")
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

    concept_info = None
    if not args.no_concepts and args.concept_scores.exists():
        concept_list = concepts.load_list()
        names = pd.read_parquet(concepts.NAMES) if concepts.NAMES.exists() else None
        embedder = common.QueryEmbedder(manifest["model"], manifest["output_dimensionality"])
        d, rows, scored, partial = concepts.build(d, concept_list, pd.read_parquet(args.concept_scores), names,
                                                  lambda name: embedder(common.query_text(name)))
        rows[["id", "name", "embedding"]].to_parquet(concepts.NAMES, index=False)
        categories = sorted(c for c, ids in scored.items() if len(ids) == len(concept_list))
        concept_info = dict(yaml=str(concepts.CONCEPTS_YAML.resolve()), yaml_sha256=concepts.file_hash(concepts.CONCEPTS_YAML),
                            scores=str(args.concept_scores.resolve()),
                            scores_sha256=concepts.file_hash(args.concept_scores), count=len(rows),
                            categories=categories, scored=scored, partial=partial)
        print(f"Concepts: {len(rows)}, all scored in {', '.join(categories) or 'no category'}"
              + "".join(f"; {c}: {a} of {b} concepts scored" for c, (a, b) in partial.items()))

    args.output.mkdir(parents=True, exist_ok=True)
    if concept_info:
        rows.to_parquet(args.output / concepts.FILE, index=False)
    elif (args.output / concepts.FILE).exists():
        (args.output / concepts.FILE).unlink()
    d.assign(features=d["features"].map(lambda f: json.dumps(f, ensure_ascii=False, sort_keys=True)),
             images=d["images"].map(json.dumps)).to_parquet(args.output / common.INDEX, index=False)
    meta = dict(created=datetime.now().isoformat(timespec="seconds"), features=[str(p.resolve()) for p in args.features],
                dataset=str(dataset), embeddings=str(args.embeddings.resolve()), model=manifest["model"],
                dim=manifest["output_dimensionality"], products=len(d), limit=args.limit,
                categories=d["category"].value_counts().to_dict(), concepts=concept_info)
    (args.output / common.META).write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Saved {args.output / common.INDEX}")
    if not args.no_bank:
        embedder = common.QueryEmbedder(manifest["model"], manifest["output_dimensionality"])
        vectors, new = bank.embed_bank(bank.load_rows(), embedder, args.output)
        print(f"Phrase bank: {len(vectors)} phrases embedded ({new} new calls) -> {args.output / bank.VECTORS}")
        if colours.NAMES.exists():
            names = list(pd.read_parquet(colours.NAMES)["name"])
            new = colours.embed_names(names, embedder, args.output)
            print(f"Colour names: {len(names)} embedded ({new} new calls) -> {args.output / colours.VECTORS}")
        if details.PRODUCTS.exists():
            names = details.names(pd.read_parquet(details.PRODUCTS))
            new = details.embed_names(names, embedder, args.output)
            print(f"Detail names: {len(names)} embedded ({new} new calls) -> {args.output / details.VECTORS}")
    if not args.no_feature_embeddings:
        embedder = common.QueryEmbedder(manifest["model"], manifest["output_dimensionality"])
        texts = [feature_text.feature_text(r) for r in d.to_dict("records")]
        new = common.embed_texts(list(d["product_id"]), texts, embedder, args.output / common.FEATURE_VECTORS)
        print(f"Feature texts: {len(texts)} embedded ({new} new calls) -> {args.output / common.FEATURE_VECTORS}")


if __name__ == "__main__":
    main()
