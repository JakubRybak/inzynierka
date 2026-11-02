# Reguły ekstrakcji cech Tank tops & Camisoles

Statystyki dla **1,020 Tank tops & Camisoles** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1 020 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 991 | 97,16% |
| `undefined` | 29 | 2,84% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 912 | 89,41% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 4 | 0,39% |
| `ambiguous_main_section` | 65 | 6,37% |
| `unmapped_material` | 8 | 0,78% |
| `sum_not_100` | 31 | 3,04% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 1 020 | 100,00% |
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
| Przypisane | 637 | 62,45% |
| `undefined` | 383 | 37,55% |
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
| Przypisane | 131 | 12,84% |
| `undefined` | 889 | 87,16% |
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
| Przypisane | 35 | 3,43% |
| `undefined` | 985 | 96,57% |
<!-- /results -->

## `strap_style`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:strap_style -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 143 | 14,02% |
| `undefined` | 877 | 85,98% |
<!-- /results -->

## `strap_width`

```text
strap_style oraz kolumny `name` i `description`
├─ strap_style = Strapless → Not Applicable
├─ liczba wartości = 1     → wykryta wartość
└─ else                   → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

**Zależność:** `strap_width = Not Applicable` wtedy i tylko wtedy, gdy `strap_style = Strapless`, również po ekstrakcji przez LLM. Konflikt z przypisaną wcześniej cechą wymaga sprawdzenia; wyników keywordów nie nadpisujemy.

<!-- results:strap_width -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 19 | 1,86% |
| `undefined` | 1 001 | 98,14% |
<!-- /results -->

## Keywordy

### `neckline`

| Wartość | Keywordy |
| --- | --- |
| `Crewneck` | `crewneck`, `crew neck`, `crew-neck` |
| `Scoop Neck` | `scoop neck`, `scoop-neck`, `scoop neckline` |
| `V-Neck` | `v-neck`, `v neck`, `v-neckline` |
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Other` | `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline`, `spread collar`, `point collar` |

### `fit`

| Wartość | Keywordy |
| --- | --- |
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `fitted tank`, `fitted tank top`, `fitted camisole`, `fitted cami`, `close-fitting`, `form-fitting`, `body-hugging` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `oversized`, `oversize`, `boxy fit`, `boxy-fit` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped tank`, `cropped tank top`, `cropped camisole`, `cropped cami`, `cropped fit`, `cropped length`, `crop top` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated body`, `extended length`, `extended-length` |

### `strap_style`

| Wartość | Keywordy |
| --- | --- |
| `Standard` | Brak — rozstrzyga LLM. |
| `Racerback` | `racerback`, `racer back`, `racer-back` |
| `Halter` | `halter`, `halterneck`, `halter neck`, `halter-neck` |
| `One-Shoulder` | `one shoulder`, `one-shoulder`, `single shoulder`, `single-shoulder` |
| `Strapless` | `strapless` |
| `Off-Shoulder` | `off shoulder`, `off-shoulder`, `off the shoulder`, `off-the-shoulder` |
| `Other` | Brak — rozstrzyga LLM. |

### `strap_width`

| Wartość | Keywordy |
| --- | --- |
| `Wide` | `wide straps`, `wide shoulder straps`, `broad straps`, `broad shoulder straps` |
| `Spaghetti` | `spaghetti straps`, `spaghetti shoulder straps`, `thin straps`, `thin shoulder straps`, `narrow straps`, `narrow shoulder straps` |
| `Other` | Brak — rozstrzyga LLM |
| `Not Applicable` | Bez keywordów — wyłącznie z `strap_style = Strapless`. |
