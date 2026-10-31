# Reguły ekstrakcji cech Blouses

Statystyki dla **1,002 Blouses** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,002 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 983 | 98,10% |
| `undefined` | 19 | 1,90% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 919 | 91,72% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 15 | 1,50% |
| `ambiguous_main_section` | 53 | 5,29% |
| `unmapped_material` | 6 | 0,60% |
| `sum_not_100` | 9 | 0,90% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 1 002 | 100,00% |
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
| Przypisane | 920 | 91,82% |
| `undefined` | 82 | 8,18% |
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
| Przypisane | 114 | 11,38% |
| `undefined` | 888 | 88,62% |
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
| Przypisane | 59 | 5,89% |
| `undefined` | 943 | 94,11% |
<!-- /results -->

## `neckline`

```text
Kolumny `name` i `description`
├─ liczba wartości ≥ 2 → Other
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:neckline -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 930 | 92,81% |
| `undefined` | 72 | 7,19% |
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

### `neckline`

| Wartość | Keywordy |
| --- | --- |
| `Crewneck` | `crewneck`, `crew neck`, `crew-neck`, `round neck`, `round-neck` |
| `Scoop Neck` | `scoop neck`, `scoop-neck`, `scoop neckline`, `scoopneck` |
| `V-Neck` | `v-neck`, `v neck`, `v-neckline`, `y-neck` |
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Collared` | `spread collar`, `point collar`, `pointed collar`, `button-down collar`, `classic collar`, `shirt collar`, `band collar`, `stand collar`, `stand-up collar`, `mandarin collar`, `tunic collar`, `camp collar`, `convertible collar`, `notched collar`, `lapel collar`, `notched lapel collar`, `shawl collar`, `shawl lapel collar`, `peter pan collar`, `tuxedo collar`, `sailor collar`, `wing collar` |
| `Other` | `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline`, `boatneck`, `cowl-neck`, `henley collar`, `off shoulder`, `off-shoulder`, `off the shoulder`, `off-the-shoulder`, `one shoulder`, `one-shoulder`, `single shoulder`, `single-shoulder`, `strapless`, `halter`, `halterneck`, `halter neck`, `halter-neck` |
