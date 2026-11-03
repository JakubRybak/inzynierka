# Reguły ekstrakcji cech Skirts

Statystyki dla **1,913 Skirts** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1 913 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1 861 | 97,28% |
| `undefined` | 52 | 2,72% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1 741 | 91,01% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 17 | 0,89% |
| `ambiguous_main_section` | 74 | 3,87% |
| `unmapped_material` | 34 | 1,78% |
| `sum_not_100` | 47 | 2,46% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 1 913 | 100,00% |
<!-- /results -->

## `length`

```text
Kolumna `original_category`
├─ SHORT SKIRTS      → Mini
├─ MID LENGTH SKIRTS → Midi
├─ LONG SKIRTS       → Maxi
└─ else             → wykluczenie produktu ze zbioru
```

`length` przypisujemy wyłącznie z `original_category`, bez keywordów i LLM.

<!-- results:length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1 913 | 100,00% |
<!-- /results -->

## `skirt_silhouette`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:skirt_silhouette -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 168 | 8,78% |
| `undefined` | 1 745 | 91,22% |
<!-- /results -->

## `skirt_type`

```text
Kolumny `name` i `description`
├─ wykryto Other      → lista zawierająca tylko Other
├─ liczba wartości ≥ 1 → lista wykrytych wartości bez powtórzeń
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:skirt_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 450 | 23,52% |
| `undefined` | 1 463 | 76,48% |
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
| Przypisane | 161 | 8,42% |
| `undefined` | 1 752 | 91,58% |
<!-- /results -->

## Keywordy

### `skirt_silhouette`

| Wartość | Keywordy |
| --- | --- |
| `Fitted` | `bodycon`, `body-con`, `figure-hugging`, `body-hugging`, `fitted silhouette`, `fitted skirt` |
| `Straight` | `straight-cut`, `straight cut`, `straight silhouette`, `straight skirt` |
| `A-Line` | `a-line`, `a line`, `fit-and-flare`, `fit and flare` |
| `Other` | Brak — rozstrzyga LLM |

### `skirt_type`

| Wartość | Keywordy |
| --- | --- |
| `Pleated` | `pleated skirt`, `pleated construction`, `pleated throughout`, `accordion pleats`, `accordion pleated`, `knife pleats`, `knife-pleated`, `box pleats`, `box-pleated`, `sunray pleats`, `sunray-pleated` |
| `Wrap` | `wrap skirt`, `wrap-front skirt`, `wrap-style skirt`, `wrap front`, `wrap-front construction`, `wrap construction` |
| `Asymmetric` | `asymmetric skirt`, `asymmetrical skirt`, `asymmetric hem`, `asymmetrical hem`, `asymmetric hemline`, `asymmetrical hemline`, `asymmetric construction`, `asymmetrical construction`, `high-low hem`, `handkerchief hem` |
| `Tiered` | `tiered skirt`, `tiered construction`, `tiered design`, `tiered hem` |
| `Ruffled` | `ruffled skirt`, `ruffled construction`, `ruffled hem`, `ruffle hem`, `ruffled trim`, `ruffle trim`, `frilled skirt`, `frilled hem`, `frilled trim`, `flounced skirt`, `flounced hem`, `flounce hem` |
| `Other` | Brak — rozstrzyga LLM |

### `rise`

| Wartość | Keywordy |
| --- | --- |
| `High-Rise` | `high-rise`, `high rise`, `high-waisted`, `high waisted`, `high-waist`, `high waist` |
| `Mid-Rise` | `mid-rise`, `mid rise`, `medium rise`, `regular rise` |
| `Low-Rise` | `low-rise`, `low rise`, `low-waisted`, `low waisted`, `low-waist`, `low waist` |
