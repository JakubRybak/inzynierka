# Mapowanie materiałów (`input_composition` -> `main_composition`)

Dokument definiuje ujednoliconą listę **13 kanonicznych materiałów** używanych w cesze `main_composition` we wszystkich 23 kategoriach odzieżowych oraz reguły mapowania surowych nazw włókien z kolumny `input_composition` w zbiorze Fashion-Gen.

---

## 1. Tabela mapowania surowców

| # | Wartość docelowa (`main_composition`) | Pokrycie w zbiorze (`input_composition`) | Surowe tokeny z `input_composition` mapowane do tej wartości (w tym synonimy i literówki z danych SSENSE) |
| :-: | :--- | :---: | :--- |
| 1 | **`Cotton`** | ~66.2% (35 703 szt.) | `cotton`, `coton`, `cototn` |
| 2 | **`Polyester`** | ~22.9% (12 350 szt.) | `polyester`, `poylester`, `polyurethane`, `polyethylene`, `polypropylene`, `pvc`, `polyvinyl chloride` |
| 3 | **`Acrylic`** | ~2.2% (1 455 szt.) | `acrylic`, `modacrylic`, `polyacrylic` |
| 4 | **`Wool`** | ~19.5% (10 500 szt.) | `wool`, `virgin wool`, `merino`, `lambswool`, `fleecewool`, `mohair`, `alpaca`, `angora`, `camel`, `yak` |
| 5 | **`Viscose`** | ~18.2% (9 800 szt.) | `viscose`, `cupro`, `cupra`, `bemberg`, `rayon`, `acetate`, `triacetate`, `modal`, `micromodal`, `lyocell`, `tencel`, `bamboo` |
| 6 | **`Elastane`** | ~16.9% (9 100 szt.) | `elastane`, `elastodiene`, `elastomultiester`, `spandex`, `lycra` |
| 7 | **`Nylon`** | ~16.5% (8 900 szt.) | `nylon`, `polyamide`, `polyamid`, `polyamide-nylon` |
| 8 | **`Silk`** | ~6.9% (3 742 szt.) | `silk` |
| 9 | **`Leather`** | ~5.1% (2 750 szt.) | `leather`, `lambskin`, `calfskin`, `goatskin`, `cowhide`, `deerskin`, `pigskin`, `horsehide`, `sheepskin`, `suede`, `nubuck`, `calf`, `lamb`, `goat`, `cow`, `buffalo`, `bull` |
| 10 | **`Cashmere`** | ~3.0% (1 606 szt.) | `cashmere` |
| 11 | **`Linen`** | ~2.3% (1 250 szt.) | `linen`, `flax`, `ramie`, `hemp` |
| 12 | **`Down`** | ~1.0% (510 szt.) | `down`, `feather`, `feathers` |
| 13 | **`Fur`** | ~0.6% (316 szt.) | `fur`, `shearling`, `faux fur` |

---

## 2. Zasady ekstrakcji `main_composition`

- Jeden skład głównej części ubrania z procentami sumującymi się do 100%. W `Jackets & Coats` jest to główna część zewnętrzna.
- Nazwy sekcji (`Body`, `Shell`, `Main`, `Outer` itd.) są wskazówkami. Nie wybieramy automatycznie pierwszej części; brak dwukropka również nie gwarantuje jednego składu.
- Nie dodajemy materiałów podszewki, wypełnienia i wykończeń do składu głównego. Dotyczy to również puchu i futra z dodatkowych części okryć wierzchnich. Futro lub skóra będące głównym materiałem zewnętrznym pozostają w składzie głównym.
- Udziały surowców mapowanych do tej samej wartości kanonicznej sumujemy.
- Nie zgadujemy brakujących procentów, nie normalizujemy błędnych sum ani nie uśredniamy składów różnych części bez informacji o ich udziałach.
- `full_composition_text` nie jest cechą docelową.
- Nazwy tkanin i wykończeń, takie jak denim, satin, corduroy, velvet, lace, jersey, fleece czy mesh, nie są samodzielnymi surowcami w `main_composition`.

## Mapowanie materiałów podszewki (`lining`)

Surowe materiały `cupro` i `acetate` mapujemy do `Viscose`, tak samo jak w `main_composition`. Ich udziały procentowe sumujemy z pozostałymi udziałami mapowanymi do `Viscose`.
