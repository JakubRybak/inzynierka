# Prompt ekstrakcji — propozycja do przeglądu

Prompty parsowania zapytań użytkownika są opisane w [query_parsing/README.md](../../query_parsing/README.md): wybór kategorii, trzy osobne prompty cech z few-shotami oraz [definicje guided decoding](../../query_parsing/structured_output.md).

Prompt jest po angielsku. Zakres: T-shirts, Dresses, Tank tops & Camisoles.
W tej zmianie nie wykonano żadnych płatnych wywołań.

## Pliki

- `system.txt`: stałe instrukcje oceny produktu i zwracania odpowiedzi.
- `feature_definitions.json`: pełne definicje cech i ich wartości; generator
  wybiera tylko potrzebne fragmenty i wartości dopuszczone w kategorii.
- `prompt.md`: czytelny zbiorczy dokument z pełnymi instrukcjami i definicjami.
- `previews/`: trzy konkretne prompty i schematy dla produktów z próbki.
- `../scripts/build_prompt.py`: generator i lokalny walidator odpowiedzi; bez API.

## Co trafia do konkretnego zapytania

1. Stała instrukcja systemowa.
2. Definicje tylko cech nieobecnych w `features` wyniku preprocessingu.
3. Dwa przykłady: nazwa, opis, etykiety tylko wymaganych cech oraz zdjęcia
   `id_gridfs_1` i `id_gridfs_3` każdego przykładu. Nie zakładamy gwarantowanego
   widoku przodu i tyłu.
4. Produkt docelowy: kategoria, nazwa, opis i wszystkie zdjęcia.
5. Schemat przekazany osobno w `responseSchema`, z `responseMimeType = application/json`.

Nie przekazujemy przypisanych wartości, ich definicji, metadanych keywordów,
listy zablokowanych cech ani całego słownika wszystkich kategorii. Surowe nazwy
oraz opisy pozostają pełne: nie usuwamy z nich zdań, które wspominają takie cechy.
Płeć służy lokalnie do selekcji przykładów; nie jest zadaniem dla modelu.
Puste gender/main_composition/brand są wykluczane przed tym etapem, więc nie ma
ich definicji ani ścieżki awaryjnego wyznaczania przez LLM.

Przykładowe prompty używają po dwóch istniejących referencjach tej samej kategorii
oraz płci, wyłącznie do pokazania formatu. To NIE są sąsiedzi z embeddingów.
W uruchamianym pipeline dobór korzysta już z policzonych embeddingów;
te statyczne podglądy nadal są ilustracją formatu. Rzeczywiste konteksty z testu
znajdują się w `poc/feature_extraction/runs/smoke_6/calls/*_prompt.json`.
`local_image_path` jest lokalnym znacznikiem dla przyszłego klienta API, nie polem
Gemini. Klient musi zamienić go na rzeczywiste części obrazowe, zachowując kolejność.

## Dynamiczne fragmenty

- Gdy np. `neckline` już przypisano, nie ma definicji ani pola `neckline` w
  schemacie, a etykiety przykładów też go nie zawierają.
- Gdy obie cechy ramiączek są wymagane, dodajemy ich wspólną zależność.
  Gdy jedna jest przypisana, nie ujawniamy jej; zgodność sprawdzamy po scaleniu.
  Konflikt trafia do sprawdzenia, bez nadpisywania wartości z keywordów.
- Wartości w definicjach i enumach są filtrowane słownikiem danej kategorii:
  np. Collared pojawia się jako wartość neckline tylko w Dresses.
- `length` sukienek pochodzi wyłącznie ze źródła; brak tej wartości wyklucza
  produkt. Definicje Cropped/Regular/Longline dotyczą tylko góry, nie sukienek.
- Przy zerowej liczbie brakujących cech pomijamy wywołanie ekstrakcyjne.

## Odpowiedź

Stałe pola to `product_status`, `product_reason`, `features`,
`outside_schema_reasons`. Samych wartości cech oczekujemy bez uzasadnień.

- `ok`: `product_reason = ""`, wszystkie i tylko wymagane cechy.
- `out_of_category`: wyraźnie inny rodzaj produktu; jedno zdanie uzasadnienia.
- `unusable_product`: cały rekord nie pozwala ocenić jednego spójnego produktu;
  jedno zdanie uzasadnienia.
- Dla obu problemów produktu: `features = null`, `outside_schema_reasons = {}`.
  To wyjątek na poziomie całego produktu, nie brakująca wartość pojedynczej cechy.
- Cecha z Other: wyłącznie wartości słownika, bez outside_schema lub
  insufficient_evidence.
- Cecha bez Other: wartość słownika albo outside_schema; w drugim przypadku
  dokładnie jedno krótkie uzasadnienie w `outside_schema_reasons`.
- Colors: lista 1–2 kolorów lub samo Multicolor; dress_type: lista, Other samo.
- Pozostałe cechy: pojedynczy string.

`outside_schema` przy braku Other obejmuje brak obronionego przypisania do słownika;
uzasadnienie rozróżnia nietypową konstrukcję od niewystarczających danych.
Nie dodajemy oddzielnej wartości insufficient_evidence.

## Structured output i walidacja

Wysyłamy `responseMimeType: application/json` i generowany per produkt
`responseSchema`. Thinking i media resolution mają MEDIUM; rozdzielczość jest
ustawieniem całego wywołania, obejmuje także zdjęcia przykładów.
Nie powielamy schematu JSON w treści promptu.

Używamy pól udokumentowanych dla Cloud responseSchema: type, enum, properties,
required, propertyOrdering, nullable, items, minItems, maxItems i anyOf.
Nie polegamy na `additionalProperties: false` w tej ścieżce API: nie figuruje ono
w liście obsługiwanych pól Cloud responseSchema. `validate_response` odrzuca
nadmiarowe pola lokalnie, a nie po cichu je usuwa.

Serwer ogranicza strukturę i wartości, ale lokalnie nadal sprawdzamy:
liczbę i unikalność wartości, wyłączność Other/Multicolor, dokładne klucze,
uzasadnienia, zgodność statusu produktu i zależności ramiączek po scaleniu.
Wywołanie z błędem, odmową, uciętą odpowiedzią lub konfliktem nie staje się
przykładem. `outside_schema` pozostaje nierozstrzygnięciem, nie wartością do indeksu.
Walidator zwraca scalone cechy, ale nie zapisuje ich ani nie zmienia keywordów.

Generator sam nie wywołuje API. Integrację sprawdzono przez
`run_llm_extraction.py` na 6 produktach: `poc/feature_extraction/runs/smoke_6/results.md`.

Źródło: [Google Cloud — structured output](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output).

## Odtworzenie podglądów

```sh
.venv/bin/python poc/scripts/build_prompt.py
```

Zbiorczy prompt.md jest dokumentem do przeglądu; pliki źródłowe generatora to
system.txt i feature_definitions.json. Nie wysyłamy prompt.md w całości do modelu.
