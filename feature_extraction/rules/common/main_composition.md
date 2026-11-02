# `main_composition`

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

## Keywordy

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
