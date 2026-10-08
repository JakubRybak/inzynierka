import csv
import json

CSV_FILE = "fashion_test_benchmark.csv"

# Mapowanie zapytań na marki
BRAND_MAPPINGS = {
    "north face jacket womens": ("The North Face", ""),
    "32 degrees jackets for women": ("32 Degrees", ""),
    "yellow champion hoodie": ("Champion", ""),
    "track jacket men venum": ("Venum", "track"),
    "g star hoodies for men": ("G-Star", ""),
    "port authority cardigan": ("Port Authority", ""),
    "jerzees long sleeve t shirt": ("Jerzees", ""),
    "nautica polo shirts for men": ("Nautica", ""),
    "dewalt shirt for men": ("DeWalt", ""),
    "carhartt double front pants for men": ("Carhartt", "double front"),
    "adidas shoes men": ("Adidas", "shoes")
}

with open(CSV_FILE, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

updated_count = 0
for r in rows:
    q = r["query"].strip()
    if q in BRAND_MAPPINGS:
        brand_name, new_residual = BRAND_MAPPINGS[q]
        attrs = json.loads(r["expected_attributes"])
        attrs["brand"] = brand_name
        r["expected_attributes"] = json.dumps(attrs)
        r["expected_residual"] = new_residual
        updated_count += 1

fieldnames = ["query_id", "query", "category", "difficulty", "borderline_note", "expected_attributes", "expected_residual"]
with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Pomyślnie zaktualizowano {updated_count} zapytań o marki w {CSV_FILE}!")
