# Raport benchmarku: Query Extraction (N = 30, konfiguracje: 5)

> [!IMPORTANT]
> **Podsumowanie wyników uruchomienia:**
> - **`full_qwen` (Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)):** komplet filtrów **28/30 (93.3%)**, F1 cech **97.3%** (TP=54/55, FP=2, FN=1), pełna zgodność zapytania **26/30 (86.7%)**, czas **p50 = 0.830 s**, **p90 = 0.989 s** (**90.0% < 1.0 s**).
> - **`full_gpt_oss` (Full · Jev (Category) → GPT-OSS-120B (Full Extraction)):** komplet filtrów **28/30 (93.3%)**, F1 cech **98.2%** (TP=54/55, FP=1, FN=1), pełna zgodność zapytania **22/30 (73.3%)**, czas **p50 = 0.732 s**, **p90 = 0.855 s** (**96.7% < 1.0 s**).
> - **`full_gemini` (Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)):** komplet filtrów **29/30 (96.7%)**, F1 cech **99.1%** (TP=54/55, FP=0, FN=1), pełna zgodność zapytania **26/30 (86.7%)**, czas **p50 = 1.124 s**, **p90 = 1.311 s** (**10.0% < 1.0 s**).
> - **`split_qwen` (Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)):** komplet filtrów **29/30 (96.7%)**, F1 cech **99.1%** (TP=55/55, FP=1, FN=0), pełna zgodność zapytania **27/30 (90.0%)**, czas **p50 = 1.024 s**, **p90 = 1.140 s** (**46.7% < 1.0 s**).
> - **`split_gpt_oss` (Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)):** komplet filtrów **28/30 (93.3%)**, F1 cech **97.3%** (TP=54/55, FP=2, FN=1), pełna zgodność zapytania **22/30 (73.3%)**, czas **p50 = 1.036 s**, **p90 = 1.261 s** (**40.0% < 1.0 s**).
>
> **Najwyższa jakość ekstrakcji cech:** `split_qwen` (Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)) — **99.1% F1 cech** oraz **90.0%** pełnej zgodności (`split_qwen`).
> **Rekomendacja < 1.0 s:** `full_qwen` (Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)) — **p50 = 0.830 s**, najszybszy wariant: `full_gpt_oss` (**p50 = 0.732 s**).

---

## Metodologia i konfiguracja testu

1. **Zbiór testowy:** `query_extraction/queries` — **30 zapytań** (losowanie stratyfikowane `--seed 42`).
2. **Prompty i few-shoty per kategoria:** Po klasyfikacji kategorii (`category_classification.yaml`) każdy kolejny etap (`full_extraction.yaml`, `closed_features.yaml`, `open_extraction.yaml`) otrzymuje wyłącznie definicje cech, reguły oraz 5 przykładów *few-shot* należących do tej konkretnej kategorii (`prompts/categories/<category>.yaml`).
3. **Równoważność semantyczna w ewaluacji:** Pojedyncza wartość w `contains_all` i `contains_any` jest traktowana jako równoważna (`contains_all ['Cotton'] == contains_any ['Cotton']`), a nazwy marek (`brand`) są porównywane bezwielkościowo ([evaluate.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/benchmark/evaluate.py)).
4. **Pomiar czasu:** Minimalny thinking (`temperature = 0`), ścisły Structured Output (`responseSchema` / `json_schema`).

---

## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)

Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.

