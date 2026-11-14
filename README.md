# Fashion-Gen clothing search

The `extraction_clean` branch contains catalog preparation and product feature
extraction. The product taxonomy is defined in
[categories_and_features.md](docs/catalog/categories_and_features.md).

## Workflow

1. [Dataset preparation](dataset_preparation/README.md) selects clothing products
   from Fashion-Gen HDF5, assigns project categories, and exports images and CSV
   manifests while preserving train and validation as separate source files.
   It also exports query candidates from Amazon ESCI.
2. [Feature extraction](feature_extraction/README.md) assigns attributes using
   keyword rules and completes missing values with Gemini structured output.

```text
dataset_preparation/      Fashion-Gen catalog and Amazon ESCI query preparation
feature_extraction/       Keyword rules, LLM prompts, embeddings and extraction
data/raw/fashiongen/       Original Fashion-Gen HDF5 files
data/raw/amazon_esci/      Original Amazon ESCI query Parquet
data/processed/fashiongen/ Generated catalog CSVs and images
data/processed/amazon_esci/ Exported Amazon ESCI query candidates
```

Use Python 3.10 or newer. Follow the module README files for environment setup,
dependencies and commands. Catalog preparation is local. Paid embedding and
feature extraction requests require GCP credentials and an explicit `--execute`
flag.

## Current scope

Catalog preparation maps all 22 project categories. Keyword definitions, LLM prompts
and 20 reviewed references per category cover all of them (440 references). The default
extraction config still selects the original 900-product pilot and uses 60
references across T-shirts, Dresses, and Tank tops & Camisoles. Additional
categories need a matching selection and embedding coverage before paid runs.
The current pipeline still needs scaling and recovery improvements before a
full-catalog LLM run.

Human-readable extraction rules are in
[feature_extraction/docs/extraction_rules/](feature_extraction/docs/extraction_rules/).
Shared feature contracts are in `feature_extraction/schema/`. Executable keyword
rules and model-facing prompts are stored separately inside the extraction module.

## Local data

Git stores the folder placeholders under `data/`, but ignores dataset contents.
`feature_extraction/artifacts/` contains local outputs, request logs and embedding
caches and is also ignored. These files are not included in a fresh clone.

On the original workspace, the previous project layout is preserved in the
ignored `archive/extraction_clean_previous/` backup. Historical annotated products
are in `feature_extraction/artifacts/runs/pilot_900_original/`. Transfer required
local data separately, or rebuild it using the documented commands.
