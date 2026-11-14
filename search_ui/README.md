# Search UI

Local web demo of the search bar on the pilot: the 9,796 products with status `ready` of the 9,922-product pilot,
in 22 categories. A query goes through the query parser of `query_parsing/`. The products are filtered by their
extracted features, and the products left are ranked. The page shows what the parser understood, lets you change the
filters by hand, switches between rankings and shows how long each stage took.

How the results are ordered, and where the ranking data comes from: [README_ranking.md](README_ranking.md).

## Quick start

From the repository root:

```sh
python search_ui/prepare.py     # builds the index of the pilot in search_ui/data/ (git-ignored)
python search_ui/server.py      # opens http://127.0.0.1:8000
```

Run `prepare.py` again after the features, concept scores, phrase bank, colours or details change. It embeds only what it has not
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
  `query_parsing/README.md`). Two parsers work without these keys:
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
   products. The default, `hybrid`, compares the query embedding with the description, image and features of each
   product and corrects it with the residual phrases (see [README_ranking.md](README_ranking.md)).

## Using the page

The server uses the enhanced WebP from `images_enhanced/pilot_9922` in the FashionGen dataset when available.
Other views use their original PNGs.

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
- **Stage timings**: parsing, with both parser steps, the query embedding (which runs while the parser parses),
  filtering, ranking and the total, which also stands next to the number of results.
- **Score**: in `hybrid`, how much each part of the score moves the ranking (see
  [README_ranking.md](README_ranking.md)).
- **Results**: every candidate, with image, name, brand, price, the features that matched and a bar of its score
  parts. Clicking a product shows all its images, its description, its features, its score parts and the details
  and colours Gemini gave it.
- A link such as `/?q=black+midi+dress&ranking=hybrid` opens a search directly.

## Files

| Path | Contents |
| --- | --- |
| `server.py` | HTTP server and search pipeline: parse, filter, rank |
| `prepare.py` | builds the index in `data/` from the features, metadata, images, concept scores, phrase bank, colour names and detail names |
| `llm_parser.py` | `--parser llm`: the QueryParser of `query_parsing/` |
| `core/` | the modules of the pipeline (below) |
| `static/` | the page (`index.html`, read on every request, so edits show after a reload) and its example queries (`example_queries.yaml`) |
| `offline/`, `ranking_data/` | the scripts and data of the ranking ([README_ranking.md](README_ranking.md)) |
| `tests/` | unit tests, which make no API calls, and `check_examples.py`, a check of the example queries against the index |
| `data/` | the index built by `prepare.py` and the call logs of the offline scripts (git-ignored) |

| `core/` module | Role |
| --- | --- |
| `parser_adapter.py` | parser loading, parser output to condition tree, mock parser |
| `benchmark_parser.py` | the reviewed benchmark parses of dev queries |
| `conditions.py` | condition tree: validation, matching, matched features |
| `facets.py` | filter panel values per category, from `feature_extraction/schema/` |
| `concepts.py` | concept scores in the index and the `concepts` ranking |
| `bank.py` | the phrase bank, the `bank` ranking and the `hybrid` terms |
| `colours.py` | product colours and the colour dictionary, for shade phrases |
| `details.py` | product details and the detail dictionary, for detail phrases |
| `feature_text.py` | a product's features as a short text for its embedding |
| `common.py` | paths, loaders, query embedder |
| `vertex.py` | Gemini calls on Vertex AI with retries, a budget and cost accounting (offline scripts) |

## Options

| `server.py` option | Default | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `mock` or `module:function` returning the parser output format |
| `--ranking` | `hybrid` | default ranking in the page; `combined` when the phrase bank is not loaded |
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
| `GET /api/product?id=…` | one product, with its colours and details from Gemini |
| `GET /images/<image_path>` | product image |

A search response contains the following fields:
- `parsed`, `tree`, `condition` and `warnings`;
- `results`, with their scores, matched features, score parts (`parts`) and the details the query asked for;
- `concepts` or `bank`, which say how each phrase was read;
- `score_parts` and `weights`: how much each part of the score moves the ranking, and the `hybrid` weights;
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
- parsing: about 0.7–1.1 s;
- query embedding: 0.3–0.6 s, during the parsing, so it adds nothing when the parser is slower;
- filtering: a few ms;
- residual phrases (`bank` and `hybrid`): every span of one to three words of the query is embedded during the
  parsing too, because most residual phrases are such spans; only a phrase that is not one (about 3–8%) needs one
  more embedding call (about 0.3–0.6 s) after the parsing. The stage timings show how many were ready.
