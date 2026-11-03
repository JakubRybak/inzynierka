# Dokument etapu 2: Propozycja rozwiązania oraz analiza danych

**Projekt:** System wyszukiwania semantycznego w e-commerce z wykorzystaniem modeli językowych  
**Autorzy:** Jakub Rybak, Michał Sulowski  
**Promotor:** dr hab. Marcin Paprzycki  
**Data:** 03.11.2026  
**Wersja:** 1.0

| Wersja | Data | Opis zmiany |
| --- | --- | --- |
| 1.0 | 03.11.2026 | Propozycja rozwiązania, uzasadnienie technik i raport z analizy danych. |

Dokument rozwija specyfikację wymagań i zakres projektu z etapu 1. Przedstawia proponowane rozwiązanie, ocenę narzędzi i technik, założenia modelowania oraz wyniki wstępnej eksploracji i oceny jakości danych. Obejmuje również podział na moduły i wykonane przygotowanie danych.

## 1. Propozycja rozwiązania

System umożliwia wyszukiwanie produktów odzieżowych na podstawie zapytań w języku naturalnym. Łączy jawne filtrowanie po cechach produktu z rankingiem uwzględniającym pozostałe potrzeby użytkownika. Przetwarzanie katalogu odbywa się offline, aby ograniczyć koszt i czas obsługi zapytań.

### Przygotowanie katalogu offline

```mermaid
flowchart TD
    A["1. Fashion-Gen"] --> B["2. Wybór produktów i kategorii"]
    B --> C["3. Ekstrakcja cech regułami"]
    B --> D["4. Embeddingi opisów i zdjęć"]
    C --> E["5. Uzupełnienie cech przez LLM"]
    D -->|Dobór podobnych przykładów| E
    E --> F["6. Walidacja wyników"]
    F --> G["7. Ocena produktów według konceptów"]
    G --> H["8. Zapis katalogu i reprezentacji do wyszukiwania"]
    classDef input fill:#eef2ff,stroke:#6366f1,color:#1e1b4b;
    classDef process fill:#eff6ff,stroke:#3b82f6,color:#172554;
    classDef output fill:#ecfdf5,stroke:#10b981,color:#064e3b;
    class A input;
    class B,C,D,E,F process;
    class G process;
    class H output;
```

| Blok | Wyjaśnienie |
| --- | --- |
| **1. Zbiór danych Fashion-Gen** | Surowe pliki HDF5 zawierające zdjęcia produktów i dane tekstowe: nazwę, opis, skład, płeć oraz kategorie źródłowe. |
| **2. Wybór produktów i kategorii** | Ograniczenie zbioru do odzieży objętej projektem i przypisanie produktów do taksonomii projektu. Wiersze zdjęć są grupowane w produkty, zdjęcia eksportowane do plików, a podział train/validation pozostaje zachowany. |
| **3. Ekstrakcja cech regułami** | Przypisanie cech, np. koloru lub długości rękawa, przez dopasowanie fraz i wyrażeń regularnych w nazwie lub opisie. Płeć jest odczytywana z odpowiedniej kolumny, a skład ustalany przez parser materiałów i procentów. Szczegółowe reguły zależą od cechy i kategorii. |
| **4. Embeddingi opisów i zdjęć** | Obliczenie osobnych wektorów dla opisu i głównego zdjęcia produktu. Pozwalają znaleźć podobne, już oznaczone produkty do przykładów dla LLM. |
| **5. Uzupełnienie cech przez LLM** | Model analizuje nazwę, opis i zdjęcia produktu oraz dwa podobne oznaczone przykłady. Przypisuje wyłącznie brakujące cechy, wybierając z dozwolonych wartości. Przypisania reguł pozostają zachowane. |
| **6. Walidacja wyników** | Sprawdzenie kompletności, dozwolonych wartości i zależności między cechami. Błędy oraz nierozstrzygnięte przypadki otrzymują status wymagający dalszej obsługi. Walidacja techniczna nie zastępuje oceny trafności etykiet. |
| **7. Ocena produktów według konceptów** | Koncepty to zdefiniowane pojęcia opisujące potrzeby użytkownika, np. elegancja, przewiewność lub przydatność na wesele. Model przypisuje każdemu produktowi ocenę dopasowania do każdego konceptu w skali 0–10 (liczby całkowite). Oceny oraz wektory reprezentujące koncepty są przygotowywane offline. |
| **8. Zapis katalogu i reprezentacji do wyszukiwania** | Zapis produktów z cechami, metadanymi przypisań i statusami, ocen dopasowania do konceptów oraz embeddingów. Dane są powiązane przez identyfikatory produktów i konceptów. Wyszukiwarka korzysta z produktów gotowych do wyszukiwania. |

