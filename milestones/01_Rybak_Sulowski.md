# Dokument etapu 1: Specyfikacja wymagań i zakres projektu

**Projekt inżynierski – Politechnika Warszawska Wydział MiNI**

---

## 1. Metadane dokumentu i historia zmian

| Wersja | Data | Autorzy | Opis zmiany |
| --- | --- | --- | --- |
| **1.0** | 18.10.2026 | Michał Sulowski | Wersja bazowa |
| **2.0** | 18.10.2026 | Jakub Rybak | Doszczegółowienie |
| **3.0** | 22.10.2026 | Jakub Rybak, Michał Sulowski | Poprawki po konsultacji |

- **Tytuł projektu:** *System wyszukiwania semantycznego w e-commerce z wykorzystaniem modeli językowych*
- **Autorzy:** Jakub Rybak, Michał Sulowski
- **Promotor:** dr hab. Marcin Paprzycki

---

## 2. Słownik pojęć

| Pojęcie | Definicja |
| --- | --- |
| **Agent konwersacyjny** | Komponent systemu, który prowadzi z klientem rozmowę w języku naturalnym, dopytuje o potrzeby i rekomenduje produkty z katalogu. |
| **Cecha produktu** | Właściwość produktu wykorzystywana w wyszukiwaniu (np. kolor, skład, rodzaj zapięcia). Każda cecha ma zamkniętą listę dopuszczalnych wartości, a zestaw cech jest określony dla każdej kategorii. |
| **Ekstrakcja cech** | Przypisanie produktom wartości cech na podstawie danych (nazwy, opisu, składu) lub przez LLM na podstawie opisu i zdjęcia. |
| **Fashion-Gen** | Publiczny zbiór danych ze zdjęciami produktów modowych i ich opisami tekstowymi, pochodzący z platformy SSENSE (opis w sekcji 3). |
| **Kategoria** | Rodzaj produktu w taksonomii projektu (np. *Classic Coats*, *Jeans*). Kategorie są pogrupowane w działy (np. *Jackets & Coats*); każdy produkt należy do dokładnie jednej kategorii. |
| **LLM (Large Language Model)** | Duży model językowy. W projekcie wykorzystywany m.in. do ekstrakcji cech produktów i w agencie konwersacyjnym. |
| **MVP (Minimum Viable Product)** | Minimalny zakres funkcjonalny projektu, spełniający wszystkie podstawowe wymagania niezbędne do oceny i obrony pracy. |
| **p95 (95. percentyl czasu odpowiedzi)** | Wartość, poniżej której mieści się 95% czasów odpowiedzi – 95% wszystkich zapytań jest obsługiwanych w czasie krótszym niż podana wartość. |
| **RAG (Retrieval-Augmented Generation)** | Technika, w której model językowy generuje odpowiedź na podstawie danych pobranych z zewnętrznego źródła – tu z katalogu produktów. |
| **Strumieniowanie (streaming)** | Przesyłanie odpowiedzi do klienta fragmentami, w miarę jej generowania, zamiast dopiero po jej ukończeniu. |
| **Unknown** | Wartość cechy oznaczająca, że nie da się jej ustalić na podstawie dostępnych danych. |
| **Wyszukiwanie semantyczne** | Wyszukiwanie oparte na znaczeniu zapytania, a nie wyłącznie na dosłownym dopasowaniu słów. |

---

## 3. Zbiór danych Fashion-Gen

Fashion-Gen (N. Rostamzadeh i in., *Fashion-Gen: The Generative Fashion Dataset and Challenge*, arXiv:1806.08317, 2018) to publiczny zbiór produktów z platformy SSENSE. Opisy produktów przygotowali profesjonalni styliści, a każdy produkt jest sfotografowany z kilku ujęć. W projekcie korzystamy z części treningowej i walidacyjnej w rozdzielczości 256 × 256 px: łącznie **67 666 produktów** i ok. 293 tys. zdjęć (średnio 4,3 zdjęcia na produkt).

Każdy produkt ma: nazwę, markę, płeć (*Men / Women*), kategorię i podkategorię SSENSE (48 kategorii), skład z udziałami procentowymi, opis tekstowy, cenę i sezon. Dane są w języku angielskim.

Po ograniczeniu zbioru do odzieży (8 działów: *Tops, Shirts & Blouses, Sweaters, Jackets & Coats, Pants, Shorts, Skirts, Dresses* – łącznie 22 kategorie) w zakresie projektu pozostaje **52 969 produktów**. Wykluczone są m.in. obuwie, akcesoria i torby, bielizna oraz część ubrań wyłączonych decyzją zespołu (np. marynarki, garnitury, kombinezony).

