# Koncepty abstrakcyjne w sortowaniu

[English version](README.md)

Ranking `concepts` sortuje produkty według miękkiej części zapytania: okazji, stylu albo pory roku („for a wedding”,
„elegant”, „for summer”). Każdy produkt ma offline ocenę 0–10 dla każdego z 33 konceptów. Parser zwraca residual
jako listę fraz, po jednej na wymaganie. Każdą frazę dopasowujemy do jednego konceptu i sortujemy produkty według
ocen tych konceptów.

## Koncepty

[concepts.yaml](concepts.yaml): 33 koncepty z polami `id`, `name`, `type` i `added`.

| Typ | Koncepty |
| --- | --- |
| occasion | wedding guest, prom, cocktail party, party, night out, date night, office, beach, gym, music festival, funeral |
| style | casual, formal, elegant, sexy, modest, boho, vintage, flowy, cute, minimalist, streetwear, edgy, romantic, preppy, sporty |
| season | summer, winter, spring, autumn, hot weather, layering, loungewear |

Z `name` porównujemy frazy residualu, więc nazwy brzmią jak fragmenty zapytań. Koncepty nie dublują twardych cech:
kolor, skład, długość itd. obsługują filtry. Listę ułożyliśmy ręcznie na podstawie raportu z `derive_concepts.py`,
który zbiera residua z 1300 zapytań ESCI i 270 zapytań syntetycznych.

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

1. Parser zwraca kategorię, filtry i residual jako listę fraz: to, czego nie dało się zamienić na filtry,
   bez nazwy ubrania. Na przykład „modest dress for work” → `["modest", "for work"]`.
2. Każda fraza dostaje osobny embedding, w tym samym formacie co nazwy konceptów. Liczymy jej podobieństwo
   kosinusowe z każdym konceptem.
3. Fraza bierze jeden koncept, najbardziej podobny, jeśli podobieństwo ≥ 0,72. Fraza bez takiego konceptu jest
   pomijana i trafia do `data/misses.jsonl`.
4. Wynik produktu to średnia geometryczna jego ocen / 10 dla konceptów wszystkich dopasowanych fraz. Sortowanie
   malejąco, remisy według rankingu `combined`.

Średnia geometryczna karze produkt słaby w jednej frazie: wyniki 9/9 dają 0,90, a 10/8 daje 0,89. Ocena 0 w jednej
frazie zeruje wynik.

Ranking wraca do `combined`, gdy:
- residual jest pusty;
- kategoria nie ma ocen;
- żadna fraza nie ma konceptu z podobieństwem ≥ 0,72.

Embeddingi fraz są liczone przy każdym zapytaniu, bez cache, równolegle ze sobą i z embeddingami do `combined`.

Przykład dla „romantic dress for a date night” (residual `["romantic", "for a date night"]`):

| Fraza | Najbardziej podobne koncepty | Wybrany |
| --- | --- | --- |
| romantic | romantic 1,000 · sexy 0,811 · date night 0,809 | romantic |
| for a date night | date night 0,940 · night out 0,856 · romantic 0,799 | date night |

Sukienka z ocenami romantic 9 i date night 8 dostaje √(0,9 · 0,8) ≈ 0,85.

Próg podobieństwa wynosi 0,72 (`--concept-threshold`).

## Strona

- Ranking `concepts` w przełączniku.
- Pod odczytem parsera:
  - frazy residualu;
  - przy każdej frazie wybrany koncept z podobieństwem;
  - dla każdej frazy lista podobieństw do wszystkich konceptów (wybrany na fioletowo, przerywana linia na progu).
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
```

| Opcja serwera | Domyślnie | Znaczenie |
| --- | --- | --- |
| `--concept-threshold` | `0.72` | minimalne podobieństwo fraza–koncept |
| `--concept-combine` | `geo` | jak łączyć oceny konceptów z różnych fraz: `geo` (średnia geometryczna), `mean`, `min` |
| `--concept-norm` | `raw` | `raw`: ocena / 10; `percentile`: percentyl oceny w kategorii |
| `--concept-alpha` | brak | `alpha · koncepty + (1 − alpha) · combined` zamiast samych konceptów |

## Pliki

| Plik | Rola |
| --- | --- |
| `poc/concepts/concepts.yaml` | lista konceptów |
| `poc/concepts/derive_concepts.py` | raport residuów z zapytań (zakłada residual jako jeden tekst) |
| `poc/concepts/score_products.py`, `prompts/` | oceny produktów |
| `poc/concepts/results/concept_scores.parquet` | oceny |
| `poc/concepts/check_threshold.py`, `threshold_cases.yaml` | dobór progu |
| `poc/concepts/data/` | logi, raporty, `misses.jsonl` (w .gitignore) |
| `poc/search_ui/concepts.py` | dopasowanie fraz do konceptów, wynik produktu |
| `poc/search_ui/parser_adapter.py` | residual zawsze jako lista fraz |
| `poc/search_ui/prepare.py`, `server.py`, `static/index.html` | indeks, ranking, strona |

Koszt ocen 893 produktów: 2,66 USD. Każde zapytanie w rankingu `concepts` to dodatkowo jeden embedding na frazę
residualu.
