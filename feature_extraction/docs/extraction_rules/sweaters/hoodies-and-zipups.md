# Reguły ekstrakcji cech Hoodies & Zipups

Statystyki dla **2,779 Hoodies & Zipups** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 779 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 760 | 99,32% |
| `undefined` | 19 | 0,68% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 616 | 94,13% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 13 | 0,47% |
| `ambiguous_main_section` | 99 | 3,56% |
| `unmapped_material` | 15 | 0,54% |
| `sum_not_100` | 36 | 1,30% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha single choice, przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2 779 | 100,00% |
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
| Przypisane | 2 705 | 97,34% |
| `undefined` | 74 | 2,66% |
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
| Przypisane | 60 | 2,16% |
| `undefined` | 2 719 | 97,84% |
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
| Przypisane | 17 | 0,61% |
| `undefined` | 2 762 | 99,39% |
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
| Przypisane | 2 400 | 86,36% |
| `undefined` | 379 | 13,64% |
<!-- /results -->

## `closure_type`

Cecha single choice, przypisywana wyłącznie przez LLM.

Wartości: `Pullover`, `Zip`, `Half-Zip`, `Other`.

```text
Każdy produkt
└─ closure_type → undefined
```

**Dalsze postępowanie:** ekstrakcja tej cechy przez LLM dla każdego produktu pozostającego w zbiorze.

<!-- results:closure_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2 779 | 100,00% |
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
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `fitted hoodie`, `fitted sweatshirt`, `fitted pullover`, `fitted zip-up`, `close-fitting`, `form-fitting`, `body-hugging` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `boxy fit`, `boxy-fit`, `oversized fit`, `oversize fit`, `oversized hoodie`, `oversize sweater`, `oversized cardigan` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped hoodie`, `cropped sweatshirt`, `cropped pullover`, `cropped zip-up`, `cropped fit`, `cropped length`, `crop top` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated body`, `extended length`, `extended-length` |

### `hood`

| Wartość | Keywordy |
| --- | --- |
| `With Hood` | `hood`, `hoods`, `hooded`, `hoodie` |
| `Without Hood` | Brak — rozstrzyga LLM. |
