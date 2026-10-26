# Search UI

[Wersja polska](README.pl.md)

Local web demo of the search bar. A query goes through the LLM query parser, the products are filtered by the
extracted features, and the remaining ones are ranked by embedding similarity. The page shows what the parser
understood, lets you adjust the filters by hand and shows how long each stage took.

It uses the outputs of the other proof-of-concept parts and computes nothing offline itself:

| Input | Where it comes from |
| --- | --- |
| product metadata and images | `data/processed/fashiongen/` (`scripts/build_fashiongen_dataset.py`) |
| product features | `poc/feature_extraction/results/products.parquet` (LLM feature extraction) |
| product embeddings | `poc/feature_extraction/embeddings/gemini_embedding_2/` (description and main image, 3072 dims) |
| query parser | `poc/scripts/query_parser.py` with prompts and schemas in `poc/query_parsing/` |

## Quick start

From the repository root, with a Python that has the requirements below:

```sh
python poc/search_ui/prepare.py --features poc/feature_extraction/results/products.parquet --status ready
python poc/search_ui/server.py --parser llm
```

The page opens at http://127.0.0.1:8000. `prepare.py` only has to be run again when the features file changes.

**Requirements**

- Python packages: `pandas`, `numpy`, `pyarrow`, `pyyaml`, `google-genai`, `google-auth`, `requests`.
- Google Cloud access to Vertex AI for the parser, the query embeddings and HyDE:
  ```sh
  gcloud auth application-default login
  export GOOGLE_CLOUD_PROJECT=<project id>
  export GOOGLE_CLOUD_LOCATION=global
  export GOOGLE_GENAI_USE_VERTEXAI=true
  ```
- Without the LLM parser: `python poc/search_ui/server.py --parser mock`. The mock answers the example queries from
  `parser_mock.yaml` and matches words against index values otherwise. Query embeddings still need Vertex AI.

## Using the page

- **Search bar and examples** – type a query (English or Polish) or click one of the examples, grouped by category.
- **Parser reading** (under the search bar) – the conditions the parser extracted, one per line: the category
  outlined, included values in green, excluded ones (AND NOT) in red.
- **Filters** (button above the results, opens a panel on the right) – every feature and value of the selected category, as defined by the parser response
  schemas, with the number of products. After a search it shows what the parser picked. Clicking a value cycles
  *include → exclude → off*; multi-valued features (`colors`, `main_composition`, `dress_type`) also have a mode:
  *any of*, *all of* or *only*. Every change searches again straight away with these filters, without the parser.
  *Reset to parser* restores the parser's filters. When the parser finds no category, you can pick one here.
- **Ranking** – `combined` (text + image), `text`, `image` or `hyde` (see below).
- **Stage timings** (left, under the parser reading) – parsing (with its two LLM steps), filtering and ranking,
  on one timeline.
- **Results** (right, all of them, scrollable) – image, name, brand, price and the features that matched the
  query. Clicking a product shows all its images, its description and every feature, the matched ones highlighted.
- A link like `/?q=black+midi+dress&ranking=text` opens a search directly.

## How it works

1. **Parsing** (`parser_adapter.py`). The parser returns `category`, `filters` and `residual`
   (`QueryParser.to_dict()`). A null category means the query is outside the catalog or too general, and no search
   is run. Otherwise the filters become a condition tree (`conditions.py`):

   | Parser operator | Condition |
   | --- | --- |
   | `in`, `contains_any` | the product has any of the values |
   | `not_in`, `contains_none` | the product has none of the values |
   | `contains_all` | the product has all the values |
   | `equals_set` | the product has exactly these values |

   ```json
   {"op": "and", "args": [
     {"feature": "category", "values": ["T-shirts"]},
     {"feature": "colors", "values": ["Black", "White"], "match": "all"},
     {"op": "not", "arg": {"feature": "main_composition", "values": ["Polyester"]}}
   ]}
   ```

2. **Filtering** (`conditions.py`). The tree is evaluated on every indexed product. Feature values are treated as
   sets; `main_composition` is the set of materials in it, whatever their share. A missing feature never matches,
   so a product without it is excluded by a positive filter and kept by a negative one. `brand` is compared with the
   product metadata. Features or values that do not occur in the index are dropped with a warning. When no product
   meets every condition, the result is empty.

