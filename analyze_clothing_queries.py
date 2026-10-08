import re
import os
import pandas as pd
import requests

DATASET_URL = "https://media.githubusercontent.com/media/amazon-science/esci-data/main/shopping_queries_dataset/shopping_queries_dataset_examples.parquet"
LOCAL_FILE = "shopping_queries_dataset_examples.parquet"

def download_dataset():
    if not os.path.exists(LOCAL_FILE):
        print(f"Pobieranie datasetu ({DATASET_URL})...")
        response = requests.get(DATASET_URL, stream=True)
        with open(LOCAL_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("Pobieranie zakończone.")
    else:
        print("Plik datasetu już istnieje lokalnie.")

# Słowa kluczowe wyłącznie w języku angielskim
CLOTHING_KEYWORDS = [
    # Ogólne odzież
    r"\bcloth\b", r"\bclothing\b", r"\bapparel\b", r"\bwear\b", r"\boutfit\b", r"\bgarment\b",
    # Góra
    r"\bshirt\b", r"\bt-shirt\b", r"\btshirt\b", r"\btee\b", r"\btop\b", r"\btops\b", r"\bblouse\b",
    r"\bhoodie\b", r"\bhoodies\b", r"\bsweater\b", r"\bsweaters\b", r"\bsweatshirt\b", r"\bcardigan\b",
    r"\btank top\b", r"\bv-neck\b", r"\bpolo\b", r"\btunic\b", r"\bvest\b",
    # Dół
    r"\bpants\b", r"\btrousers\b", r"\bjeans\b", r"\bshorts\b", r"\bleggings\b", r"\bjoggers\b",
    r"\bsweatpants\b", r"\bskirt\b", r"\bskirts\b", r"\btights\b", r"\bcapris\b",
    # Sukienki i garnitury
    r"\bdress\b", r"\bdresses\b", r"\bgown\b", r"\bsuit\b", r"\bsuits\b", r"\bblazer\b",
    r"\bjumpsuit\b", r"\bromper\b", r"\btuxedo\b",
    # Odzież wierzchnia
    r"\bjacket\b", r"\bjackets\b", r"\bcoat\b", r"\bcoats\b", r"\bparka\b", r"\bwindbreaker\b",
    r"\braincoat\b", r"\bponcho\b", r"\banorak\b",
    # Bielizna i piżamy
    r"\bunderwear\b", r"\bbra\b", r"\bbras\b", r"\bpanties\b", r"\bboxers\b", r"\bbriefs\b",
    r"\bsocks\b", r"\bpajamas\b", r"\bpyjamas\b", r"\bnightgown\b", r"\brobe\b", r"\blingerie\b",
    # Stroje kąpielowe
    r"\bswimsuit\b", r"\bbikini\b", r"\bswimwear\b", r"\btrunks\b",
    # Buty / Obuwie
    r"\bshoes\b", r"\bshoe\b", r"\bsneakers\b", r"\bboots\b", r"\bboot\b", r"\bsandals\b",
    r"\bheels\b", r"\bhigh heels\b", r"\bslippers\b", r"\bloafers\b", r"\bflats\b", r"\bcleats\b",
    # Dodatki odzieżowe
    r"\bhat\b", r"\bhats\b", r"\bcap\b", r"\bcaps\b", r"\bscarf\b", r"\bgloves\b", r"\bmittens\b",
    r"\bbelt\b", r"\bbelts\b", r"\btie\b", r"\bbeanie\b"
]

CLOTHING_REGEX = re.compile("|".join(CLOTHING_KEYWORDS), re.IGNORECASE)
# Wykrywanie jakichkolwiek znaków azjatyckich (chiński, japoński, koreański)
ASIAN_CHARS_REGEX = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

def main():
    download_dataset()

    print("\nŁadowanie danych do pamięci...")
    df = pd.read_parquet(LOCAL_FILE)
    print(f"Łączna liczba wierszy (przed filtracją): {len(df):,}")

    # Filtrujemy wyłącznie rynek amerykański (US / język angielski)
    print("Filtrowanie wyłącznie do rynku US (język angielski)...")
    df_us = df[df["product_locale"] == "us"].copy()
    print(f"Liczba wierszy w rynku US: {len(df_us):,}")

    # Unikalne zapytania
    unique_queries = df_us[["query", "query_id"]].drop_duplicates(subset=["query"]).copy()
    
    # Usuwamy ewentualne zapytania ze znakami azjatyckimi
    unique_queries = unique_queries[~unique_queries["query"].astype(str).str.contains(ASIAN_CHARS_REGEX, regex=True)]
    total_unique_queries = len(unique_queries)
    print(f"Liczba unikalnych angielskich zapytań: {total_unique_queries:,}")

    # Filtrowanie ubrań
    print("\nFiltrowanie zapytań dotyczących ubrań i obuwia...")
    unique_queries["is_clothing"] = unique_queries["query"].astype(str).str.contains(CLOTHING_REGEX, regex=True)

    clothing_df = unique_queries[unique_queries["is_clothing"]]
    clothing_count = len(clothing_df)
    clothing_pct = (clothing_count / total_unique_queries) * 100

    print("=" * 70)
    print(" WYNIKI ANALIZY AMAZON SHOPPING QUERIES (TYLKO JĘZYK ANGIELSKI - US)")
    print("=" * 70)
    print(f"Wszystkie unikalne angielskie zapytania:  {total_unique_queries:,}")
    print(f"Zapytania o ubrania/obuwie (angielskie):  {clothing_count:,} ({clothing_pct:.2f}%)")
    print(f"Zapytania pozostałe:                      {total_unique_queries - clothing_count:,} ({100 - clothing_pct:.2f}%)")
    print("=" * 70)

    # Przykłady
    print("\n Przykładowe angielskie wyszukiwania ubrań z datasetu (losowe 20):")
    sample_queries = clothing_df["query"].sample(min(20, clothing_count), random_state=42).tolist()
    for i, q in enumerate(sample_queries, 1):
        print(f" {i:2d}. {q}")

    # Kategorie
    categories = {
        "Sukienki (Dresses / Gowns)": [r"\bdress\b", r"\bdresses\b", r"\bgown\b"],
        "Buty i obuwie (Shoes / Boots / Sneakers)": [r"\bshoes\b", r"\bshoe\b", r"\bsneakers\b", r"\bboots\b", r"\bsandals\b", r"\bheels\b", r"\bslippers\b"],
        "Koszule, T-shirty i Topy (Shirts / Tops / Hoodies)": [r"\bshirt\b", r"\bt-shirt\b", r"\btshirt\b", r"\btee\b", r"\bhoodie\b", r"\btop\b", r"\bsweater\b"],
        "Spodnie i jeansy (Pants / Jeans / Shorts / Leggings)": [r"\bpants\b", r"\bjeans\b", r"\bshorts\b", r"\bleggings\b"],
        "Kurtki i płaszcze (Jackets / Coats)": [r"\bjacket\b", r"\bcoat\b", r"\bparka\b"],
        "Bielizna i piżamy (Underwear / Socks / Pajamas)": [r"\bunderwear\b", r"\bbra\b", r"\bsocks\b", r"\bpajamas\b"],
    }

    print("\n Szacunkowy rozkład podkategorii (tylko angielskie):")
    for cat_name, patterns in categories.items():
        cat_regex = re.compile("|".join(patterns), re.IGNORECASE)
        cat_matches = unique_queries["query"].astype(str).str.contains(cat_regex, regex=True).sum()
        cat_pct = (cat_matches / total_unique_queries) * 100
        print(f" - {cat_name:<52}: {cat_matches:5,d} ({cat_pct:5.2f}% wszystkich zapytań US)")

if __name__ == "__main__":
    main()
