# Product feature extraction

Keyword rules and Gemini complete the fixed product taxonomy. The initial LLM
scope is T-shirts, Dresses, and Tank tops & Camisoles. Existing keyword definitions
for the other previously implemented categories remain available in
`keywords/definitions/`; `config/extraction.yaml` selects the active scope.

## Layout

- `run.py` exposes the extraction command and `pipeline.py` manages the job.
- `keywords/` contains the matching engine, composition parser and YAML definitions.
- `llm/` contains the Vertex client, prompt builder, response validation and reference retrieval.
- `llm/prompts/system.txt` and `feature_definitions.json` are prompt sources.
- `embeddings/` builds separate main-image and description embeddings.
- `docs/extraction_rules/` documents the extraction rules; `reference/` holds manual labels.
- `artifacts/` holds local generated datasets, embedding caches, requests and run logs.
- `tests/` contains offline regression tests.

The source taxonomy stays at `categories_and_features.md` in the repository root.
Processed products and images stay at `data/processed/fashiongen/`.

## Category-specific prompt definitions

`llm/prompts/feature_definitions.json` stores independent definitions for each
category and feature. For example, `T-shirts.neckline` and `Dresses.neckline`
each have their own `instruction` and descriptions under `values`. Editing one
category's definition affects only that category. The system instruction remains
shared across categories.

The builder selects the category first, then includes only unresolved features.
Allowed labels still come from the keyword/category YAML configuration and must
all have descriptions in that category's prompt definition. An unsupported
category or a missing feature definition raises an error. To add an LLM category,
add its feature definitions explicitly and enable it in the extraction config.

## Install and configure

Run from the repository root with Python 3.10 or newer:

```sh
source .venv/bin/activate
pip install -r feature_extraction/requirements.txt
```

Edit `feature_extraction/config/extraction.yaml` to select the dataset, category
scope, sample, references, embeddings, model, Vertex project, generation settings,
timeouts, retry policy and estimated USD budgets. Relative paths resolve against
the repository root. A custom config file can be passed with `--config`.

The default selection preserves the original 900 product IDs. Set `selection` to
null or pass `--all-products` to process every product in the configured categories.
The loader supports train and validation manifests and rejects duplicate IDs.
Generated outputs retain `brand`, `section`, `category`, `features`,
`feature_metadata`, `status`, and `exclusion_reasons`, plus LLM status and provenance.

## Commands

Keyword-only extraction for the default sample:

```sh
python -m feature_extraction.run --stage keywords --run-name keywords_900
```

Prepare prompts for all selected products with existing embeddings:

```sh
python -m feature_extraction.run --run-name extraction_900
```

This mode makes no API calls. It saves keyword results, prompt previews and the
initial manual records. Its summary reports planned calls and `complete: false`.
During preparation, all examples come from the manual bank; a paid sequential run
extends that bank after each valid result and may select different examples later.

Execute the same run only after reviewing its configuration and budget:

```sh
python -m feature_extraction.run --run-name extraction_900 --execute
```

The `--stage llm` command also computes keyword inputs before completing missing
features. `--stage all` is the default. `--limit N` restricts the selected product
list for a new run. Use the same inputs and limit when resuming a run.

Inspect the embedding cache offline:

```sh
python -m feature_extraction.embeddings.build
```

Compute missing vectors with explicit paid execution:

```sh
python -m feature_extraction.embeddings.build --execute
```

Embeddings use the first source image (`id_gridfs_1`) and, separately, the verbatim
product description. Manual references are always included in embedding inputs.
Choose a new embedding folder when changing the model or input recipe.

## Run files and resuming

Each `artifacts/runs/<run_name>/` contains:

- `config.json` with settings, selected IDs and an input/code fingerprint;
- `keywords.jsonl` with all selected keyword results, including exclusions;
- `requests/*_prompt.json` and `*_attempt_*.json` with prompts, raw responses,
  image hashes, usage, costs and attempt status;
- `products.jsonl` and `products.parquet` with matching column representations;
- `reference_bank.jsonl` and `summary.json`.

Reusing a run name resumes saved products. A completed API response saved before
an interruption can be replayed locally. Changed source evidence, code, configuration,
references or existing embedding exports require a new run name. JSONL and Parquet
files are each written through temporary files, with JSONL serving as the resume source.

Paid inference requires `--execute` and Application Default Credentials for the
configured GCP project. Model API credentials are obtained through google-auth.
HTTP 429 and selected server failures have bounded retries. An uncertain transport
outcome stops the job and keeps its cost reservation for inspection. Unresolved
attempts are never silently repaid on resume. Costs are estimates based on the
configured token rates; compare them with actual billing before larger runs.

Structured output requests only missing features. Existing keyword values remain
immutable. Invalid output becomes `needs_review`; `outside_schema` remains pending.
A complete, valid `ready` product with the required image poses can join the bank.
`ready` means schema and dependency validation passed; it is not a manual accuracy label.

## Preserved data

Existing embeddings are in `artifacts/embeddings/`. The original 900 annotated
products are in `artifacts/runs/pilot_900_original/products.jsonl` and `.parquet`.
Historical prompts, calls and summaries are in `artifacts/runs/legacy/`.
The original keyword outputs are in `artifacts/runs/keywords_original/`.
These files keep their historical provenance unchanged.

The previous `poc/` and `extraction/` trees were moved into the local ignored backup
`archive/extraction_clean_previous/`. That backup also preserves unrelated query/UI
experiments and local model files. Generated artifacts and the backup are ignored
by Git. Keep a separate copy when transferring the project to another machine.

## Offline verification

```sh
python -m unittest discover -s feature_extraction/tests -v
```
