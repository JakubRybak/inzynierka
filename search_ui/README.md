# Search UI

[Wersja polska](README.pl.md)

Local web demo of the search bar on the 9,922-product pilot. A query goes through the LLM query parser, the
products are filtered by the extracted features, and the remaining ones are ranked by embedding similarity. The page
shows what the parser understood, lets you adjust the filters by hand and shows how long each stage took.

It uses the outputs of the other parts of the repository and computes nothing offline itself:

| Input | Where it comes from |
| --- | --- |
| product metadata and images | `data/processed/fashiongen/` (`dataset_preparation/fashiongen/`) |
| product features | `feature_extraction/outputs/pilot_9922/products.parquet` |
| product embeddings | `feature_extraction/outputs/pilot_9922/embeddings/` (description and main image, 3072 dims, Git LFS) |
| filter panel features and values | `feature_extraction/schema/` (all 22 categories) |
| query parser | `poc/scripts/query_parser.py` with prompts and schemas in `poc/query_parsing/` |
| benchmark parses | `query_extraction/queries/` on the `user_queries` branch (1,535 reviewed queries, 22 categories) |

Two parsers can be used:

- `--parser llm` – the two-step parser from the earlier proof of concept. It supports **T-shirts, Dresses and
  Tank tops & Camisoles**; for other queries it returns no category, and the category and filters are picked by
  hand in the filter panel. Its feature values were written before the current schemas, so a value that no longer
  exists matches no product, with a warning.
- `--parser benchmark` – the reviewed parses of the query extraction benchmark for all 22 categories, without API
  calls, for working on the ranking while there is no parser for every category. Only queries of the **dev split**
  are answered from the benchmark, and the examples in the page come from it; a test query or any other query goes to
  the LLM parser. The split is the one of the ranking evaluation (a hash of the query and its category), so test
  queries stay unseen while the ranking is tuned. The benchmark is read from `query_extraction/queries/` in the
  working tree or, while it is not merged, from `origin/user_queries`.

## Quick start

From the repository root, with a Python that has the requirements below:

```sh
git lfs pull                       # the embeddings are Git LFS files
python search_ui/prepare.py        # pilot products with status ready -> search_ui/data/
python search_ui/server.py --parser llm
```

The page opens at http://127.0.0.1:8000. `prepare.py` only has to be run again when the features file changes.

**Requirements**

- Python packages: `pandas`, `numpy`, `pyarrow`, `pyyaml`, `google-genai`, `google-auth`, `requests`, `httpx`.
- Google Cloud access to Vertex AI for the parser and the query embeddings:
  ```sh
  gcloud auth application-default login
  export GOOGLE_CLOUD_PROJECT=<project id>
  export GOOGLE_CLOUD_LOCATION=global
  export GOOGLE_GENAI_USE_VERTEXAI=true
  ```
- Without the LLM parser: `python search_ui/server.py --parser mock`. The mock matches query words against index
  values. Query embeddings still need Vertex AI.

## Using the page

- **Search bar and examples** – type a query (English or Polish) or click one of the examples, grouped by category
  (with `--parser benchmark`: five dev queries per category, those with a residual first).
- **Parser reading** (under the search bar) – the conditions the parser extracted, one per line: the category
  outlined, included values in green, excluded ones (AND NOT) in red, then the residual phrases and where the parse
  came from (benchmark or LLM parser).
- **Filters** (button above the results, opens a panel on the right) – every feature and value of the selected
  category from the feature extraction schemas, with the number of products; `Other`, `Not Applicable` and
  `Unknown` are left out, as the parser never filters on them. After a search it shows what the parser picked.
  Clicking a value cycles *include → exclude → off*; multi-valued features (`colors`, `main_composition` and the
  other multi-choice features) also have a mode: *any of*, *all of* or *only*. Every change searches again straight
  away with these filters, without the parser. The numeric Price control supports `<`, `<=`, `>`, `>=` and `=`; add
  a second condition to form a range. Currency is not converted. Products with zero or unknown prices do not match an
  active price condition. *Reset to parser* restores the parser's filters. When the parser finds no category, you
  can pick one here. The *Residual* field takes one phrase per line; the phrases are shown and passed on with the
  filters, while the current ranking uses the whole query.
- **Ranking** – `combined` (description + image), `text` (description) or `image`.
- **Stage timings** (left, under the parser reading) – parsing (with its two LLM steps), filtering and ranking,
  on one timeline.
- **Results** (right, all of them, scrollable) – image, name, brand, price and the features that matched the
  query. Clicking a product shows all its images, its description and every feature, the matched ones highlighted.
- A link like `/?q=black+midi+dress&ranking=text` opens a search directly.

## How it works

