# `colors`

Przed wyszukiwaniem keywordów maskujemy w `name` wszystkie wystąpienia pełnej nazwy marki z kolumny `brand` danego produktu. Dopasowanie ignoruje wielkość liter i różnice między myślnikami a spacjami. Przy pustym `brand` nie maskujemy niczego.

```text
Kolumna `name`
├─ wykryto Multicolor → [Multicolor]
├─ liczba kolorów > 2 → [Multicolor]
├─ liczba kolorów = 2 → [kolor₁, kolor₂]
├─ liczba kolorów = 1 → [kolor]
└─ else              → undefined
```

**Dalsze postępowanie:** `undefined` → ekstrakcja tej cechy przez LLM.

## Keywordy

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