### Obsługa zapytania

```mermaid
flowchart TD
    A["1. Zapytanie użytkownika"] --> B["2. Rozpoznanie kategorii"]
    B -->|Wybrano kategorię| C["3. Ekstrakcja filtrów i pozostałych potrzeb"]
    B -->|Brak kategorii| H["Brak wyszukiwania"]
    C --> D["4. Filtrowanie katalogu"]
    D --> E["5. Ranking według konceptów"]
    E --> F["6. Prezentacja wyników i filtrów"]
    classDef input fill:#eef2ff,stroke:#6366f1,color:#1e1b4b;
    classDef process fill:#eff6ff,stroke:#3b82f6,color:#172554;
    classDef output fill:#ecfdf5,stroke:#10b981,color:#064e3b;
    classDef stop fill:#fff7ed,stroke:#f59e0b,color:#78350f;
    class A input;
    class B,C,D,E process;
    class F output;
    class H stop;
```

| Blok | Wyjaśnienie |
| --- | --- |
| **1. Zapytanie użytkownika** | Fraza w języku naturalnym, np. „czarna sukienka na wesele poniżej 200 dolarów”. |
| **2. Rozpoznanie kategorii** | Pierwsze wywołanie modelu wybiera dokładnie jedną obsługiwaną kategorię, np. Dresses. Jeśli nie można jej ustalić, wyszukiwanie nie jest wykonywane. |
| **3. Ekstrakcja filtrów i pozostałych potrzeb** | Drugie wywołanie modelu, ze schematem wybranej kategorii, rozpoznaje warunki, np. kolor Black i cenę poniżej 200. Część zapytania, której nie da się wyrazić dostępnymi filtrami, np. „na wesele”, jest zapisywana jako pozostałe potrzeby użytkownika i wykorzystywana do sortowania wyników. Parser obsługuje też wykluczenia oraz alternatywy wartości. |
| **4. Filtrowanie katalogu** | Wybierane są produkty zgodne z kategorią i wszystkimi warunkami. Użytkownik może sprawdzić zastosowane filtry. System nie rozluźnia ich automatycznie; brak dopasowania może oznaczać pusty wynik. |
| **5. Ranking według konceptów** | Część zapytania, której nie opisują filtry, np. „na wesele”, jest zamieniana na reprezentację wektorową i porównywana z reprezentacjami zdefiniowanych konceptów. System wybiera najbliższe znaczeniowo koncepty i sortuje produkty według ich wcześniej obliczonych ocen dopasowania. Ranking zmienia kolejność wyników, zachowując produkty spełniające twarde warunki. |
| **6. Prezentacja wyników i filtrów** | Wyświetlenie uporządkowanych produktów, zdjęć, cen i dopasowanych cech. Interfejs pokazuje interpretację query i pozwala ręcznie zmienić filtry. |
| **Brak wyszukiwania** | Obsługa zapytania, dla którego nie ustalono kategorii: użytkownik nie otrzymuje wyników z przypadkowo wybranej kategorii. |

**Agent:** planowany moduł konwersacyjny korzystający z katalogu i narzędzi wyszukiwania. Ma rekomendować istniejące produkty i uzasadniać wybór. Szczegółowy mechanizm działania i jego przewaga nad samą wyszukiwarką wymagają dalszych eksperymentów.

## 2. Ocena narzędzi i technik

| Obszar | Wybrana technika i uzasadnienie | Ograniczenia |
| --- | --- | --- |
| Reguły ekstrakcji | Keywordy, wyrażenia regularne i parser składu. Pozwalają tanio i powtarzalnie przypisać cechy zapisane wprost w danych. | Opisy bywają niepełne, a dopasowana fraza może dotyczyć detalu zamiast całego produktu. |
| Uzupełnianie cech | Multimodalny Gemini 3.5 Flash-Lite analizuje tekst i zdjęcia, uzupełniając brakujące cechy. Wybrano go ze względu na stosunek jakości do kosztu. | Model może przypisać błędną wartość; odpowiedzi wymagają walidacji i oceny jakości. |
| Dobór przykładów | Gemini Embedding 2 wskazuje podobne produkty na podstawie opisu i głównego zdjęcia. Dwa oznaczone przykłady tej samej kategorii i płci stanowią kontekst dla ekstrakcji LLM. | Błędne etykiety przykładów mogą wpływać na kolejne przypisania. |
| Parser zapytań | Gemini 3.5 Flash-Lite w dwóch krokach: kategoria, potem filtry i pozostałe potrzeby, odpowiedź ograniczona schematem kategorii. Dobra jakość i obsługa wykluczeń oraz alternatyw. | Czas ok. 1,7 s i koszt ok. 0,6 gr na zapytanie – za wolny i za drogi jako jedyna warstwa parsowania. |
| Ranking | Produkty mają obliczone offline oceny dopasowania do konceptów, np. elegancji. System dobiera koncepty do potrzeb z zapytania i sortuje według tych ocen. | Jakość zależy od pokrycia potrzeb przez słownik konceptów i poprawności ocen produktów. |
| Prototyp GUI | Aplikacja WWW pozwala sprawdzić wyniki wyszukiwania, interpretację zapytania i ręcznie poprawić filtry. | Demonstrator wymaga dalszych testów użyteczności i wydajności. |

