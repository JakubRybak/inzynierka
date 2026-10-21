# Mapowanie kategorii i cech `Shirts & Blouses`

## Kategorie źródłowe

| Kategoria docelowa | `input_category` | `input_subcategory` |
| :--- | :--- | :--- |
| `Shirts` | `SHIRTS` | `SHIRTS` |
| `Shirts` | `TOPS` | `SHIRTS` |
| `Blouses` | `TOPS` | `BLOUSES` |

Kategorie wynikają z etykiet źródłowych, nie z ponownej oceny wyglądu.

## Cechy wspólne

- `gender`: `Men`, `Women`, single choice.
- `colors`: 1–2 różne kolory albo samo `Multicolor`, bez koloru dominującego; wspólny słownik odcieni.
- `main_composition`: jeden skład głównej części z udziałami sumującymi się do 100%, zgodnie z zasadami pozostałych dopracowanych działów.
- `pattern`: multi choice, bez powtórzeń; `Solid` i `Other` samodzielnie. Przy nazwanym wzorze nie dodajemy `Other` za dodatkowe logo lub grafikę.
- `sleeve_length`: `Sleeveless`, `Short Sleeve`, `Three-Quarter Sleeve`, `Long Sleeve`, single choice w obu kategoriach.
- `fit`: `Slim`, `Regular`, `Relaxed`, single choice.
- `length`: `Cropped`, `Regular`, `Longline`, single choice w obu kategoriach.

## Kołnierz koszul (`collar_type`, single choice)

| Wartość | Znaczenie |
| :--- | :--- |
| `Point Collar` | Wspólna grupa klasycznych kołnierzyków koszulowych, także spread, cutaway i button-down. |
| `Camp Collar` | Otwarty kołnierzyk kubański (`camp`, `cuban`, `revere`, `convertible`). |
| `Stand Collar` | Stójka (`stand`, `band`, `mandarin`, `mao`, `grandad`). |
| `Collarless` | Rzeczywisty brak kołnierza i stójki. |
| `Other` | Pozostałe rozpoznane konstrukcje, w tym kołnierz szalowy i klapy. |

Nie dodajemy koszulom równolegle `neckline`. `Collarless` oznacza potwierdzony brak kołnierza, a nie brak informacji.

## Dekolt bluzek (`neckline`, single choice)

| Wartość | Znaczenie |
| :--- | :--- |
| `Crewneck` | Okrągły, blisko szyi. |
| `Scoop Neck` | Głębszy, otwarty dekolt zaokrąglony. |
| `V-Neck` | W serek. |
| `High Neck` | Golf, półgolf, wysoki komin lub zabudowana stójka. |
| `Collared` | Wykładany kołnierzyk lub klapy, bez rozróżnienia szczegółowego typu. |
| `Other` | Pozostałe rozpoznane kształty, w tym łódka, cowl, kwadratowy, asymetryczny, sweetheart i prosty brzeg nad biustem. |

Znaczenia nazwanych wartości są wspólne z `Tops`, `Dresses` i `Sweaters`. Nie dodajemy bluzkom `collar_type`.

Nie wprowadzamy `full_composition_text`, `closure_type`, `hood`, `strap_style` ani `strap_width`. Te informacje mogą pozostać w opisach dla rankingu.
