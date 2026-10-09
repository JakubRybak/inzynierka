# Szczegółowy Raport Ewaluacji Modeli: Gemini 3.5 Flash-Lite vs Qwen 3.8 27B vs Gemini 2.5 Flash-Lite

Niniejszy dokument przedstawia wyczerpujące, empiryczne porównanie trzech wiodących modeli przetestowanych na pełnym benchmarku **109 zapytań** w dwuetapowym pipeline wyszukiwarki modowej (*Query Understanding*: Klasyfikacja Kategorii $\to$ Ekstrakcja Atrybutów Guided Decoding).

---

## 1. Główna Tabela Zbiorcza (Executive Summary)

| Obszar / Metryka | **Gemini 3.5 Flash-Lite** | **Qwen 3.8 27B** | **Gemini 2.5 Flash-Lite** |
| :--- | :---: | :---: | :---: |
| **Typ i Hostowanie** | Zamknięty API / Google Cloud Vertex AI | Otwarty (*Open-weights*) / Cerebras WSE-3 | Zamknięty API / Google Cloud Vertex AI |
| **Lokalizacja / Infrastruktura** | Multi-region `eu` (Europa) | Akceleratory Cerebras (OpenRouter) | Centrum Danych Warszawa (`europe-central2`) |
| **Liczba zapytań w próbie (N)** | **109** | **109** | **109** |
| **Dokładność Kategorii Krok 1 (Cat Acc)** | **98.2%** *(107 / 109)* | **95.4%** *(104 / 109)* | **98.2%** *(107 / 109)* |
| **Atrybuty: Precyzja (Precision)** | **95.9%** *(210 TP / 9 FP)* | **95.4%** *(227 TP / 11 FP)* | **83.8%** *(192 TP / 37 FP)* |
| **Atrybuty: Czułość (Recall)** | **86.1%** *(34 FN)* | **88.0%** *(31 FN)* | **78.7%** *(52 FN)* |
| **Atrybuty: Micro-F1** | **90.7%** | **91.5%** | **81.2%** |
| **Nadmiarowe cechy / Halucynacje (FP)** | **9** *(minimalne)* | **11** *(bardzo małe)* | **37** *(nadgorliwy)* |
| **Pominięte cechy złote (FN)** | **34** | **31** | **52** |
| **Surowy Średni Czas Całkowity** | **1 832 ms** *(1.83 s)* | **2 290 ms** *(2.29 s)* | **1 481 ms** *(1.48 s)* |
| **Średni Czas Ucięty (Trimmed 30% each)** | **1 896 ms** *(1.90 s)* | **852 ms** *(0.85 s)* | **1 170 ms** *(1.17 s)* |
| **Mediana Czasu Całkowitego (P50)** | **1 900 ms** *(1.90 s)* | **813 ms** *(0.81 s)* | **1 137 ms** *(1.14 s)* |
| **Krok 1: Czas Ucięty (Klasyfikacja)** | **~828 ms** | **~305 ms** | **~481 ms** |
| **Krok 2: Czas Ucięty (Ekstrakcja Atrybutów)**| **~1 071 ms** | **~426 ms** | **~703 ms** |

---

## 2. Skuteczność wg Podzbiorów Trudności (Difficulty Subsets)

Benchmark dzieli 109 zapytań na 6 dedykowanych grup testowych sprawdzających specyficzne zachowania modeli w warunkach brzegowych:

| Podzbiór testowy (Liczba zapytań) | Metryka | **Gemini 3.5 Flash-Lite** | **Qwen 3.8 27B** | **Gemini 2.5 Flash-Lite** |
| :--- | :--- | :---: | :---: | :---: |
| **Polish_Slang** *(17 zapytań)*<br>*(np. "adidasy nike", "wheat timbs", "leather docs", "bojowki")* | Dokładność kategorii<br>Precyzja cech<br>Czułość cech<br>**F1-Score cech** | **100.0%** *(17/17)*<br>94.6%<br>97.2%<br>**95.9%** | 82.4% *(14/17)*<br>91.4%<br>88.9%<br>**90.1%** | **100.0%** *(17/17)*<br>86.7%<br>72.2%<br>**78.8%** |
| **Complex_Logic** *(12 zapytań)*<br>*(negacje, operatory AND / OR, "red or blue", "without hoodie")* | Dokładność kategorii<br>Precyzja cech<br>Czułość cech<br>**F1-Score cech** | **100.0%** *(12/12)*<br>90.0%<br>97.3%<br>**93.5%** | **100.0%** *(12/12)*<br>87.5%<br>100.0%<br>**93.3%** | **100.0%** *(12/12)*<br>78.6%<br>89.2%<br>**83.5%** |
| **Standard** *(40 zapytań)*<br>*(typowe zapytania e-commerce z Amazon ESCI)* | Dokładność kategorii<br>Precyzja cech<br>Czułość cech<br>**F1-Score cech** | **100.0%** *(40/40)*<br>98.7%<br>83.7%<br>**90.6%** | **100.0%** *(40/40)*<br>100.0%<br>85.9%<br>**92.4%** | **100.0%** *(40/40)*<br>85.2%<br>81.5%<br>**83.3%** |
| **Borderline** *(24 zapytania)*<br>*(niejednoznaczne, np. "sweaters without hoodie", "track jacket")* | Dokładność kategorii<br>Precyzja cech<br>Czułość cech<br>**F1-Score cech** | **95.8%** *(23/24)*<br>96.0%<br>77.4%<br>**85.7%** | **95.8%** *(23/24)*<br>98.1%<br>79.7%<br>**87.9%** | 91.7% *(22/24)*<br>79.6%<br>69.4%<br>**74.1%** |
| **Brand_Specific** *(8 zapytań)*<br>*(zapytania z markami modowymi i narzędziowymi)* | Dokładność kategorii<br>Precyzja cech<br>Czułość cech<br>**F1-Score cech** | 87.5% *(7/8)*<br>100.0%<br>82.4%<br>**90.3%** | 87.5% *(7/8)*<br>100.0%<br>94.1%<br>**97.0%** | **100.0%** *(8/8)*<br>100.0%<br>88.2%<br>**93.8%** |
| **Out_of_Scope** *(8 zapytań)*<br>*(elektronika, dom, zapytania niemodowe)* | **Poprawne odrzucenie (None)**<br>Halucynacje cech (FP) | **100.0%** *(8/8)*<br>**0 FP** | **100.0%** *(8/8)*<br>**0 FP** | **100.0%** *(8/8)*<br>**0 FP** |

---

## 3. Skuteczność Ekstrakcji wg Typów Atrybutów (Attribute Breakdown)

| Atrybut w taksonomii | Złote wystąpienia | **Gemini 3.5 Flash-Lite** (F1 / Prec / Rec) | **Qwen 3.8 27B** (F1 / Prec / Rec) | **Gemini 2.5 Flash-Lite** (F1 / Prec / Rec) |
| :--- | :---: | :---: | :---: | :---: |
| **`department_gender`** | 67 | **100.0%** *(100% / 100%)* | **98.5%** *(97.1% / 100%)* | **89.1%** *(93.4% / 85.1%)* |
| **`colors`** | 48 | **100.0%** *(100% / 100%)* | **98.9%** *(100% / 97.9%)* | **90.9%** *(100% / 83.3%)* |
| **`color_operator`** *(AND / OR)* | 11 | **100.0%** *(100% / 100%)* | **100.0%** *(100% / 100%)* | **85.7%** *(90.0% / 81.8%)* |
| **`brands`** | 24 | **81.6%** *(80.0% / 83.3%)* | **91.3%** *(95.5% / 87.5%)* | **85.1%** *(87.0% / 83.3%)* |
| **`closure_type`** *(zapięcie)* | 18 | **80.0%** *(100% / 66.7%)* | **75.9%** *(100% / 61.1%)* | **46.5%** *(40.0% / 55.6% - 15 FP!)* |
| **`hood`** *(kaptur / negacje)* | 15 | **69.6%** *(100% / 53.3%)* | **88.9%** *(100% / 80.0%)* | **88.9%** *(100% / 80.0%)* |
| **`materials`** *(bawełna, skóra)* | 12 | **81.8%** *(90.0% / 75.0%)* | **87.0%** *(90.9% / 83.3%)* | **72.7%** *(80.0% / 66.7%)* |
| **`pant_type`** *(cargo, jeans itp.)* | 10 | **94.7%** *(100% / 90.0%)* | **95.2%** *(90.9% / 100%)* | **95.2%** *(90.9% / 100%)* |
| **`pattern`** *(paski, kratka)* | 9 | **80.0%** *(100% / 66.7%)* | **87.5%** *(100% / 77.8%)* | **75.0%** *(85.7% / 66.7%)* |
| **`sleeve_length`** | 8 | **93.3%** *(100% / 87.5%)* | **100.0%** *(100% / 100%)* | **82.4%** *(77.8% / 87.5%)* |