### Rozważane alternatywy

| Obszar | Alternatywa | Wynik / powód odrzucenia |
| --- | --- | --- |
| Ekstrakcja cech | Tylko reguły | Dobre dla cech zapisywanych w opisach słowami (kolor, rękaw, dekolt), prawie bezużyteczne dla cech wizualnych (krój, długość, sylwetka) |
| Ekstrakcja cech | Lokalny model | Odłożony: lokalny model wizyjny byłby wolniejszy i słabszy, a koszt API jest niski. |
| Parser zapytań | Słownik / reguły | Szybki, ale słaby dla parafraz, negacji i bardziej złożonych zapytań |
| Parser zapytań | Model typu „System One” (TypeSafe Jev) | Deklarowane 70–500 ms; dane tylko od producenta, wczesny dostęp; wstępne próby. |
| Ranking | Embeddingi opisu i zdjęcia (Gemini Embedding 2) | Słabe dla potrzeb typu „na wesele” – opisy nie zawierają słów o okazjach; zostają jako ranking zapasowy. |
| Ranking | HyDE (LLM pisze hipotetyczny opis produktu) | Odrzucone: dokłada znaczenia, których użytkownik nie miał na myśli. |
| Ranking | Reranking przez LLM | Ok. 1–2 s i koszt przy każdym zapytaniu; ewentualnie jako punkt odniesienia w ocenie. |

## 3. Założenia techniki modelowania

- System korzysta z gotowych modeli, bez trenowania lub dostrajania na własnych danych. Taksonomia kategorii i słowniki cech są przez nas z góry zdefiniowane.
- Produkt ma dokładnie jedną kategorię. Każda kategoria określa wymagane cechy, dozwolone wartości i ograniczenia, np. wybór pojedynczy lub wielokrotny.
- Ekstrakcja offline najpierw wykorzystuje dane źródłowe i reguły. LLM uzupełnia tylko brakujące cechy; nie nadpisuje wartości przypisanych przez keywordy. Prompty pomijają definicje i etykiety cech, które nie wymagają uzupełnienia.
- Jedno wywołanie dotyczy jednego produktu. Model otrzymuje jego nazwę, opis, dostępne zdjęcia oraz dwa oznaczone przykłady; każdy przykład dostarcza dwa zdjęcia.
- Model może zgłosić problem z całym produktem. Dla cechy bez `Other` może zgłosić `outside_schema` z uzasadnieniem. Jeśli `Other` jest dostępne, musi wybrać jedną z dopuszczonych wartości.
- Nieudana ekstrakcja płci, składu głównego lub brak marki wyklucza produkt z dalszego przetwarzania. Rekord pozostaje zapisany wraz z powodem. Pozostałe nierozstrzygnięte przypadki wymagają uzupełnienia albo przeglądu.
- Parser query wybiera dokładnie jedną kategorię albo zgłasza jej brak. Dla cech pojedynczych kilka żądanych wartości oznacza alternatywę. Dla wielowartościowych parser rozróżnia „dowolną”, „wszystkie”, „dokładnie te” i wykluczenia. Procenty materiałów nie są obecnie interpretowane jako progi filtrowania.
- Ranking opiera się na ustalonym słowniku konceptów. Oceny produktów są obliczane offline; podczas wyszukiwania dobierane są koncepty odpowiadające pozostałej intencji użytkownika, a ich oceny wyznaczają kolejność wyników.
- Prompty, definicje i przykłady dla modeli są po angielsku. Testy zapytań obejmują również język polski. Zbiór Amazon ESCI stanowi źródło rzeczywistych fraz do dalszych eksperymentów i oceny parsera.


## 4. Raport danych: wstępna eksploracja

