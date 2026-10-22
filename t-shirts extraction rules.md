# Reguły ekstrakcji cech T-shirts

<!-- extraction-statistics-note -->
Statystyki dla **8,961 T-shirts** (train + validation). Każdy procent liczony jest względem wszystkich tych produktów. „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.
<!-- /extraction-statistics-note -->

## 1. `gender`

```text
Kolumna `gender`
├─ wartość = Men   → Men
├─ wartość = Women → Women
└─ else           → undefined
```

**Dalsze postępowanie:** `undefined` → wykluczenie produktu ze zbioru.

<!-- results:gender -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8,961 | 100,00% |
| `undefined` | 0 | 0,00% |
<!-- /results -->

## 2. `colors`

```text
Kolumna `name`
├─ wykryto Multicolor → [Multicolor]
├─ liczba kolorów > 2 → [Multicolor]
├─ liczba kolorów = 2 → [kolor₁, kolor₂]
├─ liczba kolorów = 1 → [kolor]
└─ else              → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:colors -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 8,893 | 99,24% |
| `undefined` | 68 | 0,76% |
<!-- /results -->

## 3. `main_composition`

```text
Kolumna `composition`
├─ brak wartości                        → undefined
├─ brak nazwanych sekcji                 → parsuj całą wartość
├─ dokładnie jedna sekcja Main albo Body → parsuj wybraną sekcję
└─ else                                 → ambiguous_main_section
```

```text
Wybrany fragment kolumny `composition`
├─ nie można odczytać składników lub procentów → unparsed_composition
├─ materiał bez jednoznacznego mapowania       → unmapped_material
├─ suma udziałów ≠ 100%                        → sum_not_100
└─ else                                       → zapisz skład
```

**Dalsze postępowanie:** `undefined`, `unparsed_composition`, `ambiguous_main_section`, `unmapped_material` lub `sum_not_100` → wykluczenie produktu ze zbioru. Nie ustalamy składu przez LLM.

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

## 4. `pattern`

```text
Kolumny `name` i `description`
├─ liczba wartości ≥ 2 → Other
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:pattern -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 1,346 | 15,02% |
| `undefined` | 7,615 | 84,98% |
<!-- /results -->

## 5. `neckline`

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

## 6. `fit`

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

## 7. `length`

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

## 8. `sleeve_length`

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

### `gender`

Bez keywordów — odczyt wartości `Men` lub `Women` bezpośrednio z kolumny `gender`.

### `colors`

| Wartość | Keywordy |
| --- | --- |
| `Black` | `black` |
| `White` | `white`, `off-white`, `ivory`, `cream`, `ecru` |
| `Grey` | `grey`, `gray`, `charcoal`, `anthracite` |
| `Blue` | `navy`, `navy blue`, `midnight blue`, `blue`, `light blue`, `cobalt`, `indigo`, `turquoise` |
| `Red` | `red`, `burgundy`, `maroon`, `bordeaux`, `crimson`, `scarlet` |
| `Green` | `green`, `olive`, `khaki`, `emerald` |
| `Pink` | `pink`, `fuchsia`, `rose pink` |
| `Beige` | `beige`, `tan`, `sand`, `taupe` |
| `Brown` | `brown`, `chocolate`, `camel` |
| `Yellow` | `yellow`, `mustard` |
| `Orange` | `orange`, `rust` |
| `Purple` | `purple`, `violet`, `lilac`, `lavender`, `mauve` |
| `Multicolor` | `multicolor`, `multicolour`, `multicolored`, `multicoloured`, `multi-color`, `multi-colour` |

### `main_composition`

| Wartość | Keywordy |
| --- | --- |
| `Cotton` | `cotton`, `coton`, `cototn` |
| `Polyester` | `polyester`, `poylester`, `polyurethane`, `polyethylene`, `polypropylene`, `pvc`, `polyvinyl chloride` |
| `Acrylic` | `acrylic`, `modacrylic`, `polyacrylic` |
| `Wool` | `wool`, `merino`, `lambswool`, `fleecewool`, `mohair`, `alpaca`, `angora`, `camel`, `yak` |
| `Viscose` | `viscose`, `rayon`, `cupro`, `cupra`, `bemberg`, `acetate`, `triacetate`, `modal`, `micromodal`, `lyocell`, `tencel`, `bamboo` |
| `Elastane` | `elastane`, `spandex`, `lycra`, `elastodiene`, `elastomultiester` |
| `Nylon` | `nylon`, `polyamide`, `polyamid`, `polyamide-nylon` |
| `Silk` | `silk` |
| `Leather` | `leather`, `suede`, `nubuck`, `lambskin`, `calfskin`, `goatskin`, `cowhide`, `deerskin`, `pigskin`, `horsehide`, `sheepskin`, `calf`, `lamb`, `goat`, `cow`, `buffalo`, `bull` |
| `Cashmere` | `cashmere` |
| `Linen` | `linen`, `flax`, `ramie`, `hemp` |
| `Down` | `down`, `feather`, `feathers` |
| `Fur` | `fur`, `shearling`, `faux fur` |

### `pattern`

| Wartość | Keywordy |
| --- | --- |
| `Solid` | `solid color`, `solid colour`, `solid-colored`, `solid-coloured`, `plain-colored`, `plain-coloured` |
| `Striped` | `striped`, `stripes`, `pinstripe`, `pinstriped`, `breton stripe` |
| `Plaid` | `plaid`, `tartan`, `gingham`, `checkered`, `checked pattern`, `check pattern` |
| `Floral` | `floral`, `flower print`, `flower pattern`, `flower-print` |
| `Camo` | `camouflage`, `camo` |
| `Animal Print` | `animal print`, `leopard print`, `zebra print`, `tiger print`, `snake print`, `snakeskin print`, `cheetah print`, `panther print` |
| `Polka Dot` | `polka dot`, `polka-dot`, `polka dots`, `polka-dotted` |
| `Other` | `paisley`, `tie-dye`, `houndstooth`, `herringbone`, `graphic print`, `logo print`, `geometric print`, `abstract print` |

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
