# Mapowanie szerokości ramiączek (`strap_width`)

Single choice w `Tank tops & Camisoles`, `Bodysuits` i `Dresses`.

| Wartość | Znaczenie |
| :--- | :--- |
| `Wide` | Szerokie ramiączka (`wide straps`, `thick shoulder straps`). |
| `Spaghetti` | Cienkie ramiączka (`spaghetti straps`, `thin straps`, `delicate straps`). |
| `Other` | Ramiączka pośredniej szerokości lub ramiączka o różnych szerokościach. |
| `Not Applicable` | Brak rzeczywistych ramiączek, np. produkt bez ramiączek lub zwykły produkt z rękawami. |

- `strap_style = Strapless` wymaga `strap_width = Not Applicable`. Przy `strap_style = Other` szerokość określamy według rzeczywistej konstrukcji; brak ramiączek oznacza `Not Applicable`.
- Przy `One-Shoulder`, `Off-Shoulder`, `Halter` oceniamy rzeczywistą konstrukcję; szerokość dotyczy tylko ramiączek, nigdy rękawa ani zabudowanego panelu przy szyi.
- `Other` oznacza rozpoznaną szerokość lub układ szerokości poza `Wide` i `Spaghetti`.
- `Not Applicable` nie oznacza nieznanej szerokości. Jeśli ramiączka są, ale nie można ustalić ich szerokości, produkt wykluczamy.
- Sama nazwa `tank top`, `camisole` lub informacja o regulacji ramiączek nie wystarcza do ustalenia szerokości.
- Bez `null` i tablic. Zapytanie o cienkie ramiączka filtrujemy przez `strap_width = Spaghetti`.