Ograniczenia zbioru: brak rozmiarów, stanów magazynowych i danych o zachowaniach użytkowników.

---

## 4. Sformułowanie problemu inżynierskiego w jednym zdaniu

> *„Celem pracy jest zaprojektowanie i implementacja systemu inteligentnego wyszukiwania produktów odzieżowych w oparciu o semantyczną reprezentację wiedzy domenowej oraz modele językowe.”*

---

## 5. Zakres projektu: MVP a przyszłe prace

### 5.1. MVP

1. **Wyszukiwarka** – klient wpisuje zapytanie w języku naturalnym, a system zwraca listę pasujących produktów. Przy każdym wyniku pokazuje klientowi, na jakiej podstawie produkty zostały wyselekcjonowane. Zakres prac:
    - interpretacja zapytania – zamiana zapytania na kategorię i wartości cech, z obsługą wykluczeń (np. *coat without hood*),
    - filtrowanie produktów po cechach i ranking wyników (podobieństwo opisów i zdjęć produktów do zapytania),
    - wyświetlanie przy każdym wyniku cech dopasowanych do zapytania.
2. **Agent konwersacyjny** – czat, w którym agent dopytuje klienta o potrzeby i rekomenduje produkty z katalogu. Pozwala na lepsze dopasowanie do potrzeb klienta, który nie ma jasno określonych preferencji. Zakres prac:
    - pytania doprecyzowujące i rekomendacje wyłącznie z katalogu, z uzasadnieniem wyboru (RAG),
    - przekazanie ustalonych w rozmowie wymagań do wyszukiwarki, aby klient mógł zobaczyć wszystkie pasujące produkty.
3. **Przetwarzanie produktów offline** – jednorazowe przetworzenie zbioru produktów Fashion-Gen. Zakres prac:
    - ograniczenie zbioru do odzieży i przypisanie produktów do 22 kategorii,
    - opracowanie dla każdej kategorii słownika cech z dopuszczalnymi wartościami,
    - ekstrakcja wartości cech: bezpośrednio z danych tam, gdzie informacja jest jednoznaczna (np. płeć, kolor, skład), a pozostałych przez LLM na podstawie opisu i zdjęcia produktu,
    - zapis przetworzonych produktów wraz z embeddingami opisów i zdjęć, z których korzystają wyszukiwarka i agent.

### 5.2. Poza zakresem (przyszłe prace)

1. Automatyczne dostosowywanie się do zmian trendów modowych w zapytaniach użytkowników (np. nagłego wzrostu wyszukiwań konkretnych, modnych cech lub fasonów).
2. Automatyczna obsługa nowych kategorii.
3. Automatyczne wykrywanie luk w cechach produktów.
4. Profilowanie użytkowników.

---

## 6. Wymagania funkcjonalne

### **US‑01: Wyszukiwanie produktów w wyszukiwarce**

- **Jako:** klient,
- **chcę:** wpisać w wyszukiwarkę swoje zapytanie,
- **aby:** otrzymać produkty, które miałem na myśli, formułując frazę wyszukiwania, i rozumieć, z czego wynikają otrzymane wyniki.

> **Kryteria akceptacji (Gherkin):**
> 
> - **Zakładając, że:** katalog produktów został przetworzony offline, a wyszukiwarka jest uruchomiona,
> - **Jeżeli:** klient wpisze zapytanie `black wool coat for winter`,
> - **Wtedy:** system w czasie \< 2 s zwraca listę produktów z kategorii kurtki i płaszcze. Przy każdym wyniku wyświetla dopasowane cechy (np. kolor: czarny, materiał: wełna).
> - **Scenariusz (brak pełnego dopasowania):**
> - **Jeżeli:** żaden produkt nie spełnia wszystkich cech z zapytania,
> - **Wtedy:** system zwraca najbliższe wyniki i oznacza, których fragmentów zapytania nie udało się dopasować.

---

### **US‑02: Rozmowa z agentem**

- **Jako:** klient,
- **chcę:** porozmawiać z agentem, gdy jestem niezdecydowany co do planowanych zakupów,
- **aby:** agent dobrze mi doradził i żebym kupił to, czego potrzebuję.

> **Kryteria akceptacji (Gherkin):**
> 
> - **Zakładając, że:** klient otworzył czat z agentem,
> - **Jeżeli:** klient opisze ogólną potrzebę, np. `I need something warm for autumn walks`,
> - **Wtedy:** agent zadaje pytanie doprecyzowujące (np. o kolor lub fason), a następnie rekomenduje produkty z katalogu wraz z uzasadnieniem wyboru. Pierwszy fragment odpowiedzi pojawia się w ≤ 5 s.
> - **Scenariusz (produkt spoza katalogu):**
> - **Jeżeli:** klient poprosi o produkt spoza zakresu projektu (np. buty),
> - **Wtedy:** agent informuje, że katalog nie obejmuje takich produktów, i nie podaje produktów, których nie ma w katalogu.

