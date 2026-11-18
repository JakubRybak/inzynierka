# Dokument etapu 3 — Stan implementacji modułów

**Projekt inżynierski — Politechnika Warszawska, Wydział MiNI**

- **Projekt** — System wyszukiwania semantycznego w e-commerce z wykorzystaniem modeli językowych
- **Autorzy** — Jakub Rybak, Michał Sulowski
- **Data** — 17.11.2026
- **Wersja** — 1.0

Dokument przedstawia stan modułów dostępnych na głównej gałęzi repozytorium, ustawienia modeli oraz środowisko testowe. Zakres obejmuje przygotowanie danych, ekstrakcję cech produktów, przetwarzanie zdjęć, parsowanie zapytań, ranking wyników i aplikację wyszukiwarki. Wyjątkiem są ranking i testowa aplikacja wyszukiwarki, znajdują się na osobnej gałęzi `app-ranking-demo` i nie zostały jeszcze włączone do gałęzi głównej.

## 1. Stan implementacji

| Moduł | Lokalizacja | Stan i zakres |
| --- | --- | --- |
| Przygotowanie katalogu | `dataset_preparation/fashiongen/` | Zaimplementowano wybór produktów, podział produktów na kategorie, zmianę formatu. |
| Przygotowanie zapytań | `dataset_preparation/amazon_esci/` | Zaimplementowano eksport unikalnych zapytań z Amazon ESCI na podstawie fraz charakterystycznych dla branży modowej. |
| Ekstrakcja cech | `feature_extraction/` | Ustalono możliwe cechy dla każdej kategorii, słowa kluczowe na podstawie których są one określane oraz po 20 przykładów referencyjnych dla każdej kategorii z ręcznie przydzielonymi cechami. Zaimplementowano skrypt który wysyła zapytania przez API do modelu LLM który dla danego produktu przyporządkowuje brakujące cechy. Dotychczas przetworzono pilotaż: 9 922 z 52 969 produktów w zakresie projektu. |
| Parsowanie zapytań | `query_parsing/` | Dwuetapowy parser rozpoznający kategorię, filtry, markę, cenę i pozostałe potrzeby użytkownika. |
| Poprawa jakości zdjęć | `image_processing/enhancement/` | Powiększanie zdjęć metodą DAT-2 i rekonstrukcja wykrytych twarzy przez GFPGAN. |
| Maskowanie i kolor tła | `image_processing/background/`, `image_processing/background_color/` | Generowanie miękkich masek pierwszego planu oraz zmiana koloru tła na ich podstawie. |
| Ranking wyników | `search_ui/core/`, `search_ui/offline/`, `search_ui/ranking_data/` (gałąź `app-ranking-demo`) | Wersja eksperymentalna, jeszcze niewłączona do gałęzi głównej. Zaimplementowano ustalanie kolejności produktów po filtrowaniu. Kolejność zależy od podobieństwa do całego zapytania oraz potrzeb, których nie da się wyrazić filtrami (okazja, styl, odcień, detale, negacje). Dodatkowo, 30 pierwszych produktów po pierwszym etapie rankingu ocenia ponownie model Jev 1.14, w celu ich jeszcze lepszego ułozenia. |
| Aplikacja wyszukiwarki | `search_ui/` (gałąź `app-ranking-demo`) | Lokalna aplikacja webowa do testowania pozostałych modułów, nie docelowa wyszukiwarka. Łączy parser, filtrowanie i ranking, pokazuje, jak zrozumiano zapytanie, pozwala ręcznie zmieniać filtry i mierzy czas każdego etapu. |
| Agent konwersacyjny | – | Nierozpoczęty.
| Docelowa wyszukiwarka | – | Nierozpoczęta. Obecna aplikacja (`search_ui/`) służy wyłącznie do testowania pozostałych modułów. |

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

## 6. Ranking wyników

Filtry zawężają katalog do produktów spełniających warunki zapytania, ale ich nie porządkują, a po filtrach często zostają np. wszystkie niebieskie sukienki. Części potrzeb nie da się też zapisać jako filtra, bo dotyczą okazji, stylu, dokładnego odcienia albo detalu. Parser zwraca je osobno, jako listę `residual`, czyli rezyduum zapytania (w sekcji 4: fragmenty dodatkowej intencji). Przykładowo dla zapytania „turquoise midi dress for a summer wedding” (z benchmarku) parser zwraca:

