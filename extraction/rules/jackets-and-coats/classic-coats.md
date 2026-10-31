# Reguły ekstrakcji cech Classic Coats

Statystyki dla **2,198 Classic Coats** (train + validation). „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.

## `gender`

Reguły i keywordy: [common/gender.md](../common/gender.md).

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,198 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## `colors`

Reguły i keywordy: [common/colors.md](../common/colors.md).

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,164 | 98,45% |
| `undefined` | 34 | 1,55% |
<!-- /results -->

## `main_composition`

Reguły i keywordy: [common/main_composition.md](../common/main_composition.md).

<!-- results:main_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,652 | 75,16% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 52 | 2,37% |
| `ambiguous_main_section` | 409 | 18,61% |
| `unmapped_material` | 53 | 2,41% |
| `sum_not_100` | 32 | 1,46% |
<!-- /results -->

## `pattern`

Reguły: [common/pattern.md](../common/pattern.md). Cecha przypisywana wyłącznie przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2 198 | 100,00% |
<!-- /results -->

## `lining_composition`

```text
Kolumna `composition` – sekcje Lining, Body lining, Lining N
├─ ≥ 2 sekcje → Unknown
├─ 1 sekcja   → parsuj jak main_composition
│  ├─ poprawny skład → zapisz skład
│  └─ else          → Unknown
└─ brak sekcji → kolumna `description`
   ├─ keyword Unlined → Unlined
   └─ else           → Unknown
```

**Dalsze postępowanie:** `Unknown` → wartość końcowa, bez ekstrakcji przez LLM.

<!-- results:lining_composition -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,331 | 60,56% |
| `Unknown` | 867 | 39,44% |
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
| Przypisane | 635 | 28,89% |
| `undefined` | 1,563 | 71,11% |
<!-- /results -->

## `coat_style`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else                → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:coat_style -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 901 | 40,99% |
| `undefined` | 1,297 | 59,01% |
<!-- /results -->

## `closure_type`

Cecha przypisywana wyłącznie przez LLM.

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:closure_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2,198 | 100,00% |
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
| Przypisane | 1,652 | 75,16% |
| `undefined` | 546 | 24,84% |
<!-- /results -->

## `insulation`

