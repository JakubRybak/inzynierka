# Products New – katalog FashionGen

Alternatywny zbiór katalogowy (ze zdjęciami) dla wyszukiwarki.

Źródło: **FashionGen** – pliki `fashiongen_256_256_train.h5` (14,4 GB) i `fashiongen_256_256_validation.h5` (1,8 GB), zdjęcia 256×256. Surowe pliki leżą w `data/raw/` (ignorowane przez git).

## Struktura danych h5

Każdy plik ma te same kolumny (`input_*`): `productID`, `name`, `brand`, `category`, `subcategory`, `department`, `gender`, `season`, `description`, `concat_description`, `composition`, `msrpUSD`, `pose`, `image`.

* **1 wiersz = 1 zdjęcie**, nie 1 produkt. Produkt ma zwykle 4 zdjęcia (`pose` = `id_gridfs_1..6`).
* **Produkt = unikalny `input_productID`.** Ten sam fason w innym kolorze ma inny `productID` – brak wspólnego identyfikatora modelu.
* 87 produktów ma zduplikowany cały zestaw zdjęć → deduplikacja po `productID` (zdjęcia po parze `productID` + `pose`).
* Kolumna `composition` zawiera skład materiałowy (np. `100% cotton.`).
* Przy odczycie metadanych nie ładować `input_image` (to ~97% rozmiaru pliku).

## Struktura i Raporty

* **[CATEGORY_GROUPS_BREAKDOWN.md](CATEGORY_GROUPS_BREAKDOWN.md)** – raport podziału asortymentu na grupy makro (48 kategorii, 132 podkategorie), liczone po unikalnych produktach i zdjęciach.
* **[REDUCED_CATEGORIES.md](REDUCED_CATEGORIES.md)** – zredukowane podkategorie odzieży (Góra, Dół, Całe ciało) po usunięciu BLAZERS (wszystkich), LEGGINGS, JUMPSUITS oraz niszowych (53 262 produktów, 36 podkategorii).
* **[data/category_counts.csv](data/category_counts.csv)** – liczności per kategoria.
* **[data/subcategory_counts.csv](data/subcategory_counts.csv)** – liczności per podkategoria.
* **[scripts/count_categories.py](scripts/count_categories.py)** – skrypt generujący CSV i raport podziału na grupy (`.venv/bin/python products_new/scripts/count_categories.py`).
* **[scripts/reduced_categories.py](scripts/reduced_categories.py)** – skrypt generujący `REDUCED_CATEGORIES.md` (lista usuwanych podkategorii w stałej `REMOVED`).

```
products_new/
├── README.md
├── CATEGORY_GROUPS_BREAKDOWN.md
├── REDUCED_CATEGORIES.md
├── data/
│   ├── category_counts.csv
│   ├── subcategory_counts.csv
│   └── raw/
│       ├── fashiongen_256_256_train.h5        # ignorowane przez git
│       └── fashiongen_256_256_validation.h5   # ignorowane przez git
└── scripts/
    ├── count_categories.py
    └── reduced_categories.py
```
