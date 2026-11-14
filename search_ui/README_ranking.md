# Ranking

The ranking orders the products that passed the filters; it never adds or removes any. No generative model runs at
search time. The ranking uses six kinds of signals:
- **embeddings** (`gemini-embedding-2`, 3072 dims): the query, embedded at search time, compared with the
  description, main image and feature text of each product, embedded in advance;
- **concept scores**: a score from 0 to 10 of every product for each of 37 occasions, styles and season needs, given
  offline by Gemini;
- **product colours**: one to three colours of every product with their share, given offline by Gemini;
- **product details**: the details of every product (lace, sequins, cable knit, a skull graphic) with their extent,
  given offline by Gemini;
- **the phrase bank**: 2,893 residual phrases, labelled offline with what they ask for;
- **product sentences**: the name and every sentence of the description of each product, embedded in advance one
  by one.

This is the state of 2026-11-13. The default ranking is `sentences`; the other rankings stay available in the page.

## Rankings

| Ranking | Score |
| --- | --- |
| `text` | cosine of the query and the description |
| `image` | cosine of the query and the main image |
| `combined` | mean of the z-scores of `text` and `image` |
| `features` | cosine of the query and the feature text, e.g. "Dresses. For women. Black. 100% linen. Midi length." |
| `combined_features` | mean of the z-scores of description, image and feature text |
| `concepts` | the scores of the concepts that the residual phrases name |
| `bank` | one signal per residual phrase, picked with the phrase bank |
| `hybrid` | `combined_features`, plus concept, colour and detail scores and minus negations, picked with the phrase bank |
| `sentences` (default) | description, best sentences, image and feature text for the whole query, plus the concept scores and the best sentence of every phrase; fitted weights |

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

## Colours

Gemini gave every product its colours from the product name and the main photo: one to three colours, each with a
name ("dusty pink", "burgundy", "light wash blue"), a basic family, a hex value and a share of the product
(`ranking_data/product_colors.parquet`). Their names form the colour dictionary (`ranking_data/color_names.parquet`):
220 colour names, each with the typical hex of the products that got it.

A shade phrase gets a target colour:
- a lightness word followed by a colour in the query ("light pink") takes the colour of that pair;
- a bank shade phrase takes its own hex ("brudny róż" → `#C57B8C`), and a bare "dark" or "jasny" only a direction;
- any other phrase takes the most similar colour name of the dictionary, when the cosine is at least 0.80, so "wine
  red", "bordowy" or "ciemny granat" work without being in the bank;
- a phrase that asks only for lightness ("pale", "pastel", "bright colours") is about as close to colour names of many
  hues, so when the names within 0.02 of the most similar one spread over the hue circle, and are not just greys, it
  takes only the direction of their mean lightness: lighter or darker shades first. Two general entries, "light
  colour" and "dark colour", do the same for a phrase that is at most 0.03 less similar to one of them than to the
  nearest colour name ("light coloured", "w jasnym kolorze", "dark coloured").

A candidate scores by how close its colours are to the target in CIELAB, weighted by their share: a burgundy dress
beats a black one with a burgundy belt.

## Details

Gemini listed the details of every product from its name, description and two photos (front and back), up to eight,
each with an extent: all-over (a lace dress), part (a lace panel) or small (a lace trim)
(`ranking_data/product_details.parquet`). The prompt names the kinds of details to look for in every category:
surface and texture, decoration, shape and construction, prints and graphics, wear and wash. It leaves out what the
extracted features already record (colour, length, fit, sleeves, neckline, closure). 96% of the products have at
least one detail; their names form a dictionary of 1,176 names.

