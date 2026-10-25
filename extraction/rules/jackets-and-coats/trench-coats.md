# Reguły ekstrakcji cech Trench Coats

Statystyki dla **166 Trench Coats** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 166 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 163 | 98,19% |
| `undefined` | 3 | 1,81% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 143 | 86,14% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 6 | 3,61% |
| `ambiguous_main_section` | 17 | 10,24% |
| `unmapped_material` | 0 | 0,00% |
| `sum_not_100` | 0 | 0,00% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 166 | 100,00% |
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
| Przypisane | 94 | 56,63% |
| `Unknown` | 72 | 43,37% |
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
| Przypisane | 4 | 2,41% |
| `undefined` | 162 | 97,59% |
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
| Przypisane | 165 | 99,40% |
| `undefined` | 1 | 0,60% |
<!-- /results -->

## `collar_type`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:collar_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 161 | 96,99% |
| `undefined` | 5 | 3,01% |
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
| Przypisane | 31 | 18,67% |
| `undefined` | 135 | 81,33% |
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
| Przypisane | 6 | 3,61% |
| `undefined` | 160 | 96,39% |
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
| Przypisane | 166 | 100,00% |
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

### `collar_type`

| Wartość | Keywordy |
| --- | --- |
| `Lapel Collar` | `lapel`, `lapels`, `shawl collar`, `notched collar` |
| `Point Collar` | `spread collar`, `point collar`, `pointed collar`, `button-down collar`, `shirt collar`, `classic collar` |
| `Stand Collar` | `stand collar`, `stand-up collar`, `band collar`, `mandarin collar`, `funnel collar`, `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Other` | `collarless`, `crewneck`, `crew neck`, `crew-neck`, `v-neck`, `v neck`, `y-neck`, `scoop neck`, `peter pan collar` |

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
| `Short` | `short coat`, `short trench`, `short parka`, `cropped`, `hip-length`, `waist-length` |
| `Mid-Length` | `mid-length`, `midi`, `knee-length`, `three-quarter length` |
| `Long` | `long coat`, `long trench`, `long parka`, `maxi`, `floor-length`, `ankle-length`, `longline`, `long-line` |

### `fit`

Keyword nie liczy się przed częścią ubrania: lapel, collar, pull-tab, hood, zip, pocket, button, patch, cuffs, logo, buckle, hardware, tab, sleeves, shoulders, hem.

| Wartość | Keywordy |
| --- | --- |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fit`, `loose-fitting`, `oversized`, `oversize`, `boxy`, `boxy fit`, `boxy-fit`, `cocoon`, `slouchy` |
| `Regular` | Bez keywordów — brak `Oversized`. |