| Scenariusz | Opis przepływu | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_qwen` | **Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)** | 0.818 s | **0.830 s** | **0.922 s** | **0.989 s** | **1.070 s** | 1.236 s | 4/30 (13.3%) | **27/30 (90.0%)** |
| `full_gpt_oss` | **Full · Jev (Category) → GPT-OSS-120B (Full Extraction)** | 0.730 s | **0.732 s** | **0.816 s** | **0.855 s** | **0.919 s** | 1.175 s | 11/30 (36.7%) | **29/30 (96.7%)** |
| `full_gemini` | **Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)** | 1.115 s | **1.124 s** | **1.249 s** | **1.311 s** | **1.326 s** | 1.379 s | 1/30 (3.3%) | **3/30 (10.0%)** |
| `split_qwen` | **Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)** | 0.994 s | **1.024 s** | **1.084 s** | **1.140 s** | **1.250 s** | 1.326 s | 1/30 (3.3%) | **14/30 (46.7%)** |
| `split_gpt_oss` | **Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)** | 1.048 s | **1.036 s** | **1.215 s** | **1.261 s** | **1.280 s** | 1.481 s | 1/30 (3.3%) | **12/30 (40.0%)** |

---

## 2. Czas poszczególnych części (Stage-by-Stage Latency Breakdown)

| Część (Etap) | Model / API | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`category` (Klasyfikacja kategorii)** *(wspólna)* | `typesafe/jev-1.14` (OpenRouter) | 30 | 0.246 s | **0.222 s** | **0.301 s** | **0.307 s** | **0.309 s** | 0.346 s |
| **`closed_features` (Cechy zamknięte ze schematu)** | `typesafe/jev-1.14` (OpenRouter) | 29 | 0.387 s | **0.356 s** | **0.419 s** | **0.489 s** | **0.519 s** | 0.571 s |
| **`full_qwen` (Full Extraction (cechy zamknięte + brand + price + residual))** | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0.592 s | **0.554 s** | **0.690 s** | **0.783 s** | **0.811 s** | 1.028 s |
| **`full_gpt_oss` (Full Extraction (cechy zamknięte + brand + price + residual))** | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0.500 s | **0.507 s** | **0.593 s** | **0.620 s** | **0.702 s** | 0.906 s |
| **`full_gemini` (Full Extraction (cechy zamknięte + brand + price + residual))** | `gemini-3.5-flash-lite` (Vertex AI) | 29 | 0.899 s | **0.903 s** | **1.016 s** | **1.021 s** | **1.028 s** | 1.119 s |
| **`open_qwen` (Open Extraction (brand + price + residual po Jev Closed Features))** | `qwen-3.8-27b` (Cerebras, `none`) | 29 | 0.387 s | **0.390 s** | **0.492 s** | **0.508 s** | **0.525 s** | 0.534 s |
| **`open_gpt_oss` (Open Extraction (brand + price + residual po Jev Closed Features))** | `gpt-oss-120b` (Cerebras, `low`) | 29 | 0.443 s | **0.388 s** | **0.598 s** | **0.696 s** | **0.698 s** | 0.701 s |

---

## 3. Dokładność (Accuracy kompletów cech, pojedynczych cech, nadmiarowe i brakujące cechy)

### 3.1. Accuracy na poziomie całego zapytania i kompletów filtrów (Exact Set Match)

| Scenariusz | Opis przepływu | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_qwen` | **Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)** | 30/30 (100.0%) | **28/30 (93.3%)** | 28/30 (93.3%) | 30/30 (100.0%) | 28/30 (93.3%) | **26/30 (86.7%)** |
| `full_gpt_oss` | **Full · Jev (Category) → GPT-OSS-120B (Full Extraction)** | 30/30 (100.0%) | **28/30 (93.3%)** | 29/30 (96.7%) | 29/30 (96.7%) | 22/30 (73.3%) | **22/30 (73.3%)** |
| `full_gemini` | **Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)** | 30/30 (100.0%) | **29/30 (96.7%)** | 29/30 (96.7%) | 30/30 (100.0%) | 26/30 (86.7%) | **26/30 (86.7%)** |
| `split_qwen` | **Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)** | 30/30 (100.0%) | **29/30 (96.7%)** | 29/30 (96.7%) | 30/30 (100.0%) | 28/30 (93.3%) | **27/30 (90.0%)** |
| `split_gpt_oss` | **Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)** | 30/30 (100.0%) | **28/30 (93.3%)** | 29/30 (96.7%) | 29/30 (96.7%) | 24/30 (80.0%) | **22/30 (73.3%)** |

### 3.2. Dokładność pojedynczych cech (Clause-level Precision / Recall / F1) oraz cechy nadmiarowe i brakujące

W całej próbce 30 zapytań oczekiwanych było łącznie **55 klauzul filtrów** (49 klauzul cech zamkniętych + 6 klauzul `brand`/`price`).

