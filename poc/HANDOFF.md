# Handoff: Dane i Query Parser dla UI / Search Bara

Ten dokument zawiera wszystkie niezbędne informacje techniczne potrzebne do zbudowania interfejsu użytkownika (UI z search barem) oraz zintegrowania parsera zapytań z bazą produktów.

---

## 1. Struktura katalogów w `poc/`

Po reorganizacji projekt podzielony jest na dwa główne moduły:

```text
poc/
├── feature_extraction/      # Ekstrakcja cech z produktów (dane katalogowe)
│   ├── embeddings/          # Wektory Gemini Embedding 2 (3072 dim)
│   ├── prompts/             # Definicje cech i reguły dla LLM
│   ├── reference/           # Ręcznie zweryfikowany reference bank (60 produktów)
│   ├── results/             # GŁÓWNY KATALOG WYEKSTRAHOWANYCH PRODUKTÓW
│   │   ├── products.jsonl   # Główny plik z danymi produktów (JSON Lines)
│   │   ├── products.parquet # Równoważny plik w formacie Parquet
│   │   ├── summary.json     # Podsumowanie pilota (statusy, koszty)
│   │   └── benchmark_eval.json # Wyniki benchmarku jakościowego parsera
│   ├── runs/                # Historia przebiegów (smoke_6, pilot_sync)
│   └── samples/             # Zestaw pilotażowy (pilot_900)
│
├── query_parsing/           # Parser zapytań użytkownika z search bara
│   ├── prompts/             # Prompty z few-shotami (category.md, t-shirts.md, dresses.md, tank-tops-and-camisoles.md)
│   ├── schemas/             # Ścisłe schematy JSON odpowiedzi (Vertex AI responseSchema)
│   ├── rules.md             # Biznesowe reguły mapowania zapytań na filtry
│   ├── structured_output.md # Dokumentacja kontraktów wyjścia modeli
│   └── amazon_clothing_queries.csv # Korpus testowy 10k realnych zapytań
│
├── scripts/                 # Kod wykonawczy
│   ├── query_parser.py      # GŁÓWNY SILNIK PARSOWANIA ZAPYTAŃ (do importu w UI)
│   ├── run_benchmark.py     # Skrypt testujący dokładność i czasy
│   ├── llm_pipeline.py      # Pipeline ekstrakcji produktów
│   └── run_pilot.py         # Skrypt uruchamiający ekstrakcję pilota
│
└── tests/                   # Testy jednostkowe (test_query_parser.py, test_llm_pipeline.py)
```

---

## 2. Gdzie są dane i w jakiej postaci?

### Ścieżka do bazy produktów
- **JSONL:** `poc/feature_extraction/results/products.jsonl`
- **Parquet:** `poc/feature_extraction/results/products.parquet`

### Statystyka i filtracja
- Zestaw pilotażowy liczy 900 produktów z FashionGen (po 300 z każdej z 3 kategorii: `T-shirts`, `Dresses`, `Tank tops & Camisoles`).
- **WAŻNE dla wyszukiwarki:** Do indeksu i wyszukiwarki ładujemy **wyłącznie produkty ze statusem `status == "ready"`** (jest ich **893** sztuki). Pozostałe 7 produktów (`needs_review` / `pending`) miało wady w danych źródłowych.

### Schemat rekordu produktu (`products.jsonl`)

Każda linia to obiekt JSON o następującej strukturze:

```json
{
  "product_id": "2174687",
  "brand": "Comme des Garçons Shirt",
  "section": "Tops",
  "category": "T-shirts",
  "status": "ready",
  "features": {
    "gender": "Men",
    "colors": ["Black"],
    "main_composition": {
      "Cotton": 100.0
    },
    "neckline": "Crewneck",
    "sleeve_length": "Short Sleeve",
    "pattern": "Solid",
    "fit": "Regular",
    "length": "Regular"
  },
  "feature_metadata": { ... },
  "exclusion_reasons": []
}
```

### Pola kluczowe dla UI i filtrowania:
| Pole | Typ | Opis / Wartości |
|---|---|---|
| `product_id` | `string` | Unikalne ID produktu z FashionGen (np. `"2174687"`) |
| `brand` | `string` | Marka produktu (np. `"Comme des Garçons Shirt"`, `"Rag & Bone"`) |
| `section` | `string` | Sekcja nadrzędna: `"Tops"` lub `"Dresses"` |
| `category` | `string` | Kategoria: `"T-shirts"`, `"Dresses"`, `"Tank tops & Camisoles"` |
| `status` | `string` | Musi być `"ready"` |
| `features` | `dict` | Słownik wyekstrahowanych cech specyficznych dla danej kategorii (patrz niżej) |

