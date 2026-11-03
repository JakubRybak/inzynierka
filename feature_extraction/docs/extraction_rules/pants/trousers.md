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
| Przypisane | 3,584 | 91,52% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 66 | 1,69% |
| `ambiguous_main_section` | 128 | 3,27% |
| `unmapped_material` | 40 | 1,02% |
| `sum_not_100` | 98 | 2,50% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 3,916 | 100,00% |
<!-- /results -->

## `fit`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else                → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,211 | 56,46% |
| `undefined` | 1,705 | 43,54% |
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
| Przypisane | 1,463 | 37,36% |
| `undefined` | 2,453 | 62,64% |
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
├─ liczba wartości = 1 → wykryta wartość
└─ else                → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:waistband_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,994 | 76,46% |
| `undefined` | 922 | 23,54% |
<!-- /results -->

## `cuff_style`

```text
Kolumna `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else                → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:cuff_style -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 966 | 24,67% |
| `undefined` | 2,950 | 75,33% |
<!-- /results -->

## Keywordy

### `fit`

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

| Wartość | Keywordy |
| --- | --- |
| `Elasticized` | `elasticized waistband`, `elasticised waistband`, `elastic waistband`, `elasticized waist`, `elasticised waist`, `rib knit waistband`, `ribbed waistband`, `ribbed knit waistband`, `drawstring`, `drawstrings`, `bungee`, `pull-on` |
| `Other` | `paperbag`, `paper bag`, `tie-waist`, `tie waist`, `wrap waist` |
| `Structured` | `zip-fly`, `zip fly`, `button-fly`, `button fly`, `belt loop`, `belt loops`, `hook-and-eye`, `hook and eye`, `hook-and-bar`, `hook and bar` |

### `cuff_style`

| Wartość | Keywordy |
| --- | --- |
| `Zippered Cuff` | `zippered vent`, `zippered vents`, `zip vent`, `zip vents`, `zippered ankle cuffs`, `zippered cuffs`, `zipped cuffs`, `zip at cuffs`, `zip closure at cuffs`, `zippered at`, `zipped at`, `zippered hem`, `zip at hem` |
| `Elasticized Cuff` | `rib knit cuffs`, `rib knit ankle cuffs`, `ribbed knit ankle cuffs`, `ribbed knit cuffs`, `ribbed cuffs`, `ribbed ankle cuffs`, `elasticized cuffs`, `elasticised cuffs`, `elasticized ankle cuffs`, `elasticised ankle cuffs`, `elastic cuffs`, `elastic ankle cuffs`, `elasticized hem`, `elasticized hems`, `drawstring at cuffs`, `drawstring at hem`, `drawstrings at cuffs`, `cinched cuffs`, `gathered cuffs`, `elasticized waistband and cuffs`, `elasticized waistband and ankle cuffs`, `elasticised waistband and cuffs`, `elasticised waistband and ankle cuffs`, `rib knit waistband and cuffs`, `rib knit waistband and ankle cuffs` |
| `Other` | `cinch strap at cuffs`, `cinch straps at cuffs`, `buttoned vent at cuffs`, `buttoned tab at cuffs`, `button tab at cuffs`, `press-stud tab at cuffs`, `press-stud at cuffs`, `press-studs at cuffs`, `press-stud placket at ankle cuffs`, `velcro fastening at cuffs`, `velcro tab at cuffs`, `snap at cuffs`, `snaps at cuffs`, `stirrup`, `stirrups` |
| `Open Hem` | `rolled cuffs`, `rolled ankle cuffs`, `rolled hem`, `raw edge at hem`, `raw edges at hem`, `raw edge at cuffs`, `raw edges at cuffs`, `raw edge at ankle cuffs`, `raw hem`, `raw-edge hem`, `unfinished hem`, `unfinished hems`, `unfinished edge at cuffs`, `unfinished hem at ankle cuffs`, `unfinished hems at ankle cuffs`, `serged ankle cuffs`, `serged cuffs`, `serged hem`, `frayed hem`, `vented cuffs`, `vented hem`, `vent at cuffs`, `vents at cuffs`, `slit at cuffs`, `slits at cuffs`, `split at cuffs`, `turn-up cuffs`, `turn-ups`, `cuffed hem` |