Źródłem katalogu jest Fashion-Gen: produkty SSENSE z angielskimi opisami i kilkoma zdjęciami o rozdzielczości 256 × 256 px. W projekcie wykorzystywane są części train i validation. Rekordy HDF5 odpowiadają zdjęciom; przy przygotowaniu katalogu są grupowane według identyfikatora produktu.

| Zakres | Liczba produktów |
| --- | ---: |
| Pełny zbiór train i validation | 67 666 |
| Katalog odzieży po wyborze zakresu projektu | 52 969 |
| Katalog odzieży: train | 47 082 |
| Katalog odzieży: validation | 5 887 |
| Pilotaż ekstrakcji LLM: po 300 produktów z trzech kategorii | 900 |

Katalog projektu obejmuje 8 działów i 22 kategorie. Liczby poniżej dotyczą katalogu przed wykluczeniami wynikającymi z ekstrakcji cech.

| Dział | Produkty | Kategorie | Kobiety | Mediana ceny |
| --- | ---: | --- | ---: | ---: |
| Sweaters | 12 105 | Knit Sweaters 4 990, Sweatshirts 3 432, Hoodies & Zipups 2 779, Cardigans 904 | 43,9% | 470 USD |
| Tops | 10 689 | T-shirts 8 961, Tank tops & Camisoles 1 020, Polos 590, Bodysuits 118 | 40,6% | 240 USD |
| Pants | 9 944 | Trousers 3 916, Jeans 3 704, Sweatpants & Lounge Pants 2 136, Cargo Pants 188 | 39,3% | 450 USD |
| Jackets & Coats | 8 324 | Jackets 4 045, Classic Coats 2 198, Bombers 1 573, Vests 342, Trench Coats 166 | 44,1% | 1 090 USD |
| Shirts & Blouses | 5 341 | Shirts 4 339, Blouses 1 002 | 41,5% | 455 USD |
| Dresses | 2 600 | Dresses | 100% | 755 USD |
| Shorts | 2 053 | Shorts | 36,3% | 395 USD |
| Skirts | 1 913 | Skirts | 100% | 640 USD |

| Produkty spoza zakresu projektu | Produkty |
| --- | ---: |
| Akcesoria i torby | 7 573 |
| Obuwie (poza zakresem na razie) | 4 833 |
| Odzież wykluczona decyzją zespołu (garnitury i marynarki, kombinezony, legginsy, pea coats i in.) | 1 554 |
| Bielizna, skarpety, stroje kąpielowe | 439 |
| DOWN / FUR – niejednoznaczny typ ubrania | 293 |
| Inne (koce) | 5 |
| **Razem** | **14 697** |

- **Nierówne kategorie:** T-shirts to 17% katalogu, a trzy kategorie mają poniżej 200 produktów (Bodysuits 118, Trench Coats 166, Cargo Pants 188) – w nich wyniki oceny będą mniej pewne.
- **Marki i ceny:** 448 marek, 10 największych to 19,6% produktów; mediana ceny 465 USD (kwartyle 275–810 USD), maksimum 17 450 USD – segment premium. Sezony SS2014–SS2018.
- **Zdjęcia:** 85,3% produktów ma 4 zdjęcia (zakres 1–6).
- **Opisy:** mediana 25 słów.

Dostępne informacje obejmują nazwę, opis, markę, płeć, skład procentowy, kategorie źródłowe, cenę, sezon oraz zdjęcia. Dla wszystkich 52 969 produktów sprawdzono kolumny `name`, `description`, `composition`, `gender` i `brand`: nie znaleziono pustych ani zawierających wyłącznie białe znaki. Nie oznacza to, że treść każdej z tych kolumn jest poprawna lub kompletna znaczeniowo.

## 5. Raport danych: ocena jakości