```text
Kolumny `name`, `description` i `composition`
├─ liczba wartości = 1 → wykryta wartość
└─ else                → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:insulation -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 699 | 31,80% |
| `undefined` | 1,499 | 68,20% |
<!-- /results -->

## `length`

Cecha przypisywana wyłącznie przez LLM (zdjęcie).

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM (zdjęcie).

<!-- results:length -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 0 | 0,00% |
| `undefined` | 2,198 | 100,00% |
<!-- /results -->

## `fit`

```text
Kolumny `name` i `description`
├─ keyword Oversized → Oversized
└─ else             → Regular
```

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,198 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## Keywordy

### `lining_composition`

Materiały jak w [common/main_composition.md](../common/main_composition.md).

| Wartość | Keywordy |
| --- | --- |
| `Unlined` | `unlined` |
| `Unknown` | Bez keywordów. |

### `hood`

| Wartość | Keywordy |
| --- | --- |
| `With Hood` | `hood`, `hoods`, `hooded`, `hoodie` |
| `Without Hood` | Brak — rozstrzyga LLM. |

### `coat_style`

| Wartość | Keywordy |
| --- | --- |
| `Parka` | `parka`, `parkas` |
| `Other` | `raincoat`, `rain coat`, `rain jacket`, `mac coat`, `mackintosh`, `cape`, `poncho`, `duffle`, `duffel` |
| `Standard` | `overcoat`, `topcoat`, `top coat`, `chesterfield`, `peacoat`, `pea coat`, `car coat`, `classic coat`, `wool coat`, `cashmere coat`, `double-breasted coat` |

### `collar_type`

| Wartość | Keywordy |
| --- | --- |
| `Lapel Collar` | `lapel`, `lapels`, `shawl collar`, `notched collar` |
| `Point Collar` | `spread collar`, `point collar`, `pointed collar`, `button-down collar`, `shirt collar`, `classic collar` |
| `Stand Collar` | `stand collar`, `stand-up collar`, `band collar`, `mandarin collar`, `funnel collar`, `high neck`, `high-neck`, `turtleneck`, `turtle neck`, `roll neck`, `rollneck`, `mock neck`, `mock-neck`, `funnel neck` |
| `Other` | `collarless`, `crewneck`, `crew neck`, `crew-neck`, `v-neck`, `v neck`, `y-neck`, `scoop neck`, `peter pan collar` |

### `insulation`

| Wartość | Keywordy |
| --- | --- |
| `Down` | `down-filled`, `down-fill`, `down-filling`, `goose down`, `duck down`, `quilted down`, `feather`, `feathers`, `down jacket`, `down coat`, `down vest`, `down bomber`, `down parka`, `down gilet`, `down aviator`, `down blouson`, `down puffer` |
| `Shearling Lined` | `shearling-lined`, `shearling lining`, `lined in shearling`, `shearling jacket`, `shearling coat`, `shearling vest`, `shearling bomber`, `shearling parka`, `shearling gilet`, `shearling aviator`, `shearling blouson`; nie uwzględniamy dopasowania we frazie `faux shearling`; nie uwzględniamy dopasowania, gdy zaraz po keywordzie z `lined` / `lining` stoi `at hood`, `at collar`, `hood` albo `collar` (np. `fur-lined hood`) |
| `Fleece Lined` | `fleece-lined`, `fleece lining`, `lined in fleece`, `sherpa-lined`, `sherpa lining`, `teddy-lined`, `teddy lining`, `faux-shearling-lined`, `faux-shearling lining`, `pile-lined`, `pile lining`, `fleece jacket`, `fleece coat`, `fleece vest`, `fleece bomber`, `fleece parka`, `fleece gilet`, `fleece aviator`, `fleece blouson`, `sherpa jacket`, `sherpa coat`, `sherpa vest`, `sherpa bomber`, `sherpa parka`, `sherpa gilet`, `sherpa aviator`, `sherpa blouson`, `faux-shearling jacket`, `faux-shearling coat`, `faux-shearling vest`, `faux-shearling bomber`, `faux-shearling parka`, `faux-shearling gilet`, `faux-shearling aviator`, `faux-shearling blouson`, `pile jacket`, `pile coat`, `pile vest`, `pile bomber`, `pile parka`, `pile gilet`, `pile aviator`, `pile blouson`; nie uwzględniamy dopasowania, gdy zaraz po keywordzie z `lined` / `lining` stoi `at hood`, `at collar`, `hood` albo `collar` (np. `fur-lined hood`) |
| `Other` | `fur-lined`, `fur lining`, `lined in fur`, `lined in faux fur`, `faux-fur-lined`, `faux-fur lining`; nie uwzględniamy dopasowania, gdy zaraz po keywordzie z `lined` / `lining` stoi `at hood`, `at collar`, `hood` albo `collar` (np. `fur-lined hood`) |
| `Synthetic Padding` | `insulated`, `insulation`, `wadding`, `wadded`, `primaloft`, `thinsulate`, `puffer`, `puffy`, `quilted lining`, `padded jacket`, `padded coat`, `padded vest`, `padded bomber`, `padded parka`, `padded gilet`, `padded aviator`, `padded blouson`, `quilted jacket`, `quilted coat`, `quilted vest`, `quilted bomber`, `quilted parka`, `quilted gilet`, `quilted aviator`, `quilted blouson` |
| `Uninsulated` | `unlined`, `unpadded`, `uninsulated`, `non-insulated` |

### `fit`

| Wartość | Keywordy |
| --- | --- |
| `Oversized` | `relaxed fit`, `relaxed-fit`, `loose fit`, `loose-fit`, `loose-fitting`, `oversized`, `oversize`, `boxy`, `boxy fit`, `boxy-fit`, `cocoon`, `slouchy`; `oversized`, `oversize`, `boxy`, `cocoon`, `slouchy` nie uwzględniamy, gdy zaraz po nich stoi część ubrania: `lapel(s)`, `collar(s)`, `pull-tab(s)`, `hood(s)`, `zip(s)`, `zipper(s)`, `pocket(s)`, `button(s)`, `patch(es)`, `cuff(s)`, `logo(s)`, `buckle(s)`, `hardware`, `tab(s)`, `sleeves`, `shoulders`, `hem`; ani we frazach `oversized notched lapel`, `oversized peak lapel`, `oversized hoop pull-tab`, `oversized textile pull-tab`, `oversized spread collar`, `oversized funnel collar`, `slouchy funnel collar`, `oversized resin buckle` |
| `Regular` | Bez keywordów — brak `Oversized`. |
