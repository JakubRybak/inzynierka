"""Generuje products_new/REDUCED_CATEGORIES.md - podkategorie FashionGen po redukcji.

Zakres: grupy odzieżowe (Góra, Dół, Całe ciało) z products_new/CATEGORY_GROUPS_BREAKDOWN.md.
Usuwane podkategorie (input_subcategory) są zdefiniowane w REMOVED poniżej.

Liczenie jak w count_categories.py: produkt = unikalny input_productID,
zdjęcie = unikalna para (productID, pose). Obrazy nie są ładowane.
"""

import os
from collections import Counter, defaultdict

import h5py
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
SPLITS = ["train", "validation"]

GROUPS = {
    "Góra (Upper body)": ["TOPS", "SWEATERS", "SHIRTS", "JACKETS & COATS", "SUITS & BLAZERS"],
    "Dół (Lower body)": ["PANTS", "JEANS", "SHORTS", "SKIRTS"],
    "Całe ciało (Full body)": ["DRESSES", "JUMPSUITS"],
}

# podkategorie odrzucone (nazwy jak w input_subcategory)
REMOVED = [
    "HENLEYS",
    "SHAWLNECKS",
    "PEACOATS",
    "SUITS",
    "TUXEDOS",
    "WAISTCOATS",
    "BLAZERS",
    "LEGGINGS",
    "JUMPSUITS",
]


def dec(a):
    return np.char.decode(a.reshape(-1), "utf-8", errors="replace")


def fmt(n):
    return f"{n:,}".replace(",", " ")


def pct(a, b):
    return f"{a / b * 100:.2f}%"


def pct1(a, b):
    return f"{a / b * 100:.1f}%"


product = {}
images = defaultdict(set)
for split in SPLITS:
    with h5py.File(os.path.join(RAW, f"fashiongen_256_256_{split}.h5"), "r") as f:
        pid = f["input_productID"][:].reshape(-1)
        cat = dec(f["input_category"][:])
        sub = dec(f["input_subcategory"][:])
        pose = dec(f["input_pose"][:])
    for i in range(len(pid)):
        p = int(pid[i])
        product.setdefault(p, (str(cat[i]), str(sub[i])))
        images[p].add(str(pose[i]))

cat_group = {c: g for g, cs in GROUPS.items() for c in cs}

# tylko grupy odzieżowe
clothing = {p: v for p, v in product.items() if v[0] in cat_group}
before_prod = len(clothing)
before_img = sum(len(images[p]) for p in clothing)

known_subs = {s for _, s in clothing.values()}
unknown = set(REMOVED) - known_subs
assert not unknown, f"Nieistniejące podkategorie: {unknown}"

removed = {p: v for p, v in clothing.items() if v[1] in REMOVED}
kept = {p: v for p, v in clothing.items() if v[1] not in REMOVED}
total_prod = len(kept)
total_img = sum(len(images[p]) for p in kept)

# liczności
rem_prod, rem_img = Counter(), Counter()
for p, (c, s) in removed.items():
    rem_prod[(c, s)] += 1
    rem_img[(c, s)] += len(images[p])

sub_prod, sub_img = Counter(), Counter()
cat_prod, cat_img = Counter(), Counter()
for p, (c, s) in kept.items():
    n = len(images[p])
    sub_prod[(c, s)] += 1
    sub_img[(c, s)] += n
    cat_prod[c] += 1
    cat_img[c] += n

g_prod = {g: sum(cat_prod[c] for c in cs) for g, cs in GROUPS.items()}
g_img = {g: sum(cat_img[c] for c in cs) for g, cs in GROUPS.items()}
g_before = {g: sum(1 for v in clothing.values() if v[0] in cs) for g, cs in GROUPS.items()}
g_nsub = {g: len({k for k in sub_prod if k[0] in cs and sub_prod[k] > 0}) for g, cs in GROUPS.items()}
n_cat_after = len([c for c, cnt in cat_prod.items() if cnt > 0])
n_sub_after = len([k for k, cnt in sub_prod.items() if cnt > 0])
n_sub_before = len({v for v in clothing.values()})

L = []
L.append("# Zredukowana Taksonomia Podkategorii – FashionGen (odzież)\n")
L.append("Raport po usunięciu niszowych i wykluczonych podkategorii (`input_subcategory`) z grup odzieżowych "
         "(**Góra, Dół, Całe ciało**). Obuwie, akcesoria, bielizna, stroje kąpielowe i skarpetki "
         "nie wchodzą do tego zestawienia.\n")
L.append("Liczenie: produkt = unikalny `input_productID`, zdjęcie = unikalna para (`productID`, `pose`). "
         "Każdy kolor tego samego fasonu to osobny produkt.\n")
