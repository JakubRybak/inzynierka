# Raport porównawczy: Query Extraction (22 kategorie + `no_category`, per-category few-shots)

> [!IMPORTANT]
> **Główne wnioski po wprowadzeniu dedykowanych few-shotów i promptów per kategoria:**
> 1. **Skok dokładności we wszystkich 5 podejściach:** Izolacja promptów i przykładów *few-shot* w obrębie wybranej kategorii ([few_shots.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/few_shots.py) — po 5 dedykowanych przykładów na każdą z 22 kategorii, łącznie 110 przykładów + 27 przykładów klasyfikacji kategorii) podniosła dokładność kompletów cech i F1 cech w każdym z 5 wariantów:
>    - **`2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux`:** osiągnął **96.7% (29/30)** dokładności kompletów cech, **99.1% F1 cech** (**100% Recall — 55/55 poprawnych klauzul, 0 brakujących cech, tylko 1 cecha nadmiarowa**) oraz **90.0% (27/30)** pełnej zgodności całego zapytania (Cat + Filters + Residual) przy średnim czasie **0.994 s** (**p50 = 1.024 s**).
>    - **`2a · Jev Cat → Qwen 3.8 27B (Cerebras)`:** osiągnął **93.3% (28/30)** dokładności kompletów cech (wobec 90.0% wcześniej), **97.3% F1 cech** (54/55 TP, 2 nadmiarowe, 1 brakująca), **93.3% (28/30)** dokładności zbioru `residual` oraz **86.7% (26/30)** pełnej zgodności zapytania przy czasie **p50 = 0.830 s**, **p80 = 0.922 s**, **p90 = 0.989 s** (**90.0% zapytań < 1.0 s**).
>    - **`2a · Jev Cat → GPT-OSS-120B (Cerebras)`:** zanotował największy skok jakości filtrów — dokładność kompletów cech wzrosła z 80.0% do **93.3% (28/30)**, a F1 cech z 90.9% do **98.2%** (tylko **1 nadmiarowa** i **1 brakująca** cecha!) przy najszybszym czasie ze wszystkich podejść: **p50 = 0.732 s**, **p80 = 0.816 s**, **p90 = 0.855 s**, **p95 = 0.919 s** (**96.7% zapytań < 1.0 s**, **36.7% < 0.7 s**).
>    - **`2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)`:** osiągnął **96.7% (29/30)** dokładności kompletów cech, **99.1% F1 cech** (**0 cech nadmiarowych — 100.0% Precision!**) oraz **86.7% (26/30)** pełnej zgodności zapytania, a czas p50 spadł z 1.250 s do **1.124 s** (sam krok Gemini: **p50 = 0.903 s**).
> 2. **Rekomendacja architektoniczna (< 1.0 s):**
>    - Do pracy produkcyjnej z twardym wymogiem **< 1.0 s** najlepszym wyborem end-to-end jest **`2a · Jev Cat → Qwen 3.8 27B (Cerebras)`** (**p50 = 0.830 s, p90 = 0.989 s**, 93.3% dokładności kompletów cech, 93.3% dokładności `residual`, 86.7% pełnego dopasowania zapytania), a jeśli priorytetem są wyłącznie filtry twarde i czas bliski 0.7 s — **`2a · Jev Cat → GPT-OSS-120B (Cerebras)`** (**p50 = 0.732 s, p95 = 0.919 s**, 98.2% F1 cech).

---

## Metodologia i rygor testowy

1. **Rozmiar próbki testowej:** 30 zapytań (stratyfikowane losowanie [sample_queries.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/sample_queries.py) `--size 30 --seed 42`, obejmujące wszystkie 22 kategorie produktowe oraz `no_category`, języki EN/PL/ES).
2. **Prompty i few-shoty ściśle w obrębie danej kategorii:** Po wyborze kategorii w Kroku 1 każdy kolejny etap (`2a Full`, `2b.1 Jev Features`, `2b.2 Aux`) otrzymuje wyłącznie definicje cech, reguły oraz 5 przykładów *few-shot* należących do tej konkretnej kategorii ([few_shots.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/few_shots.py)).
3. **Separacja danych (Zero Data Leakage):** Wszystkie 137 przykładów *few-shot* (27 w Kroku 1 + 22×5 = 110 w Krokach 2a/2b) są w 100% rozłączne z całym zbiorem 1 535 zapytań benchmarkowych (weryfikowane testem jednostkowym w [test_query_extraction.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/tests/test_query_extraction.py)).
4. **Równoważność semantyczna w ewaluacji:** Pojedyncza wartość w `contains_all` i `contains_any` jest traktowana jako równoważna (`contains_all ['Cotton'] == contains_any ['Cotton']`), a nazwy marek (`brand`) są porównywane bezwielkościowo.
5. **Konfiguracja modeli i pomiar czasu:** każdy model działa na minimalnym thinkingu (`Gemini 3.5 Flash-Lite`: `0` thought tokens; `Qwen 3.8 27B`: `reasoning_effort='none'`; `GPT-OSS-120B`: `reasoning_effort='low'`), `temperature = 0`, ścisły Structured Output (`responseSchema` / `json_schema`). Pauza rate-limitu (5 req/min dla darmowego `GPT-OSS-120B`) odbywa się poza zegarem `time.perf_counter()`.

