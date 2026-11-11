# Ranking

The ranking orders the products that passed the filters; it never adds or removes any. No generative model runs at
search time. The ranking uses three kinds of signals:
- **embeddings** (`gemini-embedding-2`, 3072 dims): the query, embedded at search time, compared with the
  description, main image and feature text of each product, embedded in advance;
- **concept scores**: a score from 0 to 10 of every product for each of 37 occasions, styles and season needs, given
  offline by Gemini;
- **the phrase bank**: 2,893 residual phrases, labelled offline with what they ask for.

This is the state of 2026-11-11. The ranking is still an experiment, and no ranking has been chosen yet.

## Rankings

| Ranking | Score |
| --- | --- |
| `text` | cosine of the query and the description |
| `image` | cosine of the query and the main image |
| `combined` (default) | mean of the z-scores of `text` and `image` |
| `features` | cosine of the query and the feature text, e.g. "Dresses. For women. Black. 100% linen. Midi length." |
| `combined_features` | mean of the z-scores of description, image and feature text |
| `concepts` | the scores of the concepts that the residual phrases name |
| `bank` | one signal per residual phrase, picked with the phrase bank |
| `hybrid` | `combined_features`, plus concept scores and minus negations, picked with the phrase bank |

## Concepts

`ranking_data/concepts.yaml` lists the concepts, each with a description:
- 12 occasions (wedding guest, office, funeral, christmas, …);
- 16 styles (elegant, boho, goth and punk, …);
- 9 season and comfort needs (winter, rainy weather, cozy, …).

Gemini scored every product for every concept from its text and two images. The prompt asks how high the product
deserves to appear in a search for "<concept> <category>". It also says that usually fewer than one product in five
of a category deserves 7 or more. The scores therefore rank products within their category.

The `concepts` ranking gives each residual phrase the concept with the most similar name, when the cosine is at least
0.72. The scores of the matched concepts are combined with a geometric mean, and `combined` breaks ties. When no
phrase matches, the ranking is `combined`.

## Phrase bank

Each phrase of `ranking_data/phrase_bank.jsonl` has the following labels:
- a kind: occasion, style, season, detail, shade, size or audience, or other;
- a negation flag;
- an English version;
- the concepts it asks for.

The phrases come from Amazon ESCI clothing queries, typical needs listed per category, an earlier bank, and Polish
and Spanish versions of the most frequent ones. Phrases found only in benchmark test queries are left out.

At search time a residual phrase takes the labels of the first match:
1. the same phrase in the bank;
2. its nearest bank phrase, when the cosine is at least 0.86;
3. the concept with the most similar name, when the cosine is at least 0.80.

A phrase with no match is unknown. Two rules apply first:
- **Shades.** A lightness word right before a colour of the query is a shade, for example "light" in "light pink
  dress".
- **Negation.** An unknown phrase is negated when it starts with a negation word followed by at most three words, for
  example "without pockets".

## `bank`

Each phrase gives one column of percentiles within the candidates:

| Phrase | Signal |
| --- | --- |
| occasion, style or season with concepts | its concept scores |
| any other phrase with concepts | its text signals and concept scores |
| shade | its text signals, with the image counted twice |
| negated | its signal, inverted |
| size or audience ("petite") | none: the catalog has no such information |
| anything else (a print, a theme, an unknown phrase) | the `combined` similarity of the whole query |

The text signals are TF-IDF over the name and description, and the similarity of the phrase to the description and
image embeddings. The columns are combined with a geometric mean, which acts as a soft AND. `combined` breaks ties.

## `hybrid`

```
hybrid = combined_features + 0.5 × z(concept scores of each occasion, style or season phrase)
                           − 1.0 × z(what each negated phrase excludes)
```

Other phrases add nothing, because the whole query already covers them. The weights were chosen on the dev queries.

In `bank` and `hybrid`, the image counts twice in the embedding part when the query asks for a colour. A query asks
for a colour when it has a colour filter or a phrase read as a shade.

## Where the data comes from

The scripts in `offline/` made the files in `ranking_data/`. They do not run at search time. Without `--execute`,
each script prints its plan and an upper cost estimate. Their call logs in `search_ui/data/` make a rerun pay only for
what is missing.

| File in `ranking_data/` | Made by | Cost |
| --- | --- | --- |
| `concepts.yaml` | by hand; the newest concepts come from the candidates of `concept_candidates.py` | $0.48 |
| `concept_scores.parquet` | `score_concepts.py` (898 products) and `score_batch.py` (8,898 products, Batch API at half price); Gemini 3.5 Flash-Lite, prompt in `offline/prompts/` | $11.13 |
| `phrase_bank.jsonl` | `phrase_bank.py` | $0.74 |
| `concept_names.parquet` | `prepare.py`: embeddings of the concept names | |
| `esci_clothing_queries.csv` | 10,454 Amazon ESCI queries from the earlier proof of concept | |

To change the concepts:
1. Edit `concepts.yaml`.
2. Score the new pairs: `python search_ui/offline/score_batch.py --bucket <bucket> --execute`.
3. Relabel the bank: `python search_ui/offline/phrase_bank.py --execute`.
4. Rebuild the index: `python search_ui/prepare.py`.

## Evaluation

```sh
python search_ui/evaluation/evaluate.py run       # rankings and the pool to grade (embedding calls)
python search_ui/evaluation/judge.py --execute    # grades of the pool (paid)
python search_ui/evaluation/evaluate.py report    # nDCG@10, MRR and P@1 with bootstrap intervals
```

How the evaluation works:
- The queries are benchmark queries with a residual, with their reviewed parses, so parser errors do not count.
- Gemini grades the pooled top 10 of every ranking from 0 to 3. It is not told which ranking returned a product.
- Only the dev split is used for tuning.
- `results.ipynb` shows the results, and `concept_scores.ipynb` browses the concept scores.
- The grades cost $2.59 and are not in the repository.

Dev, 313 queries:

| Ranking | nDCG@10 | Difference from `combined` |
| --- | --- | --- |
| `combined` | 0.874 | |
| `hybrid` | 0.880 | +0.006 [−0.008, +0.020] |
| `combined_features` | 0.871 | −0.004 |
| `bank` | 0.843 | −0.031 [−0.054, −0.009] |
| `concepts` | 0.835 | −0.039 |

**These numbers are out of date.** They predate the following changes:
- the concept scores of all 22 categories (then only three categories had scores);
- the current phrase bank;
- the whole-query signal in `bank`;
- the image weight for colours.

The evaluation has to run again before a ranking is chosen.

## Open issues

- **Shades split by the parser.** For "light pink dress" the parser returns the filter `colors: Pink` and the
  residual "light". The shade rule works around this; keeping "light pink" together in the residual would be
  cleaner.
- **Choice of ranking.** It waits for the new evaluation.
