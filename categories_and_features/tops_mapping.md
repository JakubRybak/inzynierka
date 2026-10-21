# Mapowanie cech `Tops`

Docelowy zakres kategorii i wartości zawiera `categories_and_features.md`. Te zasady mają pierwszeństwo przed starszymi regułami `Tops` w mapowaniach wspólnych.

## Kategorie źródłowe

Wszystkie poniższe podkategorie pochodzą z `input_category = TOPS`:

| Kategoria docelowa | `input_subcategory` |
| :--- | :--- |
| `T-shirts` | `T-SHIRTS` |
| `Polos` | `POLOS` |
| `Tank tops & Camisoles` | `TANK TOPS`, `TANK TOPS & CAMISOLES` |
| `Bodysuits` | `BODYSUITS` |

Nie przypisujemy kategorii ponownie na podstawie wyglądu. Produkt identyfikujemy przez `input_productID`.

## Cechy wspólne

- `gender`: single choice, ścisłe mapowanie wartości źródłowej do `Men` lub `Women`.
- `colors`: 1–2 różne kolory bazowe albo samo `Multicolor` dla co najmniej 3 kolorów lub produktu opisanego jako multicolor. Słownik odcieni: `colors_mapping.md`. Nie rozróżniamy koloru dominującego.
- `main_composition`: jeden wiarygodnie ustalony skład głównej części, suma 100%. Słownik materiałów: `materials_mapping.md`. Sumujemy udziały materiałów mapowanych do tego samego enuma. Nie dodajemy podszewki ani wykończeń. Brak dwukropka nie gwarantuje jednego składu, a pierwsza wymieniona część nie musi być główna. Nie zgadujemy procentów, nie normalizujemy błędnych sum ani nie uśredniamy składów różnych części bez ich udziałów. Nierozstrzygalny skład oznacza wykluczenie produktu.
- `pattern`: lista bez powtórzeń; `Solid` i `Other` samodzielnie. Konkretne wzory można łączyć, np. `["Striped", "Floral"]`. Przy nazwanym wzorze nie dodajemy `Other` za logo lub grafikę. `Other` oznacza rozpoznany wzór poza nazwanymi klasami, nie brak pewności. `Solid` wymaga potwierdzenia gładkiego produktu.

## Pozostałe cechy

- `neckline`: single choice: `Crewneck`, `Scoop Neck`, `V-Neck`, `High Neck`, `Other`. Znaczenia nazwanych wartości zgodne z `Dresses`; pozostałe rozpoznane kształty, również `Collared` w body, trafiają do `Other`. Patrz `neckline_mapping.md`. `High Neck` zastępuje szeroką grupę poprzednio nazwaną `Turtleneck`. Konstrukcję `Off-Shoulder` opisuje `strap_style`, a nie dekolt.
- `sleeve_length`: `Short Sleeve` lub `Long Sleeve`, dodatkowo `Sleeveless` w `Bodysuits`. Rękawy do łokcia, 3/4 i nieustalone długości oznaczają wykluczenie z kategorii używających tej cechy.
- `fit`: `Slim`, `Regular`, `Relaxed`; patrz `fit_mapping.md`.
- `length`: `Cropped`, `Regular`, `Longline`; patrz `length_mapping.md`.
- `strap_style`, `strap_width`: patrz odpowiadające im mapowania. Występują w `Tank tops & Camisoles` i `Bodysuits`.

Nie stosujemy `null`, pustych list ani niewybranych wartości. Cechy spoza schematu kategorii pomijamy. Nierozpoznany produkt wykluczamy; `Not Applicable` oznacza wyłącznie brak zastosowania cechy. Reguły dotyczą rekordu produktu, a brak wymagania w zapytaniu oznacza pominięcie filtra.
