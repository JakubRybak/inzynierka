import os
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_FILE = "hnm_articles.csv"
OUTPUT_DIR = "hnm_sample_images"
SAMPLE_SIZE = 20  # Liczba produktów i zdjęć do pobrania

def download_single_image(article_id):
    subfolder = article_id[:3]
    img_filename = f"{article_id}.jpg"
    local_path = os.path.join(OUTPUT_DIR, img_filename)

    if os.path.exists(local_path):
        return article_id, True, "already exists"

    url = f"https://huggingface.co/datasets/einrafh/hnm-fashion-recommendations-data/resolve/main/data/raw/images/{subfolder}/{img_filename}"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            return article_id, True, "downloaded"
        else:
            return article_id, False, f"HTTP {resp.status_code}"
    except Exception as e:
        return article_id, False, str(e)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Wczytywanie bazy artykułów...")
    df = pd.read_csv(CSV_FILE, dtype={"article_id": str})
    
    # Wybieramy różnorodną próbkę z opisami (sukienki, koszule, buty, spodnie, kurtki)
    sample_df = df.dropna(subset=["detail_desc", "prod_name"]).sample(SAMPLE_SIZE, random_state=42).copy()
    
    print(f"Rozpoczynam pobieranie {len(sample_df)} zdjęć do folderu '{OUTPUT_DIR}/'...")
    
    article_ids = sample_df["article_id"].tolist()
    success_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_single_image, aid): aid for aid in article_ids}
        for future in as_completed(futures):
            aid, success, msg = future.result()
            if success:
                success_count += 1

    sample_df["local_image_path"] = sample_df["article_id"].apply(lambda aid: os.path.join(OUTPUT_DIR, f"{aid}.jpg"))
    sample_csv_path = "hnm_sample_20.csv"
    sample_df[[
        "article_id", "prod_name", "product_type_name", "product_group_name",
        "colour_group_name", "index_group_name", "detail_desc", "local_image_path"
    ]].to_csv(sample_csv_path, index=False, encoding="utf-8-sig")

    print("=" * 70)
    print(f"Pomyślnie pobrano {success_count}/{SAMPLE_SIZE} zdjęć!")
    print(f"Zapisano metadane próbki do: {sample_csv_path}")
    print(f"Zdjęcia zapisane w folderze: {OUTPUT_DIR}/")
    print("=" * 70)

if __name__ == "__main__":
    main()
