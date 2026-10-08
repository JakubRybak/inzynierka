# Podsumowanie Ewaluacji Modeli: Gemini Flash-Lite vs Qwen 3.8 27B

## 1. Główne Wnioski
Do docelowej architektury wyszukiwarki semantycznej zakwalifikowano dwa wiodące modele, które bezbłędnie poradziły sobie z zadaniem **Guided Decoding** (obsługa zamkniętej taksonomii, cech negatywnych, marek oraz logiki `AND`/`OR` z dokładnością **95–100%**):
1. **Gemini 3.1 / 3.5 Flash-Lite** (Google Cloud Vertex AI)
2. **Qwen 3.8 27B** (Open-weights na akceleratorach Cerebras via OpenRouter)

---

## 2. Porównanie Modeli

| Cecha / Metryka | Gemini Flash-Lite (Google) | Qwen 3.8 27B (Cerebras) |
| :--- | :---: | :---: |
| **Typ modelu** | Komercyjny / Zamknięty (Google) | Otwarty (*Open-weights*) |
| **Czas pojedynczego zapytania** | **~1.0 – 1.5 s** (stabilny) | **~0.2 – 0.5 s** (w szczytowej formie) |
| **Czas pełnego pipeline'u (Krok 1 + 2)** | **~2.2 – 2.6 s** | **~0.6 – 1.3 s** (przy braku kolejki) |
| **Stabilność / SLA** | **100% przewidywalny** (infrastruktura GCP) | **Zmienna** (podatny na kolejki publicznego brokera) |
| **Koszty stałe (serwer)** | **0 PLN** (model Serverless pay-per-token) | **0 PLN** (na brokerze API) |
| **Poprawność ekstrakcji (F1)** | **90.2% – 91.4%** | **95.0%** |

---

## 3. Kluczowe Spostrzeżenia Inżynierskie

* **Qwen 3.8 27B (Cerebras):**  
  * **Zaleta:** Prawdziwa prędkość układu Wafer-Scale Engine jest bezkonkurencyjna – w warunkach płynnej pracy Krok 1 zajmuje **~200 ms**, a Krok 2 **~350–500 ms**.
  * **Wada:** Korzystanie z publicznego brokera API (OpenRouter) w godzinach szczytu powoduje zjawisko *Rate Limiting (HTTP 429)* i zmusza do stosowania pacingu (odstępów między zapytaniami).

* **Gemini Flash-Lite (Vertex AI):**  
  * **Zaleta:** Niezrównana stabilność produkcyjna klasy Enterprise. Niezależnie od pory dnia i obciążenia sieci odpowiedź przychodzi w stałym, gwarantowanym oknie czasowym.
  * **Wada:** Fizyczna granica ~2.2 s dla 2-etapowego pipeline'u wynikająca z narzutu sieciowego i bezpiecznego przetwarzania w chmurze.

---

## 4. Rekomendacja Architektoniczna do Pracy
1. **Dla wdrożeń produkcyjnych Serverless (MVP / małe i średnie e-commerce):**  
   Rekomendowany jest **Gemini Flash-Lite** – zerowy koszt utrzymania infrastruktury i pełna niezawodność odpowiedzi.
2. **Dla systemów High-Performance (duże e-commerce / wysoka skala):**  
   Rekomendowany jest model **Qwen 3.8 27B** hostowany na dedykowanej infrastrukturze (np. vLLM / SGLang z Prefix Caching), co pozwala osiągnąć stabilną latencję na poziomie **~300 ms** przy zachowaniu pełnej kontroli nad danymi (On-Premise / RODO).
