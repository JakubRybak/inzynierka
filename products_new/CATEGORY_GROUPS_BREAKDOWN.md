# Podział Kategorii i Grup Asortymentowych – FashionGen

Raport statystyczny i analiza struktury asortymentu na podstawie zbioru danych **FashionGen** (`fashiongen_256_256_train.h5` + `fashiongen_256_256_validation.h5`, zdjęcia 256×256).

## Baza referencyjna zbioru danych:
* **67 666** – unikalne produkty (`input_productID`): 60 147 w train + 7 519 w validation (brak wspólnych `productID` między splitami).
* **293 018** – wierszy w plikach h5 (1 wiersz = 1 zdjęcie, nie 1 produkt).
* **292 623** – unikalnych zdjęć (para `productID` + `pose`); 395 wierszy to duplikaty.
* **48** – kategorii (`input_category`) i **132** podkategorii (`input_subcategory`).
* Płeć: Women 33 941 (50.2%), Men 33 725 (49.8%).

> **Uwagi o strukturze danych (ważne przy liczeniu):**  
> * Produkt = unikalny `productID`. Warianty kolorystyczne tego samego fasonu mają **różne** `productID` i nie ma wspólnego identyfikatora modelu – każdy kolor liczy się jako osobny produkt (odpowiednik `article_id` z H&M, a nie `product_code`).  
> * Produkt ma zwykle 4 zdjęcia (średnio 4.32). 87 produktów ma zduplikowany cały zestaw zdjęć (wiersze identyczne) – dlatego deduplikacja po `productID`.  
> * Atrybuty (`category`, `subcategory`, `name`, `brand`, `composition`…) są spójne w obrębie `productID`.

---

## 1. Główna Tabela Zbiorcza Grup Makro

| Grupa Makro | Produkty (`product_count`) | Udział w produktach (`product_pct`) | Zdjęcia (`image_count`) | Udział w zdjęciach (`image_pct`) | Liczba kategorii |
| :--- | ---: | :---: | ---: | :---: | :---: |
| **Góra (Upper body)** | **37 966** | **56.11%** | **159 093** | **54.37%** | 5 |
| **Dół (Lower body)** | **14 082** | **20.81%** | **57 473** | **19.64%** | 4 |
| **Akcesoria i torby (Accessories & Bags)** | **7 573** | **11.19%** | **33 994** | **11.62%** | 22 |
| **Obuwie (Shoes)** | **4 833** | **7.14%** | **28 709** | **9.81%** | 10 |
| **Całe ciało (Full body)** | **2 768** | **4.09%** | **11 322** | **3.87%** | 2 |
| **Bielizna (Underwear)** | **306** | **0.45%** | **1 503** | **0.51%** | 2 |
| **Skarpetki (Socks)** | **74** | **0.11%** | **283** | **0.10%** | 1 |
| **Stroje kąpielowe (Swimwear)** | **59** | **0.09%** | **227** | **0.08%** | 1 |
| **Inne / Poza modą (Home)** | **5** | **0.01%** | **19** | **0.01%** | 1 |
| **SUMA** | **67 666** | **100.00%** | **292 623** | **100.00%** | **48** |

> **Kluczowy wniosek architektoniczny:**  
> Sama **garderoba właściwa oraz obuwie** (Góra, Dół, Całe ciało, Obuwie) to **59 649 produktów (88.2% zbioru)** i **256 597 zdjęć**. Pozostałe działy (akcesoria, bielizna, stroje kąpielowe, skarpetki) można traktować jako filtr negatywny (*Out-of-Scope*).

---

## 2. Szczegółowe Zestawienie Kategorii w Grupach Makro

---

