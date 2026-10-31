# Reguły ekstrakcji cech Shirts

Statystyki dla **4,339 Shirts** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4,339 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4,302 | 99,15% |
| `undefined` | 37 | 0,85% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4,192 | 96,61% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 21 | 0,48% |
| `ambiguous_main_section` | 77 | 1,77% |
| `unmapped_material` | 20 | 0,46% |
| `sum_not_100` | 29 | 0,67% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 4,339 | 100,00% |
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
| Przypisane | 4,241 | 97,74% |
| `undefined` | 98 | 2,26% |
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
| Przypisane | 275 | 6,34% |
| `undefined` | 4,064 | 93,66% |
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
| Przypisane | 94 | 2,17% |
| `undefined` | 4,245 | 97,83% |
<!-- /results -->

## `collar_type`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:collar_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 4,173 | 96,17% |
| `undefined` | 166 | 3,83% |
<!-- /results -->

## Keywordy

### `sleeve_length`

| Wartość | Keywordy |
| --- | --- |
| `Sleeveless` | `sleeveless` |
| `Short Sleeve` | `short sleeve`, `short sleeves`, `short-sleeved`, `short-sleeve`, `cap sleeve`, `cap sleeves`, `cap-sleeve` |
| `Three-Quarter Sleeve` | `three-quarter sleeve`, `three-quarter sleeves`, `three-quarter-sleeve`, `three quarter sleeve`, `three quarter sleeves`, `3/4 sleeve`, `3/4 sleeves`, `cropped sleeve`, `cropped sleeves`, `cropped-sleeve` |
| `Long Sleeve` | `long sleeve`, `long sleeves`, `long-sleeved`, `long-sleeve` |

### `fit`

| Wartość | Keywordy |
| --- | --- |
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `close-fitting`, `form-fitting`, `body-hugging`, `fitted shirt`, `fitted blouse` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `oversized`, `oversize`, `boxy`, `boxy fit`, `boxy-fit`; `oversized`, `oversize`, `boxy` nie uwzględniamy, gdy zaraz po nich stoi część ubrania: `lapel(s)`, `collar(s)`, `pull-tab(s)`, `hood(s)`, `zip(s)`, `zipper(s)`, `pocket(s)`, `button(s)`, `patch(es)`, `cuff(s)`, `logo(s)`, `buckle(s)`, `hardware`, `tab(s)`, `sleeves`, `shoulders`, `hem` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped shirt`, `cropped blouse`, `cropped top`, `crop top`, `cropped fit`, `cropped length` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated body`, `extended length`, `extended-length`, `tunic`, `overlong fit`, `overlong shirt`, `overlong blouse`; `tunic` nie uwzględniamy we frazie `tunic collar` |

### `collar_type`

| Wartość | Keywordy |
| --- | --- |
| `Point Collar` | `spread collar`, `point collar`, `pointed collar`, `button-down collar`, `button down collar`, `classic collar`, `cutaway collar`, `shirt collar`; nie uwzględniamy dopasowania we frazie `open spread collar` |
| `Camp Collar` | `camp collar`, `cuban collar`, `revere collar`, `resort collar`, `notched lapel collar`, `open spread collar` |
| `Stand Collar` | `stand collar`, `stand-up collar`, `band collar`, `mandarin collar`, `tunic collar`, `funnel collar`, `funnel neck`, `mock neck`, `mock-neck`, `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck` |
| `Collarless` | `collarless`, `crewneck`, `crew neck`, `crew-neck`, `v-neck`, `v neck`, `y-neck`, `scoop neck` |
| `Other` | `wing collar`, `wingtip collar`, `tuxedo collar`, `peter pan collar`, `shawl collar`, `sailor collar` |
