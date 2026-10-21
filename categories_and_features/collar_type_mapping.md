# Mapowanie kołnierza (`collar_type`)

Single choice. Zakres zależy od kategorii.

- `Shirts`: `Point Collar`, `Camp Collar`, `Stand Collar`, `Collarless`, `Other`.
- `Classic Coats`: `Point Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`, `Other`.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Point Collar` | Klasyczny wykładany kołnierzyk koszulowy, także spread, cutaway i button-down. |
| `Camp Collar` | Otwarty kołnierzyk kubański (`camp`, `cuban`, `revere`, `convertible`). |
| `Lapel Collar` | Klapy marynarkowe lub płaszczowe (`notched lapel`, `peak lapel`, `tailored lapels`). |
| `Stand Collar` | Stójka lub kołnierz kominowy bez wykładanych rożków (`stand`, `band`, `mandarin`, `funnel`). |
| `Shawl Collar` | Kołnierz szalowy, płynnie przechodzący w przód ubrania (`shawl collar`, `shawl lapel`). |
| `Collarless` | Potwierdzony brak kołnierza i stójki. |
| `Other` | Rozpoznana konstrukcja poza nazwanymi klasami dostępnymi w kategorii. |

W `Shirts` klapy i kołnierz szalowy trafiają do `Other`. W `Classic Coats` kołnierz camp trafia do `Other`. `Collarless` nie oznacza braku informacji. Sam kaptur nie przesądza o obecności lub braku kołnierza.
