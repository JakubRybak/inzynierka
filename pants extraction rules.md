# Reguły ekstrakcji cech Pants

<!-- extraction-statistics-note -->
Statystyki dla **9,944 Pants** (train + validation): Trousers 3,916, Jeans 3,704, Sweatpants & Lounge Pants 2,136, Cargo Pants 188. Każdy procent liczony jest względem wszystkich tych produktów, a dla `distressing` – względem 3,704 Jeans. „Przypisane” oznacza wynik zgodny z regułami, nie ręcznie potwierdzoną poprawność.
<!-- /extraction-statistics-note -->

Wszystkie cechy dotyczą 4 kategorii (Trousers, Cargo Pants, Sweatpants & Lounge Pants, Jeans), `distressing` – tylko Jeans. Wszystkie cechy są single choice, poza `colors` (1–2 kolory albo Multicolor).

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
| Przypisane | 9,944 | 100,00% |
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
| Przypisane | 9,885 | 99,41% |
| `undefined` | 59 | 0,59% |
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
| Przypisane | 9,036 | 90,87% |
| `undefined` | 0 | 0,00% |
| `unparsed_composition` | 347 | 3,49% |
| `ambiguous_main_section` | 294 | 2,96% |
| `unmapped_material` | 93 | 0,94% |
| `sum_not_100` | 174 | 1,75% |
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
| Przypisane | 738 | 7,42% |
| `undefined` | 9,206 | 92,58% |
<!-- /results -->

## 5. `fit`

```text
Kolumna `description` – fraza „<krój>-fit” / „<krój> fit” (np. „Slim-fit jeans”)
├─ dokładnie 1 wartość  → wykryta wartość
├─ ≥ 2 różne wartości   → undefined
└─ brak frazy → kolumny `name` i `description`
   ├─ liczba wartości = 1 → wykryta wartość
   └─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

Fraza z opisu ma pierwszeństwo przed nazwą: nazwa „Skinny Jeans” + opis „Slim-fit …” → `Slim`.

<!-- results:fit -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 6,955 | 69,94% |
| `undefined` | 2,989 | 30,06% |
<!-- /results -->

## 6. `leg_shape`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

Przy ≥ 2 wartościach nie dajemy `Other`, bo `Other` to osobny fason (sarouel, harem, drop-crotch).

<!-- results:leg_shape -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,716 | 27,31% |
| `undefined` | 7,228 | 72,69% |
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
| Przypisane | 1,419 | 14,27% |
| `undefined` | 8,525 | 85,73% |
<!-- /results -->

## 8. `rise`

```text
Kolumny `name` i `description`
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

<!-- results:rise -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,972 | 29,89% |
| `undefined` | 6,972 | 70,11% |
<!-- /results -->

## 9. `waistband_type`

```text
Kolumna `description`
├─ zdanie o pasie (waist / waistband) z keywordem Elasticized → Elasticized
├─ keyword Other                                              → Other
├─ keyword Structured                                         → Structured
├─ zdanie o pasie z „partially elasticized”                   → Elasticized
└─ else                                                       → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

Kolejność ma znaczenie: spodnie dresowe z gumką często mają też `zip-fly` / `button-fly`, więc Elasticized jest sprawdzane przed Structured. „Partially elasticized waistband” przy szlufkach lub rozporku → Structured.

<!-- results:waistband_type -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 9,246 | 92,98% |
| `undefined` | 698 | 7,02% |
<!-- /results -->

## 10. `cuff_style`

```text
Kolumna `description` – zdania z cuff / cuffs / hem / hems (bez zdań o kieszeniach)
├─ keyword Zippered Cuff    → Zippered Cuff
├─ keyword Elasticized Cuff → Elasticized Cuff
├─ keyword Other            → Other
├─ keyword Open Hem         → Open Hem
└─ else                     → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

Kolejność ma znaczenie: „zippered vent at elasticized cuffs” → Zippered Cuff, „buttoned vent at cuffs” → Other. `zip-fly` / `button-fly` w zdaniu nie liczy się jako zamek przy nogawce.

<!-- results:cuff_style -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 3,371 | 33,90% |
| `undefined` | 6,573 | 66,10% |
<!-- /results -->

## 11. `distressing`

