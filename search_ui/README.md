# Search UI

Local web demo of the search bar on the pilot: the 9,796 products with status `ready` of the 9,922-product pilot,
in 22 categories. A query goes through the query parser of `query_extraction/`. The products are filtered by their
extracted features, and the products left are ranked. The page shows what the parser understood, lets you change the
filters by hand, switches between rankings and shows how long each stage took.

How the results are ordered, and where the ranking data comes from: [README_ranking.md](README_ranking.md).

## Quick start

From the repository root:

```sh
python search_ui/prepare.py     # builds the index of the pilot in search_ui/data/ (git-ignored)
python search_ui/server.py      # opens http://127.0.0.1:8000
```

Run `prepare.py` again after the features, concept scores or phrase bank change. It embeds only what it has not
embedded before, so a rerun with nothing new makes no paid calls.

**Requirements**

- Python packages: `pandas`, `numpy`, `pyarrow`, `pyyaml`, `google-genai`, `google-auth`, `requests`, `httpx`,
  `scikit-learn`, `scipy`.
- Vertex AI access, because every search embeds the query:
  ```sh
  gcloud auth application-default login
  export GOOGLE_CLOUD_PROJECT=<project id>
  export GOOGLE_CLOUD_LOCATION=global
  export GOOGLE_GENAI_USE_VERTEXAI=true
  ```
- The query parser needs `OPENROUTER_API_KEY` and `CEREBRAS_API_KEY` in `.env` at the repository root (see
  `query_extraction/README.md`). Two parsers work without these keys:
  - `--parser mock` matches query words against index values;
  - `--parser benchmark_parser:parse` answers the dev queries of the benchmark with their reviewed parses and sends
    any other query to the query parser.
- The product embeddings are Git LFS files. Run `git lfs pull` if they are still pointers.

## How a query is answered

1. **Parsing** (`llm_parser.py`, `core/parser_adapter.py`). The parser returns `category`, `filters` and `residual`.
   The residual is a list of phrases that the filters cannot express, such as "for a funeral" or "without pockets".
   A null category means the query is outside the catalog or too general, and no search is run. The filters become
   a condition tree:

   | Parser operator | Condition |
   | --- | --- |
   | `in`, `contains_any` | the product has any of the values |
   | `not_in`, `contains_none` | the product has none of the values |
   | `contains_all` | the product has all the values |
   | `equals_set` | the product has exactly these values |
   | `lt`, `lte`, `gt`, `gte`, `eq` | price (`msrpUSD`) compared with `value` |
   | `around` | price within ±20% of `value` |

2. **Filtering** (`core/conditions.py`). Filtering is strict, and a filter is never loosened:
   - feature values are treated as sets, and `main_composition` is the set of its materials, whatever their share;
   - a product without a feature fails a positive filter and passes a negative one;
   - a price condition needs a positive, finite price;
   - a value that no product has, such as a brand outside the catalog, matches nothing and shows a warning;
   - when no product meets every condition, the result is empty.

3. **Ranking** (`server.py`, `core/`). The chosen ranking orders all the candidates; it never adds or removes
   products. The default, `combined`, compares the query embedding with the description and image of each product.
   The other rankings also use the residual phrases (see [README_ranking.md](README_ranking.md)).

## Using the page

- **Search bar and examples.** Type a query, in English or Polish, or click an example. Examples are grouped by
  category. With `--parser benchmark_parser:parse`, the examples are dev queries of the benchmark that find products.
- **Parser reading**, under the search bar. It lists the category, the included values (green), the excluded values
  (red), the residual phrases and where the parse came from. With `concepts`, `bank` or `hybrid` it also shows how
  every phrase was read.
- **Filters**, a panel on the right. It lists every feature and value of the category, with product counts.
  - Clicking a value cycles include → exclude → off. Multi-valued features can require any, all, or only the chosen
    values.
  - Price takes `<`, `<=`, `>`, `>=` or `=`; add two conditions for a range. Currency is not converted.
  - Every change searches again with these filters, without the parser. *Reset to parser* restores the parsed
    filters.
  - The *Residual* field takes one phrase per line.
- **Ranking**: the order of the results (see [README_ranking.md](README_ranking.md)).
- **Stage timings**: parsing, with both parser steps, filtering and ranking.
- **Results**: every candidate, with image, name, brand, price and the features that matched. Clicking a product
  shows all its images, its description and its features.
- A link such as `/?q=black+midi+dress&ranking=hybrid` opens a search directly.

## Files

| Path | Contents |
| --- | --- |
| `server.py` | HTTP server and search pipeline: parse, filter, rank |
| `prepare.py` | builds the index in `data/` from the features, metadata, images, concept scores and phrase bank |
| `llm_parser.py` | `--parser llm`: the QueryExtractor of `query_extraction/` |
| `core/` | the modules of the pipeline (below) |
| `static/` | the page (`index.html`, read on every request, so edits show after a reload) and its example queries (`example_queries.yaml`) |
| `offline/`, `ranking_data/`, `evaluation/` | the scripts, data and evaluation of the ranking ([README_ranking.md](README_ranking.md)) |
| `tests/` | unit tests, which make no API calls, and `check_examples.py`, a check of the example queries against the index |
| `data/` | the index built by `prepare.py` and the call logs of the offline scripts (git-ignored) |