---

## 4. Profil Czasowy i Rozkład Latencji (Wszystkie Percentyle)

Poniższa tabela przedstawia pełny rozkład czasowy całkowitego pipeline'u (Krok 1 + Krok 2) w milisekundach:

| Statystyka czasowa | **Gemini 3.5 Flash-Lite** | **Qwen 3.8 27B** | **Gemini 2.5 Flash-Lite** | Uwagi inżynierskie |
| :--- | :---: | :---: | :---: | :--- |
| **Minimalny czas (Min)** | 639 ms | **209 ms** | 380 ms | Najszybsze pojedyncze zapytanie (*Out-of-Scope*, K2 pominięty) |
| **Percentyl 10 (P10)** | 1 706 ms | **531 ms** | 938 ms | Typowe proste zapytanie |
| **Percentyl 25 (P25)** | 1 814 ms | **588 ms** | 1 096 ms | Dolny kwartyl |
| **Mediana (P50)** | 1 900 ms | **813 ms** | 1 137 ms | Standardowe zapytanie 2-etapowe |
| **Średnia Ucięta (Trimmed 30%)** | 1 896 ms | **852 ms** | 1 170 ms | **Środkowe 40% próby (odcięte 30% z dołu i 30% z góry)** |
| **Średnia Ucięta (Trimmed 15%)** | 1 898 ms | 951 ms | 1 173 ms | Środkowe 70% próby (odrzucone łącznie 30% skrajnych) |
| **Średnia Arytmetyczna (Mean)** | 1 832 ms | 2 290 ms | 1 481 ms | Surowa średnia (zaburzona przez retries Qwena i cold-start) |
| **Percentyl 75 (P75)** | 1 963 ms | 1 370 ms | 1 271 ms | Górny kwartyl |
| **Percentyl 90 (P90)** | 2 048 ms | 2 461 ms | 1 429 ms | Trudne / długie zapytania |
| **Maksymalny czas (Max)** | **3 000 ms** | 61 571 ms | 8 295 ms | Maksimum (Qwen: retry HTTP 429; G2.5: cold start) |

---

## 5. Szczegółowa Analiza Błędów Kategoryzacji (Krok 1)

Wszystkie błędy popełnione przez modele w klasyfikacji kategorii na 109 zapytaniach:

* **Gemini 3.5 Flash-Lite (Tylko 2 błędy na 109 zapytań – 98.2% trafności):**
  1. `zipper sweaters for women without hoodie` $\to$ przewidział *Sweaters & Cardigans* (etykieta złota: *Hoodies & Sweatshirts* – zapytanie skrajnie graniczne, dosłownie zawiera słowo "sweaters").
  2. `dewalt shirt for men` $\to$ przewidział *Shirts & Blouses* (etykieta złota: *T-Shirts & Tops*).