L.append("---\n")
L.append("## 1. Zakres Usunięć\n")
L.append("| Usunięta podkategoria | Kategoria nadrzędna | Produkty | Zdjęcia |")
L.append("| :--- | :--- | ---: | ---: |")
for (c, s) in sorted(rem_prod.keys(), key=lambda k: (-rem_prod[k], k[1])):
    L.append(f"| **{s}** | {c} | {fmt(rem_prod[(c, s)])} | {fmt(rem_img[(c, s)])} |")
L.append(f"| **SUMA usunięć** | | **{fmt(len(removed))}** | **{fmt(sum(rem_img.values()))}** |\n")
L.append("> **Uwagi do wykluczeń:**\n"
         "> * **BLAZERS** – usunięto wszystkie marynarki i żakiety: zarówno męskie z `SUITS & BLAZERS` (696 modeli), "
         "jak i damskie z `JACKETS & COATS` (320 modeli) – łącznie **1 016 modeli** (4 179 zdjęć).\n"
         "> * **Kategoria SUITS & BLAZERS** została całkowicie zlikwidowana (wszystkie jej podkategorie: "
         "`BLAZERS`, `SUITS`, `TUXEDOS`, `WAISTCOATS` zostały usunięte).\n"
         "> * **LEGGINGS** (172 modele) – usunięto z kategorii `PANTS` w grupie Dół.\n"
         "> * **JUMPSUITS** (168 modeli) – usunięto całą kategorię kombinezonów; w grupie Całe ciało pozostają wyłącznie `DRESSES` (sukienki).\n")
L.append("---\n")
L.append("## 2. Baza Referencyjna (Reduced)\n")
L.append(f"* **{fmt(total_prod)}** – produkty (było {fmt(before_prod)}, usunięto {fmt(len(removed))}).")
L.append(f"* **{fmt(total_img)}** – zdjęcia (było {fmt(before_img)}, usunięto {fmt(before_img - total_img)}).")
L.append(f"* **{n_cat_after}** – kategorii i **{n_sub_after}** podkategorii "
         f"(było {n_sub_before}) w 3 grupach makro.\n")
L.append("| Grupa Makro | Produkty | Udział w produktach | Zdjęcia | Udział w zdjęciach | Podkategorie | Usunięto produktów |")
L.append("| :--- | ---: | :---: | ---: | :---: | :---: | ---: |")
for g in GROUPS:
    L.append(f"| **{g}** | **{fmt(g_prod[g])}** | **{pct(g_prod[g], total_prod)}** | **{fmt(g_img[g])}** | "
             f"**{pct(g_img[g], total_img)}** | {g_nsub[g]} | {fmt(g_before[g] - g_prod[g])} |")
L.append(f"| **SUMA** | **{fmt(total_prod)}** | **100.00%** | **{fmt(total_img)}** | **100.00%** | "
         f"**{n_sub_after}** | **{fmt(len(removed))}** |\n")
L.append("---\n")
L.append("## 3. Podkategorie (`input_subcategory`) w grupach odzieżowych\n")
L.append("Udziały „w całej bazie” liczone względem zredukowanej bazy odzieżowej "
         f"({fmt(total_prod)} produktów). Pełne liczności przed redukcją: "
         "[CATEGORY_GROUPS_BREAKDOWN.md](CATEGORY_GROUPS_BREAKDOWN.md).\n")
for n, g in enumerate(GROUPS, 1):
    L.append(f"### {n}. {g}")
    L.append(f"* **Łącznie w grupie:** {fmt(g_prod[g])} produktów (**{pct(g_prod[g], total_prod)}** bazy) | "
             f"{fmt(g_img[g])} zdjęć (**{pct(g_img[g], total_img)}**)\n")
    L.append("| Kategoria (`input_category`) | Podkategoria (`input_subcategory`) | Produkty | "
             "Udział w grupie | **Udział w całej bazie** | Zdjęcia |")
    L.append("| :--- | :--- | ---: | :---: | :---: | ---: |")
    cats = sorted([c for c in GROUPS[g] if cat_prod[c] > 0], key=lambda c: -cat_prod[c])
    for c in cats:
        for k in sorted((k for k in sub_prod if k[0] == c and sub_prod[k] > 0), key=lambda k: -sub_prod[k]):
            L.append(f"| **{c}** | {k[1]} | {fmt(sub_prod[k])} | {pct1(sub_prod[k], g_prod[g])} | "
                     f"**{pct(sub_prod[k], total_prod)}** | {fmt(sub_img[k])} |")
    L.append("\n---\n")

with open(os.path.join(BASE, "REDUCED_CATEGORIES.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L).rstrip("\n").rstrip("-").rstrip("\n") + "\n")

print(f"Przed: {before_prod} produktów, {n_sub_before} podkategorii | Po: {total_prod} produktów, {n_sub_after} podkategorii")
print(f"Usunięto: {len(removed)} produktów, {sum(rem_img.values())} zdjęć")
for g in GROUPS:
    print(f"{g:26} {g_prod[g]:6} ({pct(g_prod[g], total_prod)})")