1. **Parsing** (`parser_adapter.py`). The parser returns `category`, `filters` and `residual` (a list of phrases,
   one per requirement; a string becomes one phrase) (`QueryParser.to_dict()`). A null category means the query is
   outside the parser's categories, outside the catalog or too general, and no search is run. Otherwise the filters
   become a condition tree (`conditions.py`):

   | Parser operator | Condition |
   | --- | --- |
   | `in`, `contains_any` | the product has any of the values |
   | `not_in`, `contains_none` | the product has none of the values |
   | `contains_all` | the product has all the values |
   | `equals_set` | the product has exactly these values |
   | `lt`, `lte`, `gt`, `gte`, `eq` | numeric `msrpUSD` price comparisons; price uses `value` rather than `values` |
   | `around` | price within ±20% of `value` (the parser rules leave the tolerance open; the same as in the ranking evaluation) |

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
   product metadata. A price comparison uses positive finite `msrpUSD`; zero, missing or invalid prices do not
   match. A feature or value that no indexed product has (for example a brand outside the catalog) stays in the
   tree and matches nothing, with a warning, so a filter is never loosened. When no product meets every condition,
   the result is empty.

3. **Ranking** (`server.py`). The full query is embedded on every request with `gemini-embedding-2` (3072 dims)
   and compared (cosine) with the precomputed embeddings of the candidates:
   - `text` – with the product descriptions, query sent as `task: search result | query: <query>`;
   - `image` – with the main product images, plain text sent;
   - `combined` – mean of the z-scores of both, computed over the candidates.

Nothing is cached: a repeated query calls the parser and the embedding API again, and every HTTP response is sent
with `Cache-Control: no-store`. Only the index, the product embeddings and the API clients are loaded at startup.

## Options

| `server.py` option | Default | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `benchmark`, `mock` or `module:function` returning the parser output format |
| `--ranking` | `combined` | default ranking: `combined`, `text` or `image` |
| `--port` | `8000` | |
| `--data` | `search_ui/data` | index built by `prepare.py` |
| `--no-warmup` | | skip the test embedding call at startup |
| `--no-browser` | | do not open the page |

`prepare.py` takes `--features` (`.parquet`, `.jsonl` or `.csv`, one or more files; default: the pilot), `--status`
(default `ready`), `--limit`, `--dataset`, `--embeddings` and `--output`. It stops if the embeddings do not cover
every indexed product.

A parser given as `module:function` can set in its module `NAME` (shown in the page), `CATEGORIES` (the categories
it can return for an arbitrary query, shown when it returns none) and `EXAMPLES` (example queries by group, shown
instead of `example_queries.yaml`).

## HTTP API

| Endpoint | |
| --- | --- |
| `GET /api/search?q=…&ranking=…` | runs the whole pipeline |
| `GET /api/search?q=…&filters=<json>` | skips the parser; `filters` is `{"category", "filters", "residual"}` in the parser format |
| `GET /api/info` | parser name and categories, defaults, catalog categories, filter panel values, example queries |
| `GET /api/product?id=…` | product details |
| `GET /images/<image_path>` | product image |

The search response contains `parsed` (category, filters, residual and their source), `tree`, `condition`,
`warnings`, `results` (with `score`, `score_text`, `score_image`, `features` and the `matched` features),
`timings` (`parsing_ms`, `filtering_ms`, `ranking_ms`, `query_embedding_ms`, `total_ms`) and, for the LLM parser,
`parser_info` with the latency of both parser steps and the estimated cost. Errors come back as
`{"error": {"stage", "message"}}` with the timings measured so far.

## Files

| File | |
| --- | --- |
| `prepare.py` | builds `data/index.parquet` (git-ignored) from the features file, metadata and images |
| `server.py` | search pipeline, ranking and HTTP server |
| `conditions.py` | condition tree: validation, evaluation, matched features |
| `parser_adapter.py` | parser output → condition tree, mock parser, parser loading |
| `llm_parser.py` | wraps `poc/scripts/query_parser.py` for `--parser llm` |
| `benchmark_parser.py` | benchmark parses of dev queries for `--parser benchmark`, the LLM parser for other queries |
| `facets.py` | filter panel values per category from `feature_extraction/schema` |
| `common.py` | paths, loaders, query embedder |
| `static/index.html` | the page (read on every request, so edits show after a reload) |
| `example_queries.yaml` | examples shown in the page |

## Tests and checks

```sh
python -m unittest discover -s search_ui/tests   # no API calls
python search_ui/check_examples.py               # examples against the index, mock parser
python search_ui/check_examples.py --parser llm  # the same with the LLM parser (paid calls)
```

## Troubleshooting

- **`Failed to resolve 'oauth2.googleapis.com'`** or another connection error at startup – no network or DNS. The
  server still starts; the parser and embeddings work once the connection is back.
- **An error reading `embeddings/text.parquet` or `image.parquet`** – the files are still Git LFS pointers of a few
  hundred bytes; run `git lfs pull`.
- **`Missing optional dependency 'pyarrow'`** – the Python on `PATH` is not the one with the requirements.
- **`No embeddings for N indexed products`** – the features file contains products outside the embedded set.
- **The parser returns no category** for a query in one of the other 19 categories – expected with the LLM
  parser; pick the category in the filter panel, or use `--parser benchmark` with its examples.

## Latency

Typical times per query with the LLM parser: parsing about 2 s (two LLM calls), filtering a few ms, query
embedding 0.3–0.5 s. A benchmark parse and searching with filters from the panel skip the LLM.