```json
{
  "category": "Dresses",
  "filters": [
    {"feature": "colors", "operator": "equals_set", "values": ["Blue"]},
    {"feature": "length", "operator": "in", "values": ["Midi"]}
  ],
  "residual": ["turquoise", "for a summer wedding"]
}
```

Filtry zostawiają niebieskie sukienki midi, a rezyduum mówi, czego jeszcze szuka użytkownik: odcienia turkusu i sukienki na letnie wesele. Ranking ustala kolejność produktów, które przeszły filtry, tak aby na początku listy znalazły się te, które najlepiej pasują do całego zapytania, w tym do każdego fragmentu rezyduum. Ranking nie dodaje ani nie usuwa produktów.

Ranking korzysta z informacji przypisanych produktom offline, czyli jednorazowo, przed uruchomieniem wyszukiwarki. Model językowy nadaje wtedy każdemu produktowi oceny konceptów, kolory w postaci HEX i detale których nie obejmują filtry/cechy, a wyniki są zapisywane razem z katalogiem. Podczas wyszukiwania ranking tylko odczytuje te wartości i nie czeka na model. Wyjątkiem jest drugi etap rankingu, który wywołuje model dla 30 najlepszych kandydatów.

Ranking działa więc w dwóch etapach. Pierwszy etap szybko liczy wynik każdego kandydata, porównując zapytanie z danymi przypisanymi offline. Drugi etap ponownie ocenia 30 najlepszych kandydatów modelem, który czyta zapytanie razem z opisem i zdjęciem produktu.

**Stan prac.** Ranking jest w fazie eksperymentalnej. Działa obecnie w testowej aplikacji (sekcja 7), w której porównujemy jego warianty, i nie został jeszcze włączony do gałęzi głównej. Jego ostateczna postać może się zmienić po dalszych porównaniach.

### Dane przypisane offline

Każdemu produktowi katalogu przypisano offline następujące dane:

| Dane | Czym są | Jak powstają |
| --- | --- | --- |
| Embeddingi | Embedding to wektor liczb opisujący znaczenie tekstu lub zdjęcia. Podobne treści mają podobne wektory, więc podobieństwo wektorów mierzy, jak bardzo produkt pasuje do zapytania. Liczone są dla opisu produktu, głównego zdjęcia (powiększonego do 1024 px), krótkiego tekstu z cech produktu (np. „Dresses. For women. Black. 100% linen. Midi length.”), pojedynczych zdań opisu i fraz banku. | Gemini Embedding 2 |
| Oceny konceptów | Koncept to abstrakcyjna potrzeba, której nie opisuje żadna cecha produktu: okazja (np. wesele, praca, pogrzeb), styl (np. elegancki, boho, sportowy) albo potrzeba związana z sezonem lub komfortem (np. zima, deszcz). Projekt w obecnej wersji ma zamkniętą, ustaloną ręcznie listę 37 konceptów, zdefiniowanych na podstawie bazy z zapytaniami klientów. Każdy produkt ma dla każdego konceptu ocenę 0–10, np. jak dobrze dana sukienka nadaje się na wesele. | Gemini 3.5 Flash-Lite na podstawie tekstu i dwóch zdjęć produktu |
| Kolory produktów | Filtr koloru zna tylko podstawowe rodziny, np. Pink. My natomiast dla kazdego produktu przydzielamy 1–3 dokładne kolory produktu (np. „dusty pink”, „burgundy”) z kodem HEX koloru i udziałem w produkcie. | Gemini 3.5 Flash-Lite na podstawie nazwy i zdjęcia |
| Detale produktów | Widoczne elementy produktu, których nie opisują wyodrębnione cechy, np. koronka, cekiny, kieszenie, nadruk z czaszką, haftowany rękaw z informacją, czy obejmują cały produkt, jego część czy mniejszy element. | Gemini 3.5 Flash-Lite na podstawie nazwy, opisu i dwóch zdjęć |
| Bank fraz | Słownik 7 493 typowych fragmentów zapytań, opisanych z góry typem frazy (czego dotyczy dany fragment): (okazja, styl, sezon, detal, odcień, rozmiar), czy jest zaprzeczeniem („bez kieszeni”) i do których konceptów się odnosi. Dzięki niemu znaczenie fragmentu jest znane bez wywoływania modelu językowego podczas wyszukiwania. Frazy pochodzą z zapytań Amazon ESCI, typowych potrzeb w kategoriach oraz polskich odpowiedników. | Gemini 3.5 Flash-Lite |

