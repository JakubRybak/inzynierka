# Embedding storage

The fixed pilot contains 900 train products. Each product is encoded twice with
Vertex AI `gemini-embedding-2`: its first main image and its original description,
in separate requests. No title, labels or instruction prefix is added. No taskType
is sent. Images are original 256 × 256 PNGs; no upscaling or recompression.

```text
poc/feature_extraction/embeddings/gemini_embedding_2/
  image.parquet
  text.parquet
  manifest.json
  cost_ledger.json
  cache/image/<product_id>.json
  cache/text/<product_id>.json
```

Check `complete` and `counts` in manifest.json before consuming the files. Partial
runs still export the available vectors, but complete remains false until both
files contain all 900 products. Caches are saved after each successful request;
Parquet files are exported at the end of each run. Raw caches preserve the API
vectors and usage; Parquet vectors are L2-normalized float32, 3072 dimensions.

Both Parquet files contain `product_id`, `embedding` (a fixed-size float32 list,
not JSON text) and `input_sha256`. The image file additionally contains `image_id`
and repository-relative `image_path`. All selected main images have pose
`id_gridfs_1`; their hashes are computed from the exact submitted PNG bytes.
Text hashes cover the exact UTF-8 description sent to the API.

The manifest records the project, endpoint region, model, dimensionality, input
policy, normalization, pilot/settings fingerprints, counts and estimated cost.
Labels live separately in `poc/feature_extraction/reference/products.jsonl`; changing labels does
not require recomputing embeddings. Changes to input content or configuration
are rejected on resume rather than silently mixing incompatible vectors.

## Run and resume

```sh
.venv/bin/python poc/scripts/encode_embeddings.py --limit 3 --workers 2
.venv/bin/python poc/scripts/encode_embeddings.py --limit 900 --workers 2 --request-interval 0.5
```

The first three products cover all three categories. Cached inputs are skipped.
The runner uses the previously authorized GCP project
`project-3a86f100-1aae-4780-84b`, location `global`.
It refuses concurrent runs and limits concurrency to four requests. The full-pilot
command above uses two workers and spaces request starts by at least 0.5 seconds.
It never calls the feature-extraction model.

A persistent $0.25 spending guard reserves the maximum 8192 input tokens before
each request, then replaces that reservation with returned token usage. Rates:
$0.45/M image input tokens and $0.20/M text input tokens, with no output charge.
Progress totals may fluctuate because they include reservations for in-flight
requests. A finished ledger reports usage-based estimates, not a billing invoice;
credits, FX, taxes and later billing adjustments are not included.

Errors stop further scheduling, allow already in-flight calls to finish and retain
an uncertain request's reservation. No automatic API retries are performed. A
previous paid attempt without a saved cache requires inspection before resuming.
After inspecting a confirmed HTTP 429, pass `--retry-rate-limited` to explicitly
permit a new attempt. This does not retry timeouts or other uncertain failures. After inspecting one
specific uncertain failure, `--retry-uncertain PRODUCT_ID:MODALITY` permits a new
attempt for that key only. Earlier reservations remain included in the
conservative spending total in both cases.
This guard depends on the checked published rates, not on a GCP account spending
cap. It does not apply to unrelated work in the project.

Pricing verified 2026-10-25:
[Google Cloud pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing).

## Retrieval later

Load the vectors into memory and use cosine similarity. Filter reference products
by matching category and gender, complete accepted annotations, and a different
product_id. Choose one image neighbor and one distinct text neighbor. Save the
chosen reference IDs with each extraction result. No vector database is needed
for this pilot. Embeddings are currently generated without performing feature
extraction or changing the reference labels.
