# Mapowanie kolorów (`colors`) oraz obsługa wielokolorowości

Dokument definiuje ujednoliconą paletę **14 bazowych kolorów** używanych w cesze `colors` we wszystkich 22 kategoriach odzieżowych, zasady mapowania rzadkich i opisowych odcieni ze zbioru Fashion-Gen (`input_name` oraz `input_description`) oraz architekturę obsługi ubrań jedno-, dwu- i wielokolorowych.

---

## 1. Tabela mapowania 14 kolorów bazowych

Każda z 22 kategorii posiada dokładnie tę samą listę 14 wartości w cesze `colors`, co gwarantuje pełną spójność schematu i pozwala modelowi (Guided Decoding) zmapować dowolne zapytanie użytkownika o kolor w każdej kategorii.

| # | Kolor bazowy (`colors`) | Odcienie i synonimy ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- |
| 1 | **`Black`** | `black`, `jet black`, `ebony`, `onyx`, `pitch black`, `washed black`, `faded black`, `coal` |
| 2 | **`White`** | `white`, `off-white`, `ivory`, `cream`, `ecru`, `bone`, `alabaster`, `milk`, `pearl`, `chalk`, `eggshell`, `natural`, `optic white` |
| 3 | **`Grey`** | `grey`, `gray`, `charcoal`, `heather grey`, `marled grey`, `slate`, `ash`, `silver`, `metallic silver`, `gunmetal`, `graphite`, `anthracite`, `pewter`, `stone`, `smoke`, `cement`, `dove grey` |
| 4 | **`Navy`** | `navy`, `navy blue`, `midnight blue`, `dark navy`, `marine`, `ink`, `deep indigo`, `dark indigo` |
| 5 | **`Blue`** | `blue`, `light blue`, `sky blue`, `baby blue`, `powder blue`, `royal blue`, `cobalt`, `indigo`, `denim blue`, `medium blue`, `teal`, `turquoise`, `aqua`, `cyan`, `cerulean`, `periwinkle`, `cornflower`, `petrol`, `slate blue`, `ice blue` |
| 6 | **`Red`** | `red`, `burgundy`, `maroon`, `wine`, `bordeaux`, `crimson`, `scarlet`, `cherry`, `ruby`, `oxblood`, `garnet`, `brick red`, `vermilion`, `cardinal`, `claret`, `berry` |
| 7 | **`Green`** | `green`, `olive`, `army green`, `khaki green`, `military green`, `forest green`, `emerald`, `mint`, `sage`, `lime`, `hunter green`, `jade`, `moss`, `pine`, `khaki` *(gdy występuje w kontekście zieleni militarnej)*, `chartreuse`, `pistachio`, `seafoam`, `kelly green`, `bottle green` |
| 8 | **`Pink`** | `pink`, `blush`, `rose`, `magenta`, `fuchsia`, `salmon`, `coral pink`, `dusty pink`, `pastel pink`, `hot pink`, `bubblegum`, `peony`, `flamingo`, `mauve`, `raspberry`, `carnation`, `nude pink`, `millennial pink` |
| 9 | **`Beige`** | `beige`, `tan`, `camel`, `sand`, `taupe`, `oatmeal`, `champagne`, `fawn`, `buff`, `nude`, `wheat`, `biscuit`, `stone beige`, `khaki` *(w kontekście jasnych spodni/chino/trenczy)*, `latte`, `putty`, `parchment`, `sahara` |
| 10 | **`Brown`** | `brown`, `chocolate`, `cognac`, `espresso`, `chestnut`, `mahogany`, `rust`, `terracotta`, `bronze`, `copper`, `cinnamon`, `caramel`, `toffee`, `mocha`, `umber`, `sienna`, `walnut`, `sepia`, `tobacco`, `hazel`, `cocoa`, `tortoiseshell` |
| 11 | **`Yellow`** | `yellow`, `mustard`, `gold`, `metallic gold`, `lemon`, `canary`, `ochre`, `saffron`, `amber`, `honey`, `butter`, `marigold`, `citrine`, `daffodil`, `sunflower`, `banan` |
| 12 | **`Orange`** | `orange`, `coral`, `peach`, `tangerine`, `apricot`, `burnt orange`, `papaya`, `mandarin`, `pumpkin`, `mango`, `persimmon`, `neon orange`, `clementine` |
| 13 | **`Purple`** | `purple`, `violet`, `lavender`, `lilac`, `plum`, `eggplant`, `aubergine`, `amethyst`, `orchid`, `mulberry`, `grape`, `periwinkle purple`, `indigo purple`, `heliotrope`, `wisteria` |
| 14 | **`Multicolor`** | `multicolor`, `multicolored`, `multi`, `rainbow`, `tie-dye` *(wielobarwny)*, oraz automatycznie każdy produkt posiadający **$\ge 3$ kolory bazowe** |