A phrase gets detail names when the bank reads it as a detail or as "other", or does not know it. It takes the most
similar name, when the cosine is at least 0.80, and with it every name whose cosine to that name is at least 0.82.
Gemini names one detail in several ways and the similarity between two names is steadier than between a phrase and
a name, so "with graphic" → graphic, bunny graphic, skull graphic and about 160 more, "dress with pockets" → pockets
and 26 other kinds of pockets. Each name weighs by its closeness: 1 for the most similar name, 0.5 at 0.82. A negated
phrase is matched without its negation ("without pockets" → pockets). A candidate scores by its best detail among
these names: 1 for all-over, 0.7 for part, 0.4 for small, times the weight of the name.

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
3. the most similar colour name, when the cosine is at least 0.80 (see Colours);
4. detail names, when the cosine is at least 0.80 (see Details);
5. the concept with the most similar name, when the cosine is at least 0.80.

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
| shade with a target colour | the closeness of the candidate's colours to it |
| phrase with detail names | the candidate's details |
| shade without one | its text signals, with the image counted twice |
| negated | its signal, inverted |
| size or audience ("petite") | none: the catalog has no such information |
| anything else (a print, a theme, an unknown phrase) | the `combined` similarity of the whole query |

The text signals are TF-IDF over the name and description, and the similarity of the phrase to the description and
image embeddings. The columns are combined with a geometric mean, which acts as a soft AND. `combined` breaks ties.

## `hybrid`

```
hybrid = combined_features + 0.5 × z(concept scores of each occasion, style or season phrase)
                           + 1.0 × z(colour closeness of each shade phrase)
                           + 0.25 × z(details of each detail phrase)
                           − 1.0 × z(what each negated phrase excludes)
```

Other phrases add nothing, because the whole query already covers them. The page shows every part of the score: in
the side panel how much each part moves the ranking (its spread over the candidates), on every result a bar of its
parts, and in the product view their values.

In `bank` and `hybrid`, the image counts twice in the embedding part when the query asks for a colour. A query asks
for a colour when it has a colour filter or a phrase read as a shade.

## Sentences

SSENSE descriptions are lists of short sentences, each about one thing: "Short sleeve cotton jersey t-shirt in
'blush' pink.", "Two-button placket at front.", "Velcro tabs at cuffs.". The embedding of a whole description blurs
them. `prepare.py` therefore embeds the name and every sentence of every product on its own, verbatim like the
descriptions (`core/sentences.py`). Most sentences repeat across products ("Tonal stitching." occurs 9,147 times), so
the pilot has 30,977 unique ones. HTML tags left in some descriptions (`<br>`) are dropped first. Only the first 768
dimensions of the embeddings are kept; on the dev queries the ranking is as good with 768 dimensions as with all
3,072.

Two scores come from them:
- **the whole query**: the mean similarity of the query to the two most similar sentences of a candidate;
- **a residual phrase**: the similarity of the phrase to the candidate's best sentence, counted only as far as it is
  above the phrase's median similarity to all sentences. "with two buttons" is 0.68 to "Two-button placket." and 0.41
  to a typical sentence, so a polo with that sentence gets 0.27, while the median polo, whose best sentence is about
  other buttons, gets 0.17. A phrase that no sentence speaks about, such as "for work", is about as far from every
  sentence: all coats get 0.11 give or take 0.01, which hardly changes their order. This replaces a threshold.

## `sentences`

```
sentences = 1.00 × z(description) + 1.40 × z(best sentences) + 2.52 × z(image) + 0.26 × z(features)
          + 2.94 × z(concept scores of each occasion, style or season phrase)
          + 43.0 × (best sentence of each phrase, above the phrase's median)
```

- The first four parts compare the whole query with the candidate; `z` is the z-score within the candidates.
- A phrase is read with the phrase bank only for three things: its concepts when it is an occasion, style or season
  (or names a concept), whether it is negated, and whether it is a size or audience phrase, which is skipped. The
  colour and detail routes of `hybrid` are not used: a shade or a detail is found in the sentences, where the
  description states it. A negated phrase counts with a minus in both of its terms.
- A phrase of the bank uses the embedding stored with the bank, so only the spans of the query that the bank does
  not know are embedded while the parser parses.
- **The weights are fitted**, not set by hand (`experiments/ranking/learn.py`, written to
  `ranking_data/sentence_weights.json`): a pairwise logistic regression on the judge's grades of the dev queries of
  the benchmark. Of two graded products of a query, the one with the higher grade should score higher. The last
  weight is large because its part is a raw similarity difference (0 to about 0.4), not a z-score.

