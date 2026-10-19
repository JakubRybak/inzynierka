# Mapowanie wzorów (`pattern`)

Dokument definiuje ujednoliconą listę **11 kanonicznych wzorów** używanych w cesze `pattern` we wszystkich 22 kategoriach odzieżowych oraz zasady mapowania szczegółowych nazw deseni i nadruków ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Tabela mapowania 11 wzorów bazowych

Każda z 22 kategorii posiada dokładnie tę samą listę 11 wartości w cesze `pattern`, co zapewnia 100% spójności schematu dla modelu LLM (Guided Decoding) i pozwala obsłużyć zapytanie o dowolny wzór w dowolnej kategorii.

| # | Wartość docelowa (`pattern`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Solid`** | `Solid / Plain`, `Solid / Plain (Standard Wash)` | Gładkie, jednolite ubrania bez wzoru (`solid`, `plain`, `monochrome`, `unpatterned`, standardowy gładki jeans bez wzorów) |
| 2 | **`Striped`** | `Striped`, `Striped / Pinstripe`, `Striped / Side-Stripe` | Paski poziome, pionowe, ukośne, prążki garniturowe oraz lampasy (`striped`, `stripes`, `pinstripe`, `chalk stripe`, `side-stripe`, `breton`, `ticking stripe`, `variegated stripe`, `chevron stripe`) |
| 3 | **`Plaid`** | `Plaid / Check`, `Plaid / Check / Argyle`, `Plaid / Check / Houndstooth`, `Plaid / Check / Houndstooth / Herringbone` | Wszystkie rodzaje kraty, szachownicy, pepitki, jodełki i rombów (`plaid`, `check`, `checked`, `checkered`, `tartan`, `gingham`, `houndstooth`, `herringbone`, `argyle`, `windowpane`, `glen plaid`, `prince of wales`, `madras`, `buffalo check`, `tattersall`) |
| 4 | **`Graphic`** | `Graphic / Print`, `Print / Graphic`, `Embroidered / Graphic / Print`, `Paint Splatter / Graphic / Print` | Nadruki graficzne, ilustracje, zdjęcia, napisy (niebędące samym logo marki), hafty obrazkowe, abstrakcyjne i geometryczne printy, ciapki farby (`graphic`, `print`, `printed`, `artwork`, `photo print`, `text print`, `slogan`, `abstract print`, `geometric print`, `paisley`, `bandana print`, `paint splatter`, `splatter`, `star print`, `heart print`, `embroidered graphic`, `patchwork`) |
| 5 | **`Logo`** | `Logo` | Wyraźne logo, nazwa marki lub monogram jako główny motyw wizualny (`logo`, `logo-printed`, `monogram`, `wordmark`, `branded`, `embroidered logo`, `logo patch`, `intarsia logo`) |
| 6 | **`Floral`** | `Floral`, `Floral / Tropical` | Kwiaty, motywy roślinne, liście, wzory botaniczne i tropikalne/hawajskie (`floral`, `flower`, `botanical`, `tropical`, `hawaiian`, `leaf`, `foliage`, `palm`, `hibiscus`, `rose print`, `daisy`, `blossom`) |
| 7 | **`Colorblock`** | `Colorblock`, `Colorblock / Two-Tone` | Kontrastowe bloki kolorów, panele w innych kolorach (`colorblock`, `colorblocked`, `colourblock`, `two-tone`, `bi-color panels`, `contrast paneling`, `split-color`) |
| 8 | **`Camo`** | `Camo`, `Camo / Camouflage` | Wzór moro / kamuflaż (`camo`, `camouflage`, `military camo`, `woodland camo`, `digital camo`) |
| 9 | **`Animal Print`** | `Animal Print` | Wzory zwierzęce – cętki, paski zebry, skóra węża (`animal print`, `leopard`, `cheetah`, `jaguar`, `panther`, `zebra`, `tiger`, `snake`, `snakeskin`, `python`, `reptile`, `croc-embossed print`, `cow print`, `dalmatian`, `giraffe`) |
| 10 | **`Polka Dot`** | `Polka Dot` | Grochy, kropki (`polka dot`, `polka-dot`, `dotted`, `dots`, `spotted`, `pin dot`, `micro dot`) |
| 11 | **`Tie-Dye`** | `Tie-Dye`, `Acid Wash / Bleached / Tie-Dye` | Barwienia tie-dye, ombre/gradient, marmurkowe wybielanie (`tie-dye`, `tie dye`, `acid wash`, `bleached`, `dip-dye`, `ombre`, `gradient`, `marbled`, `shibori`, `cloud wash`) |

---

## 2. Zasady rozstrzygania przypadków brzegowych (Priorytety wzorów)

1. **`Logo` vs `Graphic`:**
   * Jeśli nadruk lub haft przedstawia **wyłącznie nazwę/symbol marki lub monogram** (np. koszulka z dużym napisem *"KENZO"* lub *"GIVENCHY"*), przypisujemy **`Logo`**.
   * Jeśli ubranie ma **ilustrację, fotografię, postać, abstrakcyjną grafikę lub rozbudowany plakatowy nadruk** (nawet jeśli towarzyszy mu podpis marki), przypisujemy **`Graphic`** (lub obie wartości `["Graphic", "Logo"]`, jeśli cecha obsługuje wielokrotny wybór).

2. **`Colorblock` vs zwykłe 2 kolory w `colors`:**
   * **`Colorblock`** oznacza konstrukcję z dużych, geometrycznych paneli w różnych kolorach (np. rękawy w innym kolorze niż korpus, górna połowa kurtki biała, dolna czarna).
   * Z kolei ubranie w dwukolorowe paski ma `pattern = "Striped"` oraz dwa kolory w `colors`, a nie `Colorblock`.

3. **`Solid` jako wartość domyślna:**
   * Jeśli opis i zdjęcie produktu nie wskazują na żaden z pozostałych 10 wzorów (lub gdy ubranie ma jedynie strukturę materiału, np. prążkowaną dzianinę `ribbed knit`, warkoczowy splot `cable knit` czy pikowanie `quilted` w jednym kolorze), produkt otrzymuje `pattern = "Solid"`.