---

## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)

Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.

| Podejście / Wariant | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 0.818 s | **0.830 s** | **0.922 s** | **0.989 s** | **1.070 s** | 1.236 s | 4/30 (13.3%) | **27/30 (90.0%)** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 0.730 s | **0.732 s** | **0.816 s** | **0.855 s** | **0.919 s** | 1.175 s | 11/30 (36.7%) | **29/30 (96.7%)** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 0.994 s | **1.024 s** | **1.084 s** | **1.140 s** | **1.250 s** | 1.326 s | 1/30 (3.3%) | **14/30 (46.7%)** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 1.048 s | **1.036 s** | **1.215 s** | **1.261 s** | **1.280 s** | 1.481 s | 1/30 (3.3%) | **12/30 (40.0%)** |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 1.115 s | **1.124 s** | **1.249 s** | **1.311 s** | **1.326 s** | 1.379 s | 1/30 (3.3%) | **3/30 (10.0%)** |

---

## 2. Czas poszczególnych etapów (Stage-by-Stage Latency Breakdown)

| Etap | Model / API | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Krok 1: Wybór kategorii** *(wspólny)* | `typesafe/jev-1.14` (OpenRouter) | 30 | 0.246 s | **0.222 s** | **0.301 s** | **0.307 s** | **0.309 s** | 0.346 s |
| **Krok 2b.1: Cechy zamknięte** *(per-cat Jev)* | `typesafe/jev-1.14` (OpenRouter) | 29 | 0.387 s | **0.356 s** | **0.419 s** | **0.489 s** | **0.519 s** | 0.571 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0.500 s | **0.507 s** | **0.593 s** | **0.620 s** | **0.702 s** | 0.906 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0.592 s | **0.554 s** | **0.690 s** | **0.783 s** | **0.811 s** | 1.028 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `gemini-3.5-flash-lite` (Vertex AI) | 29 | 0.899 s | **0.903 s** | **1.016 s** | **1.021 s** | **1.028 s** | 1.119 s |
| **Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)** | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0.387 s | **0.390 s** | **0.492 s** | **0.508 s** | **0.525 s** | 0.534 s |
| **Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)** | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0.443 s | **0.388 s** | **0.598 s** | **0.696 s** | **0.698 s** | 0.701 s |

---

## 3. Dokładność (Accuracy kompletów cech, pojedynczych cech, nadmiarowe i brakujące cechy)

### 3.1. Accuracy na poziomie całego zapytania i kompletów filtrów (Exact Set Match)

| Podejście / Wariant | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 30/30 (100.0%) | **28/30 (93.3%)** | 28/30 (93.3%) | 30/30 (100.0%) | 28/30 (93.3%) | **26/30 (86.7%)** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 30/30 (100.0%) | **28/30 (93.3%)** | 29/30 (96.7%) | 29/30 (96.7%) | 22/30 (73.3%) | **22/30 (73.3%)** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 30/30 (100.0%) | **29/30 (96.7%)** | 29/30 (96.7%) | 30/30 (100.0%) | 28/30 (93.3%) | **27/30 (90.0%)** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 30/30 (100.0%) | **28/30 (93.3%)** | 29/30 (96.7%) | 29/30 (96.7%) | 24/30 (80.0%) | **22/30 (73.3%)** |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 30/30 (100.0%) | **29/30 (96.7%)** | 29/30 (96.7%) | 30/30 (100.0%) | 26/30 (86.7%) | **26/30 (86.7%)** |

### 3.2. Dokładność pojedynczych cech (Clause-level Precision / Recall / F1) oraz cechy nadmiarowe i brakujące

W całej próbce 30 zapytań oczekiwanych było łącznie **55 klauzul filtrów** (49 klauzul cech zamkniętych + 6 klauzul `brand`/`price`).

