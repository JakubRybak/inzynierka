# Mapowanie konstrukcji góry (`strap_style`)

Single choice w `Tank tops & Camisoles`, `Bodysuits` i `Dresses`.

| Wartość | Znaczenie |
| :--- | :--- |
| `Standard` | Zwykłe ramiączka, bez specjalnego układu. |
| `Racerback` | Ramiączka schodzące się na plecach w układ T lub Y. |
| `Halter` | Ramiączko lub materiał biegnący wokół szyi. |
| `One-Shoulder` | Konstrukcja na jedno ramię, również z jednym rękawem. |
| `Strapless` | Góra bez ramiączek i rękawów podtrzymujących konstrukcję. |
| `Off-Shoulder` | Konstrukcja opuszczona poniżej ramion, również z rękawami. |
| `Other` | Rozpoznana konstrukcja spoza powyższych wartości, w tym zwykła konstrukcja z rękawami. |

- W `Tank tops & Camisoles`, `Bodysuits` i `Dresses` dostępne są wszystkie wartości, w tym `Other`.
- Przy konstrukcjach mieszanych pierwszeństwo: `One-Shoulder`, `Off-Shoulder`, `Halter`, `Racerback`, `Standard`.
- `Strapless` wymaga `strap_width = Not Applicable`. Przy `Other` szerokość określamy według rzeczywistej konstrukcji; brak ramiączek oznacza `Not Applicable`.
- `One-Shoulder` nie jest mapowane do `Strapless`.
- Dla pozostałych konstrukcji szerokość określamy na podstawie rzeczywistych ramiączek. Nie przypisujemy szerokości rękawowi lub zabudowanemu panelowi przy szyi.
- Brak możliwości rozpoznania konstrukcji oznacza wykluczenie produktu, nie `Standard` ani `Other`.

„Bez ramiączek” filtrujemy przez `strap_style = Strapless`. „Na jedno ramię” przez `One-Shoulder`. `strap_width = Not Applicable` nie jest filtrem braku ramiączek, ponieważ dotyczy również zwykłych produktów z rękawami.
