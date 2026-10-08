# Fashion Semantic Search & Attribute Extraction Benchmark

Projekt badawczy w ramach pracy inżynierskiej poświęcony dwuetapowemu pipeline'owi semantycznego rozumienia zapytań (*Query Understanding*) w e-commerce modowym.

## Architektura Pipeline'u
1. **Krok 1 (Klasyfikacja Taksonomiczna):** Klasyfikacja zapytania użytkownika do dokładnie jednej z 8 kategorii ubrań (lub `None` dla zapytań spoza domeny).
2. **Krok 2 (Ekstrakcja Atrybutów & Guided Decoding):** Ekstrakcja cech specyficznych dla danej kategorii z wykorzystaniem modeli Pydantic, obsługą marek, wartości wielokrotnych oraz jawnej logiki boolowskiej (`AND` / `OR`).

---

## Struktura Repozytorium

```
.
├── data/
│   ├── fashion_test_benchmark.csv             # Złoty zbiór testowy (92 zapytania Amazon ESCI z etykietami)
│   ├── clothing_queries.csv                   # Odfiltrowane zapytania odzieżowe ESCI
│   └── shopping_queries_dataset_examples.parquet # Źródłowy zbiór Amazon ESCI
│
├── results/                                   # Pełne wyniki ewaluacji benchmarku (CSV + JSON)
│   ├── results_gemini_3_5_flash_lite.*        # Wyniki Gemini 3.5 Flash-Lite
│   ├── gemini_extraction_results_gemini_3_1_flash_lite.* # Wyniki Gemini 3.1 Flash-Lite
│   ├── gemini_extraction_results_gemma_4_26b_a4b_it.*    # Wyniki Gemma 4 26B MoE
│   └── slang_and_polish_results.json          # Wyniki testów zapytań slangowych i wielojęzycznych
│
├── scripts/                                   # Skrypty pomocnicze, analiza danych i weryfikacja biasu
│   ├── export_clothing_queries.py
│   ├── analyze_clothing_queries.py
│   ├── verify_selection_bias.py
│   └── test_slang_and_polish.py
│
├── evaluate_gemini_extraction.py              # Główny skrypt ewaluacji modeli Google Vertex AI
├── evaluate_openrouter.py                     # Skrypt ewaluacji Qwen 3.8 27B na akceleratorach Cerebras
├── MODEL_EVALUATION_SUMMARY.md                # Raport porównawczy modeli (Gemini vs Qwen)
├── pyproject.toml                             # Zależności i konfiguracja projektu
└── uv.lock
```

---

## Wyniki Ewaluacji (Skrót)

| Model | Czas całkowity | Dokładność kategorii | F1-Score |
| :--- | :---: | :---: | :---: |
| **Qwen 3.8 27B @ Cerebras** (OpenRouter) | **~0.6 – 1.3 s** | **100.0%** | **95.0%** |
| **Gemini 3.1 Flash-Lite** (Google Vertex AI) | **~2.28 s** | **98.9%** | **90.2%** |
| **Gemini 3.5 Flash-Lite** (Google Vertex AI) | **~2.72 s** | **97.8%** | **91.4%** |
| **Gemma 4 26B** (Google AI Studio) | **~4.50 s** | **98.9%** | **88.8%** |

Szczegółowy opis w pliku [MODEL_EVALUATION_SUMMARY.md](MODEL_EVALUATION_SUMMARY.md).
