# Reguły ekstrakcji cech Bombers

Statystyki dla **1,573 Bombers** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,573 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,540 | 97,90% |
| `undefined` | 33 | 2,10% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,153 | 73,30% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 59 | 3,75% |
| `ambiguous_main_section` | 327 | 20,79% |
| `unmapped_material` | 21 | 1,34% |
| `sum_not_100` | 13 | 0,83% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 1 573 | 100,00% |
<!-- /results -->

## `lining_composition`

```text
Kolumna `composition` – sekcje Lining, Body lining, Lining N
├─ ≥ 2 sekcje → Unknown
├─ 1 sekcja   → parsuj jak main_composition
│  ├─ poprawny skład → zapisz skład
│  └─ else          → Unknown
└─ brak sekcji → kolumna `description`
   ├─ keyword Unlined → Unlined
   └─ else           → Unknown
```

**Dalsze postępowanie:** `Unknown` → wartość końcowa, bez ekstrakcji przez LLM.

<!-- results:lining_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 913 | 58,04% |
| `Unknown` | 660 | 41,96% |
<!-- /results -->

## `hood`

```text
Kolumny `name` i `description`
├─ keyword With Hood → With Hood
└─ else             → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:hood -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 65 | 4,13% |
| `undefined` | 1,508 | 95,87% |
<!-- /results -->

## `closure_type`

```text
Kolumna `description` – 4 słowa przed „closure” / „fastening” zapięcia głównego
├─ keywordy Zip, Button, Press-Stud            → te wartości
├─ keyword Double-Breasted (także w `name`)    → + Double-Breasted
├─ keyword Belted (także `belted` w `name`)    → + Belted
├─ ≥ 1 z powyższych                            → lista wartości
├─ keyword Open Front                          → Open Front
├─ keyword Other                               → Other
└─ else                                       → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:closure_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,518 | 96,50% |
| `undefined` | 55 | 3,50% |
<!-- /results -->

## `insulation`

```text
Kolumny `name`, `description` i `composition`
├─ keyword Down albo down / feather w składzie                      → Down
├─ keyword Shearling Lined albo shearling w składzie (poza Trim)    → Shearling Lined
├─ keyword Fleece Lined                                             → Fleece Lined
├─ keyword Other                                                    → Other
├─ keyword Synthetic Padding albo sekcja Fill / Padding w składzie  → Synthetic Padding
├─ keyword Uninsulated                                              → Uninsulated
└─ else                                                            → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:insulation -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 569 | 36,17% |
| `undefined` | 1,004 | 63,83% |
<!-- /results -->

## `length`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM (zdjęcie).

<!-- results:length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 35 | 2,23% |
| `undefined` | 1,538 | 97,77% |
<!-- /results -->

## `fit`

```text
Kolumny `name` i `description`
├─ keyword Oversized → Oversized
└─ else             → Regular
```

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,573 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## Keywordy

### `lining_composition`

Materiały jak w [common/main_composition.md](../common/main_composition.md).

| Wartość | Keywordy |
| --- | --- |
| `Unlined` | `unlined` |
| `Unknown` | Bez keywordów. |

### `hood`

| Wartość | Keywordy |
| --- | --- |
| `With Hood` | `hood`, `hoods`, `hooded`, `hoodie` |
| `Without Hood` | Brak — rozstrzyga LLM. |

### `closure_type`

Zapięcie główne: bez „closure / fastening at collar / cuffs / hood / pockets / waist / hem / …” i „collar / cuffs / hood / pockets / flap / panel / inner layer / … with … closure”, chyba że „… at front”. `snap-button` i `press-button` → Press-Stud.

| Wartość | Keywordy |
| --- | --- |
| `Zip` | `zip`, `zips`, `zipper`, `zippered`, `two-way zip`, `half-zip` |
| `Button` | `button`, `buttons`, `buttoned`, `single-button`, `two-button`, `three-button`, `four-button` |
| `Press-Stud` | `press-stud`, `press-studs`, `press stud`, `press-button`, `press-buttons`, `snap`, `snaps`, `snap-button`, `snap button` |
| `Double-Breasted` | `double-breasted`, `double breasted` |
| `Belted` | `self-tie belt`, `tie belt`, `detachable belt`, `removable belt`, `belt at waist`, `belted at waist`, `belted waist`, `tie-waist`, `tie waist`, `sash` |
| `Open Front` | `open front`, `open-front` |
| `Other` | `hook-eye`, `hook-and-eye`, `hook and eye`, `toggle`, `toggles`, `velcro`, `tie`, `self-tie`, `buckle`, `pin-buckle`, `clasp`, `magnetic`, `drawstring`, `lace-up` |

Belted: także `self-tie` / `detachable` / `removable` / `tie` + jedno słowo + `belt`, ale nie przed `at hem` / `back` / `sides` / `cuffs` / `sleeves`.

### `insulation`

Podszewka (`lining`, `lined`) w zdaniu o kapturze, kołnierzu lub mankietach się nie liczy. `shearling` z `faux` to Fleece Lined. `padded` nie liczy się przed `shoulders` / `elbows` / `knees`, `quilted` – przed częścią ubrania (`quilted panelling`, `quilted sleeves`).

| Wartość | Keywordy |
| --- | --- |
| `Down` | `down-filled`, `down-fill`, `down fill`, `down filling`, `goose down`, `duck down`, `quilted down`, `down jacket`, `down coat`, `down vest`, `down parka`, `down bomber`, `down puffer`, `down gilet`, `down aviator`, `down blouson` |
| `Shearling Lined` | `shearling lining`, `shearling-lined`, `shearling lined`, `lined in shearling`, `shearling jacket`, `shearling coat`, `shearling vest`, `shearling bomber`, `shearling parka`, `shearling gilet`, `shearling aviator`, `shearling blouson` |
| `Fleece Lined` | `fleece lining`, `fleece-lined`, `lined in fleece`, `sherpa lining`, `sherpa-lined`, `teddy lining`, `faux-shearling lining`, `faux shearling lining`, `pile lining`, `sherpa jacket`, `fleece jacket`, `faux-shearling jacket`, `faux-shearling coat`, `pile coat` |
| `Other` | `fur lining`, `fur-lined`, `fur lined`, `lined in fur`, `faux-fur lining`, `faux fur lining` |
| `Synthetic Padding` | `padded`, `padding`, `quilted`, `insulated`, `insulation`, `wadding`, `wadded`, `primaloft`, `thinsulate`, `puffer`, `puffy` |
| `Uninsulated` | `unlined`, `unpadded`, `uninsulated`, `non-insulated` |

### `length`

Keyword nie liczy się przed częścią ubrania: lapel, collar, pull-tab, hood, zip, pocket, button, patch, cuffs, logo, buckle, hardware, tab, sleeves, shoulders, hem, a także sleeve / -sleeve, panel, pile i `at` („cropped at back”).

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped`, `crop`, `cropped fit`, `cropped length` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated`, `extended length`, `long jacket`, `long vest`, `long bomber`, `long gilet` |

### `fit`

Keyword nie liczy się przed częścią ubrania: lapel, collar, pull-tab, hood, zip, pocket, button, patch, cuffs, logo, buckle, hardware, tab, sleeves, shoulders, hem.

| Wartość | Keywordy |
| --- | --- |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fit`, `loose-fitting`, `oversized`, `oversize`, `boxy`, `boxy fit`, `boxy-fit`, `cocoon`, `slouchy` |
| `Regular` | Bez keywordów — brak `Oversized`. |
