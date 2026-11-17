# Reguły ekstrakcji cech Sweatshirts

Statystyki dla **3,432 Sweatshirts** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3 432 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3 395 | 98,92% |
| `undefined` | 37 | 1,08% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3 229 | 94,09% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 22 | 0,64% |
| `ambiguous_main_section` | 134 | 3,90% |
| `unmapped_material` | 13 | 0,38% |
| `sum_not_100` | 34 | 0,99% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha single choice, przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 3 432 | 100,00% |
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
| Przypisane | 3 387 | 98,69% |
| `undefined` | 45 | 1,31% |
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
| Przypisane | 69 | 2,01% |
| `undefined` | 3 363 | 97,99% |
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
| Przypisane | 19 | 0,55% |
| `undefined` | 3 413 | 99,45% |
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
| Przypisane | 16 | 0,47% |
| `undefined` | 3 416 | 99,53% |
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
| Przypisane | 3 337 | 97,23% |
| `undefined` | 95 | 2,77% |
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
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `fitted sweatshirt`, `fitted pullover`, `close-fitting`, `form-fitting`, `body-hugging` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `boxy fit`, `boxy-fit`, `oversized fit`, `oversize fit`, `oversized hoodie`, `oversize sweater`, `oversized cardigan` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped sweatshirt`, `cropped pullover`, `cropped fit`, `cropped length`, `crop top` |
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
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Other` | `scoop neck`, `scoop-neck`, `scoop neckline`, `v-neck`, `v neck`, `v-neckline`, `spread collar`, `point collar`, `shirt collar`, `polo collar`, `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline` |
