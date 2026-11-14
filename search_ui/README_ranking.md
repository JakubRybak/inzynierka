# Ranking

The ranking orders the products that passed the filters; it never adds or removes any. The default ranking runs no
generative model at search time. It uses five kinds of signals:
- **embeddings** (`gemini-embedding-2`, 3072 dims): the query, embedded at search time, compared with the
  description, main image and feature text of each product, embedded in advance;
- **concept scores**: a score from 0 to 10 of every product for each of 37 occasions, styles and season needs, given
  offline by Gemini;
- **product colours**: one to three colours of every product with their share, given offline by Gemini;
- **product details**: the details of every product (lace, sequins, cable knit, a skull graphic) with their extent,
  given offline by Gemini;
- **the phrase bank**: 2,893 residual phrases, labelled offline with what they ask for.

This is the state of 2026-11-13. The default ranking is `hybrid`; the other rankings stay available in the page.

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
| `hybrid` (default) | `combined_features`, plus concept, colour and detail scores and minus negations, picked with the phrase bank |
| `sentences` (option) | the query and its phrases compared with single sentences of the description, with fitted weights |
| `sentences_jev`, `hybrid_jev` (options) | Jev 1.14 regrades the first 30 of `sentences` or `hybrid` |
| `hybrid_jev_vision` (option, slow) | the same as `hybrid_jev`, with the main photo |

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

Gemini listed the details of every product from its name, description and two photos (the 1024 px front photo and
the original back photo), up to eight, each with an extent: all-over (a lace dress), part (a lace panel) or small (a
lace trim), and the evidence: description, photo or both (`ranking_data/product_details.parquet`). The prompt names
the kinds of details to look for in every category: the look of the fabric (denim, leather, velvet, …, also when the
whole product is made of it), surface and texture, decoration, shape and construction, prints and graphics (always
named by their subject: "skull embroidery"), wear and wash. It leaves out what the extracted features already record
(colour, length, fit, sleeves, neckline, closure), and asks to use a list of about 150 common names; every name is
then put in one form (singular, no hyphens). 97% of the products have at least one detail; their names form a
dictionary of 547 names.

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
| `product_details.parquet` | `product_details.py` (Batch API); Gemini 3.5 Flash-Lite with the product name, description and two photos; relabelled on 2026-11-14 | $3.99 + $5.53 |
| `color_names.parquet` | `product_colors.py`: the colour names of the products; Gemini left out names that are not colours ("leopard print", "grey knit") | $0.01 |
| `concept_names.parquet` | `prepare.py`: embeddings of the concept names | |
| `sentence_weights.json` | the weights of `sentences`, fitted on the judge's grades of the dev queries | |
| `esci_clothing_queries.csv` | 10,454 Amazon ESCI queries from the earlier proof of concept | |

To change the concepts:
1. Edit `concepts.yaml`.
2. Score the new pairs: `python search_ui/offline/score_batch.py --bucket <bucket> --execute`.
3. Relabel the bank: `python search_ui/offline/phrase_bank.py --execute`.
4. Rebuild the index: `python search_ui/prepare.py`.

`prepare.py` writes the sentence embeddings of `sentences` to `data/sentence_embeddings.npz` (about $0.06).

## Open issues

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
  "lacing", "buckle" also reaches "belt", at a lower weight. The front photo is enlarged by an upscaling
  model that can draw textures, so the prompt takes fine textures from the description.
- **1024 px photos.** The front photos enlarged to 1024 px (`images_enhanced/`) were embedded too
  (`offline/image_embeddings.py`, `embeddings/image_enhanced.parquet` of the pilot, $1.14). On the dev queries they
  left nDCG@10 the same but lowered MRR and P@1 (`combined`: P@1 −0.047 [−0.081, −0.016]), so the rankings use the
  original photo embeddings; `server.py --enhanced-images` switches to them.
