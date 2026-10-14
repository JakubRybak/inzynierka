# Products – katalog H&M

Dane katalogowe produktów do wyszukiwarki (strona katalogu w pipeline).

Źródło: [H&M Personalized Fashion Recommendations (Kaggle)](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) – plik `articles.csv` (bez zdjęć).

## Struktura i Raporty

* **[SUPER_REDUCED_CATEGORIES.md](file:///Users/jakubrybak/Projekty/Test/products/SUPER_REDUCED_CATEGORIES.md)** – bardzo zredukowana taksonomia (18 kategorii w 3 grupach: Góra, Dół, Całe ciało) po odrzuceniu obuwia, kombinezonów, ogrodniczek i legginsów (z uwzględnieniem Outdoor trousers).
* **[REDUCED_CATEGORIES.md](file:///Users/jakubrybak/Projekty/Test/products/REDUCED_CATEGORIES.md)** – zredukowana taksonomia (34 kategorie w 4 grupach: Góra, Dół, Całe ciało, Buty) po odrzuceniu akcesoriów, bielizny i niszowych podtypów.
* **[CATEGORY_GROUPS_BREAKDOWN.md](file:///Users/jakubrybak/Projekty/Test/products/CATEGORY_GROUPS_BREAKDOWN.md)** – pełny raport statystyczny podziału całego asortymentu na 10 grup makro (131 kategorii).
* **[data/category_counts.csv](file:///Users/jakubrybak/Projekty/Test/products/data/category_counts.csv)** – posortowany plik CSV ze wszystkimi 131 kategoriami (`product_count`, `product_pct`, `article_count`, `article_pct`).
* **[scripts/count_categories.py](file:///Users/jakubrybak/Projekty/Test/products/scripts/count_categories.py)** – skrypt agregujący i przeliczający statystyki.

```
products/
├── README.md
├── CATEGORY_GROUPS_BREAKDOWN.md
├── data/
│   ├── category_counts.csv
│   └── raw/
│       └── articles.csv   # surowe metadane ~105k artykułów (ignorowane przez git)
└── scripts/
    └── count_categories.py
```

