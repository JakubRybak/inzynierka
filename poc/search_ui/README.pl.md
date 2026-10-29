# Search UI

[English version](README.md)

Lokalne demo paska wyszukiwania w przeglądarce. Zapytanie przechodzi przez parser zapytań oparty na LLM, produkty są
filtrowane po wyekstrahowanych cechach, a pozostałe sortowane według podobieństwa embeddingów. Strona pokazuje, jak
parser zrozumiał zapytanie, pozwala ręcznie poprawić filtry i pokazuje, ile trwał każdy etap.

Demo korzysta z wyników pozostałych części proof of concept i samo niczego nie liczy offline:

| Dane | Skąd pochodzą |
| --- | --- |
| metadane i zdjęcia produktów | `data/processed/fashiongen/` (`scripts/build_fashiongen_dataset.py`) |
| cechy produktów | `poc/feature_extraction/results/products.parquet` (ekstrakcja cech przez LLM) |
| embeddingi produktów | `poc/feature_extraction/embeddings/gemini_embedding_2/` (opis i główne zdjęcie, 3072 wymiary) |
| parser zapytań | `poc/scripts/query_parser.py` z promptami i schematami w `poc/query_parsing/` |

## Szybki start

Z katalogu głównego repozytorium, Pythonem z zainstalowanymi wymaganiami (poniżej):

```sh
python poc/search_ui/prepare.py --features poc/feature_extraction/results/products.parquet --status ready
python poc/search_ui/server.py --parser llm
```

Strona otwiera się pod http://127.0.0.1:8000. `prepare.py` trzeba uruchomić ponownie tylko wtedy, gdy zmieni się
plik z cechami.

**Wymagania**

- Pakiety Pythona: `pandas`, `numpy`, `pyarrow`, `pyyaml`, `google-genai`, `google-auth`, `requests`.
- Dostęp do Vertex AI w Google Cloud – dla parsera, embeddingów zapytań i HyDE:
  ```sh
  gcloud auth application-default login
  export GOOGLE_CLOUD_PROJECT=<id projektu>
  export GOOGLE_CLOUD_LOCATION=global
  export GOOGLE_GENAI_USE_VERTEXAI=true
  ```
- Bez parsera LLM: `python poc/search_ui/server.py --parser mock`. Mock odpowiada na przykładowe zapytania
  z `parser_mock.yaml`, a dla pozostałych dopasowuje słowa zapytania do wartości z indeksu. Embeddingi zapytań
  nadal wymagają Vertex AI.

## Korzystanie ze strony

- **Pasek wyszukiwania i przykłady** – wpisz zapytanie (po angielsku albo po polsku) albo kliknij jeden
  z przykładów, pogrupowanych według kategorii.
- **Odczyt parsera** (pod paskiem) – warunki wyciągnięte przez parser, każdy w osobnej linii: kategoria
  w obramowaniu, uwzględnione wartości na zielono, wykluczone (AND NOT) na czerwono.
- **Filtry** (przycisk nad wynikami, otwiera panel po prawej) – wszystkie cechy i wartości wybranej kategorii, zgodnie ze schematami odpowiedzi
  parsera, z liczbą produktów. Po wyszukaniu pokazuje to, co wybrał parser. Kliknięcie wartości przełącza
  *uwzględnij → wyklucz → nic*; cechy wielowartościowe (`colors`, `main_composition`, `dress_type`) mają też tryb:
  *any of*, *all of* albo *only*. Każda zmiana od razu wyszukuje ponownie z tymi filtrami, bez parsera.
  Filtr ceny obsługuje `<`, `<=`, `>`, `>=` i `=`; drugi warunek pozwala ustawić przedział. Waluty nie są przeliczane. Produkty z ceną zero lub nieznaną nie pasują do aktywnego filtra ceny.
  *Reset to parser* przywraca filtry parsera. Gdy parser nie znajdzie kategorii, można ją wybrać tutaj.
- **Ranking** – `combined` (tekst + zdjęcie), `text`, `image`, `hyde` albo `concepts` (opis niżej). Pod odczytem
  parsera: residual, a przy `concepts` wybrane koncepty i podobieństwo residualu do każdego konceptu
  (przewijane; wybrane na fioletowo, przerywana linia na progu).
- **Czasy etapów** (po lewej, pod odczytem parsera) – parsowanie (z dwoma krokami LLM), filtrowanie i sortowanie
  na jednej osi czasu.
