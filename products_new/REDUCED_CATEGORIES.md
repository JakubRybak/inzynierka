# Zredukowana Taksonomia Podkategorii – FashionGen (odzież)

Raport po usunięciu niszowych i wykluczonych podkategorii (`input_subcategory`) z grup odzieżowych (**Góra, Dół, Całe ciało**). Obuwie, akcesoria, bielizna, stroje kąpielowe i skarpetki nie wchodzą do tego zestawienia.

Liczenie: produkt = unikalny `input_productID`, zdjęcie = unikalna para (`productID`, `pose`). Każdy kolor tego samego fasonu to osobny produkt.

---

## 1. Zakres Usunięć

| Usunięta podkategoria | Kategoria nadrzędna | Produkty | Zdjęcia |
| :--- | :--- | ---: | ---: |
| **BLAZERS** | SUITS & BLAZERS | 696 | 2 879 |
| **BLAZERS** | JACKETS & COATS | 320 | 1 300 |
| **LEGGINGS** | PANTS | 172 | 716 |
| **JUMPSUITS** | JUMPSUITS | 168 | 688 |
| **PEACOATS** | JACKETS & COATS | 61 | 265 |
| **HENLEYS** | TOPS | 58 | 233 |
| **SUITS** | SUITS & BLAZERS | 45 | 198 |
| **TUXEDOS** | SUITS & BLAZERS | 17 | 73 |
| **WAISTCOATS** | SUITS & BLAZERS | 12 | 50 |
| **SHAWLNECKS** | SWEATERS | 5 | 20 |
| **SUMA usunięć** | | **1 554** | **6 422** |

> **Uwagi do wykluczeń:**
> * **BLAZERS** – usunięto wszystkie marynarki i żakiety: zarówno męskie z `SUITS & BLAZERS` (696 modeli), jak i damskie z `JACKETS & COATS` (320 modeli) – łącznie **1 016 modeli** (4 179 zdjęć).
> * **Kategoria SUITS & BLAZERS** została całkowicie zlikwidowana (wszystkie jej podkategorie: `BLAZERS`, `SUITS`, `TUXEDOS`, `WAISTCOATS` zostały usunięte).
> * **LEGGINGS** (172 modele) – usunięto z kategorii `PANTS` w grupie Dół.
> * **JUMPSUITS** (168 modeli) – usunięto całą kategorię kombinezonów; w grupie Całe ciało pozostają wyłącznie `DRESSES` (sukienki).

---

## 2. Baza Referencyjna (Reduced)

* **53 262** – produkty (było 54 816, usunięto 1 554).
* **221 466** – zdjęcia (było 227 888, usunięto 6 422).
* **9** – kategorii i **36** podkategorii (było 46) w 3 grupach makro.

| Grupa Makro | Produkty | Udział w produktach | Zdjęcia | Udział w zdjęciach | Podkategorie | Usunięto produktów |
| :--- | ---: | :---: | ---: | :---: | :---: | ---: |
| **Góra (Upper body)** | **36 752** | **69.00%** | **154 075** | **69.57%** | 23 | 1 214 |
| **Dół (Lower body)** | **13 910** | **26.12%** | **56 757** | **25.63%** | 10 | 172 |
| **Całe ciało (Full body)** | **2 600** | **4.88%** | **10 634** | **4.80%** | 3 | 168 |
| **SUMA** | **53 262** | **100.00%** | **221 466** | **100.00%** | **36** | **1 554** |

---

## 3. Podkategorie (`input_subcategory`) w grupach odzieżowych

Udziały „w całej bazie” liczone względem zredukowanej bazy odzieżowej (53 262 produktów). Pełne liczności przed redukcją: [CATEGORY_GROUPS_BREAKDOWN.md](CATEGORY_GROUPS_BREAKDOWN.md).

### 1. Góra (Upper body)
* **Łącznie w grupie:** 36 752 produktów (**69.00%** bazy) | 154 075 zdjęć (**69.57%**)