### 1. Góra (Upper body)
* **Łącznie w grupie:** 37 966 produktów (**56.11%** całego zbioru) | 159 093 zdjęć (**54.37%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **TOPS** | 12 964 | 34.1% | **19.16%** | 53 614 | 33.7% |
| **SWEATERS** | 12 110 | 31.9% | **17.90%** | 50 130 | 31.5% |
| **JACKETS & COATS** | 8 998 | 23.7% | **13.30%** | 39 345 | 24.7% |
| **SHIRTS** | 3 124 | 8.2% | **4.62%** | 12 804 | 8.0% |
| **SUITS & BLAZERS** | 770 | 2.0% | **1.14%** | 3 200 | 2.0% |

---

### 2. Dół (Lower body)
* **Łącznie w grupie:** 14 082 produktów (**20.81%** całego zbioru) | 57 473 zdjęć (**19.64%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **PANTS** | 6 412 | 45.5% | **9.48%** | 26 123 | 45.5% |
| **JEANS** | 3 704 | 26.3% | **5.47%** | 15 240 | 26.5% |
| **SHORTS** | 2 053 | 14.6% | **3.03%** | 8 337 | 14.5% |
| **SKIRTS** | 1 913 | 13.6% | **2.83%** | 7 773 | 13.5% |

---

### 3. Akcesoria i torby (Accessories & Bags)
* **Łącznie w grupie:** 7 573 produktów (**11.19%** całego zbioru) | 33 994 zdjęć (**11.62%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **HATS** | 1 662 | 21.9% | **2.46%** | 5 113 | 15.0% |
| **SHOULDER BAGS** | 1 352 | 17.9% | **2.00%** | 7 813 | 23.0% |
| **JEWELRY** | 1 157 | 15.3% | **1.71%** | 5 529 | 16.3% |
| **EYEWEAR** | 683 | 9.0% | **1.01%** | 2 798 | 8.2% |
| **BACKPACKS** | 557 | 7.4% | **0.82%** | 3 201 | 9.4% |
| **SCARVES** | 466 | 6.2% | **0.69%** | 1 283 | 3.8% |
| **TOTE BAGS** | 435 | 5.7% | **0.64%** | 2 560 | 7.5% |
| **DUFFLE & TOP HANDLE BAGS** | 288 | 3.8% | **0.43%** | 1 713 | 5.0% |
| **CLUTCHES & POUCHES** | 281 | 3.7% | **0.42%** | 1 266 | 3.7% |
| **BELTS & SUSPENDERS** | 122 | 1.6% | **0.18%** | 380 | 1.1% |
| **FINE JEWELRY** | 111 | 1.5% | **0.16%** | 532 | 1.6% |
| **MESSENGER BAGS & SATCHELS** | 101 | 1.3% | **0.15%** | 595 | 1.8% |
| **TIES** | 94 | 1.2% | **0.14%** | 283 | 0.8% |
| **KEYCHAINS** | 76 | 1.0% | **0.11%** | 226 | 0.7% |
| **BAG ACCESSORIES** | 60 | 0.8% | **0.09%** | 124 | 0.4% |
| **POUCHES & DOCUMENT HOLDERS** | 36 | 0.5% | **0.05%** | 136 | 0.4% |
| **GLOVES** | 24 | 0.3% | **0.04%** | 74 | 0.2% |
| **DUFFLE BAGS** | 22 | 0.3% | **0.03%** | 132 | 0.4% |
| **MESSENGER BAGS** | 17 | 0.2% | **0.03%** | 100 | 0.3% |
| **BRIEFCASES** | 14 | 0.2% | **0.02%** | 82 | 0.2% |
| **POCKET SQUARES & TIE BARS** | 10 | 0.1% | **0.01%** | 25 | 0.1% |
| **TRAVEL BAGS** | 5 | 0.1% | **0.01%** | 29 | 0.1% |

---

### 4. Obuwie (Shoes)
* **Łącznie w grupie:** 4 833 produktów (**7.14%** całego zbioru) | 28 709 zdjęć (**9.81%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **SNEAKERS** | 1 974 | 40.8% | **2.92%** | 11 778 | 41.0% |
| **BOOTS** | 872 | 18.0% | **1.29%** | 5 074 | 17.7% |
| **FLATS** | 722 | 14.9% | **1.07%** | 4 313 | 15.0% |
| **SANDALS** | 662 | 13.7% | **0.98%** | 3 947 | 13.7% |
| **HEELS** | 363 | 7.5% | **0.54%** | 2 169 | 7.6% |
| **LACE UPS** | 119 | 2.5% | **0.18%** | 709 | 2.5% |
| **LOAFERS** | 91 | 1.9% | **0.13%** | 541 | 1.9% |
| **ESPADRILLES** | 23 | 0.5% | **0.03%** | 137 | 0.5% |
| **MONKSTRAPS** | 5 | 0.1% | **0.01%** | 29 | 0.1% |
| **BOAT SHOES & MOCCASINS** | 2 | 0.0% | **0.00%** | 12 | 0.0% |

---

### 5. Całe ciało (Full body)
* **Łącznie w grupie:** 2 768 produktów (**4.09%** całego zbioru) | 11 322 zdjęć (**3.87%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **DRESSES** | 2 600 | 93.9% | **3.84%** | 10 634 | 93.9% |
| **JUMPSUITS** | 168 | 6.1% | **0.25%** | 688 | 6.1% |

---

### 6. Bielizna (Underwear)
* **Łącznie w grupie:** 306 produktów (**0.45%** całego zbioru) | 1 503 zdjęć (**0.51%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **LINGERIE** | 298 | 97.4% | **0.44%** | 1 475 | 98.1% |
| **UNDERWEAR & LOUNGEWEAR** | 8 | 2.6% | **0.01%** | 28 | 1.9% |

---

### 7. Skarpetki (Socks)
* **Łącznie w grupie:** 74 produktów (**0.11%** całego zbioru) | 283 zdjęć (**0.10%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **SOCKS** | 74 | 100.0% | **0.11%** | 283 | 100.0% |

---

### 8. Stroje kąpielowe (Swimwear)
* **Łącznie w grupie:** 59 produktów (**0.09%** całego zbioru) | 227 zdjęć (**0.08%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **SWIMWEAR** | 59 | 100.0% | **0.09%** | 227 | 100.0% |

---

### 9. Inne / Poza modą (Home)
* **Łącznie w grupie:** 5 produktów (**0.01%** całego zbioru) | 19 zdjęć (**0.01%**)

| Kategoria (`input_category`) | Produkty (`product_count`) | Udział w grupie (produkty) | **Udział w całym zbiorze** | Zdjęcia (`image_count`) | Udział w grupie (zdjęcia) |
| :--- | ---: | :---: | :---: | ---: | :---: |
| **BLANKETS** | 5 | 100.0% | **0.01%** | 19 | 100.0% |

---

## 3. Podkategorie (`input_subcategory`) w grupach odzieżowych

FashionGen ma wbudowaną drugą warstwę taksonomii. Poniżej podkategorie dla Góry, Dołu i Całego ciała (pełna lista wszystkich grup: `data/subcategory_counts.csv`).

### Góra (Upper body)

| Kategoria | Podkategoria | Produkty | Udział w grupie | **Udział w całym zbiorze** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **TOPS** | T-SHIRTS | 8 961 | 23.6% | **13.24%** | 36 944 |
| **TOPS** | SHIRTS | 1 215 | 3.2% | **1.80%** | 5 123 |
| **TOPS** | BLOUSES | 1 002 | 2.6% | **1.48%** | 4 135 |
| **TOPS** | TANK TOPS & CAMISOLES | 843 | 2.2% | **1.25%** | 3 450 |
| **TOPS** | POLOS | 590 | 1.6% | **0.87%** | 2 433 |
| **TOPS** | TANK TOPS | 177 | 0.5% | **0.26%** | 715 |
| **TOPS** | BODYSUITS | 118 | 0.3% | **0.17%** | 581 |
| **TOPS** | HENLEYS | 58 | 0.2% | **0.09%** | 233 |
| **SWEATERS** | CREWNECKS | 3 645 | 9.6% | **5.39%** | 14 992 |
| **SWEATERS** | SWEATSHIRTS | 3 432 | 9.0% | **5.07%** | 13 976 |
| **SWEATERS** | HOODIES & ZIPUPS | 2 779 | 7.3% | **4.11%** | 11 697 |
| **SWEATERS** | TURTLENECKS | 1 006 | 2.6% | **1.49%** | 4 253 |
| **SWEATERS** | CARDIGANS | 904 | 2.4% | **1.34%** | 3 774 |
| **SWEATERS** | V-NECKS | 339 | 0.9% | **0.50%** | 1 418 |
| **SWEATERS** | SHAWLNECKS | 5 | 0.0% | **0.01%** | 20 |
| **JACKETS & COATS** | COATS | 1 884 | 5.0% | **2.78%** | 8 125 |
| **JACKETS & COATS** | JACKETS | 1 642 | 4.3% | **2.43%** | 7 155 |
| **JACKETS & COATS** | BOMBERS | 1 496 | 3.9% | **2.21%** | 6 521 |
| **JACKETS & COATS** | DOWN | 1 252 | 3.3% | **1.85%** | 5 914 |
| **JACKETS & COATS** | DENIM JACKETS | 836 | 2.2% | **1.24%** | 3 558 |
| **JACKETS & COATS** | LEATHER JACKETS | 829 | 2.2% | **1.23%** | 3 537 |
| **JACKETS & COATS** | BLAZERS | 320 | 0.8% | **0.47%** | 1 300 |
| **JACKETS & COATS** | FUR & SHEARLING | 291 | 0.8% | **0.43%** | 1 302 |
| **JACKETS & COATS** | VESTS | 221 | 0.6% | **0.33%** | 929 |
| **JACKETS & COATS** | TRENCH COATS | 166 | 0.4% | **0.25%** | 739 |
| **JACKETS & COATS** | PEACOATS | 61 | 0.2% | **0.09%** | 265 |
| **SHIRTS** | SHIRTS | 3 124 | 8.2% | **4.62%** | 12 804 |
| **SUITS & BLAZERS** | BLAZERS | 696 | 1.8% | **1.03%** | 2 879 |
| **SUITS & BLAZERS** | SUITS | 45 | 0.1% | **0.07%** | 198 |
| **SUITS & BLAZERS** | TUXEDOS | 17 | 0.0% | **0.03%** | 73 |
| **SUITS & BLAZERS** | WAISTCOATS | 12 | 0.0% | **0.02%** | 50 |

### Dół (Lower body)

| Kategoria | Podkategoria | Produkty | Udział w grupie | **Udział w całym zbiorze** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **PANTS** | TROUSERS | 3 744 | 26.6% | **5.53%** | 15 208 |
| **PANTS** | SWEATPANTS | 1 431 | 10.2% | **2.11%** | 5 838 |
| **PANTS** | LOUNGE PANTS | 705 | 5.0% | **1.04%** | 2 892 |
| **PANTS** | CARGO PANTS | 188 | 1.3% | **0.28%** | 771 |
| **PANTS** | LEATHER PANTS | 172 | 1.2% | **0.25%** | 698 |
| **PANTS** | LEGGINGS | 172 | 1.2% | **0.25%** | 716 |
| **JEANS** | JEANS | 3 704 | 26.3% | **5.47%** | 15 240 |
| **SHORTS** | SHORTS | 2 053 | 14.6% | **3.03%** | 8 337 |
| **SKIRTS** | SHORT SKIRTS | 900 | 6.4% | **1.33%** | 3 647 |
| **SKIRTS** | MID LENGTH SKIRTS | 882 | 6.3% | **1.30%** | 3 589 |
| **SKIRTS** | LONG SKIRTS | 131 | 0.9% | **0.19%** | 537 |

### Całe ciało (Full body)

| Kategoria | Podkategoria | Produkty | Udział w grupie | **Udział w całym zbiorze** | Zdjęcia |
| :--- | :--- | ---: | :---: | :---: | ---: |
| **DRESSES** | SHORT DRESSES | 1 340 | 48.4% | **1.98%** | 5 460 |
| **DRESSES** | MID LENGTH DRESSES | 1 036 | 37.4% | **1.53%** | 4 247 |
| **DRESSES** | LONG DRESSES | 224 | 8.1% | **0.33%** | 927 |
| **JUMPSUITS** | JUMPSUITS | 168 | 6.1% | **0.25%** | 688 |

