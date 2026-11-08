# Raport porównawczy: Query Extraction (22 kategorie + `no_category`)

> [!IMPORTANT]
> **Główny wniosek z eksperymentu:**  
> Najlepszym podejściem pod względem **zarówno czasu (< 1,0 s), jak i całkowitej dokładności end-to-end (86,7% pełnej zgodności zapytania, 96,4% F1 cech, 92,9% F1 residualu)** okazał się wariant **2a: `Jev 1.14 (Kategoria) → Qwen 3.8 27B (Cerebras, thinking=none)`**:
> - **Czas całkowity (2a Qwen 3.8 27B):** **p50 = 0,765 s**, **p80 = 0,838 s**, **p90 = 0,914 s**, **p95 = 0,997 s** (93,3% zapytań mieści się poniżej obowiązkowego progu `< 1,0 s`).
> - **Dlaczego 2a wygrywa z 2b czasowo:** Wariant **2b** wymaga **trzech sekwencyjnych wywołań sieciowych** (`Jev Cat [0,24 s] → Jev Feat [0,41 s] → Cerebras Aux [0,33–0,39 s]`), co sumarycznie daje **p50 = 1,05–1,06 s**, przekraczając limit 1,0 s. Wariant **2a** wykonuje tylko **dwa wywołania** (`Jev Cat [0,24 s] → Cerebras Full [0,50 s]`), oszczędzając ~0,30 s na każdym zapytaniu oraz ~1,04 USD na każde 1 000 zapytań na koszcie drugiego wywołania Jev.
> - **Najwyższa dokładność samych filtrów twardych:** `2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)` osiągnął **96,7% (29/30)** dokładności kompletów filtrów i **98,2% F1** pojedynczych cech (tylko 1 cecha nadmiarowa na 30 zapytań), jednak sam etap Gemini na Vertex AI trwa średnio **1,02 s** (**p50 = 1,25 s** dla całego pipeline'u), więc nie spełnia wymogu `< 1,0 s`.

---

## Metodologia i rygor testowy

1. **Próbka testowa:** 30 zapytań wylosowanych stratyfikowanie ([sample_queries.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/sample_queries.py) `--size 30 --seed 42`) — pokrywa wszystkie **22 kategorie produktowe + `no_category`** oraz proporcje językowe (93,3% EN, 3,3% PL, 3,3% ES).
2. **Zero Data Leakage:** Wszystkie przykłady *few-shot* w promptach ([llm_parser.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/llm_parser.py)) oraz w definicjach Jev ([jev_parser.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/jev_parser.py)) mają **0% części wspólnej** z pełnym zbiorem 1 535 zapytań benchmarkowych (zweryfikowane testem jednostkowym w [test_query_extraction.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/tests/test_query_extraction.py)).
3. **Konfiguracja modeli:**
   - Wszystkie modele działają na minimalnym thinkingu (`Gemini 3.5 Flash-Lite`: brak `thinkingConfig` / `0` tokenów myślenia; `Qwen 3.8 27B`: `reasoning_effort="none"`; `GPT-OSS-120B`: `reasoning_effort="low"`), `temperature = 0` i wymuszonym **Structured Output** (`responseSchema` na Vertex AI, `strict: true` `json_schema` na Cerebras).
4. **Higiena pomiaru latencji i limitów Cerebras:**
   - Każdy klient wykonuje najpierw wywołanie rozgrzewkowe (*warmup*) zestawiające sesję HTTP/TLS Keep-Alive.
   - Na darmowym koncie Cerebras model `qwen-3.8-27b` ma limit **450 req/min**, natomiast `gpt-oss-120b` ma ścisły limit **5 req/min**. Pacing rate-limitu dla `gpt-oss-120b` (odczekanie na odnowienie token-bucketa) został umieszczony **poza zegarem pomiarowym** `time.perf_counter()`, dzięki czemu czasy w raporcie odzwierciedlają wyłącznie rzeczywisty czas obsługi zapytania przez serwer.

---

## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)

Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.

| Podejście / Wariant | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 0,793 s | **0,765 s** | **0,838 s** | **0,914 s** | **0,997 s** | 1,716 s | 6/30 (20,0%) | **28/30 (93,3%)** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 0,777 s | **0,752 s** | **0,855 s** | **0,922 s** | **1,110 s** | 1,248 s | 7/30 (23,3%) | **27/30 (90,0%)** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 1,097 s | **1,053 s** | **1,280 s** | **1,302 s** | **1,471 s** | 1,611 s | 1/30 (3,3%) | 9/30 (30,0%) |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 1,100 s | **1,062 s** | **1,211 s** | **1,279 s** | **1,806 s** | 2,572 s | 1/30 (3,3%) | 13/30 (43,3%) |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 1,262 s | **1,250 s** | **1,464 s** | **1,643 s** | **1,750 s** | 1,866 s | 1/30 (3,3%) | 3/30 (10,0%) |

---

## 2. Czas poszczególnych etapów (Stage-by-Stage Latency Breakdown)

Poniższa tabela pokazuje dokładnie, ile trwa każdy pojedynczy krok w każdym z badanych podejść:

| Etap | Model i dostawca | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Krok 1: Wybór kategorii** *(wspólny dla 2a i 2b)* | `typesafe/jev-1.14` (OpenRouter) | 30 | 0,276 s | **0,242 s** | **0,311 s** | **0,406 s** | **0,462 s** | 0,508 s |
| **Krok 2b.1: Cechy zamknięte** *(tylko wariant 2b)* | `typesafe/jev-1.14` (OpenRouter) | 29 | 0,421 s | **0,408 s** | **0,505 s** | **0,515 s** | **0,543 s** | 0,683 s |
| **Krok 2a: Pełna ekstrakcja** *(cechy+brand+price+residual)* | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0,534 s | **0,505 s** | **0,556 s** | **0,629 s** | **0,662 s** | 1,477 s |
| **Krok 2a: Pełna ekstrakcja** *(cechy+brand+price+residual)* | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0,518 s | **0,499 s** | **0,596 s** | **0,630 s** | **0,700 s** | 0,740 s |
| **Krok 2a: Pełna ekstrakcja** *(cechy+brand+price+residual)* | `gemini-3.5-flash-lite` (Vertex AI) | 29 | 1,019 s | **0,990 s** | **1,177 s** | **1,292 s** | **1,317 s** | 1,570 s |
| **Krok 2b.2: Ekstrakcja Aux** *(brand+price+residual po Jev)* | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0,431 s | **0,331 s** | **0,402 s** | **0,497 s** | **1,144 s** | 1,654 s |
| **Krok 2b.2: Ekstrakcja Aux** *(brand+price+residual po Jev)* | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0,428 s | **0,391 s** | **0,490 s** | **0,555 s** | **0,589 s** | 0,848 s |

**Obserwacje dotyczące czasów etapów:**
- Wywołanie pomocnicze **Krok 2b.2 (`Aux`)** na Cerebras jest szybsze o ~0,11–0,17 s na medianie (`0,331 s` dla Qwena, `0,391 s` dla GPT-OSS) od pełnego wywołania **Krok 2a (`Full`)** (`0,505 s` / `0,499 s`), ponieważ ma krótszy prompt i prostszy schemat JSON.
- Jednak ta oszczędność (~0,15 s) jest mniejsza niż narzut **Kroku 2b.1 (`Jev Features`)**, który dla 44–77 pytań na kategorię zajmuje **p50 = 0,408 s** (`p80 = 0,505 s`). W rezultacie sekwencja `Krok 1 + Krok 2b.1 + Krok 2b.2` jest o ~0,30 s wolniejsza niż `Krok 1 + Krok 2a`.

---

## 3. Dokładność (Accuracy cech, kompletów cech, cechy nadmiarowe i brakujące, residual)

### 3.1. Accuracy na poziomie całego zapytania i kompletów filtrów (Exact Set Match)

*Uwaga metodyczna:* Porównanie filtrów uwzględnia równoważność semantyczną `contains_all` i `contains_any` dla pojedynczej wartości oraz bezwielkościowe dopasowanie nazwy marki (`brand`).

| Podejście / Wariant | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 30/30 (100,0%) | **29/30 (96,7%)** | 29/30 (96,7%) | 30/30 (100,0%) | 26/30 (86,7%) | **25/30 (83,3%)** |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 30/30 (100,0%) | **27/30 (90,0%)** | 28/30 (93,3%) | 29/30 (96,7%) | **28/30 (93,3%)** | **26/30 (86,7%)** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 30/30 (100,0%) | **27/30 (90,0%)** | 27/30 (90,0%) | 29/30 (96,7%) | 27/30 (90,0%) | **24/30 (80,0%)** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 30/30 (100,0%) | **27/30 (90,0%)** | 27/30 (90,0%) | 29/30 (96,7%) | 25/30 (83,3%) | **22/30 (73,3%)** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 30/30 (100,0%) | **24/30 (80,0%)** | 25/30 (83,3%) | 29/30 (96,7%) | 23/30 (76,7%) | **18/30 (60,0%)** |

---

### 3.2. Dokładność pojedynczych cech (Clause-level Accuracy) oraz cechy nadmiarowe i brakujące

W całej próbce 30 zapytań oczekiwanych było łącznie **55 klauzul filtrów** (49 klauzul cech zamkniętych + 6 klauzul `brand`/`price`).

| Podejście / Wariant | Poprawne cechy (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe cechy / zapytanie | Brakujące cechy (FN) | Brakujące cechy / zapytanie | Precision cech | Recall cech | **F1 cech (Accuracy cech)** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 54 / 55 | **1** | 0,03 | 1 | 0,03 | 98,2% | 98,2% | **98,2%** |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 53 / 55 | **2** | 0,07 | 2 | 0,07 | 96,4% | 96,4% | **96,4%** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 54 / 55 | **4** | 0,13 | 1 | 0,03 | 93,1% | 98,2% | **95,6%** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 54 / 55 | **4** | 0,13 | 1 | 0,03 | 93,1% | 98,2% | **95,6%** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 50 / 55 | **5** | 0,17 | 5 | 0,17 | 90,9% | 90,9% | **90,9%** |

---

### 3.3. Dodatkowe metryki: jakość `residual` oraz koszty API

| Podejście / Wariant | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt za 30 zapytań (USD)* | Szacowany koszt / 1 000 zapytań (USD)* |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | **92,9%** | 86,7% | 100,0% | 88,2% (15/17) | $0,0032 Jev *(+$0,0523 cennikowo)* | **$0,11 Jev** *(+$1,74 Cerebras)* |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | **89,7%** | 81,2% | 100,0% | 88,2% (15/17) | $0,0334 Jev *(+$0,0227 cennikowo)* | **$1,15 Jev** *(+$0,72 Cerebras)* |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | **82,8%** | 75,0% | 92,3% | 82,4% (14/17) | $0,0032 Jev + $0,0612 GCP | **$2,15** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | **78,6%** | 73,3% | 84,6% | 88,2% (15/17) | $0,0334 Jev *(+$0,0205 cennikowo)* | **$1,15 Jev** *(+$0,64 Cerebras)* |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | **66,7%** | 58,8% | 76,9% | 76,5% (13/17) | $0,0032 Jev *(+$0,0445 cennikowo)* | **$0,11 Jev** *(+$1,48 Cerebras)* |

*\*Uwaga kosztowa: Na darmowym koncie Cerebras rzeczywisty koszt wywołań Qwen i GPT-OSS wyniósł **$0,00**. Całkowity realnie pobrany koszt przeprowadzenia wszystkich eksperymentów wyniósł ~**$0,033 USD** w OpenRouter (Jev) i ~**$0,061 USD** w GCP Vertex AI.*

---

## 4. Analiza błędów i różnic między podejściami

### Dlaczego `Qwen 3.8 27B (2a)` wypadł lepiej niż `GPT-OSS-120B (2a)`?
1. **Operatory zbiorowe kolorów (`contains_all` vs `contains_any`, `equals_set`):**
   - `Qwen 3.8 27B` bezbłędnie rozróżnił `T-shirt in black and white only` (`equals_set`), `pink and blue camisole, no red` (`contains_all` + `contains_none`) oraz `red and black plaid dress shirt` (`contains_all`).
   - `GPT-OSS-120B` przy minimalnym thinkingu (`low`) w 3 zapytaniach pomylił `contains_all` z `contains_any` lub `equals_set` z `contains_all`.
2. **Czystość `residual`:**
   - `Qwen 3.8 27B` uzyskał **100% Recallu** na konceptach residualowych i **93,3% (28/30)** idealnie zgodnych list `residual`.
   - `GPT-OSS-120B` w wariancie `2a` kilkukrotnie zostawił w `residual` cechy już zmapowane do filtrów (np. `['spaghetti straps', 'V-neck']` czy `['plaid']`), co w wariancie `2b` (gdy dostał listę cech z Jev) zostało w dużej mierze wyeliminowane (wzrost dokładności kompletów filtrów z 80% do 90%).

### Skąd wzięły się 4 nadmiarowe cechy w wariancie `2b (Jev Features)`?
- **Krok 1 (`Jev Category`) zadziałał ze 100% skutecznością (30/30)**, poprawnie klasyfikując wszystkie 22 kategorie, zapytania po polsku i hiszpańsku, literówki (`white trench cout`, `coctail dress`, `asidas womens hoodies`) oraz przypadek `no_category` (`elegant outfit for a wedding` → `null`).
- W **Kroku 2b.1 (`Jev Features`)** pojawiły się dokładnie 3 nadmiarowe cechy zamknięte na 30 zapytań:
  1. W `biker jeans for men skinny fit` oraz `czarne bojówki z gumką w pasie do 200 zł` Jev oprócz poprawnego `fit = Skinny` / `waistband_type = Elasticized` dodał `leg_shape = Tapered`, ponieważ definicja `Tapered` w promptach ekstrakcji produktów wspominała o zwężanych nogawkach typu skinny/joggers.
  2. W `asidas womens hoodies` Jev oprócz poprawnego `hood in ["With Hood"]` dodał redundantne wykluczenie `hood not_in ["Without Hood"]`.
- Pozostała 1 różnica na korzyść `Gemini 3.5 Flash-Lite` w tym zapytaniu to literówka w marce: zapytanie `asidas womens hoodies` — `Gemini` automatycznie skorygował literówkę `asidas` → `Adidas` (i zostawił `asidas` w residualu), podczas gdy `Qwen` zostawił `asidas` w residualu, a `GPT-OSS` wyciągnął `brand in ["asidas"]`.

---

## 5. Podsumowanie plików w repozytorium

Wszystkie moduły i wyniki zostały zapisane w katalogu `query_extraction/`:
- [catalog.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/catalog.py) — katalog 22 kategorii, definicje cech i generator schematów Structured Output dla Vertex AI i Cerebras.
- [jev_parser.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/jev_parser.py) — klient i generatory zapytań `typesafe/jev-1.14` (Krok 1: Kategoria, Krok 2b.1: Cechy i operatory).
- [llm_parser.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/llm_parser.py) — klienci `VertexGeminiClient` i `CerebrasClient` (z obsługą rate-limitu poza pomiarem czasu) oraz prompty dla wariantów `2a` i `2b`.
- [evaluate.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/evaluate.py) — ewaluator metryk (percentyle `p50, p80, p90, p95`, dokładność kompletów cech, pojedynczych cech, cechy nadmiarowe/brakujące, F1 residualu).
- [run_benchmark.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/run_benchmark.py) — skrypt uruchomieniowy z blokadą przecieku danych i wznawianiem z checkpointu.
- [benchmark_report.md](file:///Users/jakubrybak/Projekty/Test/query_extraction/benchmark_report.md) oraz [benchmark_30_seed42.json](file:///Users/jakubrybak/Projekty/Test/query_extraction/results/benchmark_30_seed42.json) — wygenerowany raport i surowe dane pomiarowe.
- [test_query_extraction.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/tests/test_query_extraction.py) — testy jednostkowe.