| Kategoria (`input_category`) | Podkategoria (`input_subcategory`) | Produkty | Udział w grupie | **Udział w całej bazie** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **TOPS** | T-SHIRTS | 8 961 | 24.4% | **16.82%** | 36 944 |
| **TOPS** | SHIRTS | 1 215 | 3.3% | **2.28%** | 5 123 |
| **TOPS** | BLOUSES | 1 002 | 2.7% | **1.88%** | 4 135 |
| **TOPS** | TANK TOPS & CAMISOLES | 843 | 2.3% | **1.58%** | 3 450 |
| **TOPS** | POLOS | 590 | 1.6% | **1.11%** | 2 433 |
| **TOPS** | TANK TOPS | 177 | 0.5% | **0.33%** | 715 |
| **TOPS** | BODYSUITS | 118 | 0.3% | **0.22%** | 581 |
| **SWEATERS** | CREWNECKS | 3 645 | 9.9% | **6.84%** | 14 992 |
| **SWEATERS** | SWEATSHIRTS | 3 432 | 9.3% | **6.44%** | 13 976 |
| **SWEATERS** | HOODIES & ZIPUPS | 2 779 | 7.6% | **5.22%** | 11 697 |
| **SWEATERS** | TURTLENECKS | 1 006 | 2.7% | **1.89%** | 4 253 |
| **SWEATERS** | CARDIGANS | 904 | 2.5% | **1.70%** | 3 774 |
| **SWEATERS** | V-NECKS | 339 | 0.9% | **0.64%** | 1 418 |
| **JACKETS & COATS** | COATS | 1 884 | 5.1% | **3.54%** | 8 125 |
| **JACKETS & COATS** | JACKETS | 1 642 | 4.5% | **3.08%** | 7 155 |
| **JACKETS & COATS** | BOMBERS | 1 496 | 4.1% | **2.81%** | 6 521 |
| **JACKETS & COATS** | DOWN | 1 252 | 3.4% | **2.35%** | 5 914 |
| **JACKETS & COATS** | DENIM JACKETS | 836 | 2.3% | **1.57%** | 3 558 |
| **JACKETS & COATS** | LEATHER JACKETS | 829 | 2.3% | **1.56%** | 3 537 |
| **JACKETS & COATS** | FUR & SHEARLING | 291 | 0.8% | **0.55%** | 1 302 |
| **JACKETS & COATS** | VESTS | 221 | 0.6% | **0.41%** | 929 |
| **JACKETS & COATS** | TRENCH COATS | 166 | 0.5% | **0.31%** | 739 |
| **SHIRTS** | SHIRTS | 3 124 | 8.5% | **5.87%** | 12 804 |

---

### 2. Dół (Lower body)
* **Łącznie w grupie:** 13 910 produktów (**26.12%** bazy) | 56 757 zdjęć (**25.63%**)

| Kategoria (`input_category`) | Podkategoria (`input_subcategory`) | Produkty | Udział w grupie | **Udział w całej bazie** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **PANTS** | TROUSERS | 3 744 | 26.9% | **7.03%** | 15 208 |
| **PANTS** | SWEATPANTS | 1 431 | 10.3% | **2.69%** | 5 838 |
| **PANTS** | LOUNGE PANTS | 705 | 5.1% | **1.32%** | 2 892 |
| **PANTS** | CARGO PANTS | 188 | 1.4% | **0.35%** | 771 |
| **PANTS** | LEATHER PANTS | 172 | 1.2% | **0.32%** | 698 |
| **JEANS** | JEANS | 3 704 | 26.6% | **6.95%** | 15 240 |
| **SHORTS** | SHORTS | 2 053 | 14.8% | **3.85%** | 8 337 |
| **SKIRTS** | SHORT SKIRTS | 900 | 6.5% | **1.69%** | 3 647 |
| **SKIRTS** | MID LENGTH SKIRTS | 882 | 6.3% | **1.66%** | 3 589 |
| **SKIRTS** | LONG SKIRTS | 131 | 0.9% | **0.25%** | 537 |

---

### 3. Całe ciało (Full body)
* **Łącznie w grupie:** 2 600 produktów (**4.88%** bazy) | 10 634 zdjęć (**4.80%**)

| Kategoria (`input_category`) | Podkategoria (`input_subcategory`) | Produkty | Udział w grupie | **Udział w całej bazie** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **DRESSES** | SHORT DRESSES | 1 340 | 51.5% | **2.52%** | 5 460 |
| **DRESSES** | MID LENGTH DRESSES | 1 036 | 39.8% | **1.95%** | 4 247 |
| **DRESSES** | LONG DRESSES | 224 | 8.6% | **0.42%** | 927 |
