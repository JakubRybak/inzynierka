# Abstract concepts in ranking

[Wersja polska](README.pl.md)

The `concepts` ranking orders products by the soft part of the query: an occasion, a style or a season ("for a
wedding", "elegant", "for summer"). Every product has an offline 0–10 score for each of 33 concepts. At query time
the parser residual is matched with the concepts and products are ranked by their scores.

## Concepts

[concepts.yaml](concepts.yaml): 33 concepts with `id`, `name`, `type` and `added`.

| Type | Concepts |
| --- | --- |
| occasion | wedding guest, prom, cocktail party, party, night out, date night, office, beach, gym, music festival, funeral |
| style | casual, formal, elegant, sexy, modest, boho, vintage, flowy, cute, minimalist, streetwear, edgy, romantic, preppy, sporty |
| season | summer, winter, spring, autumn, hot weather, layering, loungewear |

The residual is compared with `name`, so names read like parts of queries. Concepts do not duplicate hard features:
color, composition, length etc. are filters. The list was put together by hand from the report of
`derive_concepts.py`, which collects the residuals of 1300 ESCI queries and 270 synthetic queries.

## Product scores

`score_products.py` makes one `gemini-3.5-flash-lite` call per product.
- **Input:** name, brand, description, composition, extracted features and the images of poses 1 and 3.
- **Output:** an integer 0–10 for every concept, enforced by the response schema.
- **Settings:** temperature 0, thinking MEDIUM.

A score says how high the product should be in the results for the query "<concept> <category>":

| Score | Meaning |
| --- | --- |
| 0 | does not fit |
| 3 | rather not |
| 5 | neutral |
| 7 | a good result |
| 10 | an archetype |

The prompt ([prompts/score_system.txt](prompts/score_system.txt)) has reference points, e.g. funeral: a plain black
long sleeve midi dress = 10, a black dress with sequins = 2.

The output is `results/concept_scores.parquet` (`product_id, concept_id, score, model, prompt_version, scored_at`):
893 products × 33 concepts = 29,469 scores.

## Index

`prepare.py --concepts`:
- adds `concept__<id>` columns with the scores to the search index;
- embeds the concept names (`gemini-embedding-2`, text `task: search result | query: <name>`).

The server refuses to start when `concepts.yaml` changed since the index was built.

## Choosing concepts and ranking

1. The parser returns the category, the filters and the residual: the part of the query that could not become
   filters, without the garment noun.
2. The residual is embedded in the same format as the concept names and compared with every concept (cosine
   similarity).
3. Chosen: the concepts with similarity ≥ 0.72, at most the 3 most similar.
4. Weights: `softmax(similarity / 0.1)` over the chosen ones. A similarity 0.1 higher gives about 2.7 times the weight.
5. Product score: sum of (weight × score / 10). Sorted descending, ties broken by the `combined` ranking.

The ranking falls back to `combined` when:
- the residual is empty;
- the category has no scores;
- no concept has similarity ≥ 0.72. The query is then appended to `data/misses.jsonl`.

The residual is embedded on every query, without a cache, in parallel with the `combined` embeddings.

Example for "romantic dress for a date night" (residual `romantic for a date night`):

| Concept | Similarity | Chosen | Weight |
| --- | ---: | --- | ---: |
| date night | 0.908 | yes | 0.51 |
| romantic | 0.864 | yes | 0.33 |
| night out | 0.796 | yes | 0.17 |
| sexy | 0.740 | no (limit 3) | – |

A dress scored date night 8, romantic 9, night out 6 gets 0.51·0.8 + 0.33·0.9 + 0.17·0.6 ≈ 0.80.

The similarity threshold is 0.72 (`--concept-threshold`).

## Page

- The `concepts` ranking in the ranking switch.
- Under the parser reading:
  - the residual;
  - the chosen concepts with similarity and weight;
  - the similarity to every concept (the chosen ones in purple, a dashed line at the threshold).
- On result cards the scores of the chosen concepts ("wedding guest 9/10"); in the product panel all its scores.

## Running

Without `--execute` the scripts make no API calls; they only print the number of calls and a cost estimate.

```sh
# index and server
python poc/search_ui/prepare.py --features poc/feature_extraction/results/products.parquet --status ready --concepts
python poc/search_ui/server.py --parser llm --ranking concepts

# scores (only missing product-concept pairs)
python poc/concepts/score_products.py --execute --review

# threshold
python poc/concepts/check_threshold.py --execute

# residual report for building the concept list
python poc/concepts/derive_concepts.py select
python poc/concepts/derive_concepts.py synthesize --execute
python poc/concepts/derive_concepts.py parse --execute
python poc/concepts/derive_concepts.py report --execute
```

| Server option | Default | Meaning |
| --- | --- | --- |
| `--concept-threshold` | `0.72` | minimum residual–concept similarity |
| `--concept-k` | `3` | at most this many concepts |
| `--concept-temperature` | `0.1` | softmax temperature of the weights |
| `--concept-norm` | `raw` | `raw`: score / 10; `percentile`: percentile of the score within the category |
| `--concept-alpha` | none | `alpha · concepts + (1 − alpha) · combined` instead of concepts only |

## Files

| File | Role |
| --- | --- |
| `poc/concepts/concepts.yaml` | concept list |
| `poc/concepts/derive_concepts.py` | report of query residuals |
| `poc/concepts/score_products.py`, `prompts/` | product scores |
| `poc/concepts/results/concept_scores.parquet` | scores |
| `poc/concepts/check_threshold.py`, `threshold_cases.yaml` | threshold check |
| `poc/concepts/data/` | logs, reports, `misses.jsonl` (in .gitignore) |
| `poc/search_ui/concepts.py` | concept choice, weights, product score |
| `poc/search_ui/prepare.py`, `server.py`, `static/index.html` | index, ranking, page |

Scoring the 893 products cost $2.66. Every query in the `concepts` ranking adds one residual embedding.
