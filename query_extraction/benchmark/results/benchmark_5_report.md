# Raport benchmarku: Query Extraction (N = 5, konfiguracje: 5)

> [!IMPORTANT]
> **Podsumowanie wyników uruchomienia:**
> - **`2a_qwen` (2a · Jev Cat → Qwen 3.8 27B (Cerebras)):** komplet filtrów **5/5 (100.0%)**, F1 cech **100.0%** (TP=8/8, FP=0, FN=0), pełna zgodność zapytania **5/5 (100.0%)**, czas **p50 = 0.814 s**, **p90 = 1.022 s** (**80.0% < 1.0 s**).
> - **`2a_gpt_oss` (2a · Jev Cat → GPT-OSS-120B (Cerebras)):** komplet filtrów **5/5 (100.0%)**, F1 cech **100.0%** (TP=8/8, FP=0, FN=0), pełna zgodność zapytania **3/5 (60.0%)**, czas **p50 = 0.835 s**, **p90 = 0.919 s** (**100.0% < 1.0 s**).
> - **`2a_gemini` (2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)):** komplet filtrów **5/5 (100.0%)**, F1 cech **100.0%** (TP=8/8, FP=0, FN=0), pełna zgodność zapytania **5/5 (100.0%)**, czas **p50 = 1.423 s**, **p90 = 1.555 s** (**20.0% < 1.0 s**).
> - **`2b_qwen` (2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)):** komplet filtrów **5/5 (100.0%)**, F1 cech **100.0%** (TP=8/8, FP=0, FN=0), pełna zgodność zapytania **5/5 (100.0%)**, czas **p50 = 1.103 s**, **p90 = 1.187 s** (**40.0% < 1.0 s**).
> - **`2b_gpt_oss` (2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)):** komplet filtrów **5/5 (100.0%)**, F1 cech **100.0%** (TP=8/8, FP=0, FN=0), pełna zgodność zapytania **4/5 (80.0%)**, czas **p50 = 1.128 s**, **p90 = 1.210 s** (**40.0% < 1.0 s**).
>
> **Najwyższa jakość ekstrakcji cech:** `2a_qwen` (2a · Jev Cat → Qwen 3.8 27B (Cerebras)) — **100.0% F1 cech** oraz **100.0%** pełnej zgodności (`2a_qwen`).
> **Rekomendacja < 1.0 s:** `2a_qwen` (2a · Jev Cat → Qwen 3.8 27B (Cerebras)) — **p50 = 0.814 s**, najszybszy wariant: `2a_qwen` (**p50 = 0.814 s**).

---

## Metodologia i konfiguracja testu

