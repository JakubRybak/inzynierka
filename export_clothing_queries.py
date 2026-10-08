import re
import pandas as pd

LOCAL_FILE = "shopping_queries_dataset_examples.parquet"
OUTPUT_CSV = "clothing_queries.csv"

# Kategorie i słowa kluczowe (wyłącznie język angielski)
CATEGORIES = {
    "Dresses": [r"\bdress\b", r"\bdresses\b", r"\bgown\b"],
    "Footwear": [r"\bshoes\b", r"\bshoe\b", r"\bsneakers\b", r"\bboots\b", r"\bboot\b", r"\bsandals\b", r"\bheels\b", r"\bslippers\b", r"\bloafers\b", r"\bflats\b"],
    "Tops & Shirts": [r"\bshirt\b", r"\bt-shirt\b", r"\btshirt\b", r"\btee\b", r"\btop\b", r"\btops\b", r"\bblouse\b", r"\bhoodie\b", r"\bhoodies\b", r"\bsweater\b", r"\bsweaters\b", r"\bsweatshirt\b", r"\bcardigan\b", r"\bpolo\b", r"\btank top\b"],
    "Pants & Bottoms": [r"\bpants\b", r"\btrousers\b", r"\bjeans\b", r"\bshorts\b", r"\bleggings\b", r"\bjoggers\b", r"\bskirt\b", r"\bskirts\b", r"\bsweatpants\b"],
    "Outerwear": [r"\bjacket\b", r"\bjackets\b", r"\bcoat\b", r"\bcoats\b", r"\bparka\b", r"\bwindbreaker\b", r"\braincoat\b"],
    "Underwear & Sleepwear": [r"\bunderwear\b", r"\bbra\b", r"\bbras\b", r"\bpanties\b", r"\bboxers\b", r"\bbriefs\b", r"\bsocks\b", r"\bpajamas\b", r"\bpyjamas\b", r"\blingerie\b"],
    "Swimwear": [r"\bswimsuit\b", r"\bbikini\b", r"\bswimwear\b", r"\btrunks\b"],
    "Accessories": [r"\bhat\b", r"\bhats\b", r"\bcap\b", r"\bcaps\b", r"\bscarf\b", r"\bgloves\b", r"\bbelt\b", r"\bbelts\b", r"\btie\b", r"\bbeanie\b"],
    "General Apparel": [r"\bcloth\b", r"\bclothing\b", r"\bapparel\b", r"\bwear\b", r"\boutfit\b", r"\bgarment\b"]
}

ALL_KEYWORDS = [pattern for cat_patterns in CATEGORIES.values() for pattern in cat_patterns]
ALL_REGEX = re.compile("|".join(ALL_KEYWORDS), re.IGNORECASE)
ASIAN_CHARS_REGEX = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

def detect_category(query_text: str) -> str:
    matched = []
    for cat_name, patterns in CATEGORIES.items():
        if re.search("|".join(patterns), query_text, re.IGNORECASE):
            matched.append(cat_name)
    return ", ".join(matched) if matched else "Other Apparel"

def main():
    print("Wczytywanie datasetu...")
    df = pd.read_parquet(LOCAL_FILE)

    # Filtrujemy tylko rynek US (język angielski)
    print("Filtrowanie do rynku US (język angielski)...")
    df = df[df["product_locale"] == "us"]

    print("Grupowanie zapytań...")
    grouped = df.groupby("query").agg(
        query_id=("query_id", "first"),
        product_count=("product_id", "count")
    ).reset_index()

    # Odrzucamy jakiekolwiek znaki azjatyckie
    grouped = grouped[~grouped["query"].astype(str).str.contains(ASIAN_CHARS_REGEX, regex=True)]

    print("Filtrowanie ubrań...")
    is_clothing = grouped["query"].astype(str).str.contains(ALL_REGEX, regex=True)
    clothing_df = grouped[is_clothing].copy()

    # Przypisywanie kategorii
    print("Przypisywanie kategorii...")
    clothing_df["category"] = clothing_df["query"].astype(str).apply(detect_category)

    # Sortowanie po popularności
    clothing_df = clothing_df.sort_values(by="product_count", ascending=False)

    clothing_df = clothing_df[["query_id", "query", "category", "product_count"]]
    clothing_df.rename(columns={
        "query_id": "Query_ID",
        "query": "Query_Text",
        "category": "Category",
        "product_count": "Product_Count"
    }, inplace=True)

    clothing_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nZapisano {len(clothing_df):,} czysto angielskich zapytań do pliku: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