The measurements are in `experiments/ranking/RESULTS_2026-11-14.md`. With weights fitted without the query being
ranked, `sentences` reaches nDCG@10 0.855 on the dev queries against 0.837 for `hybrid` (+0.018, 95% interval
+0.005 to +0.031), with the same MRR and P@1; a second judge from another model family gives +0.022. It is weaker
than `hybrid` on occasion phrases (0.859 against 0.879).

## Where the data comes from

The scripts in `offline/` made the files in `ranking_data/`. They do not run at search time. Without `--execute`,
each script prints its plan and an upper cost estimate. Their call logs in `search_ui/data/` make a rerun pay only for
what is missing.

| File in `ranking_data/` | Made by | Cost |
| --- | --- | --- |
| `concepts.yaml` | by hand; the newest concepts come from the candidates of `concept_candidates.py` | $0.48 |
| `concept_scores.parquet` | `score_concepts.py` (898 products) and `score_batch.py` (8,898 products, Batch API at half price); Gemini 3.5 Flash-Lite, prompt in `offline/prompts/` | $11.13 |
| `phrase_bank.jsonl` | `phrase_bank.py`, with the colours of the shade phrases | $0.75 |
| `product_colors.parquet` | `product_colors.py` (Batch API); Gemini 3.5 Flash-Lite with the product name and main photo | $2.51 |
| `product_details.parquet` | `product_details.py` (Batch API); Gemini 3.5 Flash-Lite with the product name, description and two photos | $3.99 |
| `color_names.parquet` | `product_colors.py`: the colour names of the products; Gemini left out names that are not colours ("leopard print", "grey knit") | $0.01 |
| `concept_names.parquet` | `prepare.py`: embeddings of the concept names | |
| `sentence_weights.json` | `experiments/ranking/learn.py --write`: the weights of `sentences`, fitted on the judge's grades of the dev queries | |
| `esci_clothing_queries.csv` | 10,454 Amazon ESCI queries from the earlier proof of concept | |

To change the concepts:
1. Edit `concepts.yaml`.
2. Score the new pairs: `python search_ui/offline/score_batch.py --bucket <bucket> --execute`.
3. Relabel the bank: `python search_ui/offline/phrase_bank.py --execute`.
4. Rebuild the index: `python search_ui/prepare.py`.

The sentence embeddings are not in `ranking_data/`: `prepare.py` writes them to `data/sentence_embeddings.npz`
(68 MB, about 31,000 embedding calls and $0.06 for the pilot).

## Open issues

- **Fitted weights.** The weights of `sentences` come from 313 dev queries and one judge. They vary between the five
  folds of the cross-validation (for example the image 2.2 to 3.2 times the description), and the test split of the
  benchmark has not been used to confirm them. Refit them with `learn.py` when the signals or the grades change.
- **Phrases that are not spans of the query.** A residual phrase that the bank does not know and that is not a span
  of one to three words of the query (4% of the dev queries) is embedded after the parsing, which costs one more
  round trip.
- **Negations and excluded colours.** "no red" is a filter on the main colours; a navy hoodie with a red logo
  passes it. Only about four dev queries are negated, so the negation terms are not measured.

- **Shades split by the parser.** For "light pink dress" the parser returns the filter `colors: Pink` and the
  residual "light". The shade rule works around this; keeping "light pink" together in the residual would be
  cleaner.
- **"light" alone.** Without a colour after it, "light" is read as lightweight ("light coat"), as the bank says.
- **Term weights.** The detail weight 0.25 was chosen among 0.25, 0.5 and 1.0 on the dev queries of the benchmark;
  a larger one lets a wrong match ("denim" as a detail, "two buttons" as decorative buttons) push the right products
  down. The colour weight 1.0 is not measured.
- **Detail names.** Closeness cannot tell every neighbour from the same detail: "lace" also reaches "lace-up" and
  "lacing", "buckle" also reaches "belt", at a lower weight. The photos are small, so most details come
  from the description; the prompt says so and should change with better photos.
