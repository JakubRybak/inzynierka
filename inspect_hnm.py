import os
import requests
import pandas as pd

ARTICLES_URL = "https://huggingface.co/datasets/einrafh/hnm-fashion-recommendations-data/resolve/main/data/raw/articles.csv"
LOCAL_ARTICLES_CSV = "hnm_articles.csv"

def download_articles():
    if not os.path.exists(LOCAL_ARTICLES_CSV):
        print(f"Pobieranie metadanych produktów H&M ({ARTICLES_URL})...")
        response = requests.get(ARTICLES_URL, stream=True)
        with open(LOCAL_ARTICLES_CSV, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        print("Pobieranie zakończone.")
    else:
        print("Plik hnm_articles.csv już istnieje.")

def main():
    download_articles()

    print("\nWczytywanie artykułów H&M do pamięci...")
    df = pd.read_csv(LOCAL_ARTICLES_CSV, dtype={"article_id": str})
    
    print("=" * 80)
    print(" STRUKTURA DATASETU H&M PERSONALIZED FASHION RECOMMENDATIONS")
    print("=" * 80)
    print(f"Liczba produktów (artykułów): {len(df):,}")
    print(f"\nDostępne kolumny ({len(df.columns)}):")
    for col in df.columns:
        print(f" - {col}")

    print("\n" + "=" * 80)
    print(" PRZYKŁADOWE REKORDY (Tytuły, opisy, kategorie, kolory)")
    print("=" * 80)
    sample_cols = [
        "article_id", "prod_name", "product_type_name", 
        "product_group_name", "colour_group_name", 
        "index_group_name", "detail_desc"
    ]
    
    samples = df[sample_cols].dropna().sample(5, random_state=42)
    for idx, row in samples.iterrows():
        print(f"\n[ID: {row['article_id']}] {row['prod_name']}")
        print(f"  Typ produktu : {row['product_type_name']} ({row['product_group_name']})")
        print(f"  Dział / Płeć : {row['index_group_name']}")
        print(f"  Kolor        : {row['colour_group_name']}")
        print(f"  Opis         : {row['detail_desc']}")
        print(f"  Ścieżka foto : images/{row['article_id'][:3]}/{row['article_id']}.jpg")

if __name__ == "__main__":
    main()
