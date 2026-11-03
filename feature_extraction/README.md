# Product feature extraction

Keyword rules and Gemini complete the fixed product taxonomy. LLM definitions and
output validation support T-shirts, Polos, Tank tops & Camisoles, Bodysuits, Dresses,
and Skirts. Keyword rules also cover the five Jackets & Coats categories, the four
Pants categories, Shirts and Blouses ([CHANGES.md](CHANGES.md)). `config/extraction.yaml` selects the
active scope. Its default selection and manual reference bank still cover the
original 900 products in T-shirts, Dresses, and Tank tops & Camisoles. Paid runs
for the additional categories require a matching selection, complete references
and embeddings first.

## Layout

- `run.py` exposes the extraction command and `pipeline.py` manages the job.
- `schema/` defines category features, allowed values, single/multi choice and constraints.
- `keywords/` contains only matching/parsing instructions and their YAML definitions.
- `validation.py` validates feature values and dependencies for all extraction methods.
- `config_io.py` reads YAML safely and rejects duplicate keys.
- `llm/` contains the Vertex client, prompt builder, response validation and reference retrieval.
- `llm/prompts/system.txt`, `common.json` and `categories/*.json` are prompt sources.
- `embeddings/` builds separate main-image and description embeddings.
- `docs/extraction_rules/` documents the extraction rules; `reference/` holds manual labels.
- `artifacts/` holds local generated datasets, embedding caches, requests and run logs.
- `tests/` contains offline regression tests.

The source taxonomy stays at `categories_and_features.md` in the repository root.
Processed products and images stay at `data/processed/fashiongen/`.

## Category-specific prompt definitions

`llm/prompts/common.json` defines `colors` and `pattern` once for all categories.
`llm/prompts/categories/*.json` contains one file per category, with a `category`
name and a `features` dictionary. Each feature has an `instruction` and label
descriptions under `values`. For example, T-shirts and Dresses each define
`neckline` independently. The system instruction is shared across categories.

Category-specific definitions take precedence over common definitions for the
entire feature. A category can override a shared feature by defining its complete
instruction and values locally. Otherwise, changes to `common.json` apply to
every category using that feature. Gender is assigned from the dataset and has no
LLM prompt definition. Run fingerprints include JSON files in category subfolders.

The builder selects the category first, then includes only unresolved features.
Allowed labels come from `schema/common.yaml` and `schema/categories/*.yaml` and must
all have descriptions in that category's prompt definition. An unsupported
category or a missing feature definition raises an error. To add an LLM category,
add its feature definitions explicitly and enable it in the extraction config.

For matching features, category-specific entries use the same wording and label
descriptions. Polos has colors, pattern, sleeve length and fit. Bodysuits adds
neckline and shoulder construction/strap width to colors, pattern and sleeve
length. Skirts has colors, pattern, skirt silhouette, skirt type and rise. Skirt
length is assigned exclusively from `original_category`; it is never an LLM task.

## Shared feature schema and keyword rules

`schema/common.yaml` defines shared features; `schema/categories/*.yaml` lists the
complete, ordered feature set for each category and references shared definitions
with `use`. Each feature declares `type` (`single_choice`, `multi_choice` or
`composition`) and `values`. Multi choice also declares `max_items` and
`exclusive_values`; compositions declare `total`, `tolerance` and optional scalar
`special_values` such as `Unlined` and `Unknown`. `value_dependency` defines an
if-and-only-if relation between single-choice values, including strap width.
`on_unresolved: exclude` declares an exclusion policy independently of the extractor.

The LLM response builder and the shared validator read this schema directly.
They do not import keyword configurations or infer types from keyword strategies.
For example, `closure_type` is multi choice even though no keyword rule exists for it.

`keywords/definitions/` contains only extraction instructions: input columns,
phrases, source mappings, matching strategies, composition sections and fallbacks.
`main_section_patterns` optionally matches complete normalized section labels with
regular expressions; lining accepts `lining [0-9]+`, including numbers above 4.
There is no `llm` strategy, no empty keyword lists, and no duplicate allowed-value
or cardinality declarations. A feature with no keyword rule remains `undefined`
unless its schema dependency derives the value. It can then be completed by the
LLM if that category has prompt definitions. The metadata field `strategy` is
`null` when no keyword rule exists; its source is `derived_rule` if a dependency
assigned the value, otherwise `null` until another extractor fills it.

