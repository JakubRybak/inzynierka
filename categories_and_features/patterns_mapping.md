# Mapowanie wzorów (`pattern`)

We wszystkich kategoriach obowiązuje poniższy słownik. `pattern` jest multi choice: `Solid` i `Other` samodzielnie. Przy nazwanym wzorze nie dopisujemy `Other` za dodatkowe logo. Wzór oceniamy na podstawie opisu i zdjęć.

Dokument definiuje ujednoliconą listę **8 kanonicznych wartości** używanych w cesze `pattern` we wszystkich 23 kategoriach odzieżowych oraz zasady mapowania szczegółowych nazw deseni i nadruków ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Tabela mapowania 11 wzorów bazowych

Każda z 23 kategorii posiada dokładnie tę samą listę 8 wartości w cesze `pattern`, co zapewnia 100% spójności schematu dla modelu LLM (Guided Decoding) i pozwala obsłużyć zapytanie o dowolny wzór w dowolnej kategorii.

| # | Wartość docelowa (`pattern`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Solid`** | `Solid / Plain`, `Solid / Plain (Standard Wash)` | Gładkie, jednolite ubrania bez wzoru (`solid`, `plain`, `monochrome`, `unpatterned`, standardowy gładki jeans bez wzorów) |
| 2 | **`Striped`** | `Striped`, `Striped / Pinstripe`, `Striped / Side-Stripe` | Paski poziome, pionowe, ukośne, prążki garniturowe oraz lampasy (`striped`, `stripes`, `pinstripe`, `chalk stripe`, `side-stripe`, `breton`, `ticking stripe`, `variegated stripe`, `chevron stripe`) |
| 3 | **`Plaid`** | `Plaid / Check`, `Plaid / Check / Argyle`, `Plaid / Check / Houndstooth`, `Plaid / Check / Houndstooth / Herringbone` | Wszystkie rodzaje kraty, szachownicy, pepitki, jodełki i rombów (`plaid`, `check`, `checked`, `checkered`, `tartan`, `gingham`, `houndstooth`, `herringbone`, `argyle`, `windowpane`, `glen plaid`, `prince of wales`, `madras`, `buffalo check`, `tattersall`) |
| 4 | **`Floral`** | `Floral`, `Floral / Tropical` | Kwiaty, motywy roślinne, liście, wzory botaniczne i tropikalne/hawajskie (`floral`, `flower`, `botanical`, `tropical`, `hawaiian`, `leaf`, `foliage`, `palm`, `hibiscus`, `rose print`, `daisy`, `blossom`) |
| 5 | **`Camo`** | `Camo`, `Camo / Camouflage` | Wzór moro / kamuflaż (`camo`, `camouflage`, `military camo`, `woodland camo`, `digital camo`) |
| 6 | **`Animal Print`** | `Animal Print` | Wzory zwierzęce – cętki, paski zebry, skóra węża (`animal print`, `leopard`, `cheetah`, `jaguar`, `panther`, `zebra`, `tiger`, `snake`, `snakeskin`, `python`, `reptile`, `croc-embossed print`, `cow print`, `dalmatian`, `giraffe`) |
| 7 | **`Polka Dot`** | `Polka Dot` | Grochy, kropki (`polka dot`, `polka-dot`, `dotted`, `dots`, `spotted`, `pin dot`, `micro dot`) |
| 8 | **`Other`** | `Graphic`, `Logo`, `Colorblock`, `Tie-Dye` oraz ich wcześniejsze warianty | Pozostałe rozpoznawalne nadruki, motywy i zabiegi kolorystyczne: grafiki, logo, duże napisy, panele kontrastowe, colorblock, tie-dye, ombre, gradient, acid wash i podobne (`graphic`, `print`, `printed`, `artwork`, `photo print`, `text print`, `slogan`, `logo`, `logo-printed`, `monogram`, `wordmark`, `branded`, `colorblock`, `colorblocked`, `colourblock`, `two-tone`, `bi-color panels`, `contrast paneling`, `split-color`, `tie-dye`, `tie dye`, `acid wash`, `bleached`, `dip-dye`, `ombre`, `gradient`, `marbled`, `shibori`, `cloud wash`, `paint splatter`, `patchwork`) |

---

## 2. Zasady rozstrzygania przypadków brzegowych (Priorytety wzorów)

1. **Grafika/logo jako `Other`:**
   * Jeśli nadruk lub haft przedstawia nazwę/symbol marki, monogram, ilustrację, fotografię, postać, abstrakcyjną grafikę albo rozbudowany napis, przypisujemy **`Other`**.

2. **`Other` dla colorblock vs zwykłe 2 kolory w `colors`:**
   * **`Other`** oznacza tu konstrukcję z dużych, geometrycznych paneli w różnych kolorach, jeśli opis zawiera `colorblock` lub równoważne określenie.
   * Ubranie w dwukolorowe paski ma `pattern = "Striped"` oraz dwa kolory w `colors`, a nie `Other`.

3. **`Solid` jako wartość domyślna:**
   * Jeśli opis i zdjęcie produktu nie wskazują na żaden z pozostałych 7 wzorów (lub gdy ubranie ma jedynie strukturę materiału, np. prążkowaną dzianinę `ribbed knit`, warkoczowy splot `cable knit` czy pikowanie `quilted` w jednym kolorze), produkt otrzymuje `pattern = "Solid"`.
   * Jeśli występuje niejednoznaczny nadruk lub zabieg kolorystyczny należący do grupy Graphic/Logo/Colorblock/Tie-Dye, przypisujemy `Other`.