# Pilot 9922 Feature Extraction & Embeddings Output

Opublikowany zbiór wyekstrahowanych cech oraz embeddingów multimodalnych (Gemini Embedding 2) dla próby **9 922 produktów** z FashionGen (obejmującej wszystkie 22 kategorie).

## Zawartość katalogu

- **`products.parquet` (1.5 MB)** – główny, zoptymalizowany plik z cechami produktów w formacie Parquet.
- **`products.jsonl` (47 MB)** – pełne rekordy JSONL zawierające przypisane cechy (`features`), pochodzenie każdej cechy (`feature_metadata`), powody ewentualnych wykluczeń (`outside_schema_reasons`) oraz metadane modelu Gemini (`llm_metadata`).
- **`summary.json`** – podsumowanie metryk runu (9 796 `ready`, 31 `pending`, 95 `needs_review`).
- **`embeddings/`**:
  - **`image.parquet`** – znormalizowane wektory L2 (wymiar 3072) dla głównych zdjęć (`id_gridfs_1`). Zarządzany przez **Git LFS**.
  - **`text.parquet`** – znormalizowane wektory L2 (wymiar 3072) dla opisów katalogowych. Zarządzany przez **Git LFS**.
  - **`manifest.json`** – specyfikacja modelu i konfiguracji embeddingów.

## Jak wczytać dane w Pythonie

### Cechy produktów
```python
import pandas as pd
import json

# Wczytanie z Parquet (zalecane, błyskawiczne)
df = pd.read_parquet('feature_extraction/outputs/pilot_9922/products.parquet')

# Pola 'features' i 'feature_metadata' są zserializowane jako JSON
df['features'] = df['features'].apply(json.loads)
print(df[['product_id', 'category', 'status', 'features']].head())
```

### Embeddingi
```python
import pyarrow.parquet as pq

# Wczytanie wektorów zdjęć lub tekstów
image_table = pq.read_table('feature_extraction/outputs/pilot_9922/embeddings/image.parquet')
df_embeddings = image_table.to_pandas()
print(df_embeddings.head())
```

## Uwaga dotycząca Git LFS
Pliki embeddingów w podkatalogu `embeddings/*.parquet` mają ponad 100 MB i są zarządzane przez **Git LFS**.
Jeśli po sklonowaniu repozytorium pliki te mają po kilkaset bajtów (wskaźniki LFS), pobierz ich pełną zawartość poleceniem:
```sh
git lfs pull
```
