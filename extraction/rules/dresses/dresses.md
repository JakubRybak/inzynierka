# Reguły ekstrakcji cech Dresses

Statystyki dla **2,600 Dresses** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 600 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 547 | 97,96% |
| `undefined` | 53 | 2,04% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 359 | 90,73% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 28 | 1,08% |
| `ambiguous_main_section` | 134 | 5,15% |
| `unmapped_material` | 34 | 1,31% |
| `sum_not_100` | 45 | 1,73% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2 600 | 100,00% |
<!-- /results -->

## `length`

```text
Kolumna `original_category`
├─ SHORT DRESSES      → Mini
├─ MID LENGTH DRESSES → Midi
├─ LONG DRESSES       → Maxi
└─ else              → wykluczenie produktu ze zbioru
```

`length` przypisujemy wyłącznie z `original_category`, bez keywordów i LLM.

<!-- results:length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2 600 | 100,00% |
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
| Przypisane | 2 348 | 90,31% |
| `undefined` | 252 | 9,69% |
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
| Przypisane | 1 950 | 75,00% |
| `undefined` | 650 | 25,00% |
<!-- /results -->

## `dress_silhouette`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:dress_silhouette -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 192 | 7,38% |
| `undefined` | 2 408 | 92,62% |
<!-- /results -->

## `dress_type`

```text
Kolumny `name` i `description`
├─ wykryto `Other`       → `Other`
├─ liczba wartości ≥ 1 → lista wykrytych wartości bez powtórzeń
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:dress_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 490 | 18,85% |
| `undefined` | 2 110 | 81,15% |
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
| Przypisane | 114 | 4,38% |
| `undefined` | 2 486 | 95,62% |
<!-- /results -->

## `strap_width`

```text
strap_style oraz kolumny `name` i `description`
├─ strap_style = Strapless        → Not Applicable
├─ strap_style = Standard Sleeved → Not Applicable
├─ liczba wartości = 1            → wykryta wartość
└─ else                          → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:strap_width -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 27 | 1,04% |
| `undefined` | 2 573 | 98,96% |
<!-- /results -->

## Keywordy

### `sleeve_length`

| Wartość | Keywordy |
| --- | --- |
| `Sleeveless` | `sleeveless` |
| `Short Sleeve` | `short sleeve`, `short sleeves`, `short-sleeved` |
| `Three-Quarter Sleeve` | `three-quarter sleeve`, `three-quarter sleeves`, `three-quarter length sleeves`, `3/4 sleeve`, `3/4 sleeves`, `cropped sleeve`, `cropped sleeves`, `cropped-sleeve` |
| `Long Sleeve` | `long sleeve`, `long sleeves`, `long-sleeved` |

### `neckline`

| Wartość | Keywordy |
| --- | --- |
| `Crewneck` | `crewneck`, `crew neck`, `crew-neck` |
| `Scoop Neck` | `scoop neck`, `scoop-neck`, `scoop neckline` |
| `V-Neck` | `v-neck`, `v neck`, `v-neckline` |
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Collared` | `spread collar`, `point collar`, `shirt collar`, `polo collar` |
| `Other` | `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline` |

### `dress_silhouette`

| Wartość | Keywordy |
| --- | --- |
| `Fitted` | `bodycon`, `body-con`, `figure-hugging`, `body-hugging`, `fitted silhouette`, `fitted dress` |
| `Straight` | `straight-cut`, `straight cut`, `straight silhouette`, `shift dress` |
| `A-Line` | `a-line`, `a line`, `fit-and-flare`, `fit and flare` |
| `Other` | Brak — rozstrzyga LLM |

### `dress_type`

| Wartość | Keywordy |
| --- | --- |
| `Slip` | `slip dress`, `camisole dress`, `cami dress` |
| `Shirt Dress` | `shirt dress`, `shirtdress`; nie uwzględniamy dopasowania we frazie `t-shirt dress` |
| `Wrap` | `wrap dress`, `wrap-style dress`, `wrap-front dress` |
| `Sweater Dress` | `sweater dress`, `jumper dress` |
| `Sweatshirt Dress` | `sweatshirt dress`, `hoodie dress`, `hooded sweatshirt dress` |
| `T-Shirt Dress` | `t-shirt dress`, `tee dress`, `tshirt dress` |
| `Other` | Brak — rozstrzyga LLM |

### `strap_style`

| Wartość | Keywordy |
| --- | --- |
| `Standard` | Brak — rozstrzyga LLM. |
| `Standard Sleeved` | Brak — rozstrzyga LLM. |
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
| `Not Applicable` | Bez keywordów — z `strap_style = Strapless` lub `strap_style = Standard Sleeved`. |
