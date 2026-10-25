# Reguły ekstrakcji cech Cargo Pants

Statystyki dla **188 Cargo Pants** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 188 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 187 | 99,47% |
| `undefined` | 1 | 0,53% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 179 | 95,21% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 0 | 0,00% |
| `ambiguous_main_section` | 3 | 1,60% |
| `unmapped_material` | 4 | 2,13% |
| `sum_not_100` | 2 | 1,06% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 188 | 100,00% |
<!-- /results -->

## `fit`

```text
Kolumna `description` – fraza „<krój>-fit” / „<krój> fit”
├─ dokładnie 1 wartość → wykryta wartość
├─ ≥ 2 różne wartości  → undefined
└─ brak frazy → kolumny `name` i `description`
   ├─ liczba wartości = 1 → wykryta wartość
   └─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 156 | 82,98% |
| `undefined` | 32 | 17,02% |
<!-- /results -->

## `leg_shape`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:leg_shape -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 29 | 15,43% |
| `undefined` | 159 | 84,57% |
<!-- /results -->

## `length`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 15 | 7,98% |
| `undefined` | 173 | 92,02% |
<!-- /results -->

## `rise`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:rise -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 34 | 18,09% |
| `undefined` | 154 | 81,91% |
<!-- /results -->

## `waistband_type`

```text
Kolumna `description`
├─ zdanie o pasie (waist / waistband) z keywordem Elasticized → Elasticized
├─ keyword Other                                              → Other
├─ keyword Structured                                         → Structured
├─ zdanie o pasie z „partially elasticized”                   → Elasticized
└─ else                                                       → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:waistband_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 174 | 92,55% |
| `undefined` | 14 | 7,45% |
<!-- /results -->

## `cuff_style`

```text
Kolumna `description` – zdania z cuff / cuffs / hem / hems, bez zdań o kieszeniach i bez zip-fly / button-fly
├─ keyword Zippered Cuff    → Zippered Cuff
├─ keyword Elasticized Cuff → Elasticized Cuff
├─ keyword Other            → Other
├─ keyword Open Hem         → Open Hem
└─ else                     → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:cuff_style -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 95 | 50,53% |
| `undefined` | 93 | 49,47% |
<!-- /results -->

## Keywordy

### `fit`

Fraza w opisie: `skinny-fit` → Skinny, `slim-fit` → Slim, `regular-fit` / `classic fit` / `standard fit` → Regular, `relaxed-fit` / `loose-fit` / `oversized fit` / `boyfriend fit` / `baggy fit` → Relaxed. Bez frazy – keywordy:

| Wartość | Keywordy |
| --- | --- |
| `Skinny` | `skinny`, `skinny-fit`, `super skinny` |
| `Slim` | `slim`, `slim-fit`, `slim-cut` |
| `Regular` | `regular fit`, `regular-fit`, `classic fit`, `standard fit` |
| `Relaxed` | `relaxed`, `relaxed-fit`, `loose`, `loose-fit`, `loose-fitting`, `baggy`, `oversized`, `oversize`, `boyfriend`, `slouchy` |

### `leg_shape`

| Wartość | Keywordy |
| --- | --- |
| `Straight` | `straight-leg`, `straight leg`, `straight-fit`, `straight fit`, `straight-cut`, `straight jeans`, `straight trousers`, `straight pants` |
| `Tapered` | `tapered`, `tapering`, `carrot`, `jogger`, `joggers` |
| `Wide-Leg` | `wide-leg`, `wide leg`, `wide trousers`, `wide jeans`, `wide pants`, `wide lounge pants`, `palazzo`, `culotte`, `culottes` |
| `Flared` | `flared`, `flare`, `bootcut`, `boot-cut`, `bell-bottom`, `bell-bottoms` |
| `Other` | `sarouel`, `harem`, `drop-crotch`, `drop crotch`, `dropped crotch`, `balloon`, `jodhpur`, `jodhpurs` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped`, `crop`, `capri`, `capris`, `three-quarter`, `7/8`, `ankle-grazing`, `ankle grazing`, `above ankle`, `culotte`, `culottes` |
| `Full-Length` | `full-length leg`, `floor-length`, `floor length`, `extra-long`, `long jeans`, `long trousers`, `long pants` |

### `rise`

| Wartość | Keywordy |
| --- | --- |
| `High-Rise` | `high-rise`, `high rise`, `high-waisted`, `high waisted`, `high-waist`, `high waist` |
| `Mid-Rise` | `mid-rise`, `mid rise`, `medium rise`, `regular rise` |
| `Low-Rise` | `low-rise`, `low rise`, `low-waisted`, `low waisted`, `low-waist`, `low waist` |

### `waistband_type`

Elasticized: `elasticized`, `elasticised`, `elastic`, `rib knit`, `ribbed`, `ribbed knit` najwyżej 2 słowa przed `waist` / `waistband` (bez „partially”) albo `drawstring`, `bungee`, `pull-on` w zdaniu o pasie.

| Wartość | Keywordy |
| --- | --- |
| `Elasticized` | `elasticized waistband`, `elasticised waistband`, `elastic waistband`, `elasticized waist`, `rib knit waistband`, `ribbed waistband`, `ribbed knit waistband`, `drawstring`, `bungee`, `pull-on` |
| `Other` | `paperbag`, `paper bag`, `tie-waist`, `tie waist`, `wrap waist` |
| `Structured` | `zip-fly`, `zip fly`, `button-fly`, `button fly`, `belt loop`, `belt loops`, `hook-and-eye`, `hook and eye`, `hook-and-bar`, `hook and bar` |

### `cuff_style`

| Wartość | Keywordy |
| --- | --- |
| `Zippered Cuff` | `zip`, `zips`, `zipper`, `zippers`, `zippered`, `zipped` |
| `Elasticized Cuff` | `elasticized`, `elasticised`, `elastic`, `rib knit`, `rib-knit`, `ribbed`, `drawstring`, `bungee`, `cinched`, `gathered` |
| `Other` | `velcro`, `press-stud`, `press-studs`, `snap`, `snaps`, `button`, `buttoned`, `tab`, `stirrup`, `stirrups`, `strap`, `straps` |
| `Open Hem` | `raw edge`, `raw edges`, `raw-edge`, `raw-edged`, `raw hem`, `unfinished`, `rolled`, `serged`, `vent`, `vented`, `frayed`, `slit`, `slits`, `split`, `cuffed`, `turn-up`, `turn-ups` |
