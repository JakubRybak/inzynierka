# Keyword extraction

Supported categories: T-shirts, Polos, Tank tops & Camisoles, Bodysuits, Dresses and
Skirts. Extraction processes **all products** from these categories, separately for
train and validation. It uses YAML and Python, without reading Markdown or calling LLMs.

## Run

From the repository root:

```sh
.venv/bin/python -m pip install -r extraction/requirements.txt
.venv/bin/python extraction/scripts/run_extraction.py
```

To regenerate existing outputs:

```sh
.venv/bin/python extraction/scripts/run_extraction.py --overwrite
```

Optional arguments: --config, --dataset, --output. Defaults are config/ inside extraction/, data/processed/fashiongen/ at the repository root, and results/ inside
this experiment. Source CSVs and images are never modified. Unsupported categories
are skipped and counted in console output, not marked as excluded products.

## Files

- config/common.yaml: shared rules for gender, colors and main_composition, plus
  the list of allowed pattern values for later LLM extraction.
- config/categories/: six category configurations.
- scripts/engine.py: keyword matching, parsing and assignment strategies.
- scripts/run_extraction.py: complete train/validation processing and output validation.
- tests/test_extraction.py: behavior and persistence tests.

Only four files are generated:

```text
results/
  products_train.parquet
  products_train.jsonl
  products_validation.parquet
  products_validation.jsonl
```

Parquet and JSONL contain equivalent logical records. There are no sample,
inspection or summary files. Processing statistics are printed to the terminal.
Both splits are computed and validated in temporary storage before replacing the
four output files. Existing outputs require --overwrite.

## Data format

Columns: product_id, brand, section, category, features, feature_metadata, status
and exclusion_reasons. `brand` is copied from the source products CSV. An empty or
whitespace-only brand excludes the product while retaining it in the output, with
`{'feature': 'brand', 'reason': 'empty'}` in `exclusion_reasons`. In Parquet, the
three nested columns are JSON strings; JSONL contains their decoded objects.
Other original metadata and images are joined by product_id.

features contains assigned values only. feature_metadata includes the status,
source, strategy and evidence for every required feature. Product statuses are
pending, ready and excluded. Excluded products retain all successfully assigned
values and explicit reasons; no selected product is physically dropped.

## Rules and verification

YAML specifies columns, keywords, conflicts, exclusion policies and dependencies.
use references a common feature; exclude_phrases prevents T-shirt Dress from also
matching Shirt Dress. derive handles strap_width = Not Applicable. Gender and
main_composition failures exclude the product. Dresses and Skirts length comes
only from original_category; an unmapped value also excludes the product.

Colors use only name and mask that product's brand. Pattern uses the llm strategy:
it always remains undefined, without keyword matching or evidence, for later LLM
extraction. This script does not call a model. Other unresolved features also
remain undefined for later LLM extraction. Keyword-assigned features are retained.
T-shirts, Polos and Bodysuits support Sleeveless, Short Sleeve, Three-Quarter Sleeve
and Long Sleeve.

```sh
.venv/bin/python -m unittest discover -s extraction/tests -v
```

Output validation checks IDs, split separation, feature values, color constraints,
composition totals, dependencies, metadata and exact Parquet read-back. These
checks confirm implementation consistency, not independently measured accuracy.
