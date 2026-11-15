# FashionGen foreground masks

Run from the repository root.

```sh
python -m pip install -r image_processing/background/requirements.txt
python -m image_processing.background data/processed/fashiongen/pilot_9922 output/masks \
  --weights /path/to/BiRefNet_lite-matting --device auto
```

A dataset directory must contain `selection.csv` and `images_enhanced/`.
The input can also be a CSV, Parquet or JSONL file with a `product_id` column.
Use `--images` if the enhanced WebP files are stored elsewhere.
Each image must be in a subdirectory named after its product ID. By default
all available WebP photos are processed. Use `--photos main` for the
`<product_id>_id_gridfs_1.webp` pose only.

The output contains `<product_id>/<image_stem>.png` in the input resolution.
White retains the foreground and black denotes background. Intermediate
values represent soft edges. Valid masks are skipped on reruns. Use
`--force` after changing the input images or checkpoint.

`--weights` points to a trusted local snapshot of
[BiRefNet Lite Matting](https://huggingface.co/ZhengPeng7/BiRefNet_lite-matting/tree/99c33412e3f58e1f33187abdc8c435c645243690)
including its Python architecture files, configuration and weights.