| `core/` module | Role |
| --- | --- |
| `parser_adapter.py` | parser loading, parser output to condition tree, mock parser |
| `benchmark_parser.py` | the reviewed benchmark parses of dev queries |
| `conditions.py` | condition tree: validation, evaluation, matched features |
| `facets.py` | filter panel values per category, from `feature_extraction/schema/` |
| `concepts.py` | concept scores in the index and the `concepts` ranking |
| `bank.py` | the phrase bank, the `bank` ranking and the `hybrid` terms |
| `feature_text.py` | a product's features as a short text for its embedding |
| `common.py` | paths, loaders, query embedder |
| `vertex.py` | Gemini calls on Vertex AI with retries, a budget and cost accounting (offline scripts and judge) |

## Options

| `server.py` option | Default | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `mock` or `module:function` returning the parser output format |
| `--ranking` | `combined` | default ranking in the page |
| `--concept-threshold` | `0.72` | minimum phrase–concept name cosine for `concepts` |
| `--concept-combine` | `geo` | how `concepts` combines phrases: `geo`, `mean` or `min` |
| `--no-bank` | | do not load the phrase bank (`bank` and `hybrid` disappear) |
| `--port` | `8000` | |
| `--data` | `search_ui/data` | index built by `prepare.py` |
| `--no-warmup` | | skip the test embedding call at startup |
| `--no-browser` | | do not open the page |

`prepare.py` takes the following options:
- `--features`: one or more `.parquet`, `.jsonl` or `.csv` files; default the pilot;
- `--status`: default `ready`;
- `--limit`, `--dataset`, `--embeddings`, `--output`, `--concept-scores`;
- `--no-concepts`, `--no-bank`, `--no-feature-embeddings`.

It stops if the product embeddings do not cover every indexed product.

A parser given as `module:function` can set three names in its module:
- `NAME`, shown in the page;
- `CATEGORIES`, the categories it can return;
- `EXAMPLES`, example queries by group, shown instead of `static/example_queries.yaml`.

## HTTP API

| Endpoint | |
| --- | --- |
| `GET /api/search?q=…&ranking=…` | runs the whole pipeline |
| `GET /api/search?q=…&filters=<json>` | skips the parser; `filters` is `{"category", "filters", "residual"}` in the parser format |
| `GET /api/info` | parser, defaults, categories, filter panel values, example queries |
| `GET /api/product?id=…` | product details |
| `GET /images/<image_path>` | product image |

A search response contains the following fields:
- `parsed`, `tree`, `condition` and `warnings`;
- `results`, with their scores and matched features;
- `concepts` or `bank`, which say how each phrase was read;
- `timings`, in ms per stage;
- for the LLM parser, `parser_info`, with step latencies and estimated cost.

Errors come back as `{"error": {"stage", "message"}}`. Nothing is cached: every response is sent with
`Cache-Control: no-store`.

## Tests and checks

```sh
python -m unittest discover -s search_ui/tests                            # no API calls
python search_ui/tests/check_examples.py                                  # examples against the index, mock parser
python search_ui/tests/check_examples.py --parser benchmark_parser:parse  # the benchmark examples, no LLM calls
```

The mock parser knows only the English values of the index, so `check_examples.py` flags the Polish examples.

## Troubleshooting

- **A connection error at startup**, for example `Failed to resolve 'oauth2.googleapis.com'`. The server still starts;
  the parser and embeddings work once the network is back.
- **An error reading `embeddings/*.parquet`.** The files are still Git LFS pointers; run `git lfs pull`.
- **`No embeddings for N indexed products`.** The features file contains products outside the embedded set.
- **`Phrase bank ranking unavailable`.** `scikit-learn` is missing, or `data/bank_embeddings.npz` is missing or out
  of date; run `prepare.py`.
- **`Missing OPENROUTER_API_KEY` or `Jev HTTP 401`.** `.env` at the repository root is missing a key, or a key spans
  several lines.

Typical latency per query:
- parsing: about 0.7 s;
- filtering: a few ms;
- query embedding: 0.3–0.5 s;
- `concepts`, `bank` and `hybrid`: up to about 0.3 s more, because they embed the residual phrases in parallel with
  the query.

## Merging `main`

On `main` the parser is `query_parsing/`, with `parse_query(query, include_meta=True)`, no `config` argument and no
warm-up. The benchmark moved to `experiments/query_parsing/benchmark/queries/`. Two files have to follow:
- `llm_parser.py`, which imports from `query_extraction`;
- `core/benchmark_parser.py`, for the benchmark path and `query_extraction.core.catalog`.

Nothing else in `search_ui/` imports the parser.
