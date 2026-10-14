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
* **Dół:** *Outdoor trousers* (75 modeli)
* **Całe ciało:** *Costumes* (47 modeli), *Outdoor overall* (32 modele), *Garment Set* (762 modele – niespójne zestawy mix)
* **Obuwie:** *Pre-walkers* (1 model), *Moccasins* (2 modele), *Flat shoes* (6 modeli – duplikat tagu *Flat shoe*)

---

## 2. Nowa Baza Referencyjna (Core)

* **34 882** – unikalne modele produktów (`product_code`).
* **79 282** – warianty kolorystyczne / artykuły magazynowe (`article_id`).
* **33** – kategorie szczegółowe (`product_type_name`) w 4 głównych grupach makro.

---

## 3. Główna Tabela Zbiorcza Grup Makro

| Grupa Makro | Modele (`product_count`) | **Udział w modelach (`product_pct`)** | Warianty (`article_count`) | **Udział w wariantach (`article_pct`)** | Liczba kategorii |
| :--- | ---: | :---: | ---: | :---: | :---: |
| **Góra (Upper body)** | **17 220** | **49.37%** | **42 514** | **53.62%** | 13 |
| **Dół (Lower body)** | **8 477** | **24.30%** | **19 682** | **24.83%** | 4 |
| **Całe ciało (Full body)** | **6 419** | **18.40%** | **11 818** | **14.91%** | 3 |
| **Obuwie (Shoes)** | **2 776** | **7.96%** | **5 268** | **6.64%** | 13 |
| **SUMA (Core Apparel & Footwear)** | **34 882** | **100.00%** | **79 282** | **100.00%** | **33** |

---

## 4. Szczegółowe Tabele Kategorii w Grupach

---

### 1. Góra (Upper body)
* **Łącznie w grupie:** 17 220 modeli (**49.37%** bazy) | 42 514 wariantów (**53.62%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Sweater** | 3 618 | 21.0% | **10.37%** | 9 302 | 21.9% |
| **Jacket** | 2 313 | 13.4% | **6.63%** | 3 940 | 9.3% |
| **T-shirt** | 2 172 | 12.6% | **6.23%** | 7 904 | 18.6% |
| **Blouse** | 2 063 | 12.0% | **5.91%** | 3 979 | 9.4% |
| **Top** | 1 893 | 11.0% | **5.43%** | 4 155 | 9.8% |
| **Shirt** | 1 344 | 7.8% | **3.85%** | 3 405 | 8.0% |
| **Vest top** | 1 112 | 6.5% | **3.19%** | 2 991 | 7.0% |
| **Hoodie** | 739 | 4.3% | **2.12%** | 2 356 | 5.5% |
| **Cardigan** | 703 | 4.1% | **2.02%** | 1 550 | 3.6% |
| **Blazer** | 614 | 3.6% | **1.76%** | 1 110 | 2.6% |
| **Bodysuit** | 342 | 2.0% | **0.98%** | 913 | 2.1% |
| **Coat** | 294 | 1.7% | **0.84%** | 460 | 1.1% |
| **Polo shirt** | 113 | 0.7% | **0.32%** | 449 | 1.1% |

---

### 2. Dół (Lower body)
* **Łącznie w grupie:** 8 477 modeli (**24.30%** bazy) | 19 682 warianty (**24.83%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Trousers** | 4 711 | 55.6% | **13.51%** | 11 169 | 56.7% |
| **Skirt** | 1 580 | 18.6% | **4.53%** | 2 696 | 13.7% |
| **Shorts** | 1 550 | 18.3% | **4.44%** | 3 939 | 20.0% |
| **Leggings/Tights** | 656 | 7.7% | **1.88%** | 1 878 | 9.5% |

---

### 3. Całe ciało (Full body)
* **Łącznie w grupie:** 6 419 modeli (**18.40%** bazy) | 11 818 wariantów (**14.91%** bazy)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | **Udział w całej bazie** | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **Dress** | 5 551 | 86.5% | **15.91%** | 10 362 | 87.7% |
| **Jumpsuit/Playsuit** | 654 | 10.2% | **1.87%** | 1 147 | 9.7% |
| **Dungarees** (ogrodniczki) | 225 | 3.5% | **0.65%** | 309 | 2.6% |

---

### 4. Obuwie (Shoes)
* **Łącznie w grupie:** 2 776 modeli (**7.96%** bazy) | 5 268 wariantów (**6.64%** bazy)

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