| Podejście / Wariant | Poprawne filtry (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe / zapytanie | Brakujące cechy (FN) | Brakujące / zapytanie | Precision | Recall | **F1 cech (Accuracy cech)** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 54 / 55 | **2** | 0.07 | 1 | 0.03 | 96.4% | 98.2% | **97.3%** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 54 / 55 | **1** | 0.03 | 1 | 0.03 | 98.2% | 98.2% | **98.2%** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 55 / 55 | **1** | 0.03 | 0 | 0.00 | 98.2% | 100.0% | **99.1%** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 54 / 55 | **2** | 0.07 | 1 | 0.03 | 96.4% | 98.2% | **97.3%** |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 54 / 55 | **0** | 0.00 | 1 | 0.03 | 100.0% | 98.2% | **99.1%** |

### 3.3. Wpływ dedykowanych few-shotów per kategoria (Porównanie: Wspólne vs Per-Kategoria)

| Podejście / Wariant | Komplet filtrów (Przed → **Po**) | F1 cech (Przed → **Po**) | Nadmiarowe FP (Przed → **Po**) | Całe zapytanie Exact (Przed → **Po**) | Czas p50 (Przed → **Po**) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux** | 90.0% → **96.7%** | 95.6% → **99.1%** | 4 → **1** | 80.0% → **90.0%** | 1.062 s → **1.024 s** |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite** | 96.7% → **96.7%** | 98.2% → **99.1%** | 1 → **0** | 83.3% → **86.7%** | 1.250 s → **1.124 s** |
| **2a · Jev Cat → Qwen 3.8 27B** | 90.0% → **93.3%** | 96.4% → **97.3%** | 2 → **2** | 86.7% → **86.7%** | 0.765 s → **0.830 s** |
| **2a · Jev Cat → GPT-OSS-120B** | 80.0% → **93.3%** | 90.9% → **98.2%** | 5 → **1** | 60.0% → **73.3%** | 0.752 s → **0.732 s** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux** | 90.0% → **93.3%** | 95.6% → **97.3%** | 4 → **2** | 73.3% → **73.3%** | 1.053 s → **1.036 s** |

### 3.4. Metryki `residual` oraz koszty API

| Podejście / Wariant | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt na 30 zapytań (USD) | Średni koszt / 1000 zapytań (USD) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | **88.9%** | 85.7% | 92.3% | 94.1% | $0.0537 | **$1.79** |
| **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | **62.1%** | 56.2% | 69.2% | 76.5% | $0.0455 | **$1.52** |
| **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | **82.8%** | 75.0% | 92.3% | 94.1% | $0.0606 | **$2.02** |
| **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | **69.0%** | 62.5% | 76.9% | 82.4% | $0.0586 | **$1.95** |
| **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | **86.7%** | 76.5% | 100.0% | 76.5% | $0.0619 | **$2.06** |

---

## 4. Analiza różnic i przypadków błędnych na próbce testowej

### 2a · Jev Cat → Qwen 3.8 27B (Cerebras)
- `collared cardigan with no buttons` (Cardigans): brakujące filtry: `[('closure_type', 'not_in', ('Button',))]`; nadmiarowe filtry: `[('closure_type', 'in', ('Open Front',))]`;
- `long workout tops for women loose fit` (Tank tops & Camisoles): residual `['for workout']` (oczekiwano `['workout']`).
- `blusas azul celeste` (Blouses): nadmiarowe filtry: `[('gender', 'in', ('Women',))]`;
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### 2a · Jev Cat → GPT-OSS-120B (Cerebras)
- `brown leopard-print shirt` (Shirts): residual `['leopard']` (oczekiwano `['leopard print']`).
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `jean a line skirt` (Skirts): nadmiarowe filtry: `[('main_composition', 'contains_any', ('Cotton',))]`; residual `[]` (oczekiwano `['jean']`).
- `plaid wool bomber jacket` (Bombers): residual `['plaid']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): brakujące filtry: `[('brand', 'in', ('adidas',))]`; residual `['asidas']` (oczekiwano `[]`).
- `polyester sweatshirt for sublimation` (Sweatshirts): residual `['sublimation']` (oczekiwano `['for sublimation']`).
- `tshirt with thumb holes men` (T-shirts): residual `['thumb holes']` (oczekiwano `['with thumb holes']`).
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### 2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)
- `long workout tops for women loose fit` (Tank tops & Camisoles): residual `['long', 'for workout', 'loose fit']` (oczekiwano `['workout']`).
- `100% cotton shorts women` (Shorts): nadmiarowe filtry: `[('main_composition', 'contains_none', ('Elastane',))]`;
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### 2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): brakujące filtry: `[('brand', 'in', ('adidas',))]`; nadmiarowe filtry: `[('brand', 'in', ('asidas',))]`;
- `100% cotton shorts women` (Shorts): nadmiarowe filtry: `[('main_composition', 'contains_none', ('Elastane',))]`;
- `polyester sweatshirt for sublimation` (Sweatshirts): residual `['sublimation']` (oczekiwano `['for sublimation']`).
- `polo golf shirts adidas` (Polos): residual `['golf shirts']` (oczekiwano `['golf']`).
- `tshirt with thumb holes men` (T-shirts): residual `['thumb holes']` (oczekiwano `['with thumb holes']`).
- `white trench cout` (Trench Coats): residual `['cout']` (oczekiwano `[]`).
- `high waist sweatpants women` (Sweatpants & Lounge Pants): residual `['high waist']` (oczekiwano `[]`).

### 2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)
- `collared cardigan with no buttons` (Cardigans): brakujące filtry: `[('closure_type', 'not_in', ('Button',))]`; residual `['with no buttons']` (oczekiwano `[]`).
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): residual `['asidas']` (oczekiwano `[]`).
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

