# Ranking

The ranking orders the products that passed the filters; it never adds or removes any. It uses five kinds of signals:
- **embeddings** (`gemini-embedding-2`, 3072 dims): the query, embedded at search time, compared with the
  description, main image and feature text of each product, embedded in advance;
- **concept scores**: a score from 0 to 10 of every product for each of 37 occasions, styles and season needs, given
  offline by Gemini;
- **product colours**: one to three colours of every product with their share, given offline by Gemini;
- **product details**: the details of every product (lace, sequins, cable knit, a skull graphic) with their extent,
  given offline by Gemini;
- **the phrase bank**: 7,493 residual phrases, labelled offline with what they ask for.

The default ranking adds a second stage: Jev 1.14 regrades the first 30 products from their text and main photo.
This is the state of 2026-11-17.

## Rankings

The page offers these rankings:

| Ranking | Score |
| --- | --- |
| `hybrid_jev_vision` (default) | the Jev second stage on `hybrid` |
| `hybrid` | `combined_features`, plus concept, colour and detail scores and minus negations, picked with the phrase bank |
| `sentences_jev_vision` | the Jev second stage on `sentences`: the query and its phrases compared with single sentences of the description (a phrase the bank knows by its English version), with fitted weights |

`combined_features` is the mean of the z-scores of the similarity of the query to the description, the image and the
feature text, such as "Dresses. For women. Black. 100% linen. Midi length.". The rankings the evaluation compares
them with (`combined`, `text`, `image`, `concepts` and `bank`) are in
[experiments/ranking/baselines.py](../experiments/ranking/baselines.py).

**Jev second stage.** Jev 1.14 (`typesafe/jev-1.14`, the decisions API of OpenRouter) grades each of the first 30
products from 0 (wrong) to 3 (matches everything the query asks for), from its text and its main photo at 384 px.
The new order is the expected grade plus 0.25 × the z-score of the first-stage score; the products after the first 30
keep their order. It takes about 0.7 s and $0.001 per search. When Jev fails, the page shows the first-stage order
with a warning.

## Concepts

`ranking_data/concepts.yaml` lists the concepts, each with a description:
- 12 occasions (wedding guest, office, funeral, christmas, …);
- 16 styles (elegant, boho, goth and punk, …);
- 9 season and comfort needs (winter, rainy weather, cozy, …).

Gemini scored every product for every concept from its text and two images. The prompt asks how high the product
deserves to appear in a search for "<concept> <category>". It also says that usually fewer than one product in five
of a category deserves 7 or more. The scores therefore rank products within their category.

A residual phrase gets its concepts from the phrase bank (see Phrase bank).

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
a name, so "graphic print" reaches about 100 graphic prints named by their subject (skull, bunny, star, …) and
"pockets" reaches 9 kinds of pockets (patch, cargo, welt, chest, …). Each name weighs by its closeness: 1 for the most similar name, 0.5 at 0.82. A negated
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

The bank also has the Polish forms of every detail name and colour name, and of light and dark basic colours, with
and without diacritics ("z haftem", "haftowana", "haftu"; "jasnoczerwona", "w kolorze pudrowego różu"). Gemini
wrote the forms; their labels come from the English name, so "haftu" is embroidery ("bez haftu" excludes it, see
Negation below) and "jasnoczerwona" takes the colour of light red. The parser keeps the residual in the language of the query, and a Polish word in another
form ("haftu") is often too far from every English name to be matched.

At search time a residual phrase takes the labels of the first match:
1. the same phrase in the bank;
2. its nearest bank phrase, when the cosine is at least 0.86. The neighbour gives the kind and the concepts; a
   shade still looks for its own colour name and takes only the neighbour's lightness when none is close, and a
   detail phrase whose own text reaches no detail name takes the neighbour's ("z haftami" → "z haftem" → embroidery);
3. the most similar colour name, when the cosine is at least 0.80 (see Colours);
4. detail names, when the cosine is at least 0.80 (see Details);
5. the concept with the most similar name, when the cosine is at least 0.80.

A phrase with no match is unknown. Two rules apply first:
- **Shades.** A lightness word right before a colour of the query is a shade, for example "light" in "light pink
  dress".
- **Negation.** An unknown phrase is negated when it starts with a negation word followed by at most three words, for
  example "without pockets". The rest of it is matched as a phrase of its own and counts with a minus: "bez koronki"
  → "koronki" → lace. The bank keeps no negated forms of its own, so the negation never depends on a neighbour; a
  phrase the bank knows keeps its labels ("no me importa" is a slogan, not a negation).

## `hybrid`

```
hybrid = combined_features + 0.5 × z(concept scores of each occasion, style or season phrase)
                           + 1.0 × z(colour closeness of each shade phrase)
                           + 0.25 × z(details of each detail phrase)
                           − 1.0 × z(what each negated phrase excludes)
```

Other phrases add nothing, because the whole query already covers them. An embedding does not read a negation:
"sukienka bez pufiastych rękawów" is close to dresses with puff sleeves. So when the residual has a negated phrase,
`combined_features` compares the query without it ("sukienka"), and so do the whole-query parts of `sentences`. The
query without each span that starts with a negation word is embedded while the parser parses. The evaluation still
compares the full query (3 of the dev queries have a negated phrase). The page shows every part of the score: in
the side panel how much each part moves the ranking (its spread over the candidates), on every result a bar of its
parts, and in the product view their values.

In `hybrid`, the image counts twice in the embedding part when the query asks for a colour. A query asks
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
- **Term weights.** The detail weight 0.25 was chosen among 0.25, 0.5 and 1.0 on the dev queries of the benchmark,
  with the details of 2026-11-13; a larger one let a wrong match ("two buttons" as decorative buttons, "denim" before
  denim became a detail of every denim product) push the right products down. The colour weight 1.0 is not
  measured.
- **Detail names.** Closeness cannot tell every neighbour from the same detail: "lace" also reaches "lace up",
  "buckle" also reaches "belt" and "strap", at a lower weight. The front photo is enlarged by an upscaling
  model that can draw textures, so the prompt takes fine textures from the description.
- **1024 px photos.** The front photos enlarged to 1024 px (`images_enhanced/`) were embedded too
  (`offline/image_embeddings.py`, `embeddings/image_enhanced.parquet` of the pilot, $1.14). On the dev queries they
  left nDCG@10 the same but lowered MRR and P@1 (`combined`: P@1 −0.047 [−0.081, −0.016]). The rankings use them
  anyway; `server.py --original-images` switches back to the original photo embeddings.