- **Wyniki** (po prawej, wszystkie, przewijane) – zdjęcie, nazwa, marka, cena i cechy, które pasują do zapytania.
  Kliknięcie produktu pokazuje wszystkie jego zdjęcia, opis i wszystkie cechy, z podświetlonymi dopasowanymi.
- Link w rodzaju `/?q=black+midi+dress&ranking=text` od razu otwiera wyszukiwanie.

## Jak to działa

1. **Parsowanie** (`parser_adapter.py`). Parser zwraca `category`, `filters` i `residual`
   (`QueryParser.to_dict()`). Kategoria `null` oznacza zapytanie spoza katalogu albo zbyt ogólne – wtedy
   wyszukiwanie się nie odbywa. W przeciwnym razie filtry są zamieniane na drzewo warunków (`conditions.py`):

   | Operator parsera | Warunek |
   | --- | --- |
   | `in`, `contains_any` | produkt ma którąkolwiek z wartości |
   | `not_in`, `contains_none` | produkt nie ma żadnej z wartości |
   | `contains_all` | produkt ma wszystkie wartości |
   | `equals_set` | produkt ma dokładnie te wartości |
   | `lt`, `lte`, `gt`, `gte`, `eq` | porównanie liczbowej ceny `msrpUSD`; filtr ceny używa `value` zamiast `values` |

   ```json
   {"op": "and", "args": [
     {"feature": "category", "values": ["T-shirts"]},
     {"feature": "colors", "values": ["Black", "White"], "match": "all"},
     {"op": "not", "arg": {"feature": "main_composition", "values": ["Polyester"]}}
   ]}
   ```

2. **Filtrowanie** (`conditions.py`). Drzewo jest sprawdzane na każdym produkcie z indeksu. Wartości cech traktujemy
   jak zbiory; `main_composition` to zbiór materiałów w składzie, niezależnie od ich udziału. Brakująca cecha nigdy
   nie pasuje, więc produkt bez niej odpada przy filtrze pozytywnym i zostaje przy negatywnym. `brand` jest
   porównywany z metadanymi produktu. Filtr ceny porównuje dodatnią, skończoną wartość `msrpUSD`; zero, brak lub niepoprawna cena nie pasują. Cechy albo wartości, których nie ma w indeksie, są pomijane z ostrzeżeniem.
   Gdy żaden produkt nie spełnia wszystkich warunków, wynik jest pusty.

3. **Sortowanie** (`server.py`). Przy każdym żądaniu liczony jest embedding całego zapytania
   (`gemini-embedding-2`, 3072 wymiary) i porównywany (cosinus) z gotowymi embeddingami kandydatów:
   - `text` – z opisami produktów; zapytanie wysyłane jako `task: search result | query: <zapytanie>`;
   - `image` – z głównymi zdjęciami produktów; wysyłany sam tekst;
   - `combined` – średnia z-score obu podobieństw, liczonych na kandydatach;
   - `hyde` – LLM (`gemini-3.5-flash-lite`) pisze opis idealnego produktu, a jego embedding jest porównywany
     z opisami produktów;
   - `concepts` – tylko z indeksem zbudowanym przez `prepare.py --concepts` (`concepts.py`, opis
     w `poc/concepts/README.pl.md`). Embedding residualu z parsera, w tym samym formacie co nazwy konceptów, jest
     porównywany z nimi; koncepty z podobieństwem ≥ `--concept-threshold`, najwyżej `--concept-k`, dostają wagi
     `softmax(podobieństwo / --concept-temperature)`. Wynik produktu to ważona suma jego ocen 0–10, podzielonych
     przez 10 (`--concept-norm raw`) albo jako percentyle w obrębie kategorii (`percentile`), a remisy rozstrzyga
     `combined`. Przy pustym residualu, kategorii bez ocen albo braku
     konceptu powyżej progu sortowanie to `combined`; ostatni przypadek jest dopisywany do
     `poc/concepts/data/misses.jsonl` (log, wyszukiwarka go nie czyta). Embedding residualu liczy się równolegle
     z embeddingami zapytania.

Nic nie jest cache'owane: powtórzone zapytanie znów wywołuje parser i API embeddingów, a każda odpowiedź HTTP ma
nagłówek `Cache-Control: no-store`. Przy starcie wczytywane są tylko indeks, embeddingi produktów i klienci API.

## Opcje serwera