### Dostępne cechy w `features`:
- **Wspólne:**
  - `gender`: `"Men"`, `"Women"`, `"Unisex"`
  - `colors`: lista stringów, np. `["Black"]`, `["Blue", "White"]`
  - `main_composition`: słownik `{składnik: procent}`, np. `{"Cotton": 100.0}`, `{"Silk": 95.0, "Elastane": 5.0}`
  - `pattern`: `"Solid"`, `"Striped"`, `"Graphic"`, `"Floral"`, `"Polka Dot"`, itp.
  - `fit`: `"Regular"`, `"Slim"`, `"Oversized"`, `"Loose"`, itp.
  - `length`: `"Regular"`, `"Cropped"`, `"Long"`, `"Mini"`, `"Midi"`, `"Maxi"`
- **Dla T-shirts:**
  - `neckline`: `"Crewneck"`, `"V-Neck"`, `"Henley"`, `"Polo"`, itp.
  - `sleeve_length`: `"Short Sleeve"`, `"Long Sleeve"`, `"Sleeveless"`
- **Dla Dresses:**
  - `neckline`: `"V-Neck"`, `"Round Neck"`, `"Off-the-Shoulder"`, itp.
  - `sleeve_length`: `"Sleeveless"`, `"Short Sleeve"`, `"Long Sleeve"`
  - `straps_or_sleeves`: `"Straps"`, `"Sleeves"`, `"Strapless"`
- **Dla Tank tops & Camisoles:**
  - `neckline`: `"Scoop Neck"`, `"Square Neck"`, `"V-Neck"`, itp.
  - `straps_or_sleeves`: `"Spaghetti Straps"`, `"Wide Straps"`, `"Halterneck"`

---

## 3. Query Parser (`poc/scripts/query_parser.py`)

Silnik parsowania zapytań naturalnych z search bara (np. *"czarna bawełniana koszulka nike"* lub *"red midi floral dress for wedding"*).

### Architektura: 2-krokowy pipeline Vertex AI
Działa w oparciu o model `gemini-3.5-flash-lite` z wymuszoną strukturą JSON (`responseSchema`):
1. **Krok 1 (Category Classification):**
   - Klasyfikuje zapytanie do jednej z 3 kategorii: `"T-shirts"`, `"Dresses"`, `"Tank tops & Camisoles"` lub zwraca `null`.
   - **Optymalizacja:** Jeśli zapytanie jest poza katalogiem (np. buty, jeansy, garnitur) lub zbyt ogólne, zwraca `category: null` i **natychmiast pomija Krok 2** (oszczędność czasu i kosztów: latencja ~0.6s).
2. **Krok 2 (Category-Specific Feature & Residual Extraction):**
   - Na podstawie kategorii ładuje dedykowany prompt z regułami i few-shotami (`poc/query_parsing/prompts/<category>.md`) oraz schemat JSON (`poc/query_parsing/schemas/<category>.json`).
   - Ekstrahuje:
     - **Strukturalne filtry (`filters`):** cechy, operatory i dopuszczalne wartości ze słownika (w tym markę `brand`).
     - **Frazę rezydualną (`residual`):** fragmenty zapytania, które nie pasują do sztywnych filtrów atrybutowych (np. okazje: *"na wesele"*, *"do biura"*, styl: *"vintage"*, *"casual"*). Fraza rezydualna służy do wyszukiwania wektorowego/semantycznego (np. embeddings) lub tekstowego BM25.

---

### Jak używać w kodzie Pythona (integracja z backendem UI)

```python
from poc.scripts.query_parser import QueryParser, ParsedQuery

# 1. Inicjalizacja parsera (najlepiej jako singleton w aplikacji backendowej)
parser = QueryParser(
    project="project-3a86f100-1aae-4780-84b", # lub ustaw zmienną env GOOGLE_CLOUD_PROJECT
    model="gemini-3.5-flash-lite",             # szybki model produkcyjny
    location="global",                         # endpoint global
    thinking="NONE"                            # NONE dla ultra niskiego opóźnienia wyszukiwarki
)

# 2. Parsowanie zapytania użytkownika
query = "czarna sukienka na wesele"
result: ParsedQuery = parser.parse(query)

# 3. Dostęp do wyników
print(result.category)               # "Dresses"
print(result.residual)               # "na wesele"
print(result.total_latency_seconds)  # np. 1.72s

for f in result.filters:
    print(f.feature, f.operator, f.values)
    # colors contains_any ['Black']

# 4. Eksport do słownika lub JSON
data_dict = result.to_dict()
json_string = result.to_json()
```