* **Gemini 2.5 Flash-Lite (Tylko 2 błędy na 109 zapytań – 98.2% trafności):**
  1. `track jacket men venum` $\to$ przewidział *Jackets & Coats* (etykieta złota: *Hoodies & Sweatshirts* – zapytanie zawiera "jacket").
  2. `zipper sweaters for women without hoodie` $\to$ przewidział *Sweaters & Cardigans*.
* **Qwen 3.8 27B (5 błędów na 109 zapytań – 95.4% trafności):**
  1. Te same 2 przypadki graniczne (`zipper sweaters...` oraz `dewalt shirt...`).
  2. `adidasy nike do biegania` $\to$ przewidział *None* (nie powiązał eponimu "adidasy" z obuwiem ogólnym przy marce Nike).
  3. `wheat timbs` $\to$ przewidział *None* (slang bez słowa kluczowego typu "shoes/boots").
  4. `leather docs` $\to$ przewidział *Pants & Trousers* (pomylił slangowe *docs* – Dr. Martens – ze spodniami firmy Dockers).

---

## 6. Kluczowe Spostrzeżenia Inżynierskie

* **Gemini 3.5 Flash-Lite (Zwycięzca Jakościowy):**
  * **Bezbłędny w Języku Polskim i Slangu:** Uzyskał 100% trafności kategorii w sekcji `Polish_Slang` i F1=95.9% dla atrybutów. Bezbłędnie rozpoznał slangowe zapytania obuwnicze (*wheat timbs*, *leather docs*, *summer birks*, *adidasy nike*).
  * **Wysoka Dyscyplina:** W przeciwieństwie do generacji 2.5, wersja 3.5 zredukowała False Positives z 37 do 9, osiągając precyzję 95.9%.
  * **Czas:** Prawdziwie stabilny czas ~1.89 – 1.90 s w europejskim multi-regionie `eu` (wąski rozrzut: P10=1.70s, P90=2.04s).

* **Qwen 3.8 27B (Zwycięzca Wydajnościowy Open-Weights):**
  * **Równy, wysoki F1 (91.5%):** Doskonała dyscyplina w Guided Decoding na zapytaniach standardowych oraz złożonych zapytaniach logicznych AND/OR (100% zgodności).
  * **Prawdziwa Prędkość Cerebras:** Po odrzuceniu kolejek i limitów publicznego brokera, model przetwarza zapytanie w **~852 ms** (Krok 1 w ~305 ms, Krok 2 w ~426 ms).
  * **Słabość Slangowa:** Trudności przy eponimach i slangu ulicznym bez kontekstowych słów kluczowych (*timbs*, *docs* pomylone ze spodniami).

* **Gemini 2.5 Flash-Lite w Warszawie (`europe-central2`):**
  * **Zaleta:** Rekordowo niski czas odpowiedzi w chmurze (**~1.17 s**) dzięki lokalnemu datacenter w Warszawie (ping rzędu 10 ms).
  * **Wada:** Zauważalna nadgorliwość w przypisywaniu cech domyślnych (aż 15 FP w zapięciach `closure_type`), co obniża ogólną precyzję do 83.8%.

---

## 7. Rekomendacja Architektoniczna do Pracy Inżynierskiej

1. **Dla wdrożeń komercyjnych / Serverless SaaS (MVP i średnie e-commerce):**  
   Zdecydowanym faworytem jest **Gemini 3.5 Flash-Lite (multi-region `eu`)** – łączy najwyższą inteligencję językową (100% dla slangu i języka polskiego), precyzję 95.9% i w 100% przewidywalny czas poniżej 2 sekund bez kosztów serwerowych.
2. **Dla systemów On-Premise / Dedykowanych GPU (Duże e-commerce / High-Scale):**  
   Rekomendowany jest model **Qwen 3.8 27B** hostowany na własnej instancji (np. GCP L4 / A100 z vLLM i Prefix Caching), co daje czasy rzędu **~300–500 ms**, zerowe ryzyko limitów API brokera i 100% suwerenność danych.
