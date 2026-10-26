# Fashion-Gen proof of concept

> **UI / Search Bar Integration Hand-off**: Pełna dokumentacja integracyjna dla wyszukiwarki i bazy produktów znajduje się w [HANDOFF.md](HANDOFF.md).

Pilot: 900 train products, 300 each from T-shirts, Dresses and Tank tops &
Camisoles. Initial reference bank: 60 assistant-reviewed products with complete
labels. Embeddings: main source image and description separately, Gemini
Embedding 2, 3072 dimensions. See the corresponding subfolder READMEs.

## Query parsing

Agreed query interpretation rules: [query_parsing/rules.md](query_parsing/rules.md).
All prompts, definitions, schema descriptions, and model-facing examples are written
in English.

## LLM extraction

```sh
# Offline preparation of two products per category (no authentication/API calls)
.venv/bin/python poc/scripts/run_llm_extraction.py --run-name preview_6

# Paid test, same selection; maximum $0.30 reserved for this run
.venv/bin/python poc/scripts/run_llm_extraction.py --run-name preview_6 --execute
```

The runner is deliberately limited to 1–5 products per category. It is not a
command for starting the whole 840-product extraction. Completed results are
skipped on resume. An attempt without a validated saved result requires inspection;
no automatic inference retries are performed. Separate run names can repeat work
and incur additional costs; the budget guard applies per run.

Settings: Vertex AI `gemini-3.5-flash-lite`, global endpoint, thinking MEDIUM,
media resolution MEDIUM for every image. One target per request, all its images,
plus source poses `id_gridfs_1` and `id_gridfs_3` of each of two references. There
is no silent image fallback and no guaranteed semantic front/back assignment.

Retrieval filters the bank by category and gender, excluding the query product.
It picks the highest cosine image match, then the highest text match excluding
the already selected image neighbor. Neighbors can change after a successful
product extends the bank. No new embedding computation is necessary: all pilot
products already have vectors.

Only missing feature definitions, schema fields and example labels enter the
request. Raw names/descriptions stay complete. Keyword assignments are preserved.
Client-side validation checks extra fields, enum values, exclusivity, explanations
and shoulder/strap dependencies after merging. Product-level problems produce
needs_review records; outside_schema values remain pending, absent from features.
Only complete, validated ready records can extend the reference bank. A ready
record is a validated model result, not independently confirmed human truth.

## Run outputs

```text
poc/feature_extraction/runs/<run-name>/
  manifest.json             model, settings, selected IDs and version fingerprint
  calls/<id>_prompt.json     exact text, schema and local image references
  calls/<id>.json            raw response, usage, cost, image hashes and neighbors
  products.jsonl            merged features, provenance, statuses and metadata
  products.parquet          equivalent records; nested objects as JSON strings
  reference_bank.jsonl      initial references plus validated ready results
  summary.json              counts, statuses, estimated cost and bank size
```

Initial manual labels remain in `feature_extraction/reference/products.jsonl`; each run saves its own
expanded bank snapshot. A new run starts from the initial bank, not automatically
from another run's results. Reusing an expanded bank across experiments will need
an explicit bank choice to keep runs reproducible.

The fingerprint covers model settings, system prompt, definitions, source rules,
retrieval/prompt code, references and embedding configuration. Each call also
stores the actual request hash, neighbors, image hashes and returned usage.
Prices used: $0.30/M input and $2.50/M output tokens including thinking. Requests
are counted before inference, then charged against a conservative output/schema
reservation. Usage-based costs are estimates, not a Cloud Billing invoice.

## Test result

`feature_extraction/runs/smoke_6/` contains the first real six-product run. See `results.md` for the
manual review and per-product outputs; it is a small integration check, not an
accuracy benchmark.

```sh
.venv/bin/python -m unittest discover -s poc/tests -v
```

## Full sequential pilot run

```sh
.venv/bin/python -u poc/scripts/run_pilot.py --execute --budget-usd 5
```

This processes the 834 remaining products, starting from 60 manual references and
6 completed smoke-test products. Requests run sequentially, round-robin across
categories. Every complete validated response extends the in-memory bank before
the next request. Model, thinking, resolution, image policy and feature rules
are the same as in the small run. For schemas in which all requested features
have Other, the unnecessary outside_schema_reasons field is omitted entirely;
saved records normalize it to an empty object.

Run data: `poc/feature_extraction/runs/pilot_sync/`. Exact prompts, attempts and responses are persisted
per product. `records/<id>.json` is written atomically after each product.
`progress.json` is updated after each product; JSONL, Parquet and bank snapshots
are refreshed every 20 products and at completion. The log is `run.log` when
launched through tee. `poc/feature_extraction/results/products.{jsonl,parquet}` combines the manual
references, smoke-test results and newly processed records into one pilot dataset.
The final dataset is complete only when summary.json says complete=true.

A persistent guard includes successful token-based costs and conservative
reservations for uncertain attempts. The 5 USD cap covers this new run; prior
embedding and smoke costs are reported separately. At most two attempts are
allowed per product for transient transport/HTTP failures; there are no automatic
semantic retries. A validation failure is retained as needs_review and never
enters the bank. Repeated failures and configuration/authentication errors stop
processing. An unresolved prior attempt must be inspected before restarting.

Resume uses saved per-product records without paying for them again and rebuilds
the bank from them. The manifest rejects changed prompt/code/rule versions.
The full runner offers an offline validation mode (default, no --execute):

```sh
.venv/bin/python poc/scripts/run_pilot.py --limit 834
```
