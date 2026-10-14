# Podział Kategorii i Grup Asortymentowych Katalogu H&M

Raport statystyczny i analiza struktury asortymentu na podstawie zbioru danych **H&M Personalized Fashion Recommendations** (`articles.csv`).

## Baza referencyjna zbioru danych:
* **47 224** – unikalne modele produktów (`product_code`).
* **105 542** – wszystkie warianty kolorystyczne / artykuły magazynowe (`article_id`).
* **131** – szczegółowych kategorii (`product_type_name`).

---

## 1. Główna Tabela Zbiorcza Grup Makro

| Grupa Makro | Modele (`product_count`) | Udział w modelach (`product_pct`) | Warianty (`article_count`) | Udział w wariantach (`article_pct`) | Liczba kategorii |
| :--- | ---: | :---: | ---: | :---: | :---: |
| **Góra (Upper body)** | **17 343** | **36.72%** | **42 741** | **40.50%** | 15 |
| **Dół (Lower body)** | **8 551** | **18.11%** | **19 812** | **18.77%** | 5 |
| **Całe ciało (Full body)** | **7 253** | **15.36%** | **13 292** | **12.59%** | 6 |
| **Akcesoria i torby (Accessories & Bags)** | **6 508** | **13.78%** | **11 186** | **10.60%** | 44 |
| **Obuwie (Shoes)** | **2 779** | **5.88%** | **5 283** | **5.01%** | 16 |
| **Bielizna (Underwear)** | **1 984** | **4.20%** | **5 490** | **5.20%** | 11 |
| **Stroje kąpielowe (Swimwear)** | **1 391** | **2.95%** | **3 127** | **2.96%** | 6 |
| **Skarpetki i rajstopy (Socks & Tights)** | **685** | **1.45%** | **2 442** | **2.31%** | 3 |
| **Bielizna nocna i piżamy (Nightwear)** | **670** | **1.42%** | **1 953** | **1.85%** | 6 |
| **Inne / Poza modą (Home, Cosmetic, Fun)** | **144** | **0.30%** | **216** | **0.20%** | 19 |
| **SUMA** | **47 224** | **100.00%** | **105 542** | **100.00%** | **131** |

> **Kluczowy wniosek architektoniczny:**  
> Sama **garderoba właściwa oraz obuwie** (Góra, Dół, Całe ciało, Obuwie) stanowi **35 926 unikalnych modeli ubrań (ponad 76% całego sklepu!)** i **81 128 wariantów magazynowych**. Pozostałe działy (bielizna, piżamy, akcesoria, dom) można w systemie traktować jako filtr negatywny (*Out-of-Scope*) lub wydzielić dla nich prostsze schematy zapytań.

---

## 2. Szczegółowe Zestawienie Kategorii w Grupach Makro

---