Skrypty znajdują się w `search_ui/offline/`, a ich wyniki w `search_ui/ranking_data/`.

### Pierwszy etap (`hybrid`)

Wynik produktu po wyszukaniu to suma kilku składników. Podstawą jest podobieństwo embeddingu całego zapytania do embeddingów opisu, zdjęcia i tekstu cech produktu. Każdy fragment rezyduum dodaje składnik zależny od swojego rodzaju, który odczytuje bank fraz:

| Rodzaj fragmentu | Przykład | Składnik wyniku | Waga |
| --- | --- | --- | ---: |
| całe zapytanie | „turquoise midi dress for a summer wedding” | podobieństwo zapytania do opisu, zdjęcia i cech produktu | 1 |
| okazja, styl lub sezon | „for a summer wedding”, „na wesele” | ocena konceptu, do którego odnosi się fragment | 0,5 |
| odcień | „turquoise”, „turkusowa” | bliskość kolorów produktu do szukanego odcienia | 1 |
| detal | „z koronką” | obecność detalu i jego zasięg | 0,25 |
| zaprzeczenie | „bez koronki” | obecność wykluczonego elementu (składnik odejmowany) | −1 |

Przed zsumowaniem każdy składnik jest przeliczany na z-score, czyli odległość od średniej wśród kandydatów mierzoną w odchyleniach standardowych, aby składniki miały porównywalną skalę. Wagi w obecnej wersji są dobrane ręcznie, częściowo na podstawie porównań na zapytaniach dev (sekcja 8). W planach jest ich automatyczny dobór na części dev, a część test posłuży do końcowego sprawdzenia.

Fragment spoza banku jest przypisywany do najbliższej frazy banku albo bezpośrednio do nazwy koloru, detalu lub konceptu, jeśli podobieństwo ich embeddingów jest wystarczająco duże. Bliskość kolorów liczona jest w przestrzeni barw CIELAB. Embedding nie rozumie zaprzeczeń, dlatego podobieństwo liczone jest dla zapytania bez zaprzeczonych fragmentów („sukienka bez pufiastych rękawów” → embedding liczymy z „sukienka”).

**Zrównoleglenie.** Pierwszy etap rankingu jest częściowo zrównoleglony z parsowaniem. Zanim parser zwróci filtry oraz rezyduum (0,7–1,1 s), aplikacja równolegle, liczy embeddingi całego zapytania, zapytania bez zaprzeczonych fragmentów i wszystkich fragmentów zapytania o długości 1–3 słów. Przed odpowiedzią parsera nie wiadomo, które fragmenty trafią do rezyduum, ale w benchmarku parsowania  około 90% fragmentów rezyduum to dosłowne fragmenty do 3 słów z zapytania, a frazy znane z banku mają zapisane embeddingi. Osobnego wywołania (dodatkowy narzut 0,3–0,6 s) wymaga więc tylko fragment spoza tych obliczonych w trakcie zapytania parsera, co dotyczy jedynie bardziej złozonych/nieoczywistych rezyduów zwróconych przez parser.

### Drugi etap (Jev)

Model, który czyta zapytanie razem z opisem i zdjęciem produktu, ocenia dopasowanie dokładniej niż porównanie embeddingów, ale jest wolniejszy. Nie mozemy sobie pozwolić na ocenę wszystkich produktów po filtrowaniu, dlatego oceniamy tylko 30 pierwszych kandydatów z pierwszego etapu. Używany jest Jev 1.14 (`typesafe/jev-1.14`, Decisions API w OpenRouter), ten sam model, który w parserze wybiera kategorię. Jest to model decyzyjny: nie pisze odpowiedzi, tylko zwraca prawdopodobieństwo kazdej z podanych opcji.

