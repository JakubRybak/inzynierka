# Cechy `Jackets & Coats`

Kategorie: `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`. Zachowujemy nazwę `Classic Coats`.

## Cechy wspólne

- `gender`: `Men`, `Women`, single choice.
- `colors`: 1–2 różne kolory albo samo `Multicolor`, bez koloru dominującego; wspólny słownik odcieni.
- `main_composition`: jeden skład głównej części zewnętrznej, suma 100%. Nie dodajemy procentów materiałów podszewki, wypełnienia ani futrzanych wykończeń do składu zewnętrznego. Skóra lub futro będące główną częścią zewnętrzną pozostają w składzie głównym.
- `pattern`: multi choice; `Solid` i `Other` samodzielnie. Nie dodajemy `Other` za logo przy nazwanym wzorze.
- `hood`: `With Hood`, `Without Hood`, single choice we wszystkich pięciu kategoriach.
- `closure_type`: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`, `Other`, multi choice. Osobne pole `belt` jest usunięte. Szczegóły w `closure_type_mapping.md`.
- `insulation`: `Unpadded`, `Padded`, `Fur Lined`, `Fleece Lined`, `Other`, multi choice. `Unpadded` i `Other` samodzielnie. Opisuje konstrukcję ocieplenia, a nie przewidywaną temperaturę użytkowania.
- `fit`: `Slim`, `Regular`, `Relaxed`, single choice.
- `length`: single choice; `Short`, `Mid-Length`, `Long` w `Classic Coats` i `Trench Coats`; `Cropped`, `Regular`, `Longline` w pozostałych kategoriach.

## Cechy kategorii

- `collar_type`: tylko `Classic Coats`; `Point Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`, `Other`, single choice.
- `jacket_type`: tylko `Jackets`; `Biker`, `Trucker`, `Puffer`, `Windbreaker`, `Utility`, `Parka`, `Other`, multi choice. `Other` samodzielnie.
- `bomber_style`: tylko `Bombers`; `Flight`, `Varsity`, `Other`, single choice. Pikowanie nie jest typem bomberki. Bomberka pikowana może nadal mieć typ `Flight` lub `Varsity`; pozostałe konstrukcje, również blouson, trafiają do `Other`.

## Przykłady

- Dwurzędowy trencz z paskiem: `closure_type = ["Double-Breasted", "Belted"]`.
- Kurtka z wypełnieniem i futrzaną podszewką: `insulation = ["Padded", "Fur Lined"]`.
- Puchowa parka: `jacket_type = ["Puffer", "Parka"]`.

Nie wprowadzamy `full_composition_text`, `neckline`, cech ramiączek ani osobnej cechy pikowania.
