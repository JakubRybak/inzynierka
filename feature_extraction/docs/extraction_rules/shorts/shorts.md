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
| Przypisane | 1,911 | 93,08% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 27 | 1,32% |
| `ambiguous_main_section` | 51 | 2,48% |
| `unmapped_material` | 24 | 1,17% |
| `sum_not_100` | 40 | 1,95% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha single choice, przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2,053 | 100,00% |
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
| Przypisane | 1,272 | 61,96% |
| `undefined` | 781 | 38,04% |
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
| Przypisane | 1,563 | 76,13% |
| `undefined` | 490 | 23,87% |
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
| Przypisane | 82 | 3,99% |
| `undefined` | 1,971 | 96,01% |
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
| Przypisane | 752 | 36,63% |
| `undefined` | 1,301 | 63,37% |
<!-- /results -->

## Keywordy

### `fit`

| Wartość | Keywordy |
| --- | --- |
| `Skinny` | `skinny`, `skinny-fit`, `super skinny` |
| `Slim` | `slim`, `slim-fit`, `slim-cut` |
| `Regular` | `regular fit`, `regular-fit`, `classic fit`, `standard fit` |
| `Relaxed` | `relaxed`, `relaxed-fit`, `loose`, `loose-fit`, `loose-fitting`, `baggy`, `oversized`, `oversize`, `boyfriend`, `slouchy` |

### `waistband_type`

| Wartość | Keywordy |
| --- | --- |
| `Elasticized` | `elasticized waistband`, `elasticised waistband`, `elastic waistband`, `elasticized waist`, `elasticised waist`, `rib knit waistband`, `ribbed waistband`, `ribbed knit waistband`, `drawstring`, `drawstrings`, `bungee`, `pull-on` |
| `Other` | `paperbag`, `paper bag`, `tie-waist`, `tie waist`, `wrap waist` |
| `Structured` | `zip-fly`, `zip fly`, `button-fly`, `button fly`, `belt loop`, `belt loops`, `hook-and-eye`, `hook and eye`, `hook-and-bar`, `hook and bar` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Short` | `short shorts`, `short-length shorts`, `short length shorts`, `mini shorts`, `hot pants`, `hotpants` |
| `Mid-Length` | `mid-length`, `mid length`, `mid-thigh`, `mid thigh` |
| `Long` | `long shorts`, `long-length shorts`, `long length shorts`, `knee-length`, `knee length`, `bermuda`, `bermudas` |

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
| `Cargo` | `cargo` |
| `Sweatshorts` | `sweatshorts`, `sweat shorts`, `sweat-shorts`, `terry shorts`, `terrycloth shorts`, `fleece shorts`, `lounge shorts` |
| `Athletic` | `athletic shorts`, `running shorts`, `training shorts`, `gym shorts`, `basketball shorts`, `track shorts` |
| `Tailored` | `tailored`, `dress shorts`, `formal shorts` |
| `Other` | Brak — rozstrzyga LLM |