> [!NOTE]
> **Uwaga dotycząca odcienia `Off-White / Cream / Ecru` vs `Beige`:**
> W opisach SSENSE określenia `off-white`, `ivory`, `cream`, `ecru` są używane dla złamanej bieli (np. koszule, t-shirty, sukienki) i mapujemy je do **`White`**, natomiast typowo ziemiste/piaskowe tony (`beige`, `tan`, `camel`, `sand`, `taupe`) mapujemy do **`Beige`**.
> Z kolei kolory metaliczne są przypisane do swoich naturalnych odpowiedników: `silver` / `gunmetal` $\rightarrow$ **`Grey`**, `gold` / `brass` $\rightarrow$ **`Yellow`**, `bronze` / `copper` $\rightarrow$ **`Brown`**.

---

## 2. Architektura wielokolorowości (1 kolor, 2 kolory, $\ge 3$ kolory)

Cecha `colors` dla każdego produktu w bazie jest przechowywana jako **lista (tablica) wartości** z powyższego słownika 14 kolorów, bez sztucznego dzielenia na `main_color` i `secondary_color`.

### Reguły indeksowania produktów (w bazie danych):

1. **Produkt jednokolorowy (1 kolor):**
   * Produkt ma dokładnie 1 kolor w tablicy `colors`.
   * *Przykład:* Czarna koszulka $\rightarrow$ `colors = ["Black"]`
   * *Przykład:* Koszulka z drobnym białym logo, ale opisana jako jednolicie czarna $\rightarrow$ `colors = ["Black"]` (chyba że stanowi wyraźny układ dwukolorowy).

2. **Produkt dwukolorowy / Bicolor (2 kolory):**
   * Jeśli produkt składa się z **dwóch wyraźnych kolorów** (np. biało-granatowe paski, czarno-czerwona krata, kurtka colorblock z dwóch kolorów, dwukolorowy wzór), zapisujemy oba kolory w tablicy `colors`.
   * *Przykład:* Biało-czarna koszulka w paski $\rightarrow$ `colors = ["Black", "White"]`
   * *(Opcjonalnie na poziomie rekordu w bazie możemy wyliczyć flagę pomocniczą `color_count = len(colors)` lub `is_bicolor = (len(colors) == 2)`).*

3. **Produkt wielokolorowy ($\ge 3$ kolory $\rightarrow$ `Multicolor`):**
   * Jeśli produkt posiada **3 lub więcej kolorów** (np. wielobarwny nadruk graficzny, kolorowy wzór kwiatowy, tęczowe paski, wielokolorowa krata) lub jest wprost opisany w Fashion-Gen jako `multicolor`, nie wypisujemy poszczególnych składowych kolorów – przypisujemy mu pojedynczą wartość **`Multicolor`**.
   * *Przykład:* Sukienka w czerwono-zielono-żółte kwiaty na białym tle $\rightarrow$ `colors = ["Multicolor"]`

---

## 3. Reguły wyszukiwania i dopasowania (Query Matching)

Dzięki przechowywaniu kolorów w jednej spójnej tablicy `colors` obsługujemy wszystkie scenariusze zapytań użytkownika w sposób intuicyjny i odporny na błędy:

| Scenariusz zapytania użytkownika | Wyekstrahowany filtr z LLM | Działanie wyszukiwarki (filtrowanie i ranking) |
| :--- | :--- | :--- |
| **1. Użytkownik podaje 1 kolor** *(np. "black t-shirt")* | `colors contains "Black"` | Zwracamy wszystkie produkty, które mają `"Black"` w tablicy `colors` (zarówno `["Black"]`, jak i dwukolorowe `["Black", "White"]`).<br>**Ranking:** Produkty jednokolorowe (`len(colors) == 1`, czyli czysto czarne `["Black"]`) mogą otrzymać wyższy priorytet (boost) niż produkty dwukolorowe (`len(colors) == 2`), chyba że użytkownik poprosił jednocześnie o wzór dwukolorowy (np. `"black striped t-shirt"`). |
| **2. Użytkownik podaje 2 kolory** *(np. "black and white striped shirt")* | `colors contains ALL ["Black", "White"]` | Zwracamy produkty dwukolorowe, których tablica `colors` zawiera jednocześnie `"Black"` oraz `"White"`. |
| **3. Użytkownik szuka rzeczy wielokolorowej** *(np. "colorful dress" / "multicolor hoodie")* | `colors contains "Multicolor"` | Zwracamy produkty posiadające wartość `["Multicolor"]`. |
