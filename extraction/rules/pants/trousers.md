# Reguły ekstrakcji cech Trousers

Statystyki dla **3,916 Trousers** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,916 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,880 | 99,08% |
| `undefined` | 36 | 0,92% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,501 | 89,40% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 95 | 2,43% |
| `ambiguous_main_section` | 213 | 5,44% |
| `unmapped_material` | 37 | 0,94% |
| `sum_not_100` | 70 | 1,79% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 3 916 | 100,00% |
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
| Przypisane | 2,227 | 56,87% |
| `undefined` | 1,689 | 43,13% |
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
| Przypisane | 1,460 | 37,28% |
| `undefined` | 2,456 | 62,72% |
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
| Przypisane | 729 | 18,62% |
| `undefined` | 3,187 | 81,38% |
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
| Przypisane | 805 | 20,56% |
| `undefined` | 3,111 | 79,44% |
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
| Przypisane | 3,478 | 88,82% |
| `undefined` | 438 | 11,18% |
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
| Przypisane | 1,269 | 32,41% |
| `undefined` | 2,647 | 67,59% |
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
