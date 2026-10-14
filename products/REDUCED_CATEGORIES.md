# Zredukowana Taksonomia Katalogu H&M (Core Apparel & Footwear)

Raport statystyczny po oczyszczeniu katalogu H&M ze zbędnego szumu, niszowych kategorii oraz działów spoza garderoby właściwej i obuwia.

---

## 1. Zakres Oczyszczenia Danych

### A. Odrzucone całe działy (poza garderobą i obuwiem):
* **Akcesoria i torby (Accessories & Bags)** – 6 508 modeli
* **Bielizna (Underwear)** – 1 984 modele
* **Stroje kąpielowe (Swimwear)** – 1 391 modeli
* **Skarpetki i rajstopy (Socks & Tights)** – 685 modeli
* **Bielizna nocna i piżamy (Nightwear)** – 670 modeli
* **Inne / Poza modą (Home, Cosmetic, Furniture, Fun)** – 144 modele

### B. Odrzucone niszowe mikro-kategorie odzieżowe i obuwnicze:
* **Góra:** *Outdoor Waistcoat* (89 modeli), *Tailored Waistcoat* (34 modele)
* **Całe ciało:** *Costumes* (47 modeli), *Outdoor overall* (32 modele), *Garment Set* (762 modele – niespójne zestawy mix)
* **Obuwie:** *Pre-walkers* (1 model), *Moccasins* (2 modele), *Flat shoes* (6 modeli – duplikat tagu *Flat shoe*)

*(Uwaga: Kategoria `Outdoor trousers` – 75 modeli / 130 wariantów – została zachowana w grupie Dół).*

---

## 2. Nowa Baza Referencyjna (Core)

* **34 956** – unikalne modele produktów (`product_code`).
* **79 412** – warianty kolorystyczne / artykuły magazynowe (`article_id`).
* **34** – kategorie szczegółowe (`product_type_name`) w 4 głównych grupach makro.

---

## 3. Główna Tabela Zbiorcza Grup Makro

| Grupa Makro | Modele (`product_count`) | **Udział w modelach (`product_pct`)** | Warianty (`article_count`) | **Udział w wariantach (`article_pct`)** | Liczba kategorii |
| :--- | ---: | :---: | ---: | :---: | :---: |
| **Góra (Upper body)** | **17 220** | **49.26%** | **42 514** | **53.54%** | 13 |
| **Dół (Lower body)** | **8 551** | **24.46%** | **19 812** | **24.95%** | 5 |
| **Całe ciało (Full body)** | **6 419** | **18.36%** | **11 818** | **14.88%** | 3 |
| **Obuwie (Shoes)** | **2 776** | **7.94%** | **5 268** | **6.63%** | 13 |
| **SUMA (Core Apparel & Footwear)** | **34 956** | **100.00%** | **79 412** | **100.00%** | **34** |

---

## 4. Szczegółowe Tabele Kategorii w Grupach

---

### 1. Góra (Upper body)
* **Łącznie w grupie:** 17 220 modeli (**49.26%** bazy) | 42 514 wariantów (**53.54%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Sweater** | 3 618 | 21.0% | **10.35%** | 9 302 | 21.9% |
| **Jacket** | 2 313 | 13.4% | **6.62%** | 3 940 | 9.3% |
| **T-shirt** | 2 172 | 12.6% | **6.21%** | 7 904 | 18.6% |
| **Blouse** | 2 063 | 12.0% | **5.90%** | 3 979 | 9.4% |
| **Top** | 1 893 | 11.0% | **5.42%** | 4 155 | 9.8% |
| **Shirt** | 1 344 | 7.8% | **3.84%** | 3 405 | 8.0% |
| **Vest top** | 1 112 | 6.5% | **3.18%** | 2 991 | 7.0% |
| **Hoodie** | 739 | 4.3% | **2.11%** | 2 356 | 5.5% |
| **Cardigan** | 703 | 4.1% | **2.01%** | 1 550 | 3.6% |
| **Blazer** | 614 | 3.6% | **1.76%** | 1 110 | 2.6% |
| **Bodysuit** | 342 | 2.0% | **0.98%** | 913 | 2.1% |
| **Coat** | 294 | 1.7% | **0.84%** | 460 | 1.1% |
| **Polo shirt** | 113 | 0.7% | **0.32%** | 449 | 1.1% |

---

### 2. Dół (Lower body)
* **Łącznie w grupie:** 8 551 modeli (**24.46%** bazy) | 19 812 wariantów (**24.95%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Trousers** | 4 711 | 55.1% | **13.48%** | 11 169 | 56.4% |
| **Skirt** | 1 580 | 18.5% | **4.52%** | 2 696 | 13.6% |
| **Shorts** | 1 550 | 18.1% | **4.43%** | 3 939 | 19.9% |
| **Leggings/Tights** | 656 | 7.7% | **1.88%** | 1 878 | 9.5% |
| **Outdoor trousers** | 75 | 0.9% | **0.21%** | 130 | 0.7% |

---

### 3. Całe ciało (Full body)
* **Łącznie w grupie:** 6 419 modeli (**18.36%** bazy) | 11 818 wariantów (**14.88%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Dress** | 5 551 | 86.5% | **15.88%** | 10 362 | 87.7% |
| **Jumpsuit/Playsuit** | 654 | 10.2% | **1.87%** | 1 147 | 9.7% |
| **Dungarees** (ogrodniczki) | 225 | 3.5% | **0.64%** | 309 | 2.6% |

---

### 4. Obuwie (Shoes)
* **Łącznie w grupie:** 2 776 modeli (**7.94%** bazy) | 5 268 wariantów (**6.63%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Sneakers** | 807 | 29.1% | **2.31%** | 1 621 | 30.8% |
| **Boots** | 611 | 22.0% | **1.75%** | 1 028 | 19.5% |
| **Sandals** | 362 | 13.0% | **1.04%** | 757 | 14.4% |
| **Other shoe** | 233 | 8.4% | **0.67%** | 395 | 7.5% |
| **Ballerinas** | 161 | 5.8% | **0.46%** | 372 | 7.1% |
| **Slippers** | 139 | 5.0% | **0.40%** | 249 | 4.7% |
| **Heeled sandals** | 115 | 4.1% | **0.33%** | 202 | 3.8% |
| **Flat shoe** | 99 | 3.6% | **0.28%** | 165 | 3.1% |
| **Pumps** | 91 | 3.3% | **0.26%** | 188 | 3.6% |
| **Flip flop** | 64 | 2.3% | **0.18%** | 125 | 2.4% |
| **Wedge** | 61 | 2.2% | **0.17%** | 113 | 2.1% |
| **Bootie** | 21 | 0.8% | **0.06%** | 31 | 0.6% |
| **Heels** | 17 | 0.6% | **0.05%** | 22 | 0.4% |
