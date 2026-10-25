# Reguły ekstrakcji cech T-shirts

Statystyki dla **8 961 T-shirts** (train + validation). „Przypisane” oznacza zgodność z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8,961 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8,893 | 99,24% |
| `undefined` | 68 | 0,76% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8,635 | 96,36% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 164 | 1,83% |
| `ambiguous_main_section` | 85 | 0,95% |
| `unmapped_material` | 15 | 0,17% |
| `sum_not_100` | 62 | 0,69% |
<!-- /results -->

## `pattern`

Reguły i keywordy: [common/pattern.md](../common/pattern.md).

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,346 | 15,02% |
| `undefined` | 7,615 | 84,98% |
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
| Przypisane | 8,507 | 94,93% |
| `undefined` | 454 | 5,07% |
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
| Przypisane | 551 | 6,15% |
| `undefined` | 8,410 | 93,85% |
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
| Przypisane | 39 | 0,44% |
| `undefined` | 8,922 | 99,56% |
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
| Przypisane | 8,517 | 95,05% |
| `undefined` | 444 | 4,95% |
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
| `Slim` | `slim fit`, `slim-fit`, `slim-fitting`, `fitted t-shirt`, `fitted tee`, `close-fitting`, `form-fitting`, `body-hugging` |
| `Regular` | `regular fit`, `regular-fit`, `standard fit`, `classic fit` |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fitting`, `oversized`, `oversize`, `boxy fit`, `boxy-fit` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped t-shirt`, `cropped tee`, `cropped fit`, `cropped length`, `crop top` |
| `Regular` | `regular length`, `standard length` |
| `Longline` | `longline`, `long-line`, `long length`, `elongated body`, `extended length`, `extended-length` |

### `sleeve_length`

| Wartość | Keywordy |
| --- | --- |
| `Short Sleeve` | `short sleeve`, `short sleeves`, `short-sleeved` |
| `Long Sleeve` | `long sleeve`, `long sleeves`, `long-sleeved` |
