# Query Extraction Engine

Kompleksowy moduł semantycznej ekstrakcji intencji, kategorii, cech katalogowych (zamkniętych i otwartych) oraz pojęć residualnych z zapytań wyszukiwarkowych dla platformy e-commerce modowej.

---

## 📌 Spis treści
1. [Przegląd możliwości](#-przegląd-możliwości)
2. [Struktura modułu (Co gdzie jest)](#-struktura-modułu-co-gdzie-jest)
3. [Dostępne konfiguracje pipeline'u](#-dostępne-konfiguracje-pipelineu)
4. [Dostępne skrypty i CLI](#-dostępne-skrypty-i-cli)
   - [1. Parsowanie zapytań (parser.py)](#1-parsowanie-pojedynczych-zapytań-parserpy)
   - [2. Runner benchmarku (benchmark/run.py)](#2-uruchamianie-benchmarku-benchmarkrunpy)
   - [3. Próbkowanie zapytań (benchmark/dataset.py)](#3-próbkowanie-zbioru-testowego-benchmarkdatasetpy)
   - [4. Testy jednostkowe](#4-uruchamianie-testów-jednostkowych)
5. [Użycie jako biblioteka Python (API)](#-użycie-jako-biblioteka-python-api)
6. [Wyniki benchmarku (N = 250)](#-wyniki-benchmarku-próba-n--250)
7. [Zmienne środowiskowe i wymagania](#-zmienne-środowiskowe-i-wymagania)

---

## 🚀 Przegląd możliwości

Moduł przetwarza surowe zapytanie użytkownika (np. *"czarna dopasowana sukienka na wesele do 250 zł"*, *"men's white cotton tee without elastane"*) na ustrukturyzowany obiekt filtrów wyszukiwarki:

- **Pełne pokrycie 22 kategorii modowych** oraz detekcja zapytań spoza katalogu (`category: null`).
- **Ekstrakcja cech zamkniętych**: kolory, wzory, długość, fason, dekolt, skład materiałowy, rodzaj zapięcia, ocieplenie itp. (zgodnie z restrykcyjnym słownikiem dozwolonych wartości katalogu).
- **Ekstrakcja cech otwartych**:
  - `brand`: nazwa marki (`in`).
  - `price`: cena numeryczna z precyzyjną relacją (`around`, `lte`, `gte`, `lt`, `gt`).
- **Pojęcia residualne (`residual`)**: słowa i frazy wykraczające poza sztywny schemat bazy (styl, okazja, specyficzne detale, np. *"na wesele"*, *"for gym"*, *"oversized"*, *"vintage"*), przekazywane do rankera wektorowego / wyszukiwania semantycznego.
- **Wsparcie wielojęzyczne**: poprawne rozpoznawanie zapytań w języku polskim, angielskim, hiszpańskim oraz tolerancja na literówki.
- **Ultra-niskie opóźnienia**: $\sim 0.7\text{ s}$ w architekturze `full_qwen` dzięki inferencji Cerebras.

---

## 📁 Struktura modułu (Co gdzie jest)

```
query_extraction/
├── README.md                  # Niniejsza dokumentacja
├── __init__.py                # Eksport publicznego API (parse_query, QueryExtractor, CONFIGS)
├── parser.py                  # Główny rejestr konfiguracji, assembler wyników, klasa QueryExtractor i CLI
│
├── core/                      # Rdzeń domeny, schematy i logika promptów
│   ├── catalog.py             # Definicje 22 kategorii, cech, wartości, reguł walidacji i schematów JSON
│   ├── few_shots.py           # Zbiory przykładów: 15 dla kategoryzacji + po 5 dla każdej kategorii (110 łącznie)
│   └── prompts_loader.py      # Moduł wczytujący modularne pliki YAML z cache'owaniem
│
├── clients/                   # Klienci zewnętrznych modeli z obsługą retry i connection poolingu
│   ├── jev.py                 # Klient Jev 1.14 (OpenRouter Decisions API) do kategoryzacji i cech zamkniętych
│   └── llm.py                 # Klient Cerebras (Qwen 3.8 27B, GPT-OSS-120B) oraz Vertex AI (Gemini 3.5 Flash-Lite)
│
├── prompts/                   # Modularne definicje promptów w formacie YAML
│   ├── category_classification.yaml # Instrukcje i kryteria etapu 1 (klasyfikacja kategorii w Jev)
│   ├── closed_features.yaml         # Pytania i kryteria wyboru cech zamkniętych w Jev (dla architektury split)
│   ├── feature_definitions.yaml     # Reguły cech wspólnych i specyfiki residual
│   ├── full_extraction.yaml         # Szablon promptu pełnej ekstrakcji 2-etapowej (LLM)
│   ├── open_extraction.yaml         # Szablon promptu ekstrakcji cech otwartych (brand, price, residual)
│   └── categories/                  # 22 pliki YAML ze specyficznymi regułami per kategoria
│       ├── dresses.yaml
│       ├── t-shirts.yaml
│       ├── jeans.yaml
│       └── ...
│
├── benchmark/                 # Środowisko testowe i ewaluacyjne
│   ├── run.py                 # Główny runner benchmarku z inkrementalnym zapisem JSON (checkpoint)
│   ├── dataset.py             # Wczytywanie i warstwowe próbkowanie (stratified sampling) zbioru testowego
│   ├── evaluate.py            # Obliczanie metryk: F1, Precision, Recall, Exact Match, percentyle latencji, koszty
│   ├── queries/               # Zbiór 1535 zapytań testowych podzielonych na foldery tematyczne
│   └── results/               # Pliki JSON z wynikami benchmarków (np. benchmark_250_seed42.json)
│
└── tests/                     # Testy jednostkowe offline
    ├── test_query_extraction.py # 9 testów offline (schematy, pokrycie 22 kategorii, walidacja, brak wycieku)
    └── test_query_schema.py     # Walidacja poprawności wartości etykiet w zapytaniach benchmarkowych
```

---

## ⚙️ Dostępne konfiguracje pipeline'u

Wszystkie konfiguracje są zdefiniowane w słowniku `CONFIGS` w [`parser.py`](file:///Users/jakubrybak/Projekty/Test/query_extraction/parser.py):

| Klucz konfiguracji | Architektura | Model LLM / Dostawca | Etapy pipeline'u | Typowa latencja p50 | Rekomendacja |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **`full_qwen`** *(domyślna)* | **2-step (Full)** | **Qwen 3.8 27B** (Cerebras, `reasoning: none`) | Jev 1.14 (Kategoria) → Qwen 3.8 27B (Pełna ekstrakcja) | **0.72 s** | 🏆 **Lider jakości i szybkości** (82% Exact Match) |
| **`full_gpt_oss`** | **2-step (Full)** | **GPT-OSS-120B** (Cerebras, `reasoning: low`) | Jev 1.14 (Kategoria) → GPT-OSS-120B (Pełna ekstrakcja) | **0.74 s** | Najtańsza opcja LLM, słabsza w residualu |
| **`full_gemini`** | **2-step (Full)** | **Gemini 3.5 Flash-Lite** (Vertex AI) | Jev 1.14 (Kategoria) → Gemini 3.5 Flash-Lite | **1.35 s** | Najwyższa czystość filtrów (97.2% F1), ale wolniejsza |
| **`split_qwen`** | **3-step (Split)** | **Qwen 3.8 27B** (Cerebras, `reasoning: none`) | Jev (Kategoria) → Jev (Cechy zamknięte) → Qwen (Brand/Price/Residual) | **1.01 s** | Architektura dzielona (większe narzuty sieciowe) |
| **`split_gpt_oss`** | **3-step (Split)** | **GPT-OSS-120B** (Cerebras, `reasoning: low`) | Jev (Kategoria) → Jev (Cechy zamknięte) → GPT-OSS (Brand/Price/Residual) | **1.05 s** | Architektura dzielona |

---

## 🛠️ Dostępne skrypty i CLI

### 1. Parsowanie pojedynczych zapytań (`parser.py`)

Umożliwia szybkie przetestowanie parsowania zapytania bezpośrednio z wiersza poleceń:

```bash
# Podstawowe parsowanie (używa domyślnej konfiguracji full_qwen)
.venv/bin/python -m query_extraction.parser "czarna skórzana kurtka z zamkiem do 300 zł"

# Parsowanie inną konfiguracją (np. full_gemini lub split_qwen)
.venv/bin/python -m query_extraction.parser "orange trench coat with hood" --config full_gemini

# Wyświetlenie pełnego JSON-a z metadanymi czasów i kosztu
.venv/bin/python -m query_extraction.parser "damska koszula w paski zara" --json
```

**Dostępne opcje:**
- `query`: Zapytanie tekstowe do sparsowania.
- `--config`: Wybór pipeline'u (`full_qwen`, `full_gpt_oss`, `full_gemini`, `split_qwen`, `split_gpt_oss`). Domyślnie: `full_qwen`.
- `--json`: Format wyjściowy w czystym JSON (zawiera predykcje, czasy etapów i koszt).

---

### 2. Uruchamianie benchmarku (`benchmark/run.py`)

Uruchamia wsadową ewaluację modeli na wybranym zbiorze danych testowych:

```bash
# Szybki benchmark dla N=30 zapytań (wszystkie 5 konfiguracji)
.venv/bin/python -m query_extraction.benchmark.run --size 30

# Większy benchmark dla N=250 zapytań z losowaniem warstwowym
.venv/bin/python -m query_extraction.benchmark.run --size 250 --seed 42

# Benchmark tylko dla wybranej konfiguracji (np. full_qwen)
.venv/bin/python -m query_extraction.benchmark.run --configs full_qwen --size 100

# Pełny benchmark na całym dostępnym zbiorze (1535 zapytań)
.venv/bin/python -m query_extraction.benchmark.run --all-queries

# Ograniczenie benchmarku tylko do wybranych kategorii
.venv/bin/python -m query_extraction.benchmark.run --category Dresses --category Shirts --size 50
```

**Dostępne opcje:**
- `--configs`: Konfiguracje do uruchomienia (np. `full_qwen`, `split_qwen` lub `all`). Domyślnie: `all`.
- `--size`: Wielkość próby (liczba całkowita) lub `all`. Wybiera próbę warstwową ze wszystkich 22 kategorii. Domyślnie: `30`.
- `--all-queries`: Flaga równoznaczna z `--size all` (uruchamia wszystkie 1535 zapytań).
- `--seed`: Ziarno losowości dla powtarzalnego próbkowania. Domyślnie: `42`.
- `--category`: Ograniczenie benchmarku do określonej kategorii (można powtarzać flagę).
- `--budget-usd`: Limit budżetu API Jev w USD (domyślnie skalowany automatycznie na podstawie wielkości próby).
- `--output`: Własna ścieżka do pliku wynikowego JSON. Domyślnie: `query_extraction/benchmark/results/benchmark_<size>_seed<seed>.json`.
- `--fresh`: Wymuszenie ponownego przeliczenia zapytań od zera (ignoruje istniejący checkpoint).

> [!TIP]
> Runner benchmarku zapisuje stan do pliku JSON po **każdym pojedynczym zapytaniu**. Jeśli przerwiesz proces (np. `Ctrl+C`), ponowne uruchomienie z tą samą ścieżką wznowi pracę dokładnie od miejsca przerwania!

---

### 3. Próbkowanie zbioru testowego (`benchmark/dataset.py`)

Narzędzie pomocnicze do inspekcji i eksportu próbek zapytań testowych:

```bash
# Wygenerowanie losowej próby 50 zapytań do pliku CSV
.venv/bin/python -m query_extraction.benchmark.dataset --size 50 --seed 42 > sample_50.csv
```

**Dostępne opcje:**
- `--size`: Liczba zapytań lub `all`.
- `--seed`: Ziarno losowości (domyślnie `42`).
- `--category`: Ograniczenie do wybranej kategorii.

---

### 4. Uruchamianie testów jednostkowych

Wszystkie testy w `query_extraction/tests/` są testami offline – wykonują się błyskawicznie bez konieczności połączenia z płatnymi API:

```bash
.venv/bin/python -m unittest discover -s query_extraction/tests -v
```

Testy sprawdzają m.in.:
- Pokrycie wszystkich 22 kategorii i integralność kryteriów katalogu.
- Poprawność schematów JSON dla Vertex AI i Cerebras.
- Brak wycieku danych (*zero data leakage*) między 110 przykładami few-shot a bazą zapytań benchmarkowych.
- Poprawność mapowania reguł, operatorów i walidatora odpowiedzi.
- Działanie parsera w trybie offline przy użyciu mocków.

---

## 💻 Użycie jako biblioteka Python (API)

### Proste wywołanie funkcyjne (`parse_query`)

Najprostszy sposób na sparsowanie zapytania w aplikacji:

```python
from query_extraction import parse_query

# Podstawowe parsowanie (domyślnie full_qwen)
result = parse_query("czarna sukienka na wesele do 200 zł")

print(result)
# {
#   "category": "Dresses",
#   "filters": [
#     {"feature": "colors", "operator": "contains_any", "values": ["Black"]},
#     {"feature": "price", "operator": "lte", "value": 200.0}
#   ],
#   "residual": ["na wesele"]
# }

# Parsowanie z dołączeniem metadanych o czasie i kosztach
result_with_meta = parse_query("polo big and tall", config="full_qwen", include_meta=True)
print(result_with_meta["_meta"]["total_latency_seconds"])  # np. 0.684
print(result_with_meta["_meta"]["total_cost_usd"])        # np. 0.0017
```

### Zaawansowane: Klasa `QueryExtractor` (Thread-safe singleton)

Dla serwisów webowych, mikroserwisów FastAPI/Flask i workerów zaleca się użycie instancji `QueryExtractor`, która utrzymuje pulę połączeń HTTP i sesje autoryzacyjne:

```python
from query_extraction import QueryExtractor

# Inicjalizacja ekstraktora (wczytuje katalog i przygotowuje klientów)
extractor = QueryExtractor()

# Opcjonalny warmup połączeń sieciowych przy starcie aplikacji
warmup_times = extractor.warmup(["full_qwen"])
print("Połączenia rozgrzane:", warmup_times)

# Wydajne parsowanie zapytań w pętli obsługi żądań
res = extractor.parse("white silk blouse with long sleeves", config="full_qwen")
```

---

## 📊 Wyniki benchmarku (Próba N = 250)

Zestawienie wyników na zrównoważonej próbie 250 zapytań ze wszystkich 22 kategorii oraz zapytań spoza katalogu:

| Konfiguracja | Kategoria Acc | Zestaw filtrów Acc | Exact Match zapytania | Klauzule F1 | Residual F1 | Opóźnienie p50 | % < 1.0s SLA | Śr. koszt / zap. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`full_qwen`** 🏆 | **100.0%** | **93.6%** | **82.0%** (205/250) | **96.9%** | **80.0%** | **0.719 s** | **94.0%** | **$0.0018** |
| `full_gemini` | **100.0%** | **94.0%** | **80.0%** (200/250) | **97.2%** | 78.6% | 1.351 s | 2.4% | $0.0021 |
| `split_qwen` | **100.0%** | 84.0% | 72.8% (182/250) | 94.1% | 79.6% | 1.007 s | 48.0% | $0.0018 |
| `full_gpt_oss` | **100.0%** | 87.6% | 69.2% (173/250) | 94.2% | 65.5% | 0.735 s | **98.0%** | **$0.0015** |
| `split_gpt_oss` | **100.0%** | 83.6% | 68.0% (170/250) | 94.1% | 72.0% | 1.052 s | 32.8% | $0.0017 |

---

## 🔑 Zmienne środowiskowe i wymagania

W głównym katalogu projektu powinien znajdować się plik `.env` zawierający klucze do dostawców API:

```env
# Klucz API do OpenRouter (dla Jev 1.14: kategoryzacja i cechy zamknięte)
OPENROUTER_API_KEY=sk-or-v1-...

# Klucz API do Cerebras (dla Qwen 3.8 27B oraz GPT-OSS-120B)
CEREBRAS_API_KEY=csk-...

# Opcjonalnie dla Vertex AI (Gemini 3.5 Flash-Lite):
GOOGLE_CLOUD_PROJECT=project-3a86f100-1aae-4780-84b
GOOGLE_CLOUD_LOCATION=global
```

W przypadku korzystania z Vertex AI wymagane jest aktywne uwierzytelnienie Google Cloud Application Default Credentials (`gcloud auth application-default login`).
