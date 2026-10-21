# Mapowanie zakończenia nogawki (`cuff_style`)

Single choice we wszystkich czterech kategoriach `Pants`: `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans`.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Open Hem` | Zwykły dół bez ściągacza i zamka. Może być obszyty, podwinięty lub surowo zakończony. Zastępuje nazwę `Straight Hem`; nie określa kształtu nogawki. |
| `Elasticized Cuff` | Dół zebrany gumką lub prążkowanym ściągaczem, bez zamka (`elasticized cuffs`, `rib-knit cuffs`, `ribbed cuffs`). |
| `Zippered Cuff` | Zamek przy kostce umożliwiający rozpięcie lub poszerzenie dołu (`zippered cuffs`, `ankle zips`, `zip vent at cuffs`). Obejmuje również zakończenie ze ściągaczem i zamkiem. Nie dotyczy rozporka ani zamków kieszeni. |
| `Other` | Inne rozpoznane zakończenie, np. regulowane paskiem na rzep lub sznurkiem ze stoperem. |

- Przy jednoczesnym występowaniu ściągacza i zamka wybieramy `Zippered Cuff`.
- Sam sznurek, stoper lub pasek zwężający nogawkę nie oznacza `Elasticized Cuff`, jeśli nie ma gumki ani ściągacza.
- Rozszerzana nogawka może mieć `Open Hem`; jej kształt opisuje `leg_shape`.
