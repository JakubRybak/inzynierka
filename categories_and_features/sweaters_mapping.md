# Mapowanie kategorii i cech `Sweaters`

## Kategorie źródłowe

Wszystkie poniższe podkategorie pochodzą z `input_category = SWEATERS`.

| Kategoria docelowa | `input_subcategory` |
| :--- | :--- |
| `Knit Sweaters` | `CREWNECKS`, `V-NECKS`, `TURTLENECKS` |
| `Sweatshirts` | `SWEATSHIRTS` |
| `Hoodies & Zipups` | `HOODIES & ZIPUPS` |
| `Cardigans` | `CARDIGANS` |

`SHAWLNECKS` pozostają wykluczone. Nie przypisujemy kategorii ponownie na podstawie wyglądu.

## Cechy wspólne

- `gender`: `Men`, `Women`, single choice.
- `colors`: 1–2 różne kolory albo samo `Multicolor`; wspólny słownik odcieni, bez koloru dominującego.
- `main_composition`: jeden skład głównej części z procentami sumującymi się do 100%; zasady jak w pozostałych dopracowanych działach.
- `pattern`: multi choice, bez powtórzeń; `Solid` i `Other` samodzielnie. Przy nazwanym wzorze nie dodajemy `Other` za dodatkowe logo lub grafikę.
- `sleeve_length`: `Sleeveless`, `Short Sleeve`, `Three-Quarter Sleeve`, `Long Sleeve`, single choice we wszystkich czterech kategoriach. Brak rękawów nie zmienia kategorii źródłowej.
- `fit`: `Slim`, `Regular`, `Relaxed`, single choice.
- `length`: `Cropped`, `Regular`, `Longline`, single choice.
- `hood`: `With Hood`, `Without Hood`, single choice we wszystkich czterech kategoriach. Dotyczy również kardiganów i swetrów z kapturem.

## Zapięcie (`closure_type`, single choice)

Dotyczy wszystkich czterech kategorii. Oceniamy główne zapięcie, nie zamki kieszeni, ozdobne guziki ani pomocnicze zapięcie przy karku.

| Wartość | Znaczenie |
| :--- | :--- |
| `Zip` | Pełne rozpięcie przodu zamkiem. |
| `Half-Zip` | Częściowy zamek pod szyją, również quarter-zip. |
| `Button` | Główne zapięcie na guziki lub napy. |
| `Belted` | Główne zapięcie kopertowe lub wiązane paskiem, bez głównego zamka lub rzędu guzików. |
| `Open Front` | Otwarty przód bez głównego zapięcia i paska wiążącego. |
| `Pullover` | Wkładane przez głowę bez głównego rozpięcia. |
| `Other` | Pozostałe konstrukcje, w tym `Double-Breasted`. |

W `Sweaters` każdą potwierdzoną konstrukcję `Double-Breasted` przypisujemy do `Other`, również gdy ma guziki lub zamek. Jest to wyjątek względem starszego mapowania okryć wierzchnich. Zamek częściowy ma pierwszeństwo przed `Pullover`.

## Dekolt (`neckline`, single choice)

Występuje w `Knit Sweaters`, `Sweatshirts`, `Cardigans`; pomijamy go w `Hoodies & Zipups`.

| Wartość | Znaczenie |
| :--- | :--- |
| `Crewneck` | Okrągły, blisko szyi. |
| `Scoop Neck` | Głębszy, otwarty dekolt zaokrąglony. |
| `V-Neck` | W serek. |
| `High Neck` | Golf, półgolf, wysoki komin. |
| `Collared` | Wykładany kołnierzyk lub klapy. |
| `Other` | Pozostałe rozpoznane kształty, w tym `Boat Neck` i `Cowl Neck`. |

Znaczenia nazwanych klas są zgodne z `Tops` i `Dresses`; zakres jest celowo uproszczony. Odkryte ramiona nie przesądzają o kształcie dekoltu.

Nie wprowadzamy `sweater_type`, `strap_style`, `strap_width` ani `full_composition_text`. Informacje o ramiączkach i konstrukcji ramion pozostają w opisach dla rankingu.
