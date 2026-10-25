# Reguły ekstrakcji cech Shorts

Statystyki dla **2,053 Shorts** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,053 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,021 | 98,44% |
| `undefined` | 32 | 1,56% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,833 | 89,28% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 71 | 3,46% |
| `ambiguous_main_section` | 89 | 4,34% |
| `unmapped_material` | 23 | 1,12% |
| `sum_not_100` | 37 | 1,80% |
<!-- /results -->

## `pattern`

Reguły i keywordy: [common/pattern.md](../common/pattern.md).

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 274 | 13,35% |
| `undefined` | 1,779 | 86,65% |
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
| Przypisane | 1,279 | 62,30% |
| `undefined` | 774 | 37,70% |
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
| Przypisane | 1,877 | 91,43% |
| `undefined` | 176 | 8,57% |
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
| Przypisane | 61 | 2,97% |
| `undefined` | 1,992 | 97,03% |
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
| Przypisane | 344 | 16,76% |
| `undefined` | 1,709 | 83,24% |
<!-- /results -->

## `shorts_type`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:shorts_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 536 | 26,11% |
| `undefined` | 1,517 | 73,89% |
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

### `waistband_type`

Elasticized: `elasticized`, `elasticised`, `elastic`, `rib knit`, `ribbed`, `ribbed knit` najwyżej 2 słowa przed `waist` / `waistband` (bez „partially”) albo `drawstring`, `bungee`, `pull-on` w zdaniu o pasie.

| Wartość | Keywordy |
| --- | --- |
| `Elasticized` | `elasticized waistband`, `elasticised waistband`, `elastic waistband`, `elasticized waist`, `rib knit waistband`, `ribbed waistband`, `ribbed knit waistband`, `drawstring`, `bungee`, `pull-on` |
| `Other` | `paperbag`, `paper bag`, `tie-waist`, `tie waist`, `wrap waist` |
| `Structured` | `zip-fly`, `zip fly`, `button-fly`, `button fly`, `belt loop`, `belt loops`, `hook-and-eye`, `hook and eye`, `hook-and-bar`, `hook and bar` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Short` | `short shorts`, `short-length shorts`, `short length shorts`, `hot pants`, `hotpants` |
| `Mid-Length` | `mid-length shorts`, `mid length shorts`, `mid-thigh length`, `mid-thigh shorts` |
| `Long` | `long shorts`, `long-length shorts`, `long length shorts`, `knee-length shorts`, `knee length shorts`, `bermuda shorts`, `bermudas` |

### `rise`

| Wartość | Keywordy |
| --- | --- |
| `High-Rise` | `high-rise`, `high rise`, `high-waisted`, `high waisted`, `high-waist`, `high waist` |
| `Mid-Rise` | `mid-rise`, `mid rise`, `medium rise`, `regular rise` |
| `Low-Rise` | `low-rise`, `low rise`, `low-waisted`, `low waisted`, `low-waist`, `low waist` |

### `shorts_type`

| Wartość | Keywordy |
| --- | --- |
| `Denim` | `denim`, `jean shorts` |
| `Cargo` | `cargo shorts`, `cargo pockets`, `cargo pocket` |
| `Sweatshorts` | `sweatshorts`, `sweat shorts`, `sweat-shorts`, `french terry shorts`, `fleece shorts` |
| `Athletic` | `athletic shorts`, `running shorts`, `training shorts`, `gym shorts`, `basketball shorts`, `track shorts` |
| `Tailored` | `tailored shorts`, `dress shorts`, `formal shorts` |
| `Other` | Brak — rozstrzyga LLM |