```text
Kolumny `name` i `description` (tylko Jeans)
├─ keyword Distressed → Distressed
├─ keyword Faded      → Faded
├─ keyword Clean      → Clean
└─ else              → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

Kolejność ma znaczenie: „fading and distressing throughout” → Distressed.

<!-- results:distressing -->
| Wynik | Produkty | % |
| --- | ---: | ---: |
| Przypisane | 2,592 | 69,98% |
| `undefined` | 1,112 | 30,02% |
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

### `fit`

Fraza w opisie: `skinny-fit`, `slim-fit`, `regular-fit` / `classic fit` / `standard fit` (→ Regular), `relaxed-fit` / `loose-fit` / `oversized fit` / `boyfriend fit` / `baggy fit` (→ Relaxed). Gdy jej nie ma – keywordy z tabeli w nazwie i opisie:

| Wartość | Keywordy |
| --- | --- |
| `Skinny` | `skinny`, `skinny-fit`, `super skinny` |
| `Slim` | `slim`, `slim-fit`, `slim-cut` |
| `Regular` | `regular fit`, `regular-fit`, `classic fit`, `standard fit` |
| `Relaxed` | `relaxed`, `relaxed-fit`, `loose`, `loose-fit`, `loose-fitting`, `baggy`, `oversized`, `oversize`, `boyfriend`, `slouchy` |

### `leg_shape`

| Wartość | Keywordy |
| --- | --- |
| `Straight` | `straight-leg`, `straight leg`, `straight-fit`, `straight fit`, `straight-cut`, `straight jeans`, `straight trousers`, `straight pants` |
| `Tapered` | `tapered`, `tapering`, `carrot`, `jogger`, `joggers` |
| `Wide-Leg` | `wide-leg`, `wide leg`, `wide trousers`, `wide jeans`, `wide pants`, `wide lounge pants`, `palazzo`, `culotte`, `culottes` |
| `Flared` | `flared`, `flare`, `bootcut`, `boot-cut`, `bell-bottom`, `bell-bottoms` |
| `Other` | `sarouel`, `harem`, `drop-crotch`, `drop crotch`, `dropped crotch`, `balloon`, `jodhpur`, `jodhpurs` |

### `length`

| Wartość | Keywordy |
| --- | --- |
| `Cropped` | `cropped`, `crop`, `capri`, `capris`, `three-quarter`, `7/8`, `ankle-grazing`, `ankle grazing`, `above ankle`, `culotte`, `culottes` |
| `Full-Length` | `full-length leg`, `floor-length`, `floor length`, `extra-long`, `long jeans`, `long trousers`, `long pants` |

### `rise`

| Wartość | Keywordy |
| --- | --- |
| `High-Rise` | `high-rise`, `high rise`, `high-waisted`, `high waisted`, `high-waist`, `high waist` |
| `Mid-Rise` | `mid-rise`, `mid rise`, `medium rise`, `regular rise` |
| `Low-Rise` | `low-rise`, `low rise`, `low-waisted`, `low waisted`, `low-waist`, `low waist` |

### `waistband_type`

Elasticized: przymiotnik (`elasticized`, `elasticised`, `elastic`, `rib knit`, `ribbed`, `ribbed knit`) najwyżej 2 słowa przed `waist` / `waistband` (np. `elasticized cotton poplin waistband`) albo `drawstring`, `bungee`, `pull-on` w zdaniu o pasie. Samo `ribbed` gdzieś w zdaniu nie wystarcza („ribbed panelling at knees and back waistband”).

| Wartość | Keywordy |
| --- | --- |
| `Elasticized` | `elasticized waistband`, `elasticised waistband`, `elastic waistband`, `elasticized waist`, `rib knit waistband`, `ribbed waistband`, `ribbed knit waistband`, `drawstring`, `bungee`, `pull-on` |
| `Other` | `paperbag`, `paper bag`, `tie-waist`, `tie waist`, `wrap waist` |
| `Structured` | `zip-fly`, `zip fly`, `button-fly`, `button fly`, `belt loop`, `belt loops`, `hook-and-eye`, `hook and eye`, `hook-and-bar`, `hook and bar` |

### `cuff_style`

Słowa szukane w zdaniach o nogawce (cuff / cuffs / hem / hems), bez zdań o kieszeniach.

| Wartość | Keywordy |
| --- | --- |
| `Zippered Cuff` | `zip`, `zips`, `zipper`, `zippered` |
| `Elasticized Cuff` | `elasticized`, `elasticised`, `elastic`, `rib knit`, `rib-knit`, `ribbed`, `drawstring`, `bungee`, `cinched`, `gathered` |
| `Other` | `velcro`, `press-stud`, `press-studs`, `snap`, `snaps`, `button`, `buttoned`, `tab`, `stirrup`, `stirrups`, `strap`, `straps` |
| `Open Hem` | `raw edge`, `raw-edge`, `unfinished`, `rolled`, `serged`, `vent`, `vented`, `frayed`, `slit`, `slits`, `split`, `cuffed`, `turn-up`, `turn-ups` |

### `distressing`

| Wartość | Keywordy |
| --- | --- |
| `Distressed` | `distressed`, `distressing`, `ripped`, `rips`, `torn`, `destroyed`, `shredded`, `shredding`, `slashed`, `slashes`, `abrasion`, `abrasions` |
| `Faded` | `fading`, `faded`, `whiskering`, `whiskered`, `stonewashed`, `stone-washed`, `acid wash`, `acid-wash`, `bleached`, `bleaching`, `honeycombing`, `vintage wash` |
| `Clean` | `raw denim`, `unwashed`, `rinse`, `rinsed`, `dry denim` |