---

### **US‑03: Przetwarzanie produktów offline**

- **Jako:** administrator katalogu (członek zespołu),
- **chcę:** jednorazowo przetworzyć zbiór Fashion-Gen,
- **aby:** każdy produkt w zakresie projektu miał przypisaną kategorię i wartości cech, z których korzystają wyszukiwarka i agent.

> **Kryteria akceptacji (Gherkin):**
> 
> - **Zakładając, że:** dostępne są pliki zbioru Fashion-Gen oraz zdefiniowane kategorie i słownik cech z dopuszczalnymi wartościami,
> - **Jeżeli:** administrator uruchomi przetwarzanie,
> - **Wtedy:** każdy produkt w zakresie otrzymuje dokładnie jedną kategorię oraz wartości cech tej kategorii wybrane wyłącznie z listy dopuszczalnych wartości, a produkty spoza zakresu (np. obuwie, akcesoria) są wykluczone z podaniem powodu.
> - **Scenariusz (brak informacji w danych):**
> - **Jeżeli:** opis i skład produktu nie podają wartości cechy,
> - **Wtedy:** wartość ustala LLM na podstawie zdjęcia, a gdy nie jest to możliwe, cecha otrzymuje wartość *Unknown*.

---

## 7. Mierzalne wymagania niefunkcjonalne (NFR)

| ID | Kategoria | Opis | Mierzalna metryka docelowa | Metoda weryfikacji |
| --- | --- | --- | --- | --- |
| **NFR‑01** | Wydajność | Wyszukiwarka zwraca wyniki szybko | 95% zapytań otrzymuje odpowiedź w \< 2 s (p95 \< 2 s) | Skrypt wysyłający ≥ 100 zapytań testowych; pomiar p95 czasu odpowiedzi |
| **NFR‑02** | Wydajność | Agent konwersacyjny odpowiada w akceptowalnym czasie | Pierwsza odpowiedź ≤ 5 s (p95), z możliwością strumieniowania | Pomiar czasu do pierwszego fragmentu odpowiedzi w ≥ 30 rozmowach testowych |
| **NFR‑03** | Skalowalność | System obsługuje cały katalog z zakresu projektu | Wyszukiwanie działa na pełnym zbiorze Fashion-Gen bez spadku wydajności: p95 \< 2 s, jak w NFR‑01 | Test z NFR‑01 wykonany na danych zawierających wszystkie produkty z zakresu |
| **NFR‑04** | Niezawodność | Awaria dostawcy chmury | Przy awarii dostawcy modelu językowego przełączenie na innego dostawcę w ciągu ≤ 60 s | Test z symulowaną awarią głównego dostawcy (zablokowane połączenie); pomiar czasu do pierwszej poprawnej odpowiedzi od dostawcy zapasowego |
| **NFR‑05** | Koszt | Koszt jednego zapytania w wyszukiwarce | \< 0,5 gr za jedno wyszukiwanie | Średni koszt z ≥ 100 zapytań testowych, wyliczony ze zużycia (tokeny, wywołania API) i cennika dostawcy, przeliczony na PLN |
| **NFR‑06** | Koszt | Koszt jednej interakcji z agentem | \< 1 gr za jedną interakcję (pytanie i odpowiedź) | Średni koszt z ≥ 30 interakcji testowych, wyliczony jak w NFR‑05 |

---

## 8. Wstępny rejestr ryzyk i podział ról

### 8.1. Wstępny rejestr ryzyk

P – prawdopodobieństwo, W – wpływ; skala 1–3 (1 – niskie, 2 – średnie, 3 – wysokie).