1. **Zbiór testowy:** `query_extraction/queries` — **5 zapytań** (losowanie stratyfikowane `--seed 42`).
2. **Prompty i few-shoty per kategoria:** Po klasyfikacji kategorii w Kroku 1 każdy kolejny etap (`2a Full`, `2b.1 Jev Features`, `2b.2 Aux`) otrzymuje wyłącznie definicje cech, reguły oraz 5 przykładów *few-shot* należących do tej konkretnej kategorii ([few_shots.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/few_shots.py)).
3. **Równoważność semantyczna w ewaluacji:** Pojedyncza wartość w `contains_all` i `contains_any` jest traktowana jako równoważna (`contains_all ['Cotton'] == contains_any ['Cotton']`), a nazwy marek (`brand`) są porównywane bezwielkościowo ([evaluate.py](file:///Users/jakubrybak/Projekty/Test/query_extraction/evaluate.py)).
4. **Pomiar czasu:** Minimalny thinking (`temperature = 0`), ścisły Structured Output (`responseSchema` / `json_schema`).

---

## 1. Czas całkowity pipeline'u (End-to-End Latency: p50, p80, p90, p95)

Cel projektowy: **< 1,0 s obowiązkowo**, **< 0,7 s idealnie**.

| Konfiguracja | Podejście / Wariant | Średnia | **p50** | **p80** | **p90** | **p95** | Max | **< 0,7 s** | **< 1,0 s (Obowiązkowe)** |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2a_qwen` | **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 0.766 s | **0.814 s** | **0.951 s** | **1.022 s** | **1.058 s** | 1.093 s | 1/5 (20.0%) | **4/5 (80.0%)** |
| `2a_gpt_oss` | **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 0.717 s | **0.835 s** | **0.868 s** | **0.919 s** | **0.945 s** | 0.971 s | 1/5 (20.0%) | **5/5 (100.0%)** |
| `2a_gemini` | **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 1.176 s | **1.423 s** | **1.470 s** | **1.555 s** | **1.598 s** | 1.640 s | 1/5 (20.0%) | **1/5 (20.0%)** |
| `2b_qwen` | **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 0.927 s | **1.103 s** | **1.146 s** | **1.187 s** | **1.208 s** | 1.228 s | 1/5 (20.0%) | **2/5 (40.0%)** |
| `2b_gpt_oss` | **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 0.935 s | **1.128 s** | **1.168 s** | **1.210 s** | **1.231 s** | 1.252 s | 1/5 (20.0%) | **2/5 (40.0%)** |

---

## 2. Czas poszczególnych etapów (Stage-by-Stage Latency Breakdown)

| Etap | Model / API | Liczba wywołań | Średnia | **p50** | **p80** | **p90** | **p95** | Max |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Krok 1: Wybór kategorii** *(wspólny)* | `typesafe/jev-1.14` (OpenRouter) | 5 | 0.235 s | **0.214 s** | **0.266 s** | **0.284 s** | **0.294 s** | 0.303 s |
| **Krok 2b.1: Cechy zamknięte** *(per-cat Jev)* | `typesafe/jev-1.14` (OpenRouter) | 4 | 0.496 s | **0.502 s** | **0.533 s** | **0.547 s** | **0.555 s** | 0.562 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `qwen-3.8-27b` (Cerebras, `none`) | 4 | 0.663 s | **0.613 s** | **0.703 s** | **0.770 s** | **0.803 s** | 0.837 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `gpt-oss-120b` (Cerebras, `low`) | 4 | 0.602 s | **0.587 s** | **0.670 s** | **0.693 s** | **0.704 s** | 0.715 s |
| **Krok 2a: Pełna ekstrakcja (cechy+brand+price+residual)** | `gemini-3.5-flash-lite` (Vertex AI) | 4 | 1.176 s | **1.223 s** | **1.271 s** | **1.304 s** | **1.321 s** | 1.337 s |
| **Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)** | `qwen-3.8-27b` (Cerebras, `none`) | 4 | 0.368 s | **0.365 s** | **0.397 s** | **0.404 s** | **0.407 s** | 0.410 s |
| **Krok 2b.2: Ekstrakcja Aux (brand+price+residual po Jev)** | `gpt-oss-120b` (Cerebras, `low`) | 4 | 0.379 s | **0.384 s** | **0.422 s** | **0.428 s** | **0.431 s** | 0.434 s |

---

## 3. Dokładność (Accuracy kompletów cech, pojedynczych cech, nadmiarowe i brakujące cechy)

### 3.1. Accuracy na poziomie całego zapytania i kompletów filtrów (Exact Set Match)

| Konfiguracja | Podejście / Wariant | Kategoria (Accuracy) | **Komplet wszystkich filtrów** (Accuracy kompletów cech) | Komplet cech zamkniętych (bez brand/price) | Komplet `brand` + `price` | Residual (Exact Set) | **Całe zapytanie 100% Exact** (Cat+Filters+Residual) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `2a_qwen` | **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 5/5 (100.0%) | **5/5 (100.0%)** | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | **5/5 (100.0%)** |
| `2a_gpt_oss` | **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 5/5 (100.0%) | **5/5 (100.0%)** | 5/5 (100.0%) | 5/5 (100.0%) | 3/5 (60.0%) | **3/5 (60.0%)** |
| `2a_gemini` | **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 5/5 (100.0%) | **5/5 (100.0%)** | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | **5/5 (100.0%)** |
| `2b_qwen` | **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 5/5 (100.0%) | **5/5 (100.0%)** | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | **5/5 (100.0%)** |
| `2b_gpt_oss` | **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 5/5 (100.0%) | **5/5 (100.0%)** | 5/5 (100.0%) | 5/5 (100.0%) | 4/5 (80.0%) | **4/5 (80.0%)** |

### 3.2. Dokładność pojedynczych cech (Clause-level Precision / Recall / F1) oraz cechy nadmiarowe i brakujące

W całej próbce 5 zapytań oczekiwanych było łącznie **8 klauzul filtrów** (8 klauzul cech zamkniętych + 0 klauzul `brand`/`price`).

| Konfiguracja | Podejście / Wariant | Poprawne filtry (TP) | **Ilość nadmiarowych cech (FP)** | Nadmiarowe / zapytanie | Brakujące cechy (FN) | Brakujące / zapytanie | Precision | Recall | **F1 cech (Accuracy cech)** |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2a_qwen` | **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | 8 / 8 | **0** | 0.00 | 0 | 0.00 | 100.0% | 100.0% | **100.0%** |
| `2a_gpt_oss` | **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | 8 / 8 | **0** | 0.00 | 0 | 0.00 | 100.0% | 100.0% | **100.0%** |
| `2a_gemini` | **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | 8 / 8 | **0** | 0.00 | 0 | 0.00 | 100.0% | 100.0% | **100.0%** |
| `2b_qwen` | **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | 8 / 8 | **0** | 0.00 | 0 | 0.00 | 100.0% | 100.0% | **100.0%** |
| `2b_gpt_oss` | **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | 8 / 8 | **0** | 0.00 | 0 | 0.00 | 100.0% | 100.0% | **100.0%** |

### 3.3. Metryki `residual` oraz koszty API

| Konfiguracja | Podejście / Wariant | Residual F1 (koncepty) | Residual Precision | Residual Recall | Pusty residual poprawny (`[]`) | Koszt na 5 zapytań (USD) | Średni koszt / 1000 zapytań (USD) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `2a_qwen` | **2a · Jev Cat → Qwen 3.8 27B (Cerebras)** | **100.0%** | 100.0% | 100.0% | 100.0% | $0.0076 | **$1.52** |
| `2a_gpt_oss` | **2a · Jev Cat → GPT-OSS-120B (Cerebras)** | **0.0%** | 0.0% | 0.0% | 75.0% | $0.0065 | **$1.29** |
| `2a_gemini` | **2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)** | **100.0%** | 100.0% | 100.0% | 100.0% | $0.0087 | **$1.73** |
| `2b_qwen` | **2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)** | **100.0%** | 100.0% | 100.0% | 100.0% | $0.0086 | **$1.72** |
| `2b_gpt_oss` | **2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)** | **66.7%** | 50.0% | 100.0% | 75.0% | $0.0083 | **$1.67** |

---

## 4. Analiza różnic i przypadków błędnych na próbce testowej

### `2a_qwen` — 2a · Jev Cat → Qwen 3.8 27B (Cerebras)
- Brak błędów (5/5 idealnie zgodne).

### `2a_gpt_oss` — 2a · Jev Cat → GPT-OSS-120B (Cerebras)
- `polyester sweatshirt for sublimation` (Sweatshirts): residual `['sublimation']` (oczekiwano `['for sublimation']`).
- `plaid wool bomber jacket` (Bombers): residual `['plaid']` (oczekiwano `[]`).

### `2a_gemini` — 2a · Jev Cat → Gemini 3.5 Flash-Lite (Vertex AI)
- Brak błędów (5/5 idealnie zgodne).

### `2b_qwen` — 2b · Jev Cat → Jev Feat → Qwen 3.8 27B Aux (Cerebras)
- Brak błędów (5/5 idealnie zgodne).

### `2b_gpt_oss` — 2b · Jev Cat → Jev Feat → GPT-OSS-120B Aux (Cerebras)
- `high waist sweatpants women` (Sweatpants & Lounge Pants): residual `['high waist']` (oczekiwano `[]`).