| Scenariusz | Opis przepływu | Poprawne filtry (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe / zapytanie | Brakujące cechy (FN) | Brakujące / zapytanie | Precision | Recall | **F1 cech (Accuracy cech)** |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_qwen` | **Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)** | 54 / 55 | **2** | 0.07 | 1 | 0.03 | 96.4% | 98.2% | **97.3%** |
| `full_gpt_oss` | **Full · Jev (Category) → GPT-OSS-120B (Full Extraction)** | 54 / 55 | **1** | 0.03 | 1 | 0.03 | 98.2% | 98.2% | **98.2%** |
| `full_gemini` | **Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)** | 54 / 55 | **0** | 0.00 | 1 | 0.03 | 100.0% | 98.2% | **99.1%** |
| `split_qwen` | **Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)** | 55 / 55 | **1** | 0.03 | 0 | 0.00 | 98.2% | 100.0% | **99.1%** |
| `split_gpt_oss` | **Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)** | 54 / 55 | **2** | 0.07 | 1 | 0.03 | 96.4% | 98.2% | **97.3%** |

### 3.3. Metryki `residual` oraz koszty API

| Scenariusz | Opis przepływu | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt na 30 zapytań (USD) | Średni koszt / 1000 zapytań (USD) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_qwen` | **Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)** | **88.9%** | 85.7% | 92.3% | 94.1% | $0.0537 | **$1.79** |
| `full_gpt_oss` | **Full · Jev (Category) → GPT-OSS-120B (Full Extraction)** | **62.1%** | 56.2% | 69.2% | 76.5% | $0.0455 | **$1.52** |
| `full_gemini` | **Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)** | **86.7%** | 76.5% | 100.0% | 76.5% | $0.0619 | **$2.06** |
| `split_qwen` | **Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)** | **82.8%** | 75.0% | 92.3% | 94.1% | $0.0606 | **$2.02** |
| `split_gpt_oss` | **Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)** | **69.0%** | 62.5% | 76.9% | 82.4% | $0.0586 | **$1.95** |

---

## 4. Analiza różnic i przypadków błędnych na próbce testowej

### `full_qwen` — Full · Jev (Category) → Qwen 3.8 27B (Full Extraction)
- `collared cardigan with no buttons` (Cardigans): brakujące filtry: `[('closure_type', 'not_in', ('Button',))]`; nadmiarowe filtry: `[('closure_type', 'in', ('Open Front',))]`;
- `long workout tops for women loose fit` (Tank tops & Camisoles): residual `['for workout']` (oczekiwano `['workout']`).
- `blusas azul celeste` (Blouses): nadmiarowe filtry: `[('gender', 'in', ('Women',))]`;
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### `full_gpt_oss` — Full · Jev (Category) → GPT-OSS-120B (Full Extraction)
- `brown leopard-print shirt` (Shirts): residual `['leopard']` (oczekiwano `['leopard print']`).
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `jean a line skirt` (Skirts): nadmiarowe filtry: `[('main_composition', 'contains_any', ('Cotton',))]`; residual `[]` (oczekiwano `['jean']`).
- `plaid wool bomber jacket` (Bombers): residual `['plaid']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): brakujące filtry: `[('brand', 'in', ('adidas',))]`; residual `['asidas']` (oczekiwano `[]`).
- `polyester sweatshirt for sublimation` (Sweatshirts): residual `['sublimation']` (oczekiwano `['for sublimation']`).
- `tshirt with thumb holes men` (T-shirts): residual `['thumb holes']` (oczekiwano `['with thumb holes']`).
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### `full_gemini` — Full · Jev (Category) → Gemini 3.5 Flash-Lite (Full Extraction)
- `collared cardigan with no buttons` (Cardigans): brakujące filtry: `[('closure_type', 'not_in', ('Button',))]`; residual `['with no buttons']` (oczekiwano `[]`).
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): residual `['asidas']` (oczekiwano `[]`).
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### `split_qwen` — Split · Jev (Category) → Jev (Closed Features) → Qwen 3.8 27B (Open Extraction)
- `long workout tops for women loose fit` (Tank tops & Camisoles): residual `['long', 'for workout', 'loose fit']` (oczekiwano `['workout']`).
- `100% cotton shorts women` (Shorts): nadmiarowe filtry: `[('main_composition', 'contains_none', ('Elastane',))]`;
- `lee slacks for women relaxed fit` (Trousers): residual `['slacks']` (oczekiwano `[]`).

### `split_gpt_oss` — Split · Jev (Category) → Jev (Closed Features) → GPT-OSS-120B (Open Extraction)
- `silk bodysuit long sleevetops` (Bodysuits): residual `['tops']` (oczekiwano `[]`).
- `asidas womens hoodies` (Hoodies & Zipups): brakujące filtry: `[('brand', 'in', ('adidas',))]`; nadmiarowe filtry: `[('brand', 'in', ('asidas',))]`;
- `100% cotton shorts women` (Shorts): nadmiarowe filtry: `[('main_composition', 'contains_none', ('Elastane',))]`;
- `polyester sweatshirt for sublimation` (Sweatshirts): residual `['sublimation']` (oczekiwano `['for sublimation']`).
- `polo golf shirts adidas` (Polos): residual `['golf shirts']` (oczekiwano `['golf']`).
- `tshirt with thumb holes men` (T-shirts): residual `['thumb holes']` (oczekiwano `['with thumb holes']`).
- `white trench cout` (Trench Coats): residual `['cout']` (oczekiwano `[]`).
- `high waist sweatpants women` (Sweatpants & Lounge Pants): residual `['high waist']` (oczekiwano `[]`).

