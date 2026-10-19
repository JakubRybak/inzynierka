# Mapowanie materiałów (`input_composition` -> `main_composition`)

Dokument definiuje ujednoliconą listę **12 kanonicznych materiałów** używanych w cesze `main_composition` we wszystkich 22 kategoriach odzieżowych oraz reguły mapowania surowych nazw włókien z kolumny `input_composition` w zbiorze Fashion-Gen.

---

## 1. Tabela mapowania surowców

| # | Wartość docelowa (`main_composition`) | Pokrycie w zbiorze (`input_composition`) | Surowe tokeny z `input_composition` mapowane do tej wartości (w tym synonimy i literówki z danych SSENSE) |
| :-: | :--- | :---: | :--- |
| 1 | **`Cotton`** | ~66.2% (35 703 szt.) | `cotton`, `coton`, `cototn` |
| 2 | **`Polyester`** | ~22.9% (12 350 szt.) | `polyester`, `poylester`, `acrylic`, `modacrylic`, `polyacrylic`, `polyurethane`, `polyethylene`, `polypropylene`, `pvc`, `polyvinyl chloride` |
| 3 | **`Wool`** | ~19.5% (10 500 szt.) | `wool`, `virgin wool`, `merino`, `lambswool`, `fleecewool`, `mohair`, `alpaca`, `angora`, `camel`, `yak` |
| 4 | **`Viscose`** | ~18.2% (9 800 szt.) | `viscose`, `cupro`, `cupra`, `bemberg`, `rayon`, `acetate`, `triacetate`, `modal`, `micromodal`, `lyocell`, `tencel`, `bamboo` |
| 5 | **`Elastane`** | ~16.9% (9 100 szt.) | `elastane`, `elastodiene`, `elastomultiester`, `spandex`, `lycra` |
| 6 | **`Nylon`** | ~16.5% (8 900 szt.) | `nylon`, `polyamide`, `polyamid` |
| 7 | **`Silk`** | ~6.9% (3 742 szt.) | `silk` |
| 8 | **`Leather`** | ~5.1% (2 750 szt.) | `leather`, `lambskin`, `calfskin`, `goatskin`, `cowhide`, `deerskin`, `pigskin`, `horsehide`, `sheepskin`, `suede`, `nubuck`, `calf`, `lamb`, `goat`, `cow`, `buffalo`, `bull` |
| 9 | **`Cashmere`** | ~3.0% (1 606 szt.) | `cashmere` |
| 10 | **`Linen`** | ~2.3% (1 250 szt.) | `linen`, `flax`, `ramie`, `hemp` |
| 11 | **`Down`** | ~1.0% (510 szt.) | `down`, `feather`, `feathers` |
| 12 | **`Fur`** | ~0.6% (316 szt.) | `fur`, `shearling`, `faux fur` |

---

## 2. Zasady ekstrakcji `main_composition` oraz `full_composition_text`

1. **`main_composition` (lista wielokrotnego wyboru + opcjonalne wagi procentowe):**
   * Wyciągana z **głównej części ubrania** w `input_composition`:
     * Jeśli `input_composition` nie zawiera dwukropka `:` (70% produktów) – parsujemy cały tekst.
     * Jeśli `input_composition` jest podzielone na części z dwukropkiem (np. `Body: ... Lining: ... Trim: ...`) – do `main_composition` bierzemy główną sekcję korpusu (`Body`, `Shell`, `Main`, `Fabric 1`, `Outer` lub pierwszą wymienioną część), a w przypadku okryć wierzchnich (`Jackets & Coats`) uwzględniamy również `Down` z sekcji wypełnienia (`Fill`, `Filling`, `Padding`) oraz `Fur` z kołnierza/podszewki.
   * Zwykłe techniczne podszewki (`Lining`, `Sleeve lining`, `Pocket lining`) oraz drobne wykończenia/ściągacze (`Trim`, `Ribbed trim`) nie zaśmiecają głównego pola `main_composition`.

2. **`full_composition_text` (pełny tekst składu):**
   * Przechowuje oryginalny, pełny zapis z kolumny `input_composition` (wraz z podziałem na wszystkie części ubrania i dokładnymi wartościami procentowymi) na potrzeby interpretowalności wyników oraz kontekstu dla Agenta konwersacyjnego.

3. **Sploty i tekstury tkanin (poza `main_composition`):**
   * Określenia splotu lub wykończenia materiału, które nie są surowcami chemicznymi w `input_composition` (takie jak `denim`, `satin`, `corduroy`, `velvet`, `flannel`, `lace`, `jersey`, `french terry`, `fleece`, `mesh`, `chiffon`, `neoprene`, `sequin`), nie są trzymane w `main_composition` – są obsługiwane przez cechy opisujące styl/fason lub dedykowaną cechę tekstury/tkaniny.
