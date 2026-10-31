# Reguły ekstrakcji cech Jeans

Statystyki dla **3,704 Jeans** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,704 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,690 | 99,62% |
| `undefined` | 14 | 0,38% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,561 | 96,14% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 48 | 1,30% |
| `ambiguous_main_section` | 22 | 0,59% |
| `unmapped_material` | 33 | 0,89% |
| `sum_not_100` | 40 | 1,08% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 3 704 | 100,00% |
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
| Przypisane | 2,886 | 77,92% |
| `undefined` | 818 | 22,08% |
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
| Przypisane | 740 | 19,98% |
| `undefined` | 2,964 | 80,02% |
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
| Przypisane | 497 | 13,42% |
| `undefined` | 3,207 | 86,58% |
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
| Przypisane | 1,941 | 52,40% |
| `undefined` | 1,763 | 47,60% |
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
| Przypisane | 3,441 | 92,90% |
| `undefined` | 263 | 7,10% |
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
| Przypisane | 433 | 11,69% |
| `undefined` | 3,271 | 88,31% |
<!-- /results -->

## `distressing`

```text
Kolumny `name` i `description`
├─ keyword Distressed → Distressed
├─ keyword Faded      → Faded
├─ keyword Clean      → Clean
└─ else              → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:distressing -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,592 | 69,98% |
| `undefined` | 1,112 | 30,02% |
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

### `distressing`

| Wartość | Keywordy |
| --- | --- |
| `Distressed` | `distressed`, `distressing`, `ripped`, `rips`, `torn`, `destroyed`, `shredded`, `shredding`, `slashed`, `slashes`, `abrasion`, `abrasions` |
| `Faded` | `fading`, `faded`, `whiskering`, `whiskered`, `stonewashed`, `stone-washed`, `acid wash`, `acid-wash`, `bleached`, `bleaching`, `honeycombing`, `vintage wash` |
| `Clean` | `raw denim`, `unwashed`, `rinse`, `rinsed`, `dry denim` |
