# Query parsing

Jev 1.14 przez OpenRouter wybiera jedną z 22 kategorii. Dla obsługiwanej kategorii Qwen 3.8 27B przez Cerebras w jednym wywołaniu zwraca filtry, w tym markę i cenę, oraz listę fragmentów zapytania do rankingu. Qwen używa ścisłego schematu JSON, a parser waliduje odpowiedź względem katalogu.

Ustaw `OPENROUTER_API_KEY` i `CEREBRAS_API_KEY` w zmiennych środowiskowych lub w lokalnym `.env` w katalogu głównym repozytorium. Pakiet wymaga Pythona 3.10+, `requests` i `PyYAML`.

```bash
python -m query_parsing "black Nike T-shirt under 40 for travel"
```

```python
from query_parsing import parse_query

result = parse_query("black Nike T-shirt under 40 for travel")
```

Wynik zawiera `category`, `filters` i `residual`. Jev może zwrócić kategorię spoza katalogu. Wtedy `category` ma wartość `null`, obie listy są puste i parsowanie kończy się po pierwszym wywołaniu. Opcja `--meta` w CLI lub `include_meta=True` w Pythonie dodaje czasy i szacunkowy koszt.
