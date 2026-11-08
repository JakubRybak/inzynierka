# Model latency measurements

## Jev 1.14 przez OpenRouter

| Jedno wywołanie | p50 | p80 | **p95** |
| --- | ---: | ---: | ---: |
| Wybór kategorii · 92 zapytania | 0,218 s | 0,254 s | **0,318 s** |
| Wszystkie cechy i ich operatory dla ustalonej kategorii · 47 zapytań | 0,277 s | 0,319 s | **0,377 s** |

## Ekstrakcja cech i residualu

Każdy wariant dostał to samo zapytanie 12 razy po jednym wywołaniu rozgrzewkowym. Pomiar obejmuje czas do odebrania całej odpowiedzi, bez etapu Jev.

| Model i dostawca | p50 | **p80** | p95 | Odpowiedzi < 0,6 s |
| --- | ---: | ---: | ---: | ---: |
| **GPT-OSS-120B · Cerebras** | 0,483 s | **0,526 s** | 0,532 s | **12/12** |
| Mercury 3 · Inception, bez thinkingu | 0,564 s | 0,607 s | 0,721 s | 9/12 |
| GPT-OSS-20B · Groq | 0,498 s | 0,611 s | 0,732 s | 9/12 |
| GPT-OSS-120B · Groq | 0,726 s | 0,823 s | 0,854 s | 0/12 |
| Gemini 3.5 Flash-Lite · Vertex Global | 1,096 s | 1,155 s | 1,252 s | 0/12 |
| GLM 5.3 Flash · Friendli, thinking `minimal` | 0,991 s | 1,285 s | 1,510 s | 0/12 |
| Gemini 3.5 Flash-Lite · Vertex EU | 1,160 s | 1,290 s | 1,484 s | 0/12 |
| Gemini 3.5 Flash-Lite · Vertex EU Priority | 1,260 s | 1,291 s | 1,328 s | 0/12 |
| Qwen 3.8 27B · Modal, bez thinkingu | 1,163 s | 1,303 s | 1,436 s | 0/12 |
| Gemini 3.5 Flash-Lite · OpenRouter / AI Studio Priority | 1,231 s | 1,329 s | 1,415 s | 0/12 |
| GLM 5.3 Flash · InferenceNet (US), thinking `minimal` | 1,598 s | 1,909 s | 2,094 s | 0/12 |
| Qwen 3.8 27B · ModelRun (FP4), bez thinkingu | 1,449 s | 1,962 s | 3,127 s | 0/12 |
| Qwen 3.8 27B · Cloudflare, bez thinkingu | 5,619 s | 5,957 s | 7,206 s | 0/12 |

Wywołania poza Vertex AI przechodziły przez OpenRouter ze wskazanym dostawcą i wyłączonym fallbackiem. W dodatkowej serii zachowano to samo zapytanie, ścisły schemat JSON, temperaturę 0 i limit 384 tokenów.

- Qwen na Modal i ModelRun ukończył wszystkie 12 prób. Percentyle Qwen na Cloudflare obejmują 8 z 12 prób. Pozostałe 4 osiągnęły limit tokenów.
- GLM na Friendli i InferenceNet ukończył po 11 z 12 prób. W obu przypadkach jedna odpowiedź osiągnęła limit tokenów i została pominięta w percentylach.
- OpenRouter odrzucał próby GLM z wyłączonym thinkingiem na Baseten i InferenceNet. Przy ustawieniu `minimal` Baseten zwracał HTTP 429, więc pomiar tego endpointu przerwano.

## Ekstrakcja przez bezpośrednie API Cerebras

Użyto tego samego zapytania, ścisłego schematu JSON, temperatury 0 i limitu 384 tokenów. Na każdy model przypadło jedno wywołanie rozgrzewkowe i 12 prób pomiarowych. Czas obejmuje odbiór całej odpowiedzi, bez etapu Jev.

| Model | p50 | **p80** | p95 | Odpowiedzi < 0,5 s | Odpowiedzi < 0,6 s | Zgodne ze schematem |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Qwen 3.8 27B** · thinking `none` | 0,415 s | **0,445 s** | 0,498 s | 11/12 | 12/12 | 12/12 |
| GPT-OSS-120B · thinking `low` | 0,457 s | **0,545 s** | 0,605 s | 7/12 | 11/12 | 12/12 |
