# Wyszukiwarka – UI

[English version](README.md)

Lokalne demo wyszukiwarki na pilotażu 9 922 produktów. Zapytanie przechodzi przez parser LLM, produkty są
filtrowane po wyekstrahowanych cechach, a pozostałe sortowane według podobieństwa embeddingów. Strona pokazuje, co
zrozumiał parser, pozwala ręcznie zmienić filtry i pokazuje czas każdego etapu.

Korzysta z wyników innych części repozytorium i sama niczego nie liczy offline:

| Wejście | Skąd |
| --- | --- |
| metadane i zdjęcia produktów | `data/processed/fashiongen/` (`dataset_preparation/fashiongen/`) |
| cechy produktów | `feature_extraction/outputs/pilot_9922/products.parquet` |
| embeddingi produktów | `feature_extraction/outputs/pilot_9922/embeddings/` (opis i główne zdjęcie, 3072 wymiary, Git LFS) |
| cechy i wartości w panelu filtrów | `feature_extraction/schema/` (wszystkie 22 kategorie) |
| parser zapytań | `poc/scripts/query_parser.py` z promptami i schematami w `poc/query_parsing/` |
| wzorcowe parsowania | `query_extraction/queries/` na gałęzi `user_queries` (1 535 sprawdzonych zapytań, 22 kategorie) |

Do wyboru są dwa parsery:

- `--parser llm` – dwuetapowy parser z wcześniejszego proof of concept. Obsługuje **T-shirts, Dresses i Tank tops &
  Camisoles**. Dla innych zapytań nie zwraca kategorii, wtedy kategorię i filtry wybiera się ręcznie w panelu
  filtrów. Jego wartości cech powstały przed obecnymi schematami, więc wartość, której już nie ma, nie dopasowuje
  żadnego produktu, z ostrzeżeniem.
- `--parser benchmark` – sprawdzone parsowania z benchmarku ekstrakcji zapytań dla wszystkich 22 kategorii, bez
  wywołań API, do pracy nad rankingiem, dopóki nie ma parsera dla wszystkich kategorii. Z benchmarku odpowiadane są
  tylko zapytania z **podziału dev** i z niego pochodzą przykłady na stronie; zapytanie testowe albo każde inne trafia
  do parsera LLM. Podział jest ten sam co w ewaluacji rankingu (skrót zapytania i kategorii), więc zapytania testowe
  pozostają niewidziane podczas strojenia rankingu. Benchmark jest czytany z `query_extraction/queries/` w katalogu
  roboczym, a dopóki nie jest scalony, z `origin/user_queries`.

## Szybki start

Z katalogu głównego repozytorium, Pythonem z wymaganiami poniżej:

```sh
git lfs pull                       # embeddingi są plikami Git LFS
python search_ui/prepare.py        # produkty pilotażu ze statusem ready -> search_ui/data/
python search_ui/server.py --parser llm
```

Strona otwiera się pod http://127.0.0.1:8000. `prepare.py` trzeba uruchomić ponownie tylko po zmianie pliku cech.

**Wymagania**

- Pakiety Pythona: `pandas`, `numpy`, `pyarrow`, `pyyaml`, `google-genai`, `google-auth`, `requests`, `httpx`.
- Dostęp do Vertex AI w Google Cloud dla parsera i embeddingów zapytań:
  ```sh
  gcloud auth application-default login
  export GOOGLE_CLOUD_PROJECT=<id projektu>
  export GOOGLE_CLOUD_LOCATION=global
  export GOOGLE_GENAI_USE_VERTEXAI=true
  ```
- Bez parsera LLM: `python search_ui/server.py --parser mock`. Mock dopasowuje słowa zapytania do wartości z
  indeksu. Embeddingi zapytań nadal wymagają Vertex AI.

## Korzystanie ze strony

- **Pole wyszukiwania i przykłady** – wpisz zapytanie (po angielsku lub polsku) albo kliknij przykład; przykłady są
  pogrupowane według kategorii (z `--parser benchmark`: pięć zapytań dev na kategorię, najpierw te z residualem).
- **Odczyt parsera** (pod polem wyszukiwania) – warunki wyciągnięte przez parser, po jednym w wierszu: kategoria w
  ramce, wartości wymagane na zielono, wykluczone (AND NOT) na czerwono, a pod nimi frazy residual i źródło
  parsowania (benchmark albo parser LLM).