For example:

```yaml
# schema/categories/<category>.yaml
closure_type:
  type: multi_choice
  values: [Zip, Button, Press-Stud, Double-Breasted, Belted, Open Front, Other]
  max_items: 5
  exclusive_values: [Open Front, Other]
```

No corresponding keyword entry is needed. The keyword loader validates all rule
outputs against the schema, including mappings, defaults and fallback values.
`validation.py` checks actual scalar/list/composition values and dependencies;
`llm/validation.py` additionally checks response status, requested keys and reasons.

## Install and configure

Run from the repository root with Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r feature_extraction/requirements.txt
```

Create the environment only on first setup; activate the existing environment
on later runs.

For paid calls, install the Google Cloud CLI and configure Application Default
Credentials for the project selected in `config/extraction.yaml`:

```sh
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

The account needs permission to call Vertex AI in that project. Replace
`YOUR_PROJECT_ID` with the configured project ID.

Edit `feature_extraction/config/extraction.yaml` to select the dataset, category
scope, sample, references, embeddings, model, Vertex project, generation settings,
timeouts, retry policy and estimated USD budgets. Relative paths resolve against
the repository root. A custom config file can be passed with `--config`.

The default selection preserves the original 900 product IDs. Set `selection` to
null or pass `--all-products` to process every product in the configured categories.
The loader supports train and validation manifests and rejects duplicate IDs.
Current extraction outputs combine selected splits in a single dataset and do
not retain a split column. The reference bank is shared across selected splits.
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
For a new run, preparation uses the manual bank. When resuming, previously saved
ready results can also enter the bank. A paid sequential run extends the bank
after each valid result and may select different examples later.

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

Runs are stored under the configured `artifacts` directory in `runs/<run_name>/`.
The default is `feature_extraction/artifacts/runs/<run_name>/`.

| File | Keyword-only stage | LLM preparation or execution |
| --- | --- | --- |
| `config.json` | Settings, selected IDs and fingerprint | Settings, selected IDs and fingerprint |
| `keywords.jsonl` | All selected keyword results, including exclusions | Same keyword inputs |
| `products.jsonl`, `products.parquet` | All selected keyword records | Saved records only; preparation may contain just manual, excluded or keyword-complete records |
| `requests/*_prompt.json` | — | Prompt for each prepared product |
| `requests/*_attempt_*.json` | — | Paid attempt journals with responses, usage, costs and status |
| `reference_bank.jsonl` | — | Current bank of complete examples |
| `summary.json` | Keyword counts and statuses | Progress, bank size and estimated cost |

Parquet is written when at least one result record exists. Use a distinct run
name for keyword-only exploration: running `--stage keywords` on a completed LLM
run currently replaces that run's product outputs with keyword-only records.

Reusing a run name resumes saved products. A completed API response saved before
an interruption can be replayed locally. Changed source evidence, code, configuration,
references, shared schemas or existing embedding exports require a new run name. JSONL and Parquet
files are each written through temporary files, with JSONL serving as the resume source.

Paid inference requires `--execute` and Application Default Credentials for the
configured GCP project. Model API credentials are obtained through google-auth.
HTTP 429 and selected server failures have bounded retries. An uncertain transport
outcome stops the job and keeps its cost reservation for inspection. Unresolved
attempts are never silently repaid on resume. Costs are estimates based on the
configured token rates; compare them with actual billing before larger runs.

Structured output requests only missing features. Existing keyword values remain
immutable. A parsed response rejected by the local feature validator is saved as
`needs_review` with `product_status: processing_error`. A valid response reporting
`out_of_category` or `unusable_product` is also saved as `needs_review`, preserving
the model's reason and the features assigned before the call. `outside_schema`
leaves the product `pending`.

Transport failures, exhausted HTTP retries, malformed JSON, missing usage, and
incomplete output such as `MAX_TOKENS` stop the run. Attempt journals preserve the
response or error for inspection; these failures do not automatically produce a
`needs_review` product record. Input/configuration errors and budget limits also
stop execution. Resume after inspecting the saved state.

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
