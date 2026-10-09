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
│   ├── fashion_test_benchmark.csv             # Złoty zbiór testowy (109 zapytań: Amazon ESCI + PL i Slang)
│   ├── clothing_queries.csv                   # Odfiltrowane zapytania odzieżowe ESCI
│   └── shopping_queries_dataset_examples.parquet # Źródłowy zbiór Amazon ESCI
│
├── docs/                                      # Dokumentacja i raporty badawcze
│   ├── MODEL_EVALUATION_SUMMARY.md            # Raport porównawczy modeli (Gemini vs Qwen)
│   └── PIPELINE_ARCHITECTURE_GUIDE.md         # Opis taksonomii, cech, logiki AND/OR i promptów
│
├── evaluation/                                # Skrypty ewaluacji modeli (harness testowy)
│   ├── evaluate_gemini_extraction.py          # Główny skrypt ewaluacji modeli Google Vertex AI
│   └── evaluate_openrouter.py                 # Skrypt ewaluacji Qwen 3.8 27B na Cerebras
│
├── results/                                   # Pełne wyniki ewaluacji benchmarku (109 zapytań, CSV + JSON)
│   ├── openrouter_qwen_3_8_27b_results.*      # Wyniki Qwen 3.8 27B (Cerebras)
│   ├── gemini_extraction_results_gemini_3_5_flash_lite.* # Wyniki Gemini 3.5 Flash-Lite (Region EU)
│   └── gemini_extraction_results_gemini_2_5_flash_lite.* # Wyniki Gemini 2.5 Flash-Lite (Region Warszawa)
│
├── scripts/                                   # Skrypty pomocnicze, analiza danych i weryfikacja biasu
│   ├── export_clothing_queries.py
│   ├── analyze_clothing_queries.py
│   ├── verify_selection_bias.py
│   └── test_slang_and_polish.py
│
├── pyproject.toml                             # Zależności i konfiguracja projektu
└── uv.lock
```

---

## Wyniki Ewaluacji (Pełny Benchmark: 109 Zapytań)

| Model | Region / Silnik | Średni czas | Kategoria (Krok 1) | Atrybuty F1 | PL & Slang (K1 / F1) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gemini 3.5 Flash-Lite** | Vertex AI (`eu`) | **~1.83 s** | **98.2%** | **90.7%** | **100% / 95.9%** |
| **Qwen 3.8 27B** | Cerebras (OpenRouter) | **~2.29 s** *(pacing)* | **95.4%** | **91.5%** | **82.4% / 90.1%** |
| **Gemini 2.5 Flash-Lite** | Vertex AI (Warszawa) | **~1.48 s** | **98.2%** | **81.2%** | **100% / 78.8%** |

Szczegółowy opis w pliku [docs/MODEL_EVALUATION_SUMMARY.md](docs/MODEL_EVALUATION_SUMMARY.md).