Jev otrzymuje zapytanie oraz nazwę, markę, opis, skład i główne zdjęcie o mniejszej rozdzielczości (384 px) każdego z 30 produktów. Dla każdego produktu przydziela prawdopodobieństwo ocenie od 0 (nie pasuje) do 3 (spełnia wszystko, o co prosi zapytanie). Produkty są ustawiane według oczekiwanej oceny, czyli średniej z ocen 0–3 ważonej ich prawdopodobieństwami, z niewielkim dodatkiem wyniku pierwszego etapu (waga 0,25 po przeliczeniu na z-score). Produkty spoza pierwszych 30 zachowują kolejność. Drugi etap dodaje ok. 0,7 s na wyszukiwanie.

### Rankingi w aplikacji

| Ranking | Opis |
| --- | --- |
| `hybrid_jev_vision` (domyślny) | Pierwszy i drugi etap opisane wyżej. |
| `hybrid` | Tylko pierwszy etap: szybszy i bez dodatkowego kosztu. |

Prostsze rankingi, z którymi porównujemy powyższe (np. samo podobieństwo embeddingów do opisu produktu), znajdują się w `experiments/ranking/baselines.py`.

## 7. Aplikacja wyszukiwarki

Aplikacja to lokalna strona z paskiem wyszukiwania, która łączy parser, filtrowanie i ranking w jeden przepływ. W obecnej wersji powstała wyłącznie do testowania działania pozostałych modułów i nie jest docelową wyszukiwarką. Pełni rolę środowiska testowego: pozwala prześledzić każde zapytanie krok po kroku, ręcznie zmieniać filtry i rankingi oraz zmierzyć czas etapów. Uruchamia się ją poleceniem `python search_ui/server.py` (adres `http://127.0.0.1:8000`). Działa na 9 774 produktach pilotażu ze statusem `ready`, po wykluczeniu 22 produktów wskazanych podczas przeglądu zdjęć. Wymaga dostępu do Vertex AI (embeddingi zapytań) oraz kluczy OpenRouter i Cerebras (parser i drugi etap rankingu).

### Przebieg zapytania

1. **Parsowanie.** Parser z `query_parsing/` (sekcja 4) zwraca kategorię, filtry i rezyduum. Brak kategorii kończy wyszukiwanie.
2. **Filtrowanie.** Filtry są zapisywane jako warunki połączone spójnikami „i”, „lub” i „nie” (np. kolor czarny lub granatowy, nie z poliestru, cena poniżej 300 USD). Filtrowanie jest ścisłe: produkt bez danej cechy nie spełnia filtra, który jej wymaga, a wartość, której nie ma żaden produkt (np. marka spoza katalogu), nie pasuje do niczego i wyświetla ostrzeżenie.
3. **Ranking.** Wybrany ranking ustala kolejność wszystkich kandydatów (sekcja 6).

### Funkcje strony

- Odczyt zapytania: kategoria, wartości włączone i wykluczone, rezyduum oraz to, jak ranking odczytał każdy jego fragment (np. „na wesele” → koncept wedding_guest).
- Panel filtrów z liczbą produktów dla każdej wartości. Ręczna zmiana filtra uruchamia wyszukiwanie bez parsera.
- Wybór rankingu oraz wpływ każdego składnika wyniku na kolejność.
- Czasy etapów: parsowania (z obydwoma krokami parsera), embeddingu zapytania, filtrowania, rankingu oraz łączny.
- Lista wyników ze zdjęciem, marką, ceną i dopasowanymi cechami oraz widok produktu ze wszystkimi zdjęciami, opisem, cechami, kolorami i detalami.


### Czasy etapów

| Etap | Typowy czas | Koszt zapytań do modeli|
| --- | --- | --- |
| Parsowanie | 0,7–1,1 s | ok. 0,0019 USD |
| Embedding zapytania | 0,3–0,6 s, równolegle z parsowaniem | poniżej 0,0001 USD |
| Filtrowanie | kilka ms | - |
| Pierwszy etap rankingu | dziesiątki ms; 3–8% zapytań czeka dodatkowo 0,3–0,6 s na embedding fragmentu | - |
| Drugi etap rankingu | ok. 0,7 s | ok. 0,001 USD |
| Łącznie | | ok. 0,003 USD |

