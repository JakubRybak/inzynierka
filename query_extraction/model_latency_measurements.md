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
| Gemini 3.5 Flash-Lite · Vertex EU | 1,160 s | 1,290 s | 1,484 s | 0/12 |
| Gemini 3.5 Flash-Lite · Vertex EU Priority | 1,260 s | 1,291 s | 1,328 s | 0/12 |
| Gemini 3.5 Flash-Lite · OpenRouter / AI Studio Priority | 1,231 s | 1,329 s | 1,415 s | 0/12 |
| Qwen 3.8 27B · Cloudflare, bez thinkingu | 5,619 s | 5,957 s | 7,206 s | 0/12 |

Wywołania Cerebras, Groq, Inception i Cloudflare przechodziły przez OpenRouter z wyłączonym fallbackiem. Percentyle Qwen obejmują 8 ukończonych odpowiedzi. Pozostałe 4 osiągnęły limit tokenów.
