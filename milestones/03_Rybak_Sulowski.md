# Dokument etapu 3 — Stan implementacji modułów

**Projekt inżynierski — Politechnika Warszawska, Wydział MiNI**

- **Projekt** — System wyszukiwania semantycznego w e-commerce z wykorzystaniem modeli językowych
- **Autorzy** — Jakub Rybak, Michał Sulowski
- **Data** — 17.11.2026
- **Wersja** — 1.0

Dokument przedstawia stan modułów dostępnych na głównej gałęzi repozytorium, ustawienia modeli oraz środowisko testowe. Zakres obejmuje przygotowanie danych, ekstrakcję cech produktów, przetwarzanie zdjęć i parsowanie zapytań.

## 1. Stan implementacji

| Moduł | Lokalizacja | Stan i zakres |
| --- | --- | --- |
| Przygotowanie katalogu | `dataset_preparation/fashiongen/` | Zaimplementowano wybór produktów, podział produktów na kategorie, zmianę formatu. |
| Przygotowanie zapytań | `dataset_preparation/amazon_esci/` | Zaimplementowano eksport unikalnych zapytań z Amazon ESCI na podstawie fraz charakterystycznych dla branży modowej. |
| Ekstrakcja cech | `feature_extraction/` | Ustalono możliwe cechy dla każdej kategorii, słowa kluczowe na podstawie których są one określane oraz po 20 przykładów referencyjnych dla każdej kategorii z ręcznie przydzielonymi cechami. Zaimplementowano skrypt który wysyła zapytania przez API do modelu LLM który dla danego produktu przyporządkowuje brakujące cechy. |
| Parsowanie zapytań | `query_parsing/` | Dwuetapowy parser rozpoznający kategorię, filtry, markę, cenę i pozostałe potrzeby użytkownika. |
| Poprawa jakości zdjęć | `image_processing/enhancement/` | Powiększanie zdjęć metodą DAT-2 i rekonstrukcja wykrytych twarzy przez GFPGAN. |
| Maskowanie i kolor tła | `image_processing/background/`, `image_processing/background_color/` | Generowanie miękkich masek pierwszego planu oraz zmiana koloru tła na ich podstawie. |

## 2. Przygotowanie danych

### Katalog Fashion-Gen

Skrypt `prepare_catalog.py` odczytuje źródłowe części train i validation. Reguły z `fashiongen_taxonomy.yaml` określają mapowanie kategorii źródłowych na 22 kategorie projektu oraz wykluczenia produktów spoza zakresu.

Wiersze źródłowe odpowiadają zdjęciom. Oryginalne dane są w formacie HDF5. Skrypt zapisuje osobne pliki CSV z danymi produktów oraz listami zdjęć i ich ścieżkami dla części treningowej i walidacyjnej. Zachowuje m.in. nazwę, opis, markę, płeć, skład, cenę i oryginalną kategorię. Zdjęcia są eksportowane do PNG i powiązane z produktem przez identyfikator oraz oznaczenie ujęcia.

### Zapytania Amazon ESCI

Skrypt `export_query_candidates.py` odczytuje kolumnę `query`, wybiera frazy pasujące do wskazanej grupy keywordów i usuwa duplikaty. Dostępne grupy obejmują T-shirts, Polos, Tank tops & Camisoles oraz Bodysuits. Eksport jest źródłem kandydatów do budowy zbioru testowego. Oczekiwane kategorie, filtry i pozostałe fragmenty zapytań wymagają osobnego oznaczenia.

## 3. Ekstrakcja cech produktów

### Przebieg przetwarzania

1. **Ekstrakcja regułami.** Płeć i marka pochodzą z danych źródłowych. Wyrażenia regularne przypisują wybrane cechy z nazwy lub opisu. Parser składu rozpoznaje materiały, sekcje składu i udziały procentowe.
2. **Przygotowanie kontekstu.** Dla każdego produktu obliczony jest embedding. Produkty które mają wyznaczone wszystkie cechy stanowią 'bank przykładów', który jest regularnie powiększany.
3. **Uzupełnienie brakujących cech.** Jedno wywołanie modelu dotyczy jednego produktu. Prompt zawiera nazwę, opis, dostępne zdjęcia, definicje wymagających uzupełnienia cech oraz po 2 przykłady najbardziej podobnych (według podobieństwa embeddingów) produktów które mają wyznaczone wszystkie cechy. Każdy przykład dostarcza etykiety tych cech oraz dwa zdjęcia.
4. **Walidacja i zapis.** Sprawdzane są dozwolone wartości, liczba etykiet, kompletność i zależności między cechami. Wyniki trafiają do JSONL i Parquet.

