# Fashion-Gen dataset preparation

`build_fashiongen.py` reads the original HDF5 datasets, selects clothing products,
assigns project categories using `config/fashiongen_taxonomy.yaml`, and exports
product/image CSV manifests and lossless PNG images. Train and validation remain
separate. Product descriptions and other metadata come from the first row of each
product; each source image is linked by product ID and pose.

The taxonomy defines source category mappings, conditional name/description rules
and source exclusions. Product feature extraction is handled by `feature_extraction/`.

## Run

Dependencies: `h5py`, `numpy`, and `PyYAML`.
From the repository root:

```sh
source .venv/bin/activate
python dataset_preparation/build_fashiongen.py \
  --train data/raw/fashiongen_256_256_train.h5 \
  --validation data/raw/fashiongen_256_256_validation.h5
```

The default taxonomy is resolved next to the script. The default output is
`data/processed/fashiongen/` relative to the repository root, regardless of the
shell's working directory. Explicit command-line paths are relative to the shell's
working directory unless absolute paths are supplied.

Use `--taxonomy PATH` and `--output PATH` to override the defaults. Provide either
or both input splits. `--metadata-only` skips PNG export and leaves image paths empty.

## Output

```text
data/processed/fashiongen/
├── products_train.csv
├── products_validation.csv
├── images_train.csv
├── images_validation.csv
└── images/
    ├── train/<product_id>/
    └── validation/<product_id>/
```

Each product CSV contains one row per product. `section` and `category` use the
project taxonomy; `original_section` and `original_category` retain the source
category and subcategory. Image manifests connect PNG files to their product ID,
pose and image ID. Source HDF5 files stay in `data/raw/`.