---

### Struktura zwracanego obiektu `ParsedQuery`

Obiekt dataclass `ParsedQuery` (oraz jego odpowiednik `result.to_dict()`):

```python
{
  "query": "czarna koszulka nike regular fit",
  "category": "T-shirts",
  "filters": [
    {
      "feature": "brand",
      "operator": "in",
      "values": ["Nike"]
    },
    {
      "feature": "colors",
      "operator": "contains_any",
      "values": ["Black"]
    },
    {
      "feature": "fit",
      "operator": "in",
      "values": ["Regular"]
    }
  ],
  "residual": "",
  "step1_latency_seconds": 0.72,
  "step2_latency_seconds": 1.15,
  "total_latency_seconds": 1.87,
  "metadata": {
    "model": "gemini-3.5-flash-lite",
    "thinking": "NONE",
    "total_tokens": {"input": 4120, "output": 45, "total": 4165},
    "estimated_cost_usd": 0.001348
  }
}
```

Gdy zapytanie jest poza katalogiem (np. `"niebieskie jeansy rurki"`):
```json
{
  "query": "niebieskie jeansy rurki",
  "category": null,
  "filters": [],
  "residual": "niebieskie jeansy rurki",
  "step1_latency_seconds": 0.61,
  "step2_latency_seconds": 0.0,
  "total_latency_seconds": 0.61,
  "metadata": { ... }
}
```

---

### Operatory w filtrach (`FilterClause`)
- `in` / `not_in` — dla cech jedno-wartościowych (np. `gender`, `fit`, `neckline`, `brand`).
- `contains_any` / `contains_none` — dla list wartości (np. `colors`).
- `equals` / `not_equals` — dla specyficznych dopasowań ścisłych.
- `gte` / `lte` — dla filtrów numerycznych / proporcji (np. minimalna zawartość bawełny).

---

### Uruchomienie z linii komend (CLI)

```bash
# Tryb pojedynczego zapytania z czytelnym podsumowaniem:
.venv/bin/python poc/scripts/query_parser.py "black silk evening dress"

# Tryb JSON (np. do testowania z zewnętrznymi skryptami):
.venv/bin/python poc/scripts/query_parser.py "oversized cotton t-shirt" --json

# Tryb interaktywny REPL (wpisywanie zapytań w pętli):
.venv/bin/python poc/scripts/query_parser.py
```

---

## 4. Wydajność, koszty i benchmark

- **Dokładność kategoryzacji:** **96.2%** w benchmarku na 26 zapytaniach spoza zbioru few-shot.
- **Średnie czasy odpowiedzi (`thinking: NONE`):**
  - Krok 1 (Kategoria): **~0.75s**
  - Krok 2 (Cechy): **~1.18s**
  - Łącznie (zapytanie z cechami): **~1.6 - 1.9s**
  - Łącznie (zapytanie odrzucone / poza zakresem): **~0.6 - 0.8s**
- **Średni koszt per zapytanie:** **~$0.0016** (ok. 0.16 centa za 2-krokowe zapytanie).
- **Obsługa języków:** Działa w języku angielskim oraz polskim (np. *"czarna sukienka na wesele"* $\to$ `colors contains_any ['Black']`, `residual: "na wesele"`).

---

## 5. Jak spiąć to z Search Barem (Rekomendowany przepływ w UI)

```text
[Użytkownik wpisuje w Search Bar]
               │
               ▼
   [QueryParser.parse(query)]
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[category is None]             [category is recognized]
       │                                │
       ▼                                ▼
• Pokaz info: "Brak produktów       • Filtruj produkty w products.jsonl:
  w tej kategorii (obsługujemy:        1. product['category'] == parsed.category
  T-shirty, Sukienki, Topy)"           2. Dla każdego f w parsed.filters:
• Ewentualnie fallback na BM25            zastosuj filtr na product['features']
                                       3. Jeśli parsed.residual != "":
                                          sortuj po podobieństwie tekstowym/wektorowym
                                       4. Wyświetl dopasowane produkty w UI!
```
