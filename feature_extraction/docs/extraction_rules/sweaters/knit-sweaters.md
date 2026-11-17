# Reguły ekstrakcji cech Knit Sweaters

Statystyki dla **4,990 Knit Sweaters** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4 990 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4 921 | 98,62% |
| `undefined` | 69 | 1,38% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4 685 | 93,89% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 33 | 0,66% |
| `ambiguous_main_section` | 98 | 1,96% |
| `unmapped_material` | 76 | 1,52% |
| `sum_not_100` | 98 | 1,96% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha single choice, przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 4 990 | 100,00% |
<!-- /results -->

## `sleeve_length`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:sleeve_length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4 810 | 96,39% |
| `undefined` | 180 | 3,61% |
<!-- /results -->

## `fit`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 150 | 3,01% |
| `undefined` | 4 840 | 96,99% |
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
| Przypisane | 65 | 1,30% |
| `undefined` | 4 925 | 98,70% |
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
| Przypisane | 8 | 0,16% |
| `undefined` | 4 982 | 99,84% |
<!-- /results -->

## `neckline`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:neckline -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4 631 | 92,81% |
| `undefined` | 359 | 7,19% |
<!-- /results -->

## Keywordy

### `sleeve_length`

| Wartość | Keywordy |
| --- | --- |
| `Sleeveless` | `sleeveless` |
| `Short Sleeve` | `short sleeve`, `short sleeves`, `short-sleeved` |
| `Three-Quarter Sleeve` | `three-quarter sleeve`, `three-quarter sleeves`, `three-quarter length sleeves`, `3/4 sleeve`, `3/4 sleeves`, `cropped sleeve`, `cropped sleeves`, `cropped-sleeve` |
| `Long Sleeve` | `long sleeve`, `long sleeves`, `long-sleeved` |

### `fit`

| Wartość | Keywordy |
| --- | --- |
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `fitted sweater`, `fitted pullover`, `fitted jumper`, `close-fitting`, `form-fitting`, `body-hugging` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `boxy fit`, `boxy-fit`, `oversized fit`, `oversize fit`, `oversized hoodie`, `oversize sweater`, `oversized cardigan` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped sweater`, `cropped pullover`, `cropped jumper`, `cropped fit`, `cropped length`, `crop top` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated body`, `extended length`, `extended-length` |

### `hood`

| Wartość | Keywordy |
| --- | --- |
| `With Hood` | `hood`, `hoods`, `hooded`, `hoodie` |
| `Without Hood` | Brak — rozstrzyga LLM. |

### `neckline`

| Wartość | Keywordy |
| --- | --- |
| `Crewneck` | `crewneck`, `crew neck`, `crew-neck` |
| `V-Neck` | `v-neck`, `v neck`, `v-neckline` |
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Collared` | `spread collar`, `point collar`, `shirt collar`, `polo collar` |
| `Other` | `scoop neck`, `scoop-neck`, `scoop neckline`, `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline` |