| ID | Ryzyko | P | W | Wskaźnik ostrzegawczy | Zapobieganie | Plan awaryjny |
| --- | --- | --- | --- | --- | --- | --- |
| R‑01 | Niska dokładność ekstrakcji cech – LLM przypisuje produktom błędne wartości cech | 2 | 3 | \< 80% poprawnych wartości cech w ręcznie sprawdzonej próbce 100 produktów | Zamknięte listy dopuszczalnych wartości i wartość *Unknown* zamiast zgadywania; cechy jednoznaczne w danych (płeć, kolor, skład) przypisywane bez LLM; sprawdzenie jakości na próbce przed przetworzeniem całego katalogu | Ograniczenie zestawu cech do tych, które LLM wyciąga poprawnie; pozostałe cechy nie są używane w wyszukiwaniu |
| R‑02 | Przekroczenie budżetu lub limitów Google Cloud / API LLM | 2 | 3 | Koszt zapytania w wyszukiwarce ≥ 0,5 gr (NFR‑05) lub interakcji z agentem ≥ 1 gr (NFR‑06) | Alerty budżetowe 50% / 90%; cache odpowiedzi; przetwarzanie katalogu wsadowo, jednorazowo | Przejście na mniejszy / tańszy model lub model open-source |
| R‑03 | Zbyt długi czas odpowiedzi potoku z LLM | 2 | 2 | p95 > 2 s dla wyszukiwarki (NFR‑01) lub > 5 s dla agenta (NFR‑02) | Cache częstych zapytań | Tryb wyszukiwarki bez LLM; parser zapytań oparty na regułach i słownikach zamiast LLM |
| R‑04 | <div style="page-break-inside: avoid; break-inside: avoid;">Zmiana warunków licencyjnych zbioru Fashion-Gen</div> | 1 | 3 | <div style="page-break-inside: avoid; break-inside: avoid;">Aktualizacja licencji ograniczająca możliwość wykorzystania zbioru w projekcie</div> | <div style="page-break-inside: avoid; break-inside: avoid;">Weryfikacja warunków licencji na starcie projektu; oddzielenie modułu importu danych od reszty systemu</div> | <div style="page-break-inside: avoid; break-inside: avoid;">Przejście na alternatywny publiczny zbiór produktów odzieżowych</div> |
| R‑05 | Wycofanie lub zmiana cennika używanego modelu LLM | 2 | 2 | Ogłoszenie wycofania modelu lub wzrost ceny o > 50% | Dostęp do LLM przez jedną warstwę abstrakcji; wersja modelu przypięta w konfiguracji | Zmiana modelu w konfiguracji i ponowny pomiar NFR‑01, NFR‑02, NFR‑05 i NFR‑06 |

### 8.2. Podział ról

| Członek zespołu | Zakres pracy |
| --- | --- |
| **Jakub Rybak** | Zaprojektowanie i implementacja odrębnego agenta konwersacyjnego wspomagającego proces zakupowy, opartego na architekturze RAG (Retrieval-Augmented Generation). Przygotowanie, konfiguracja i dostrojenie modelu językowego do zadań ekstrakcji cech oraz płynnej obsługi okna dialogowego. |
| **Michał Sulowski** | Zaprojektowanie i wdrożenie inteligentnego paska wyszukiwania, obejmującego mechanizmy interpretacji intencji użytkownika oraz przekierowań do wyników. Ranking wyników poprzez ich odpowiednie sortowanie oraz przetwarzanie produktów offline. |

---

## 9. Harmonogram prac

Orientacyjny plan na 15 tygodni zajęć. **J** – Jakub Rybak, **M** – Michał Sulowski, **J+M** – wspólnie; ■ – tydzień realizacji zadania.

| Zadanie | Kto | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Analiza Fashion-Gen i ustalenie kategorii | J+M | ■ | ■ | ■ | | | | | | | | | | | | |
| Ustalenie cech i dopuszczalnych wartości (podział działów między osoby) | J+M | | | ■ | ■ | ■ | | | | | | | | | | |
| Wstępne eksperymenty z wyszukiwaniem i rankingiem | M | | ■ | ■ | ■ | ■ | | | | | | | | | | |
| Wstępne eksperymenty z ekstrakcją cech z zapytań | J | | ■ | ■ | ■ | ■ | | | | | | | | | | |
| Ekstrakcja cech produktów przez LLM i sprawdzenie jakości | J | | | | | | ■ | ■ | | | | | | | | |
| Przetworzenie całego katalogu offline (cechy, embeddingi) | M | | | | | | | ■ | ■ | | | | | | | |
| Ekstrakcja cech z zapytań użytkownika | J | | | | | | | | ■ | ■ | | | | | | |
| Ranking produktów na podstawie zapytania | M | | | | | | | | ■ | ■ | | | | | | |
| Implementacja agenta konwersacyjnego | J | | | | | | | | | | ■ | ■ | | | | |
| Połączenie agenta z wyszukiwarką | J+M | | | | | | | | | | | ■ | ■ | | | |
| Testy całego systemu i poprawki | J+M | | | | | | | | | | | | ■ | ■ | ■ | |
| Przygotowanie wersji demonstracyjnej | J+M | | | | | | | | | | | | | | ■ | ■ |

---

## 10. Formalna akceptacja promotora

- [ ] **Akceptacja zakresu i MVP:** Promotor zapoznał się ze specyfikacją wymagań i akceptuje zakres MVP jako podstawę projektu inżynierskiego.

**Podpis promotora:** ............................................................ **Data:** ....................