3. **Ranking** (`server.py`). The full query is embedded on every request with `gemini-embedding-2` (3072 dims)
   and compared (cosine) with the precomputed embeddings of the candidates:
   - `text` – with the product descriptions, query sent as `task: search result | query: <query>`;
   - `image` – with the main product images, plain text sent;
   - `combined` – mean of the z-scores of both, computed over the candidates;
   - `hyde` – an LLM (`gemini-3.5-flash-lite`) writes the description of an ideal product, and its embedding is
     compared with the product descriptions.

Nothing is cached: a repeated query calls the parser and the embedding API again, and every HTTP response is sent
with `Cache-Control: no-store`. Only the index, the product embeddings and the API clients are loaded at startup.

## Server options

| Option | Default | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `mock` or `module:function` returning the parser output format |
| `--ranking` | `combined` | default ranking: `combined`, `text`, `image`, `hyde` |
| `--hyde-model` | `gemini-3.5-flash-lite` | model writing HyDE descriptions |
| `--port` | `8000` | |
| `--data` | `poc/search_ui/data` | index built by `prepare.py` |
| `--no-warmup` | | skip the test embedding call at startup |
| `--no-browser` | | do not open the page |

`prepare.py` takes `--features` (`.parquet`, `.jsonl` or `.csv`, one or more files), `--status` (keep only these
statuses, e.g. `ready`), `--limit`, `--dataset`, `--embeddings` and `--output`. It stops if the embeddings do not
cover every indexed product.

## HTTP API

| Endpoint | |
| --- | --- |
| `GET /api/search?q=…&ranking=…` | runs the whole pipeline |
| `GET /api/search?q=…&filters=<json>` | skips the parser; `filters` is `{"category", "filters"}` in the parser format |
| `GET /api/info` | parser name, defaults, categories, filter panel values, example queries |
| `GET /api/product?id=…` | product details |
| `GET /images/<image_path>` | product image |

The search response contains `parsed` (category, filters, residual and their source), `tree`, `condition`,
`warnings`, `results` (with `score`, `features` and the `matched` features), `hyde`,
`timings` (`parsing_ms`, `filtering_ms`, `ranking_ms`, `hyde_ms`, `query_embedding_ms`, `total_ms`) and, for the LLM
parser, `parser_info` with the latency of both parser steps and the estimated cost. Errors come back as
`{"error": {"stage", "message"}}` with the timings measured so far.

## Files

| File | |
| --- | --- |
| `prepare.py` | builds `data/index.parquet` (git-ignored) from the features file, metadata and images |
| `server.py` | search pipeline, ranking and HTTP server |
| `conditions.py` | condition tree: validation, evaluation, matched features |
| `parser_adapter.py` | parser output → condition tree, mock parser, parser loading |
| `llm_parser.py` | wraps `poc/scripts/query_parser.py` for `--parser llm` |
| `facets.py` | filter panel values per category from `poc/query_parsing/schemas` |
| `common.py` | paths, loaders, query embedder, HyDE |
| `static/index.html` | the page (read on every request, so edits show after a reload) |
| `example_queries.yaml` | examples shown in the page |
| `parser_mock.yaml` | mock parser answers in the parser output format |

## Tests and checks

```sh
python -m unittest discover -s poc/search_ui/tests   # no API calls
python poc/search_ui/check_examples.py               # examples against the index, mock parser
python poc/search_ui/check_examples.py --parser llm  # the same with the LLM parser (about $0.04)
```

## Troubleshooting

- **`Failed to resolve 'oauth2.googleapis.com'`** or another connection error at startup – no network or DNS. The
  server still starts; the parser and embeddings work once the connection is back.
- **`Missing optional dependency 'pyarrow'`** – the Python on `PATH` is not the one with the requirements.
- **`No embeddings for N indexed products`** – the features file contains products outside the embedded set; use
  the matching features file or compute embeddings for the new products first.
- **The parser returns no category** for some queries of the form "X or Y …" (e.g. "racerback or halter tank top"),
  while "halter or racerback tank top" works. This is the parser's behaviour, not the UI's.

## Latency

Typical times per query with the LLM parser: parsing about 2 s (two LLM calls), filtering about 1 ms, query
embedding 0.3–0.5 s, HyDE another 1–2 s. Searching with filters from the panel skips parsing and takes about 0.5 s.
