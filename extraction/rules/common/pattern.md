# `pattern`

```text
Kolumny `name` i `description`
├─ liczba wartości ≥ 2 → Other
├─ liczba wartości = 1 → wykryta wartość
└─ else               → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

## Keywordy

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
