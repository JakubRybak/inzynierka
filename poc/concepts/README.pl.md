# Koncepty abstrakcyjne w sortowaniu

[English version](README.md)

Ranking `concepts` sortuje produkty według miękkiej części zapytania: okazji, stylu albo pory roku („for a wedding”,
„elegant”, „for summer”). Każdy produkt ma offline ocenę 0–10 dla każdego z 33 konceptów. Przy zapytaniu residual
z parsera dopasowujemy do konceptów i sortujemy produkty według ich ocen.

## Koncepty

[concepts.yaml](concepts.yaml): 33 koncepty z polami `id`, `name`, `type` i `added`.

| Typ | Koncepty |
| --- | --- |
| occasion | wedding guest, prom, cocktail party, party, night out, date night, office, beach, gym, music festival, funeral |
| style | casual, formal, elegant, sexy, modest, boho, vintage, flowy, cute, minimalist, streetwear, edgy, romantic, preppy, sporty |
| season | summer, winter, spring, autumn, hot weather, layering, loungewear |

Z `name` porównujemy residual, więc nazwy brzmią jak fragmenty zapytań. Koncepty nie dublują twardych cech: kolor,
skład, długość itd. obsługują filtry. Listę ułożyliśmy ręcznie na podstawie raportu z `derive_concepts.py`, który
zbiera residua z 1300 zapytań ESCI i 270 zapytań syntetycznych.

## Oceny produktów

`score_products.py` robi jedno wywołanie `gemini-3.5-flash-lite` na produkt.
- **Wejście:** nazwa, marka, opis, skład, cechy z ekstrakcji i zdjęcia z ujęć 1 i 3.
- **Wyjście:** liczba całkowita 0–10 dla każdego konceptu, wymuszona schematem odpowiedzi.
- **Ustawienia:** temperatura 0, thinking MEDIUM.

Ocena mówi, jak wysoko produkt powinien być w wynikach dla zapytania „<koncept> <kategoria>”:

| Ocena | Znaczenie |
| --- | --- |
| 0 | nie pasuje |
| 3 | raczej nie |
| 5 | neutralnie |
| 7 | dobry wynik |
| 10 | archetyp |

Prompt ([prompts/score_system.txt](prompts/score_system.txt)) ma punkty odniesienia, np. funeral: prosta czarna
sukienka midi z rękawem = 10, czarna sukienka z cekinami = 2.

Wynik to `results/concept_scores.parquet` (`product_id, concept_id, score, model, prompt_version, scored_at`):
893 produkty × 33 koncepty = 29 469 ocen.

## Indeks

`prepare.py --concepts`:
- dodaje do indeksu wyszukiwarki kolumny `concept__<id>` z ocenami;
- liczy embeddingi nazw konceptów (`gemini-embedding-2`, tekst `task: search result | query: <nazwa>`).

Serwer nie wystartuje, gdy `concepts.yaml` zmienił się od budowy indeksu.

## Wybór konceptów i sortowanie

1. Parser zwraca kategorię, filtry i residual, czyli część zapytania, której nie dało się zamienić na filtry
   (bez nazwy ubrania).
2. Embedding residualu w tym samym formacie co nazwy konceptów i podobieństwo kosinusowe z każdym konceptem.
3. Wybór: koncepty z podobieństwem ≥ 0,72, najwyżej 3 najbardziej podobne.
4. Wagi: `softmax(podobieństwo / 0,1)` po wybranych. Różnica podobieństw o 0,1 daje ok. 2,7 razy większą wagę.
5. Wynik produktu: suma (waga × ocena / 10). Sortowanie malejąco, remisy według rankingu `combined`.

Ranking wraca do `combined`, gdy:
- residual jest pusty;
- kategoria nie ma ocen;
- żaden koncept nie ma podobieństwa ≥ 0,72. Wtedy zapytanie trafia do `data/misses.jsonl`.

Embedding residualu jest liczony przy każdym zapytaniu, bez cache, równolegle z embeddingami do `combined`.

Przykład dla „romantic dress for a date night” (residual `romantic for a date night`):

| Koncept | Podobieństwo | Wybrany | Waga |
| --- | ---: | --- | ---: |
| date night | 0,908 | tak | 0,51 |
| romantic | 0,864 | tak | 0,33 |
| night out | 0,796 | tak | 0,17 |
| sexy | 0,740 | nie (limit 3) | – |

Sukienka z ocenami date night 8, romantic 9, night out 6 dostaje 0,51·0,8 + 0,33·0,9 + 0,17·0,6 ≈ 0,80.

Próg podobieństwa wynosi 0,72 (`--concept-threshold`).

## Strona

- Ranking `concepts` w przełączniku.
- Pod odczytem parsera:
  - residual;
  - wybrane koncepty z podobieństwem i wagą;
  - lista podobieństw do wszystkich konceptów (wybrane na fioletowo, przerywana linia na progu).
- Na kartach wyników oceny wybranych konceptów („wedding guest 9/10”), w panelu produktu wszystkie jego oceny.

## Uruchomienie

Bez `--execute` skrypty nie wywołują API; pokazują tylko liczbę wywołań i szacunek kosztu.

```sh
# indeks i serwer
python poc/search_ui/prepare.py --features poc/feature_extraction/results/products.parquet --status ready --concepts
python poc/search_ui/server.py --parser llm --ranking concepts

# oceny (tylko brakujące pary produkt-koncept)
python poc/concepts/score_products.py --execute --review

# próg
python poc/concepts/check_threshold.py --execute

# raport residuów do układania listy konceptów
python poc/concepts/derive_concepts.py select
python poc/concepts/derive_concepts.py synthesize --execute
python poc/concepts/derive_concepts.py parse --execute
python poc/concepts/derive_concepts.py report --execute
```

| Opcja serwera | Domyślnie | Znaczenie |
| --- | --- | --- |
| `--concept-threshold` | `0.72` | minimalne podobieństwo residual–koncept |
| `--concept-k` | `3` | najwyżej tyle konceptów |
| `--concept-temperature` | `0.1` | temperatura softmaksu wag |
| `--concept-norm` | `raw` | `raw`: ocena / 10; `percentile`: percentyl oceny w kategorii |
| `--concept-alpha` | brak | `alpha · koncepty + (1 − alpha) · combined` zamiast samych konceptów |

## Pliki

| Plik | Rola |
| --- | --- |
| `poc/concepts/concepts.yaml` | lista konceptów |
| `poc/concepts/derive_concepts.py` | raport residuów z zapytań |
| `poc/concepts/score_products.py`, `prompts/` | oceny produktów |
| `poc/concepts/results/concept_scores.parquet` | oceny |
| `poc/concepts/check_threshold.py`, `threshold_cases.yaml` | dobór progu |
| `poc/concepts/data/` | logi, raporty, `misses.jsonl` (w .gitignore) |
| `poc/search_ui/concepts.py` | wybór konceptów, wagi, wynik produktu |
| `poc/search_ui/prepare.py`, `server.py`, `static/index.html` | indeks, ranking, strona |

Koszt ocen 893 produktów: 2,66 USD. Każde zapytanie w rankingu `concepts` to dodatkowo jeden embedding residualu.
