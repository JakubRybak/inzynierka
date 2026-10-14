"""Liczy liczność i udział procentowy każdej kategorii (product_type_name) w katalogu H&M.

Wejście:  products/data/raw/articles.csv
Wyjście:  products/data/category_counts.csv (posortowane malejąco po product_count)
"""

import csv
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "data", "raw", "articles.csv")
DST = os.path.join(BASE, "data", "category_counts.csv")

articles = defaultdict(int)          # liczba wierszy (warianty kolorystyczne)
products = defaultdict(set)          # unikalne product_code
groups = defaultdict(set)            # product_group_name, do których należy kategoria

with open(SRC, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        cat = row["product_type_name"]
        articles[cat] += 1
        products[cat].add(row["product_code"])
        groups[cat].add(row["product_group_name"])

total_articles = sum(articles.values())
total_unique_products = len({code for codes in products.values() for code in codes})

# Sortowanie malejąco po product_count, a potem article_count
rows = sorted(articles, key=lambda c: (-len(products[c]), -articles[c], c))

with open(DST, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "category",
        "product_group",
        "product_count",
        "product_pct",
        "article_count",
        "article_pct",
    ])
    for cat in rows:
        p_cnt = len(products[cat])
        a_cnt = articles[cat]
        p_pct = f"{(p_cnt / total_unique_products) * 100:.2f}%"
        a_pct = f"{(a_cnt / total_articles) * 100:.2f}%"
        w.writerow([
            cat,
            " | ".join(sorted(groups[cat])),
            p_cnt,
            p_pct,
            a_cnt,
            a_pct,
        ])

print(f"Zapisano {len(rows)} kategorii do {DST}")
print(f"Baza referencyjna: {total_unique_products} unikalnych produktów, {total_articles} wariantów (artykułów).")