| Obserwacja | Znaczenie dla rozwiązania | Postępowanie |
| --- | --- | --- |
| Jeden produkt występuje w wielu wierszach źródłowych. | Liczenie wierszy jako produktów zawyżałoby liczebność katalogu. | Grupowanie po `product_id`, zachowanie podziału train/validation. |
| Część opisów nie podaje wprost cech takich jak krój, długość czy dekolt. | Brak keyworda nie oznacza braku cechy. | Uzupełnianie przez model na podstawie tekstu i zdjęć. |
| Skład może zawierać kilka sekcji, nieznane materiały lub błędną sumę procentów. | Nie można bezwarunkowo potraktować całego pola jako składu głównego. | Wybór dopuszczonej sekcji, mapowanie materiałów i kontrola sumy 100%; zapis powodów niepowodzenia. |
| Keyword może opisywać detal, markę lub element innego ubrania. | Ryzyko fałszywego przypisania. | Dobór kolumn i fraz, maskowanie marki przy kolorach oraz przeglądy przykładów. Pattern oraz inne niejednoznaczne cechy przekazano w całości do LLM. |
| Zdjęcia mają małą rozdzielczość; ujęcia mogą przedstawiać całą stylizację. | Drobne detale bywają nieczytelne, a inne ubrania mogą zmylić model. | Analiza wielu zdjęć produktu; embedding wizualny wyłącznie z głównego zdjęcia. |
| Granice niektórych wartości, szczególnie fit i length, są subiektywne. | Rozbieżność ocen nie zawsze jest jednoznacznym błędem. | Jawne definicje, przykłady oraz oddzielne oznaczanie niejednoznaczności podczas oceny. |
| Brakuje rozmiarów, stanów magazynowych i historii zachowań użytkowników. | Nie można ocenić dostępności ani zbudować personalizacji na podstawie interakcji. | Zakres ograniczony do wyszukiwania i rankingu istniejącego katalogu. |
| Opisy nie zawierają informacji o okazji ani stylu: słowa *wedding, party, evening, office, formal, elegant* – 0 wystąpień na 52 969 opisów. | Embeddingi opisów nie wyłapią potrzeb typu „na wesele”. | Oceny konceptów przypisywane offline. |
| Skład nieczytelny dla parsera w 7,5% produktów | Produkt wykluczany z katalogu. | Rozszerzanie parsera, np. lepsza obsługa sekcji|
### Wynik pilotażu

Pilotaż obejmuje po 300 produktów z kategorii T-shirts, Dresses oraz Tank tops & Camisoles. Przygotowano 60 ręcznie oznaczonych przykładów początkowych, a dla pozostałych 840 produktów wykonano ekstrakcję LLM.

| Status końcowy | Produkty | Udział |
| --- | ---: | ---: |
| `ready` – komplet wymaganych cech i poprawna walidacja | 893 | 99,22% |
| `pending` – nierozstrzygnięta cecha | 4 | 0,44% |
| `needs_review` – problem techniczny lub wymagający sprawdzenia | 3 | 0,33% |

Wszystkie identyfikatory odpowiadają ustalonej próbce, przypisania keywordów zostały zachowane, a zapis JSONL i Parquet jest zgodny. Przypadki wymagające uwagi obejmowały m.in. nietypowe rękawy, kolor spoza słownika, niespójne zdjęcia, konflikt cech i błąd API.

**99,22% to kompletność zwalidowanych rekordów, a nie dokładność etykiet.** Przeglądy wskazały błędy i niejednoznaczności, ale nie stanowią kompletnego, niezależnego benchmarku trafności. Ta wartość nie stanowi dowodu poprawności 99,22% przypisań.

Dla pilotażu obliczono również 900 embeddingów zdjęć i 900 embeddingów opisów, po 3072 wymiary. Sprawdzono pokrycie identyfikatorów, wymiar, skończoność wartości i normalizację wektorów.

## 6. Moduły, GUI i przygotowanie danych

| Moduł | Odpowiedzialność |
| --- | --- |
| Przygotowanie katalogu | Odczyt HDF5, wybór kategorii, grupowanie produktów, eksport metadanych i zdjęć. |
| Ekstrakcja cech | Reguły YAML, parser składu, uzupełnianie przez LLM i walidacja wyników. |
| Embeddingi | Obliczanie i przechowywanie reprezentacji zdjęć oraz opisów. |
| Parser query | Rozpoznanie kategorii, filtrów, marki, ceny i residual. |
| Wyszukiwanie i ranking | Wykonanie filtrów, wybór konceptów odpowiadających zapytaniu i sortowanie według ocen produktów dla tych konceptów. |
| GUI | Wprowadzanie query, podgląd i edycja filtrów, lista wyników oraz szczegóły produktu. |
| Agent – planowany | Obsługa rozmowy i rekomendacje oparte na katalogu. |

Przygotowanie danych jest zaimplementowane: powstają osobne pliki produktów i manifesty zdjęć dla train oraz validation. Zdjęcia są eksportowane do plików i łączone z metadanymi przez identyfikatory. Wyniki ekstrakcji są zapisywane w JSONL i Parquet wraz z cechami, źródłem przypisań, statusem i powodami wykluczeń. Dane źródłowe pozostają zachowane.

Prototyp GUI pozwala wpisać query, zobaczyć interpretację parsera, zmienić filtry i przejrzeć zdjęcia oraz cechy wyników. Służy także do obserwowania czasu parsowania, filtrowania i rankingu.


---

**Supervisor Signature (Architecture Acceptance):** ............................................ **Date:** 05.11.2026