Embeddingi są liczone równolegle z parsowaniem (sekcja 6), dlatego pierwszy etap rankingu zwykle nie czeka na dodatkowe wywołania.

## 8. Środowisko testowe i wykonane próby

### Testy automatyczne

Testy offline w `feature_extraction/tests/` obejmują keywordy, parser składu, schematy, budowanie promptów, walidację odpowiedzi, komunikację z API oraz odzyskiwanie po błędach i przerwaniu. Wywołania zewnętrzne są zastępowane w testach kontrolowanymi odpowiedziami.

Testy w `experiments/query_parsing/tests/` obejmują m.in. schematy parsera i poprawność etykiet w plikach zapytań. Osobny benchmark wykonuje rzeczywiste wywołania modeli.

Testy w `search_ui/tests/` sprawdzają filtrowanie (także ceny i kolory), połączenie z parserem, bank fraz i odczyt fragmentów, kolory, detale, koncepty, drugi etap Jev, wczytywanie danych. Testy prostszych rankingów porównawczych są w `experiments/ranking/test_baselines.py`. Żaden z tych testów nie wywołuje API; tam, gdzie kod korzysta z modelu, testy podstawiają przygotowane odpowiedzi. Skrypt `search_ui/tests/check_examples.py` sprawdza dodatkowo, czy przykładowe zapytania aplikacji znajdują produkty.

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

### Ewaluacja rankingu

Nie mamy danych o zachowaniu klientów, takich jak kliknięcia czy zakupy, więc ocen dokonujemy z pomocą modelu językowego w roli sędziego. Środowisko `experiments/ranking/` uruchamia rankingi na zapytaniach benchmarku parsowania z ich oczekiwanymi odpowiedziami parsera, więc błędy parsera nie wpływają na wynik. Brane są zapytania, które mają kategorię, niepuste rezyduum i co najmniej dwóch kandydatów po filtrach. Zapytania podzielono na dwie części: dev, na której dostrajano warianty, oraz test, odłożoną do końcowej weryfikacji.

Sędzia (Gemini 3.5 Flash-Lite, `judge.py`) dla każdej pary zapytanie–produkt czyta nazwę, markę, opis, skład i główne zdjęcie produktu i wystawia ocenę od 0 (zły wynik) do 3 (spełnia wszystko, o co prosi zapytanie). Trafne są oceny 2 i 3. Oceniono 10 pierwszych wyników każdego rankingu, łącznie 13 507 par w części dev.

| Miara | Co mierzy |
| --- | --- |
| nDCG@10 | Jakość kolejności 10 pierwszych wyników w porównaniu z najlepszą możliwą kolejnością. Wyższe oceny na wyższych miejscach dają więcej punktów, a 1 oznacza kolejność idealną. |
| MRR | Pozycję pierwszego trafnego wyniku: 1 za pierwsze miejsce, 1/2 za drugie, 1/3 za trzecie i 0, gdy w pierwszej dziesiątce nie ma trafnego wyniku. Wynikiem jest średnia po zapytaniach. |
| P@1 | Odsetek zapytań, w których pierwszy wynik jest trafny. |

Wyniki na 310 zapytaniach dev (MRR i P@1 na 262 z nich, dla których istnieje trafny produkt):

| Ranking | nDCG@10 | MRR | P@1 |
| --- | ---: | ---: | ---: |
| Losowa kolejność kandydatów | 0,567 | 0,552 | 0,454 |
| Samo podobieństwo całego zapytania (`combined`) | 0,811 | 0,854 | 0,794 |
| Pierwszy etap (`hybrid`) | 0,830 | 0,893 | 0,855 |
| Pierwszy i drugi etap (`hybrid_jev_vision`, domyślny) | 0,880 | 0,935 | 0,912 |


Sędzia to ten sam model, który przygotował oceny konceptów, kolory i detale, więc mógłby faworyzować rankingi korzystające z jego danych. Dlatego rankingi, ocenił też drugi sędzia z innej rodziny modeli (Claude Haiku 5.5). Sędziowie zgadzają się co do trafności w 87% par, a kolejność rankingów się nie zmienia.

 Dane ewaluacji są przechowywane lokalnie w `experiments/ranking/data/`

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

---

**Podpis promotora:** ............................................ **Data** ................
