# Abstract concepts in ranking

[Wersja polska](README.pl.md)

The `concepts` ranking orders products by the soft part of the query: an occasion, a style or a season ("for a
wedding", "elegant", "for summer"). Every product has an offline 0–10 score for each of 33 concepts. The parser
returns the residual as a list of phrases, one per requirement. Each phrase is matched with one concept and products
are ranked by the scores of these concepts.

## Concepts

[concepts.yaml](concepts.yaml): 33 concepts with `id`, `name`, `type` and `added`.

| Type | Concepts |
| --- | --- |
| occasion | wedding guest, prom, cocktail party, party, night out, date night, office, beach, gym, music festival, funeral |
| style | casual, formal, elegant, sexy, modest, boho, vintage, flowy, cute, minimalist, streetwear, edgy, romantic, preppy, sporty |
| season | summer, winter, spring, autumn, hot weather, layering, loungewear |

The residual phrases are compared with `name`, so names read like parts of queries. Concepts do not duplicate hard
features: color, composition, length etc. are filters. The list was put together by hand from the report of
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

1. The parser returns the category, the filters and the residual as a list of phrases: what could not become
   filters, without the garment noun. For example "modest dress for work" → `["modest", "for work"]`.
2. Every phrase is embedded separately, in the same format as the concept names, and compared with every concept
   (cosine similarity).
3. A phrase takes one concept, the most similar one, when its similarity is ≥ 0.72. A phrase without such a concept
   is skipped and appended to `data/misses.jsonl`.
4. Product score: the geometric mean of its scores / 10 for the concepts of all matched phrases. Sorted
   descending, ties broken by the `combined` ranking.

The geometric mean penalises a product that is weak in one phrase: scores 9/9 give 0.90, 10/8 gives 0.89. A 0 in
one phrase gives 0.

The ranking falls back to `combined` when:
- the residual is empty;
- the category has no scores;
- no phrase has a concept with similarity ≥ 0.72.

The phrases are embedded on every query, without a cache, in parallel with each other and with the `combined`
embeddings.

Example for "romantic dress for a date night" (residual `["romantic", "for a date night"]`):

| Phrase | Most similar concepts | Chosen |
| --- | --- | --- |
| romantic | romantic 1.000 · sexy 0.811 · date night 0.809 | romantic |
| for a date night | date night 0.940 · night out 0.856 · romantic 0.799 | date night |

A dress scored romantic 9 and date night 8 gets √(0.9 · 0.8) ≈ 0.85.

The similarity threshold is 0.72 (`--concept-threshold`).

## Page

- The `concepts` ranking in the ranking switch.
- Under the parser reading:
  - the residual phrases;
  - the chosen concept of every phrase with its similarity;
  - for every phrase, its similarity to every concept (the chosen one in purple, a dashed line at the threshold).
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
```

| Server option | Default | Meaning |
| --- | --- | --- |
| `--concept-threshold` | `0.72` | minimum phrase–concept similarity |
| `--concept-combine` | `geo` | how the concept scores of different phrases are combined: `geo` (geometric mean), `mean`, `min` |
| `--concept-norm` | `raw` | `raw`: score / 10; `percentile`: percentile of the score within the category |
| `--concept-alpha` | none | `alpha · concepts + (1 − alpha) · combined` instead of concepts only |

## Files

| File | Role |
| --- | --- |
| `poc/concepts/concepts.yaml` | concept list |
| `poc/concepts/derive_concepts.py` | report of query residuals (expects the residual as one text) |
| `poc/concepts/score_products.py`, `prompts/` | product scores |
| `poc/concepts/results/concept_scores.parquet` | scores |
| `poc/concepts/check_threshold.py`, `threshold_cases.yaml` | threshold check |
| `poc/concepts/data/` | logs, reports, `misses.jsonl` (in .gitignore) |
| `poc/search_ui/concepts.py` | matching phrases with concepts, product score |
| `poc/search_ui/parser_adapter.py` | the residual always as a list of phrases |
| `poc/search_ui/prepare.py`, `server.py`, `static/index.html` | index, ranking, page |

Scoring the 893 products cost $2.66. Every query in the `concepts` ranking adds one embedding per residual phrase.
