"""Liczy produkty i zdjęcia per kategoria / podkategoria w zbiorze FashionGen 256x256.

Wejście:  products_new/data/raw/fashiongen_256_256_{train,validation}.h5
Wyjście:  products_new/data/category_counts.csv        (poziom kategorii)
          products_new/data/subcategory_counts.csv     (poziom podkategorii)
          products_new/CATEGORY_GROUPS_BREAKDOWN.md    (raport z grupami makro)

Uwaga o strukturze danych:
  * 1 wiersz w pliku h5 = 1 zdjęcie (input_pose = id_gridfs_1..6), a nie 1 produkt.
  * Produkt = unikalny `input_productID`. Kolorystyczne warianty tego samego
    fasonu mają RÓŻNE productID (brak wspólnego identyfikatora modelu).
  * 87 productID ma zduplikowane wiersze (cały zestaw zdjęć powtórzony), dlatego
    zdjęcia liczymy jako unikalne pary (productID, pose).
  * Czytamy wyłącznie kolumny tekstowe - obrazy (input_image) nie są ładowane.
"""

import csv
import os
from collections import Counter, defaultdict

import h5py
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
SPLITS = ["train", "validation"]

# Grupy makro (analogicznie do products/CATEGORY_GROUPS_BREAKDOWN.md)
GROUPS = {
    "Góra (Upper body)": [
        "TOPS", "SWEATERS", "SHIRTS", "JACKETS & COATS", "SUITS & BLAZERS",
    ],
    "Dół (Lower body)": ["PANTS", "JEANS", "SHORTS", "SKIRTS"],
    "Całe ciało (Full body)": ["DRESSES", "JUMPSUITS"],
    "Obuwie (Shoes)": [
        "SNEAKERS", "BOOTS", "FLATS", "SANDALS", "HEELS", "LACE UPS", "LOAFERS",
        "ESPADRILLES", "MONKSTRAPS", "BOAT SHOES & MOCCASINS",
    ],
    "Akcesoria i torby (Accessories & Bags)": [
        "HATS", "SHOULDER BAGS", "JEWELRY", "EYEWEAR", "BACKPACKS", "SCARVES",
        "TOTE BAGS", "DUFFLE & TOP HANDLE BAGS", "CLUTCHES & POUCHES",
        "BELTS & SUSPENDERS", "FINE JEWELRY", "MESSENGER BAGS & SATCHELS", "TIES",
        "KEYCHAINS", "BAG ACCESSORIES", "POUCHES & DOCUMENT HOLDERS", "GLOVES",
        "DUFFLE BAGS", "MESSENGER BAGS", "BRIEFCASES", "POCKET SQUARES & TIE BARS",
        "TRAVEL BAGS",
    ],
    "Bielizna (Underwear)": ["LINGERIE", "UNDERWEAR & LOUNGEWEAR"],
    "Stroje kąpielowe (Swimwear)": ["SWIMWEAR"],
    "Skarpetki (Socks)": ["SOCKS"],
    "Inne / Poza modą (Home)": ["BLANKETS"],
}
CLOTHING_GROUPS = ["Góra (Upper body)", "Dół (Lower body)", "Całe ciało (Full body)"]


def dec(a):
    return np.char.decode(a.reshape(-1), "utf-8", errors="replace")


def fmt(n):
    return f"{n:,}".replace(",", " ")


def pct(a, b):
    return f"{a / b * 100:.2f}%"


def pct1(a, b):
    return f"{a / b * 100:.1f}%"


# --- wczytanie metadanych ---------------------------------------------------
product = {}                       # productID -> (category, subcategory, gender, split)
images = defaultdict(set)          # productID -> {pose}
raw_rows = Counter()
split_products = defaultdict(set)

for split in SPLITS:
    path = os.path.join(RAW, f"fashiongen_256_256_{split}.h5")
    with h5py.File(path, "r") as f:
        pid = f["input_productID"][:].reshape(-1)
        cat = dec(f["input_category"][:])
        sub = dec(f["input_subcategory"][:])
        pose = dec(f["input_pose"][:])
        gender = dec(f["input_gender"][:])
    raw_rows[split] = len(pid)
    for i in range(len(pid)):
        p = int(pid[i])
        product.setdefault(p, (str(cat[i]), str(sub[i]), str(gender[i]), split))
        images[p].add(str(pose[i]))
        split_products[split].add(p)