### 1. Góra (Upper body)
* **Łącznie w grupie:** 17 343 modele (**36.72%** całego katalogu) | 42 741 wariantów (**40.50%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | ---: | :---: |
| **Sweater** | 3 618 | 20.9% | 9 302 | 21.8% |
| **Jacket** | 2 313 | 13.3% | 3 940 | 9.2% |
| **T-shirt** | 2 172 | 12.5% | 7 904 | 18.5% |
| **Blouse** | 2 063 | 11.9% | 3 979 | 9.3% |
| **Top** | 1 893 | 10.9% | 4 155 | 9.7% |
| **Shirt** | 1 344 | 7.7% | 3 405 | 8.0% |
| **Vest top** | 1 112 | 6.4% | 2 991 | 7.0% |
| **Hoodie** | 739 | 4.3% | 2 356 | 5.5% |
| **Cardigan** | 703 | 4.1% | 1 550 | 3.6% |
| **Blazer** | 614 | 3.5% | 1 110 | 2.6% |
| **Bodysuit** | 342 | 2.0% | 913 | 2.1% |
| **Coat** | 294 | 1.7% | 460 | 1.1% |
| **Polo shirt** | 113 | 0.7% | 449 | 1.1% |
| **Outdoor Waistcoat** | 89 | 0.5% | 154 | 0.4% |
| **Tailored Waistcoat** | 34 | 0.2% | 73 | 0.2% |

---

### 2. Dół (Lower body)
* **Łącznie w grupie:** 8 551 modeli (**18.11%** całego katalogu) | 19 812 wariantów (**18.77%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | ---: | :---: |
| **Trousers** | 4 711 | 55.1% | 11 169 | 56.4% |
| **Skirt** | 1 580 | 18.5% | 2 696 | 13.6% |
| **Shorts** | 1 550 | 18.1% | 3 939 | 19.9% |
| **Leggings/Tights** | 656 | 7.7% | 1 878 | 9.5% |
| **Outdoor trousers** | 75 | 0.9% | 130 | 0.7% |

---

### 3. Całe ciało (Full body)
* **Łącznie w grupie:** 7 253 modele (**15.36%** całego katalogu) | 13 292 warianty (**12.59%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | ---: | :---: |
| **Dress** | 5 551 | 76.5% | 10 362 | 78.0% |
| **Garment Set** | 762 | 10.5% | 1 320 | 9.9% |
| **Jumpsuit/Playsuit** | 654 | 9.0% | 1 147 | 8.6% |
| **Dungarees** (ogrodniczki) | 225 | 3.1% | 309 | 2.3% |
| **Costumes** | 47 | 0.6% | 90 | 0.7% |
| **Outdoor overall** | 32 | 0.4% | 64 | 0.5% |

---

### 4. Obuwie (Shoes)
* **Łącznie w grupie:** 2 779 modeli (**5.88%** całego katalogu) | 5 283 warianty (**5.01%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) | Udział w grupie (warianty) |
| :--- | ---: | :---: | ---: | :---: |
| **Sneakers** | 807 | 29.0% | 1 621 | 30.7% |
| **Boots** | 611 | 22.0% | 1 028 | 19.5% |
| **Sandals** | 362 | 13.0% | 757 | 14.3% |
| **Other shoe** | 233 | 8.4% | 395 | 7.5% |
| **Ballerinas** | 161 | 5.8% | 372 | 7.0% |
| **Slippers** | 139 | 5.0% | 249 | 4.7% |
| **Heeled sandals** | 115 | 4.1% | 202 | 3.8% |
| **Flat shoe** | 99 | 3.6% | 165 | 3.1% |
| **Pumps** | 91 | 3.3% | 188 | 3.6% |
| **Flip flop** | 64 | 2.3% | 125 | 2.4% |
| **Wedge** | 61 | 2.2% | 113 | 2.1% |
| **Bootie** | 21 | 0.8% | 31 | 0.6% |
| **Heels** | 17 | 0.6% | 22 | 0.4% |
| **Flat shoes** | 6 | 0.2% | 10 | 0.2% |
| **Moccasins** | 2 | 0.1% | 4 | 0.1% |
| **Pre-walkers** | 1 | 0.0% | 1 | 0.0% |

---

### 5. Akcesoria i torby (Accessories & Bags)
* **Łącznie w grupie:** 6 508 modeli (**13.78%** całego katalogu) | 11 186 wariantów (**10.60%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) |
| :--- | ---: | :---: | ---: |
| **Earring** | 918 | 14.1% | 1 159 |
| **Bag** | 779 | 12.0% | 1 280 |
| **Other accessories** | 634 | 9.7% | 1 034 |
| **Hat/beanie** | 624 | 9.6% | 1 349 |
| **Hair/alice band** | 432 | 6.6% | 854 |
| **Scarf** | 421 | 6.5% | 1 013 |
| **Necklace** | 418 | 6.4% | 581 |
| **Sunglasses** | 348 | 5.3% | 621 |
| **Belt** | 288 | 4.4% | 458 |
| **Cap/peaked** | 261 | 4.0% | 573 |
| **Hat/brim** | 255 | 3.9% | 396 |
| **Gloves** | 224 | 3.4% | 367 |
| **Hair clip** | 195 | 3.0% | 244 |
| **Ring** | 160 | 2.5% | 240 |
| **Bracelet** | 141 | 2.2% | 180 |
| **Hair string** | 140 | 2.2% | 238 |
| **Tie** | 82 | 1.3% | 141 |
| **Wallet** | 43 | 0.7% | 77 |
| **Soft Toys** | 38 | 0.6% | 46 |
| **Watch** | 29 | 0.4% | 73 |
| **Beanie** | 28 | 0.4% | 56 |
| **Waterbottle** | 15 | 0.2% | 22 |
| **Dog Wear** | 15 | 0.2% | 20 |
| **Hair ties** | 11 | 0.2% | 24 |
| **Giftbox** | 10 | 0.2% | 15 |
*(Pozostałe mikro-typy poniżej 10 sztuk: Cap, Bucket hat, Straw hat, Felt hat, Backpack, Cross-body bag, Weekend bag, Braces itp.).*

---

### 6. Bielizna (Underwear)
* **Łącznie w grupie:** 1 984 modele (**4.20%**) | 5 490 wariantów (**5.20%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) |
| :--- | ---: | :---: | ---: |
| **Bra** | 947 | 47.7% | 2 212 |
| **Underwear bottom** | 757 | 38.2% | 2 748 |
| **Underwear body** | 125 | 6.3% | 174 |
| **Robe** | 53 | 2.7% | 136 |
| **Underwear set** | 28 | 1.4% | 47 |
| **Kids Underwear top** | 26 | 1.3% | 96 |
| **Nipple covers** | 18 | 0.9% | 19 |
| **Underdress** | 12 | 0.6% | 20 |
| **Long John** | 10 | 0.5% | 30 |
| **Underwear corset** | 7 | 0.4% | 7 |
| **Bra extender** | 1 | 0.1% | 1 |

---

### 7. Stroje kąpielowe (Swimwear)
* **Łącznie w grupie:** 1 391 modeli (**2.95%**) | 3 127 wariantów (**2.96%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) |
| :--- | ---: | :---: | ---: |
| **Swimwear bottom** | 452 | 32.5% | 1 307 |
| **Swimsuit** | 383 | 27.5% | 662 |
| **Bikini top** | 355 | 25.5% | 850 |
| **Swimwear set** | 131 | 9.4% | 192 |
| **Sarong** | 44 | 3.2% | 66 |
| **Swimwear top** | 31 | 2.2% | 50 |

---

### 8. Skarpetki i rajstopy (Socks & Tights)
* **Łącznie w grupie:** 685 modeli (**1.45%**) | 2 442 warianty (**2.31%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) |
| :--- | ---: | :---: | ---: |
| **Socks** | 474 | 69.2% | 1 889 |
| **Underwear Tights** | 208 | 30.4% | 546 |
| **Leg warmers** | 4 | 0.6% | 7 |

---

### 9. Bielizna nocna i piżamy (Nightwear)
* **Łącznie w grupie:** 670 modeli (**1.42%**) | 1 953 warianty (**1.85%**)

| Kategoria (`product_type_name`) | Modele (`product_count`) | Udział w grupie (modele) | Warianty (`article_count`) |
| :--- | ---: | :---: | ---: |
| **Pyjama set** | 387 | 57.8% | 1 120 |
| **Pyjama jumpsuit/playsuit** | 102 | 15.2% | 388 |
| **Night gown** | 92 | 13.7% | 171 |
| **Pyjama bottom** | 78 | 11.6% | 220 |
| **Sleeping sack** | 10 | 1.5% | 48 |
| **Sleep Bag** | 2 | 0.3% | 6 |

---

### 10. Inne / Poza modą (Home, Cosmetic, Fun)
* **Łącznie w grupie:** 144 modele (**0.30%**) | 216 wariantów (**0.20%**)
* `Unknown` (67 modeli, 121 sztuk), `Fine cosmetics` (37), `Side table` (13), `Dog wear` (5), `Chem. cosmetics` (3), `Zipper head` (3), `Stain remover spray` (2), `Blanket` (1), `Cushion` (1), `Towel` (1), `Sewing kit` (1) itp.
