# Reguły ekstrakcji cech Bodysuits

Statystyki dla **118 Bodysuits** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 118 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 116 | 98,31% |
| `undefined` | 2 | 1,69% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 112 | 94,92% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 4 | 3,39% |
| `ambiguous_main_section` | 1 | 0,85% |
| `unmapped_material` | 0 | 0,00% |
| `sum_not_100` | 1 | 0,85% |
<!-- /results -->

## `pattern`

Reguły i keywordy: [common/pattern.md](../common/pattern.md).

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8 | 6,78% |
| `undefined` | 110 | 93,22% |
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
| Przypisane | 111 | 94,07% |
| `undefined` | 7 | 5,93% |
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
| Przypisane | 96 | 81,36% |
| `undefined` | 22 | 18,64% |
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
| Przypisane | 9 | 7,63% |
| `undefined` | 109 | 92,37% |
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
| Przypisane | 1 | 0,85% |
| `undefined` | 117 | 99,15% |
<!-- /results -->

## Keywordy

### `sleeve_length`

| Wartość | Keywordy |
| --- | --- |
| `Sleeveless` | `sleeveless` |
| `Short Sleeve` | `short sleeve`, `short sleeves`, `short-sleeved` |
| `Long Sleeve` | `long sleeve`, `long sleeves`, `long-sleeved` |

### `neckline`

| Wartość | Keywordy |
| --- | --- |
| `Crewneck` | `crewneck`, `crew neck`, `crew-neck` |
| `Scoop Neck` | `scoop neck`, `scoop-neck`, `scoop neckline` |
| `V-Neck` | `v-neck`, `v neck`, `v-neckline` |
| `High Neck` | `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Other` | `boat neck`, `bateau neck`, `cowl neck`, `square neck`, `sweetheart neckline`, `henley neckline`, `spread collar`, `point collar` |

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
