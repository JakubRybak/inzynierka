# Podsumowanie Ewaluacji Modeli: Gemini Flash-Lite vs Qwen 3.8 27B

## 1. Główne Wnioski (Pełny Benchmark: 109 Zapytań)
Do docelowej architektury wyszukiwarki semantycznej zakwalifikowano i zewaluowano wiodące modele na rozszerzonym zbiorze **109 zapytań** (Amazon ESCI + zapytania wielojęzyczne, eponimy i slang młodzieżowy):
1. **Gemini 3.5 Flash-Lite** (Google Cloud Vertex AI, multi-region `eu`)
2. **Qwen 3.8 27B** (Open-weights na akceleratorach Cerebras via OpenRouter)
3. **Gemini 2.5 Flash-Lite** (Google Cloud Vertex AI, region `europe-central2` – Warszawa)

---

## 2. Zestawienie Porównawcze Modeli (109 Zapytań)

| Cecha / Metryka | Gemini 3.5 Flash-Lite (Vertex AI EU) | Qwen 3.8 27B (Cerebras) | Gemini 2.5 Flash-Lite (Warszawa) |
| :--- | :---: | :---: | :---: |
| **Typ modelu** | Komercyjny API (Google) | Otwarty (*Open-weights*) | Komercyjny API (Google) |
| **Lokalizacja / Infrastruktura** | Multi-region `eu` (Europa) | Akceleratory Cerebras (OpenRouter) | Centrum danych w Warszawie (`europe-central2`) |
| **Dokładność Kategorii (K1)** | **98.2%** (107 / 109) | **95.4%** (104 / 109) | **98.2%** (107 / 109) |
| **Precyzja Atrybutów (Precision)** | **95.9%** (Tylko 9 FP) | **95.4%** (11 FP) | **83.8%** (37 FP) |
| **Czułość Atrybutów (Recall)** | **86.1%** | **88.0%** | **78.7%** |
| **F1-Score Atrybutów (K2)** | **90.7%** | **91.5%** | **81.2%** |
| **Grupa Polish_Slang (K1 / F1)** | **100.0% / 95.9%** | **82.4% / 90.1%** | **100.0% / 78.8%** |
| **Logika AND / OR (Complex_Logic)** | **100.0%** (11 / 11) | **100.0%** (11 / 11) | **90.9%** (10 / 11) |
| **Średni Czas Krok 1 (Klasyfikacja)** | **~841 ms** | **~1199 ms** | **~607 ms** |
| **Średni Czas Krok 2 (Ekstrakcja)** | **~1079 ms** | **~1212 ms** | **~952 ms** |
| **Średni Czas Łączny (K1 + K2)** | **~1.83 s** | **~2.29 s** *(z pacingiem)* | **~1.48 s** *(rekordowo niski ping)* |

---

## 3. Kluczowe Spostrzeżenia Inżynierskie

* **Gemini 3.5 Flash-Lite (Zwycięzca Jakościowy):**
  * **Bezbłędny w Języku Polskim i Slangu:** Uzyskał 100% trafności kategorii w sekcji `Polish_Slang` i F1=95.9% dla atrybutów. Bezbłędnie rozpoznał slangowe zapytania obuwnicze (*wheat timbs*, *leather docs*, *summer birks*, *adidasy nike*).
  * **Wysoka Dyscyplina:** W przeciwieństwie do generacji 2.5, wersja 3.5 zredukowała False Positives z 37 do 9, osiągając precyzję 95.9%.
  * **Czas:** Średni czas ~1.83 s w europejskim multi-regionie `eu`.

* **Qwen 3.8 27B (Zwycięzca w Kategorii Open-Weights):**
  * **Równy, wysoki F1 (91.5%):** Doskonała dyscyplina w Guided Decoding na zapytaniach po angielsku i złożonych zapytaniach logicznych AND/OR (100% zgodności).
  * **Wyzwanie Slangu:** Lekkie trudności przy slangu miejskim bez słów kluczowych (*timbs*, *docs* pomylone z Dockers).
  * **Wydajność:** W warunkach płynnej pracy bez kolejki surowy czas wnioskowania to ~0.6 – 1.0 s, lecz współdzielony publiczny broker wymaga pacingu.

* **Gemini 2.5 Flash-Lite w Warszawie (`europe-central2`):**
  * **Zaleta:** Rekordowo niski czas odpowiedzi (**~1.48 s**) dzięki znikomemu opóźnieniu sieciowemu (ping krajowy ~10 ms) oraz 100% zgodność z RODO i suwerenność danych w Polsce.
  * **Wada:** Zauważalna nadgorliwość w przypisywaniu cech domyślnych (wyższa liczba FP niż w 3.5).

---

## 4. Rekomendacja Architektoniczna do Pracy Inżynierskiej
1. **Dla wdrożeń komercyjnych / Serverless SaaS:**
   Zdecydowanym faworytem jest **Gemini 3.5 Flash-Lite (multi-region `eu`)** – łączy najwyższą inteligencję językową (100% dla slangu/PL), precyzję 95.9% i stabilny czas poniżej 2 sekund bez kosztów serwera.
2. **Dla systemów On-Premise / Suwerennych / High-Scale:**
   Rekomendowany jest model **Qwen 3.8 27B** uruchomiony na własnej instancji GPU (np. GCP L4 / A100 z vLLM i Prefix Caching), co daje pełną niezależność od dostawców chmurowych, brak limitów API i czasy rzędu ~300 ms.