| Opcja | Domyślnie | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `mock` albo `modul:funkcja` zwracająca wynik w formacie parsera |
| `--ranking` | `combined` | domyślny ranking: `combined`, `text`, `image`, `hyde`, `concepts` |
| `--hyde-model` | `gemini-3.5-flash-lite` | model piszący opisy HyDE |
| `--port` | `8000` | |
| `--data` | `poc/search_ui/data` | indeks zbudowany przez `prepare.py` |
| `--concept-threshold` | `0.72` | minimalne podobieństwo kosinusowe residual–koncept (zob. krok E w `poc/concepts/README.pl.md`) |
| `--concept-k` | `3` | najwyżej tyle konceptów na zapytanie |
| `--concept-temperature` | `0.1` | temperatura softmaksu wag konceptów |
| `--concept-norm` | `raw` | oceny konceptów podzielone przez 10 albo `percentile` w obrębie kategorii |
| `--concept-alpha` | | `alpha · koncepty + (1 − alpha) · combined` na z-score zamiast samych konceptów |
| `--no-warmup` | | bez próbnego wywołania embeddingu przy starcie |
| `--no-browser` | | nie otwiera strony |

`prepare.py` przyjmuje `--features` (`.parquet`, `.jsonl` albo `.csv`, jeden lub kilka plików), `--status`
(tylko produkty z tymi statusami, np. `ready`), `--limit`, `--dataset`, `--embeddings` i `--output`. Kończy się
błędem, jeśli embeddingi nie obejmują wszystkich produktów z indeksu. `--concepts` dodaje kolumnę `concept__<id>`
na każdy koncept z `poc/concepts/results/concept_scores.parquet` i zapisuje embeddingi nazw konceptów (jedno
wywołanie na koncept, `--concept-format` `query` (domyślnie) albo `plain`) w `data/concepts.parquet`. Kategorie bez ocen są
dozwolone; brak oceny w ocenionej kategorii przerywa budowanie. Hash `concepts.yaml` trafia do `meta.json`, a serwer
nie wystartuje, jeśli plik się od tego czasu zmienił.

## HTTP API

| Endpoint | |
| --- | --- |
| `GET /api/search?q=…&ranking=…` | cały pipeline |
| `GET /api/search?q=…&filters=<json>` | bez parsera; `filters` to `{"category", "filters", "residual"}` w formacie parsera |
| `GET /api/info` | nazwa parsera, ustawienia domyślne, kategorie, wartości panelu filtrów, przykładowe zapytania |
| `GET /api/product?id=…` | szczegóły produktu |
| `GET /images/<image_path>` | zdjęcie produktu |

Odpowiedź wyszukiwania zawiera `parsed` (kategoria, filtry, residual i ich źródło), `tree`, `condition`,
`warnings`, `results` (z `score`, `features`, dopasowanymi cechami `matched` i ocenami wybranych konceptów
`concepts`), `hyde`, `concepts` (residual, wybrane koncepty z podobieństwem i wagą, podobieństwo do każdego konceptu,
powód fallbacku), `timings` (`parsing_ms`, `filtering_ms`, `ranking_ms`, `hyde_ms`, `query_embedding_ms`, `concepts_ms`,
`total_ms`), a przy
parserze LLM także `parser_info` z czasem obu kroków parsera i szacowanym kosztem. Błędy wracają jako
`{"error": {"stage", "message"}}` razem z czasami zmierzonymi do tego momentu.

## Pliki

| Plik | |
| --- | --- |
| `prepare.py` | buduje `data/index.parquet` (w `.gitignore`) z pliku cech, metadanych i zdjęć |
| `server.py` | pipeline wyszukiwania, sortowanie i serwer HTTP |
| `conditions.py` | drzewo warunków: walidacja, ocena, dopasowane cechy |
| `parser_adapter.py` | wynik parsera → drzewo warunków, mock parsera, wczytywanie parsera |
| `llm_parser.py` | opakowanie `poc/scripts/query_parser.py` dla `--parser llm` |
| `facets.py` | wartości panelu filtrów dla kategorii, ze schematów w `poc/query_parsing/schemas` |
| `concepts.py` | oceny konceptów i embeddingi nazw w indeksie, wybór konceptów i sortowanie, log pudeł |
| `common.py` | ścieżki, wczytywanie danych, embedder zapytań, HyDE |
| `static/index.html` | strona (czytana przy każdym żądaniu, więc zmiany widać po odświeżeniu) |
| `example_queries.yaml` | przykłady pokazywane na stronie |
| `parser_mock.yaml` | odpowiedzi mocka w formacie parsera |

## Testy i sprawdzenia

```sh
python -m unittest discover -s poc/search_ui/tests   # bez wywołań API
python poc/search_ui/check_examples.py               # przykłady na indeksie, mock parsera
python poc/search_ui/check_examples.py --parser llm  # to samo z parserem LLM (ok. 0,04 $)
```
