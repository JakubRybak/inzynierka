# Mapowanie zapięcia (`closure_type`)

## Wartości

| Wartość | Znaczenie |
| :--- | :--- |
| `Zip` | Pełne rozpięcie przodu zamkiem. |
| `Half-Zip` | Częściowy zamek pod szyją, również quarter-zip. |
| `Button` | Główne zapięcie na guziki, napy, zatrzaski, haftki lub kołki. |
| `Double-Breasted` | Konstrukcja dwurzędowa; osobna wartość tylko w `Jackets & Coats`. |
| `Belted` | W `Jackets & Coats`: rzeczywisty pasek w talii, główny lub dodatkowy. W `Sweaters`: główne zapięcie wiązane paskiem. |
| `Open Front` | Otwarty przód bez głównego zapięcia i wiązania paskiem. |
| `Pullover` | Wkładane przez głowę bez głównego rozpięcia przodu. |
| `Other` | Pozostałe konstrukcje. |

Oceniamy rzeczywiste zapięcie ubrania, nie zamki kieszeni, ozdobne guziki ani pomocnicze zapięcie przy karku.

## `Jackets & Coats` — multi choice

Wszystkie osiem wartości we wszystkich pięciu kategoriach. Bez osobnego pola `belt`.

- Lista bez powtórzeń; `Open Front` i `Other` występują samodzielnie.
- Pasek może współwystępować z innym zapięciem: `["Double-Breasted", "Belted"]`, `["Zip", "Belted"]`.
- Płaszcz zamykany wyłącznie paskiem: `["Belted"]`.
- Zamek i funkcjonalna plisa na napy lub guziki: `["Zip", "Button"]`.
- `Double-Breasted` zastępuje `Button` dla tego samego dwurzędowego zapięcia; nie dublujemy jednej konstrukcji. Może współwystępować z niezależnym zamkiem.
- `Zip`, `Half-Zip` i `Pullover` wykluczają się jako sposoby głównego otwarcia przodu.
- Same szlufki, marszczenie lub mała klamerka regulacyjna nie wystarczają do przypisania `Belted`.

## `Sweaters` — single choice

We wszystkich czterech kategoriach: `Zip`, `Half-Zip`, `Button`, `Belted`, `Open Front`, `Pullover`, `Other`.

- Potwierdzone `Double-Breasted` zawsze trafia do `Other`, również przy guzikach lub zamku.
- Częściowy zamek oznacza `Half-Zip`, nie `Pullover`.
- Główny zamek kryty pomocniczą plisą oznacza `Zip`.
- `Belted` dotyczy głównego zamknięcia wiązanego paskiem, bez głównego zamka lub rzędu guzików.