Definicje cech znajdują się w `schema/`, reguły wykonawcze w `keywords/definitions/`, a instrukcje modeli w `llm/prompts/`. Opis zasad dostępny jest w `docs/extraction_rules/`. Cechy przypisane wcześniej regułami są zachowywane. Prompt pomija ich definicje i etykiety.

Structured output ogranicza odpowiedź do wymaganego formatu i słowników.

### Modele i parametry

| Zastosowanie | Model | Ustawienia |
| --- | --- | --- |
| Uzupełnianie cech | Gemini 3.5 Flash-Lite, Vertex AI, lokalizacja `global` | Temperatura 0, thinking `MEDIUM`, media resolution `MEDIUM`, limit wejścia kontrolowany przez pipeline 20 000 tokenów, limit wyjścia 32 768 tokenów obejmujący myślenie i końcową odpowiedź. |
| Reprezentacje produktów | Gemini Embedding 2 | Wymiar 3072, osobne wektory opisu i głównego zdjęcia, limit wejścia 8192 tokeny, domyślnie 10 równoległych wywołań. |

Embedding tekstowy powstaje wyłącznie z opisu. Embedding wizualny powstaje z głównego zdjęcia oznaczonego `id_gridfs_1`. Znormalizowane wektory są przechowywane w plikach Parquet. Dobór przykładów odbywa się w obrębie tej samej kategorii i płci, osobno według podobieństwa opisu oraz zdjęcia, z zachowaniem dwóch różnych produktów.

Początkowy bank zawiera 440 produktów referencyjnych, po 20 na kategorię. Gotowe produkty spełniające warunki przyjęcia do banku rozszerzają go podczas przetwarzania.

### Tryby wykonania i odporność na przerwanie

Dostępne są zwykłe API i Vertex Batch API. W trybie batch kolejne joby korzystają z banku uzupełnionego wynikami poprzednich partii. Bez jawnego `--batch-size` limit jest wyliczany przed każdym nowym jobem.

| Liczba przykładów w banku | Maksymalna liczba produktów w jobie |
| --- | ---: |
| 0–499 | 50 |
| 500–999 | 100 |
| 1 000–1 999 | 200 |
| 2 000–4 999 | 500 |
| 5 000–9 999 | 1 000 |
| 10 000–19 999 | 2 000 |
| Od 20 000 | 5 000 |

Parametr `--batch-size` ustawia stały limit. Manifesty żądań, identyfikatory jobów i wyniki pośrednie są zapisywane, aby umożliwić wznowienie. Pipeline obsługuje ponowienia wybranych błędów API i kontroluje szacowany budżet. Tryb batch wymaga skonfigurowanego bucketu Google Cloud Storage na wejście i wyjście jobów. Płatne operacje wymagają flagi `--execute`.

### Wyniki i statusy

| Status | Znaczenie |
| --- | --- |
| `ready` | Wymagane cechy są kompletne i przechodzą walidację. |
| `pending` | Pozostaje nierozstrzygnięta cecha, np. model zgłosił `outside_schema`. |
| `needs_review` | Wystąpił problem z produktem, odpowiedzią modelu albo przetwarzaniem. |
| `excluded` | Produkt wykluczono zgodnie z regułami, z zapisaniem przyczyny. |

Model może zgłosić niezgodność całego produktu z kategorią lub niespójne dane produktu. Rekordy zawierają cechy, markę, metadane ich pochodzenia, statusy i przyczyny problemów. Status `ready` potwierdza zgodność techniczną ze schematem. Trafność przypisanych etykiet wymaga oceny merytorycznej.

## 4. Parsowanie zapytań

Parser jest udostępniony jako moduł Python i narzędzie CLI. Obsługuje 22 kategorie.

1. **Jev 1.14 przez OpenRouter** wybiera jedną kategorię na podstawie kryteriów i przykładów. Wynik spoza katalogu kończy przetwarzanie z pustymi filtrami i pustą listą pozostałych potrzeb.
2. **Qwen 3.8 27B przez Cerebras** otrzymuje ustaloną kategorię i jej schemat. Zwraca filtry cech, markę, warunki cenowe oraz listę fragmentów zapytania przeznaczonych do dalszego rankingu.

Przykładowo dla „turkusowa sukienka na wesele” kategorią jest Dresses, kolor zostaje sprowadzony do Blue, a dokładny odcień i okazja mogą pozostać jako osobne fragmenty dodatkowej intencji.

| Model | Konfiguracja w kodzie |
| --- | --- |
| `typesafe/jev-1.14` | OpenRouter Decisions API, jedno pytanie typu `choice` o kategorię. Payload obejmuje kryteria i przykłady. Temperatura nie jest przekazywana. |
| `qwen-3.8-27b` | Bezpośrednie API Cerebras, temperatura 0, `reasoning_effort = none`, maksymalnie 512 tokenów odpowiedzi, ścisły schemat JSON. |