total_products = len(product)
total_images = sum(len(v) for v in images.values())
total_raw = sum(raw_rows.values())

cat_prod = Counter()
cat_img = Counter()
sub_prod = Counter()
sub_img = Counter()
for p, (c, s, _, _) in product.items():
    n_img = len(images[p])
    cat_prod[c] += 1
    cat_img[c] += n_img
    sub_prod[(c, s)] += 1
    sub_img[(c, s)] += n_img

cat_group = {c: g for g, cs in GROUPS.items() for c in cs}
missing = set(cat_prod) - set(cat_group)
assert not missing, f"Kategorie bez grupy: {missing}"

# --- CSV --------------------------------------------------------------------
with open(os.path.join(BASE, "data", "category_counts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category", "group", "product_count", "product_pct", "image_count", "image_pct"])
    for c in sorted(cat_prod, key=lambda c: (-cat_prod[c], c)):
        w.writerow([c, cat_group[c], cat_prod[c], pct(cat_prod[c], total_products),
                    cat_img[c], pct(cat_img[c], total_images)])

with open(os.path.join(BASE, "data", "subcategory_counts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category", "subcategory", "group", "product_count", "product_pct", "image_count", "image_pct"])
    for (c, s) in sorted(sub_prod, key=lambda k: (-sub_prod[k], k)):
        w.writerow([c, s, cat_group[c], sub_prod[(c, s)], pct(sub_prod[(c, s)], total_products),
                    sub_img[(c, s)], pct(sub_img[(c, s)], total_images)])

# --- agregaty grup ----------------------------------------------------------
g_prod = {g: sum(cat_prod[c] for c in cs if c in cat_prod) for g, cs in GROUPS.items()}
g_img = {g: sum(cat_img[c] for c in cs if c in cat_img) for g, cs in GROUPS.items()}
g_ncat = {g: sum(1 for c in cs if c in cat_prod) for g, cs in GROUPS.items()}
order = sorted(GROUPS, key=lambda g: -g_prod[g])
genders = Counter(v[2] for v in product.values())

core = ["Góra (Upper body)", "Dół (Lower body)", "Całe ciało (Full body)", "Obuwie (Shoes)"]
core_prod = sum(g_prod[g] for g in core)
core_img = sum(g_img[g] for g in core)

# --- Markdown ---------------------------------------------------------------
L = []
L.append("# Podział Kategorii i Grup Asortymentowych – FashionGen\n")
L.append("Raport statystyczny i analiza struktury asortymentu na podstawie zbioru danych **FashionGen** "
         "(`fashiongen_256_256_train.h5` + `fashiongen_256_256_validation.h5`, zdjęcia 256×256).\n")
L.append("## Baza referencyjna zbioru danych:")
L.append(f"* **{fmt(total_products)}** – unikalne produkty (`input_productID`): "
         f"{fmt(len(split_products['train']))} w train + {fmt(len(split_products['validation']))} w validation "
         f"(brak wspólnych `productID` między splitami).")
L.append(f"* **{fmt(total_raw)}** – wierszy w plikach h5 (1 wiersz = 1 zdjęcie, nie 1 produkt).")
L.append(f"* **{fmt(total_images)}** – unikalnych zdjęć (para `productID` + `pose`); "
         f"{fmt(total_raw - total_images)} wierszy to duplikaty.")
L.append(f"* **{len(cat_prod)}** – kategorii (`input_category`) i **{len(sub_prod)}** podkategorii (`input_subcategory`).")
L.append(f"* Płeć: Women {fmt(genders['Women'])} ({pct1(genders['Women'], total_products)}), "
         f"Men {fmt(genders['Men'])} ({pct1(genders['Men'], total_products)}).\n")
L.append("> **Uwagi o strukturze danych (ważne przy liczeniu):**  ")
L.append("> * Produkt = unikalny `productID`. Warianty kolorystyczne tego samego fasonu mają **różne** `productID` "
         "i nie ma wspólnego identyfikatora modelu – każdy kolor liczy się jako osobny produkt "
         "(odpowiednik `article_id` z H&M, a nie `product_code`).  ")
L.append(f"> * Produkt ma zwykle 4 zdjęcia (średnio {total_images / total_products:.2f}). "
         "87 produktów ma zduplikowany cały zestaw zdjęć (wiersze identyczne) – dlatego deduplikacja po `productID`.  ")