- **Filtry** (przycisk nad wynikami, otwiera panel po prawej) – wszystkie cechy i wartości wybranej kategorii ze
  schematów ekstrakcji cech, z liczbą produktów; `Other`, `Not Applicable` i `Unknown` są pominięte, bo parser nigdy
  po nich nie filtruje. Po wyszukaniu panel pokazuje wybór parsera. Kliknięcie wartości przełącza
  *wymagaj → wyklucz → wyłącz*; cechy wielowartościowe (`colors`, `main_composition` i pozostałe multi-choice) mają
  też tryb: *dowolna z*, *wszystkie* albo *tylko te*. Każda zmiana od razu wyszukuje ponownie z tymi filtrami, bez
  parsera. Cena obsługuje `<`, `<=`, `>`, `>=` i `=`; drugi warunek tworzy przedział. Waluty nie są przeliczane.
  Produkty z ceną zerową lub nieznaną nie spełniają aktywnego warunku ceny. *Reset to parser* przywraca filtry
  parsera. Gdy parser nie znajdzie kategorii, można ją wybrać tutaj. Pole *Residual* przyjmuje jedną frazę na
  wiersz; frazy są pokazywane i przekazywane razem z filtrami, a obecny ranking korzysta z całego zapytania.
- **Ranking** – `combined` (opis + zdjęcie), `text` (opis) albo `image`.
- **Czasy etapów** (po lewej, pod odczytem parsera) – parsowanie (z dwoma krokami LLM), filtrowanie i ranking na
  jednej osi czasu.
- **Wyniki** (po prawej, wszystkie, przewijane) – zdjęcie, nazwa, marka, cena i cechy, które pasowały do zapytania.
  Kliknięcie produktu pokazuje wszystkie zdjęcia, opis i wszystkie cechy, z wyróżnieniem dopasowanych.
- Link w rodzaju `/?q=black+midi+dress&ranking=text` od razu uruchamia wyszukiwanie.

## Jak to działa

1. **Parsowanie** (`parser_adapter.py`). Parser zwraca `category`, `filters` i `residual` (listę fraz, po jednej na
   wymaganie; tekst staje się jedną frazą) (`QueryParser.to_dict()`). Brak kategorii oznacza zapytanie spoza
   kategorii parsera, spoza katalogu albo zbyt ogólne; wyszukiwanie wtedy się nie odbywa. W przeciwnym razie filtry
   stają się drzewem warunków (`conditions.py`):

   | Operator parsera | Warunek |
   | --- | --- |
   | `in`, `contains_any` | produkt ma którąś z wartości |
   | `not_in`, `contains_none` | produkt nie ma żadnej z wartości |
   | `contains_all` | produkt ma wszystkie wartości |
   | `equals_set` | produkt ma dokładnie te wartości |
   | `lt`, `lte`, `gt`, `gte`, `eq` | porównania liczbowe ceny `msrpUSD`; cena używa `value` zamiast `values` |
   | `around` | cena w granicach ±20% od `value` (zasady parsera zostawiają tolerancję otwartą; tak samo jak w ewaluacji rankingu) |

2. **Filtrowanie** (`conditions.py`). Drzewo jest sprawdzane na każdym produkcie z indeksu. Wartości cech są
   zbiorami; `main_composition` to zbiór materiałów, niezależnie od udziałów. Brakująca cecha nigdy nie pasuje, więc
   produkt bez niej odpada przy filtrze pozytywnym i zostaje przy negatywnym. `brand` jest porównywany z metadanymi
   produktu. Warunek ceny używa dodatniej, skończonej `msrpUSD`; cena zerowa, brakująca lub błędna nie pasuje. Cecha
   albo wartość, której nie ma żaden produkt z indeksu (na przykład marka spoza katalogu), zostaje w drzewie i niczego
   nie dopasowuje, z ostrzeżeniem, więc filtr nigdy nie jest luzowany. Gdy żaden produkt nie spełnia wszystkich
   warunków, wynik jest pusty.

3. **Ranking** (`server.py`). Całe zapytanie jest przy każdym wyszukaniu zamieniane na embedding `gemini-embedding-2`
   (3072 wymiary) i porównywane (cosinus) z gotowymi embeddingami kandydatów:
   - `text` – z opisami produktów, zapytanie wysyłane jako `task: search result | query: <zapytanie>`;
   - `image` – z głównymi zdjęciami produktów, wysyłany sam tekst;
   - `combined` – średnia z-score obu podobieństw, liczonych w obrębie kandydatów.

Nic nie jest cache'owane: powtórzone zapytanie znowu wywołuje parser i API embeddingów, a każda odpowiedź HTTP ma
`Cache-Control: no-store`. Przy starcie ładowane są tylko indeks, embeddingi produktów i klienci API.

## Opcje