Parser obsługuje alternatywy, łączenie wartości i wykluczenia zgodnie z typem cechy. Uwzględnia markę, cenę oraz fragmenty, których schemat cech nie opisuje w pełni.

## 5. Przetwarzanie zdjęć

### Poprawa rozdzielczości

Moduł przyjmuje CSV, Parquet lub JSONL z kolumną `product_id` oraz ścieżkę wyjściową. Zdjęcia wybierane są z manifestów katalogu. Dostępne jest przetwarzanie głównego ujęcia lub wszystkich ujęć produktu.

| Element | Model lub ustawienie |
| --- | --- |
| Powiększenie całego zdjęcia | DAT-2, skala ×4 (256 × 256 → 1024 × 1024 px). |
| Detekcja twarzy | RetinaFace ResNet50, wyrównanie twarzy do kadru 512 × 512 px. |
| Rekonstrukcja twarzy | GFPGAN v1.4. |
| Połączenie wyniku | ParseNet wyznacza obszar twarzy, który po poprawieniu jest płynnie łączony z oryginalnym zdjęciem. |
| Zapis | WebP, jakość 90. |

Model działa w trybie inferencji. Poprawne pliki wynikowe są pomijane przy ponownym uruchomieniu. Dla zdjęć bez wykrytej twarzy wynikiem powiększenia jest obraz z DAT-2.

### Maski pierwszego planu i kolor tła

BiRefNet Lite Matting generuje miękką maskę pierwszego planu. Maska jest zapisywana jako PNG.

Biel maski zachowuje pierwszy plan, czerń wskazuje tło, a wartości pośrednie pozwalają płynnie połączyć krawędzie. Osobny moduł zmienia tło przez mnożenie kolorów zdjęcia przez odcień `#F4F3F7` i połączenie wyniku z oryginałem według maski. Wynik renderowania zapisywany jest jako bezstratny WebP.

## 6. Środowisko testowe i wykonane próby

### Testy automatyczne

Testy offline w `feature_extraction/tests/` obejmują keywordy, parser składu, schematy, budowanie promptów, walidację odpowiedzi, komunikację z API oraz odzyskiwanie po błędach i przerwaniu. Wywołania zewnętrzne są zastępowane w testach kontrolowanymi odpowiedziami.

Testy w `experiments/query_parsing/tests/` obejmują m.in. schematy parsera i poprawność etykiet w plikach zapytań. Osobny benchmark wykonuje rzeczywiste wywołania modeli.

### Benchmark parsowania zapytań

Środowisko `experiments/query_parsing/benchmark/` zawiera zapytania z oczekiwanymi odpowiedziami, próbkowanie, uruchamianie porównywanych wariantów oraz obliczanie metryk. Sprawdzane są poprawność kategorii, filtry, pozostałe fragmenty intencji, czas i koszt. Porównania obejmują różne modele oraz podział zadań między Jev i LLM.

Wyniki na teście 100 zapytań.

| Metryka tej próby | Wynik |
| --- | ---: |
| Dokładna zgodność całej odpowiedzi | 83% |
| F1 fragmentów dodatkowej intencji | 85,7% |
| Mediana czasu całego parsera | 0,702 s |
| p95 czasu całego parsera | 0,984 s |
| Odpowiedzi poniżej 1 s | 96% |

Źródłem jest `experiments/query_parsing/benchmark/results/benchmark_100_seed42.json`.

### Pilotaż ekstrakcji cech

Zapisany pilotaż obejmuje 9 922 produkty ze wszystkich 22 kategorii. Podsumowanie znajduje się w `data/processed/fashiongen/pilot_9922/summary.json`.

| Wynik pilotażu | Liczba |
| --- | ---: |
| Zapisane produkty | 9 922 |
| `ready` | 9 796 |
| `pending` | 31 |
| `needs_review` | 95 |
| Zakończone joby batch | 10 |

Po pilotażu poprawiono obsługę pustych uzasadnień, ograniczenia zależnych cech i wartości wyłączne w schemacie odpowiedzi. Wprowadzono także adaptacyjne rozmiary partii. Powyższe wyniki pochodzą z wcześniejszego eksperymentu.

### Eksperymenty obrazowe

W `experiments/image_processing/` znajdują się skrypty i raporty porównawcze. Porównanie powiększania obejmuje Lanczos + Unsharp, DAT-2, DAT-2 + GFPGAN oraz Stable Diffusion x4. Raport HTML pozwala porównywać produkty i metody wizualnie.

Osobne eksperymenty dotyczą masek pierwszego planu i kolorowania tła. Ocena wizualna pozwala sprawdzić szczegóły ubrania, twarz oraz krawędzie maski. W repozytorium nie ma niezależnego benchmarku potwierdzającego zachowanie wszystkich detali produktu po rekonstrukcji.