L.append("> * Atrybuty (`category`, `subcategory`, `name`, `brand`, `composition`…) są spójne w obrębie `productID`.\n")
L.append("---\n")
L.append("## 1. Główna Tabela Zbiorcza Grup Makro\n")
L.append("| Grupa Makro | Produkty (`product_count`) | Udział w produktach (`product_pct`) | "
         "Zdjęcia (`image_count`) | Udział w zdjęciach (`image_pct`) | Liczba kategorii |")
L.append("| :--- | ---: | :---: | ---: | :---: | :---: |")
for g in order:
    L.append(f"| **{g}** | **{fmt(g_prod[g])}** | **{pct(g_prod[g], total_products)}** | "
             f"**{fmt(g_img[g])}** | **{pct(g_img[g], total_images)}** | {g_ncat[g]} |")
L.append(f"| **SUMA** | **{fmt(total_products)}** | **100.00%** | **{fmt(total_images)}** | **100.00%** | "
         f"**{len(cat_prod)}** |\n")
L.append("> **Kluczowy wniosek architektoniczny:**  ")
L.append(f"> Sama **garderoba właściwa oraz obuwie** (Góra, Dół, Całe ciało, Obuwie) to **{fmt(core_prod)} produktów "
         f"({pct1(core_prod, total_products)} zbioru)** i **{fmt(core_img)} zdjęć**. "
         "Pozostałe działy (akcesoria, bielizna, stroje kąpielowe, skarpetki) można traktować jako filtr negatywny "
         "(*Out-of-Scope*).\n")
L.append("---\n")
L.append("## 2. Szczegółowe Zestawienie Kategorii w Grupach Makro\n")
L.append("---\n")

for n, g in enumerate(order, 1):
    L.append(f"### {n}. {g}")
    L.append(f"* **Łącznie w grupie:** {fmt(g_prod[g])} produktów (**{pct(g_prod[g], total_products)}** całego zbioru) | "
             f"{fmt(g_img[g])} zdjęć (**{pct(g_img[g], total_images)}**)\n")
    L.append("| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | "
             "**Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |")
    L.append("| :--- | ---: | :---: | :---: | ---: | :---: |")
    for c in sorted((c for c in GROUPS[g] if c in cat_prod), key=lambda c: -cat_prod[c]):
        L.append(f"| **{c}** | {fmt(cat_prod[c])} | {pct1(cat_prod[c], g_prod[g])} | "
                 f"**{pct(cat_prod[c], total_products)}** | {fmt(cat_img[c])} | {pct1(cat_img[c], g_img[g])} |")
    L.append("\n---\n")

L.append("## 3. Podkategorie (`input_subcategory`) w grupach odzieżowych\n")
L.append("FashionGen ma wbudowaną drugą warstwę taksonomii. Poniżej podkategorie dla Góry, Dołu i Całego ciała "
         "(pełna lista wszystkich grup: `data/subcategory_counts.csv`).\n")
for g in CLOTHING_GROUPS:
    L.append(f"### {g}\n")
    L.append("| Kategoria | Podkategoria | Produkty | Udział w grupie | **Udział w całym zbiorze** | Zdjęcia |")
    L.append("| :--- | :--- | ---: | :---: | :---: | ---: |")
    cats = sorted((c for c in GROUPS[g] if c in cat_prod), key=lambda c: -cat_prod[c])
    for c in cats:
        subs = sorted((k for k in sub_prod if k[0] == c), key=lambda k: -sub_prod[k])
        for k in subs:
            L.append(f"| **{c}** | {k[1]} | {fmt(sub_prod[k])} | {pct1(sub_prod[k], g_prod[g])} | "
                     f"**{pct(sub_prod[k], total_products)}** | {fmt(sub_img[k])} |")
    L.append("")

with open(os.path.join(BASE, "CATEGORY_GROUPS_BREAKDOWN.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")

print(f"Produkty: {total_products}, wiersze h5: {total_raw}, unikalne zdjęcia: {total_images}")
print(f"Kategorie: {len(cat_prod)}, podkategorie: {len(sub_prod)}")
for g in order:
    print(f"{g:42} {g_prod[g]:6} ({pct(g_prod[g], total_products)})  zdjęcia {g_img[g]}")