| Opcja `server.py` | Domyślnie | |
| --- | --- | --- |
| `--parser` | `llm` | `llm`, `benchmark`, `mock` albo `moduł:funkcja` zwracająca format parsera |
| `--ranking` | `combined` | domyślny ranking: `combined`, `text` albo `image` |
| `--port` | `8000` | |
| `--data` | `search_ui/data` | indeks zbudowany przez `prepare.py` |
| `--no-warmup` | | bez testowego wywołania embeddingu przy starcie |
| `--no-browser` | | bez otwierania strony |

`prepare.py` przyjmuje `--features` (`.parquet`, `.jsonl` lub `.csv`, jeden lub więcej plików; domyślnie pilotaż),
`--status` (domyślnie `ready`), `--limit`, `--dataset`, `--embeddings` i `--output`. Zatrzymuje się, jeśli
embeddingi nie obejmują wszystkich produktów z indeksu.

Parser podany jako `moduł:funkcja` może ustawić w module `NAME` (nazwa na stronie), `CATEGORIES` (kategorie, które
potrafi zwrócić dla dowolnego zapytania; strona pokazuje je, gdy nie zwróci żadnej) i `EXAMPLES` (przykładowe
zapytania w grupach, pokazywane zamiast `example_queries.yaml`).

## HTTP API

| Endpoint | |
| --- | --- |
| `GET /api/search?q=…&ranking=…` | cały pipeline |
| `GET /api/search?q=…&filters=<json>` | bez parsera; `filters` to `{"category", "filters", "residual"}` w formacie parsera |
| `GET /api/info` | nazwa i kategorie parsera, ustawienia, kategorie katalogu, wartości panelu filtrów, przykłady |
| `GET /api/product?id=…` | szczegóły produktu |
| `GET /images/<image_path>` | zdjęcie produktu |

Odpowiedź wyszukiwania zawiera `parsed` (kategoria, filtry, residual i ich źródło), `tree`, `condition`,
`warnings`, `results` (z `score`, `score_text`, `score_image`, `features` i dopasowanymi cechami `matched`),
`timings` (`parsing_ms`, `filtering_ms`, `ranking_ms`, `query_embedding_ms`, `total_ms`) oraz, dla parsera LLM,
`parser_info` z czasem obu kroków parsera i szacowanym kosztem. Błędy wracają jako
`{"error": {"stage", "message"}}` z czasami zmierzonymi do tej chwili.

## Pliki

| Plik | |
| --- | --- |
| `prepare.py` | buduje `data/index.parquet` (ignorowany przez git) z pliku cech, metadanych i zdjęć |
| `server.py` | pipeline wyszukiwania, ranking i serwer HTTP |
| `conditions.py` | drzewo warunków: walidacja, ewaluacja, dopasowane cechy |
| `parser_adapter.py` | wynik parsera → drzewo warunków, parser mock, ładowanie parsera |
| `llm_parser.py` | opakowuje `poc/scripts/query_parser.py` dla `--parser llm` |
| `benchmark_parser.py` | parsowania z benchmarku dla zapytań dev w `--parser benchmark`, parser LLM dla pozostałych |
| `facets.py` | wartości panelu filtrów dla kategorii z `feature_extraction/schema` |
| `common.py` | ścieżki, wczytywanie danych, embedder zapytań |
| `static/index.html` | strona (czytana przy każdym żądaniu, więc zmiany widać po odświeżeniu) |
| `example_queries.yaml` | przykłady na stronie |

## Testy i sprawdzenia

```sh
python -m unittest discover -s search_ui/tests   # bez wywołań API
python search_ui/check_examples.py               # przykłady na indeksie, parser mock
python search_ui/check_examples.py --parser llm  # to samo z parserem LLM (płatne wywołania)
```

## Problemy

- **`Failed to resolve 'oauth2.googleapis.com'`** albo inny błąd połączenia przy starcie – brak sieci lub DNS.
  Serwer i tak startuje; parser i embeddingi zadziałają po powrocie połączenia.
- **Błąd odczytu `embeddings/text.parquet` lub `image.parquet`** – pliki są jeszcze kilkusetbajtowymi wskaźnikami
  Git LFS; uruchom `git lfs pull`.
- **`Missing optional dependency 'pyarrow'`** – Python na `PATH` nie jest tym z wymaganiami.
- **Parser nie zwraca kategorii** dla zapytania z jednej z pozostałych 19 kategorii – tak ma być przy parserze
  LLM; wybierz kategorię w panelu filtrów albo użyj `--parser benchmark` z jego przykładami.

## Czasy

Typowe czasy na zapytanie z parserem LLM: parsowanie około 2 s (dwa wywołania LLM), filtrowanie kilka ms,
embedding zapytania 0,3–0,5 s. Parsowanie z benchmarku i wyszukiwanie z filtrami z panelu omijają LLM.
