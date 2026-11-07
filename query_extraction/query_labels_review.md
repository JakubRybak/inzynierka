# Przegląd etykiet zapytań

Przegląd objął 1 515 zapytań w 22 kategoriach. Poniżej są przypadki, w których proponuję zmianę lub potrzebna jest decyzja. Kategoria, filtry i residual pochodzą bezpośrednio z CSV.

## Reguły do doprecyzowania

- Określ, czy jawne preferencje trafiają do residualu, a twarde filtry są zarezerwowane dla wymagań.
- Ustal, jak zapisywać w residualu alternatywę, gdy tylko jedna opcja wymienia konkretny odcień.
- Zapisz regułę dla `lining_composition`. W testach jawnie wskazany materiał podszewki używa `contains_any`, a brak podszewki używa `equals_set [Unlined]`. Sekcja Materials obecnie opisuje tylko skład główny. [Reguły materiałów](rules.md#materials)

## 1. Tops

Przejrzano 484 zapytań.

### `colorful graphic tee`

- **Kategoria** — `T-shirts`
- **Filtry** — `colors contains_any ["Multicolor"]`
- **Residual** — `["graphic"]`

**Sugestia** — Usuń filtr `Multicolor` i zapisz `colorful graphic` jako jeden residual. Kolorowy może być sam nadruk. [CSV, w. 83](queries/tops/t-shirt_queries.csv#L83)

### `women's Off-White t-shirt with a small logo`

- **Kategoria** — `T-shirts`
- **Filtry** — `gender in ["Women"]` · `brand in ["Off-White"]`
- **Residual** — `["with a small logo"]`

**Sugestia** — Jeśli `Off-White` oznacza odcień, zamień filtr marki na `colors contains_any [White]` i dodaj `Off-White` do residualu. Wielkie litery wspierają obecną interpretację jako marki. [CSV, w. 134](queries/tops/t-shirt_queries.csv#L134)

### `black or navy t-shirt with a front pocket`

- **Kategoria** — `T-shirts`
- **Filtry** — `colors contains_any ["Black", "Blue"]`
- **Residual** — `["navy", "with a front pocket"]`

**Sugestia** — Zachowaj filtr kolorów. Zastąp `navy` przez `black or navy` w residualu, żeby ranking nie faworyzował jednej z alternatyw. [CSV, w. 87](queries/tops/t-shirt_queries.csv#L87)

### `izod big and tall grid polo shirts`

- **Kategoria** — `Polos`
- **Filtry** — `brand in ["IZOD"]`
- **Residual** — `["big and tall", "grid"]`

**Sugestia** — Dodaj `pattern in [Plaid]`, jeśli `grid` opisuje widoczną kratę. Jeżeli chodzi o fakturę, zostaw `grid` w residualu. [CSV, w. 30](queries/tops/polos_queries.csv#L30)

### `sexy cheetah body suit for women halloween`

- **Kategoria** — `Bodysuits`
- **Filtry** — `pattern in ["Animal Print"]` · `gender in ["Women"]`
- **Residual** — `["sexy", "cheetah", "halloween"]`

**Sugestia** — Rozważ usunięcie `Animal Print` i zachowanie `cheetah` w residualu. Kontekst Halloween dopuszcza kostium lub grafikę z gepardem. [CSV, w. 28](queries/tops/bodysuits_queries.csv#L28)

## 2. Shirts & Blouses

Przejrzano 118 zapytań.

### `blouses under 7 dollars women`

- **Kategoria** — `Blouses`
- **Filtry** — `price lte 7` · `gender in ["Women"]`
- **Residual** — `[]`

**Sugestia** — Ustal znaczenie `under`. Przy granicy ścisłej potrzebna jest obsługa `price lt 7`. Jeśli świadomie stosujemy granice domknięte, zostaw `lte 7` i dopisz tę konwencję do reguł. [CSV, w. 7](queries/shirts-and-blouses/blouses_queries.csv#L7)

### `short-sleeve shirt with a spread collar for the office`

- **Kategoria** — `Shirts`
- **Filtry** — `sleeve_length in ["Short Sleeve"]` · `collar_type in ["Point Collar"]`
- **Residual** — `["for the office"]`

**Sugestia** — Dodaj `spread collar` do residualu i zachowaj `Point Collar`. Filtr obejmuje też inne typy kołnierzyków. [CSV, w. 32](queries/shirts-and-blouses/shirts_queries.csv#L32)

### `camisas de lino cuello mao hombre manga larga`

- **Kategoria** — `Shirts`
- **Filtry** — `main_composition contains_any ["Linen"]` · `collar_type in ["Stand Collar"]` · `gender in ["Men"]` · `sleeve_length in ["Long Sleeve"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `cuello mao` do residualu i zachowaj `Stand Collar`. Filtr obejmuje też inne typy stójek. [CSV, w. 31](queries/shirts-and-blouses/shirts_queries.csv#L31)

### `mustard saree blouse readymade`

- **Kategoria** — `Blouses`
- **Filtry** — `colors contains_any ["Yellow"]`
- **Residual** — `["mustard", "saree", "readymade"]`

**Sugestia** — Zastąp `saree` w residualu przez `saree blouse`. Pełna fraza określa fason bluzki. [CSV, w. 17](queries/shirts-and-blouses/blouses_queries.csv#L17)

### `V-neck blouse with no collar`

- **Kategoria** — `Blouses`
- **Filtry** — `neckline in ["V-Neck"]` · `neckline not_in ["Collared"]`
- **Residual** — `[]`

**Sugestia** — Zachowaj `neckline in [V-Neck]` i zastąp wykluczenie `Collared` frazą `with no collar` w residualu. Przy cesze single choice to wykluczenie nie zawęża wyników i nie opisuje niezależnie konstrukcji bluzki. [CSV, w. 34](queries/shirts-and-blouses/blouses_queries.csv#L34)

### `flannel shirt with quilted lining`

- **Kategoria** — `Shirts`
- **Filtry** — `[]`
- **Residual** — `["flannel", "with quilted lining"]`

**Sugestia** — Zostaw `Shirts` i `with quilted lining` w residualu. Zmianę na `Jackets` rozważ tylko po przyjęciu osobnej reguły dla pikowanych koszul noszonych jako okrycie. [CSV, w. 13](queries/shirts-and-blouses/shirts_queries.csv#L13)

### `mens insulated flannel shirts`

- **Kategoria** — `Shirts`
- **Filtry** — `gender in ["Men"]`
- **Residual** — `["insulated", "flannel"]`

**Sugestia** — Zostaw `Shirts`. Jeśli ocieplane koszule mają domyślnie trafiać do `Jackets`, opisz tę decyzję w regułach i zmień etykietę. [CSV, w. 26](queries/shirts-and-blouses/shirts_queries.csv#L26)

## 3. Sweaters

Przejrzano 200 zapytań.

### `wool blend sweater women ligbt blue`

- **Kategoria** — `Knit Sweaters`
- **Filtry** — `main_composition contains_any ["Wool"]` · `gender in ["Women"]` · `colors contains_any ["Blue"]`
- **Residual** — `["light blue"]`

**Sugestia** — Dodaj `wool blend` do residualu. Filtr obecności wełny dopuszcza też produkty ze 100% wełny. [CSV, w. 17](queries/sweaters/knit_sweaters_queries.csv#L17)

### `green plaid flannel hoodie`

- **Kategoria** — `Hoodies & Zipups`
- **Filtry** — `colors contains_any ["Green"]` · `pattern in ["Plaid"]` · `hood in ["With Hood"]`
- **Residual** — `["flannel"]`

**Sugestia** — Zostaw `Hoodies & Zipups` jako domyślną interpretację `hoodie`. Do zmiany na `Shirts` lub `Jackets` potrzebna byłaby silniejsza wskazówka, że chodzi o flanelową koszulę lub kurtkę z kapturem. [CSV, w. 16](queries/sweaters/hoodies_%26_zipups_queries.csv#L16)

### `longline sweatshirt with a detachable hood`

- **Kategoria** — `Sweatshirts`
- **Filtry** — `length in ["Longline"]` · `hood in ["With Hood"]`
- **Residual** — `["detachable hood"]`

**Sugestia** — Ustal regułę dla odpinanego kaptura. Jeśli dowolny kaptur kieruje bluzę do `Hoodies & Zipups`, zmień kategorię i zachowaj `detachable hood` w residualu. [CSV, w. 37](queries/sweaters/sweatshirts_queries.csv#L37)

### `black or burgundy cardigan, no beige`

- **Kategoria** — `Cardigans`
- **Filtry** — `colors contains_any ["Black", "Red"]` · `colors contains_none ["Beige"]`
- **Residual** — `["burgundy"]`

**Sugestia** — Zachowaj oba filtry kolorów. Zastąp `burgundy` przez `black or burgundy` w residualu. [CSV, w. 42](queries/sweaters/cardigans_queries.csv#L42)

## 4. Jackets & Coats

Przejrzano 252 zapytań.

### `A bomber jacket with inner warming lining, preferrably black`

- **Kategoria** — `Bombers`
- **Filtry** — `colors contains_any ["Black"]` · `lining_composition contains_none ["Unlined"]`
- **Residual** — `["inner warming lining"]`

**Sugestia** — Rozważ usunięcie filtra `Black`, jeśli jawne preferencje kolorów mają pozostać opcjonalne. [CSV, w. 2](queries/jackets-and-coats/bombers_queries.csv#L2)

### `A warm jacket that feels comfy. Also probably one with plaid.`

- **Kategoria** — `Jackets`
- **Filtry** — `pattern in ["Plaid"]`
- **Residual** — `["warm", "comfy"]`

**Sugestia** — Usuń filtr `Plaid` i dodaj `probably one with plaid` do residualu. Zachowaj pozostałe preferencje. [CSV, w. 6](queries/jackets-and-coats/jackets_queries.csv#L6)

### `plain coat with oversized buttons`

- **Kategoria** — `Classic Coats`
- **Filtry** — `pattern in ["Solid"]` · `closure_type contains_any ["Button"]`
- **Residual** — `["oversized buttons"]`

**Sugestia** — Usuń filtr `Button`. Zostaw `Solid` i `oversized buttons` w residualu. Zapytanie nie wskazuje, że guziki zapinają przód. [CSV, w. 21](queries/jackets-and-coats/classic_coats_queries.csv#L21)

### `Black leather jacket with a removable hood insert. Similar to a biker jacket.`

- **Kategoria** — `Jackets`
- **Filtry** — `colors contains_any ["Black"]` · `main_composition contains_any ["Leather"]` · `hood in ["With Hood"]` · `jacket_style in ["Biker"]`
- **Residual** — `["removable hood insert"]`

**Sugestia** — Usuń filtr `Biker` i dodaj `similar to a biker jacket` do residualu. Zachowaj filtr kaptura dla odpinanego elementu. [CSV, w. 7](queries/jackets-and-coats/jackets_queries.csv#L7)

### `carhartt men's brookville quilted nylon vest`

- **Kategoria** — `Vests`
- **Filtry** — `brand in ["Carhartt"]` · `gender in ["Men"]` · `main_composition contains_any ["Nylon"]`
- **Residual** — `["brookville", "quilted"]`

**Sugestia** — Zostaw `quilted` w residualu, jeśli filtr ocieplenia ma wymagać jawnego rodzaju wypełnienia. Jeśli parser ma stosować heurystykę katalogową dla pikowania, dodaj `insulation in [Synthetic Padding]`. [CSV, w. 3](queries/jackets-and-coats/vests_queries.csv#L3)

### `chaleco acolchado largo mujer`

- **Kategoria** — `Vests`
- **Filtry** — `length in ["Longline"]` · `gender in ["Women"]`
- **Residual** — `["acolchado"]`

**Sugestia** — Zostaw `acolchado` w residualu, jeśli filtr ma wymagać jawnego wypełnienia. Jeśli stosujemy heurystykę katalogową dla watowania, dodaj `insulation in [Synthetic Padding]`. [CSV, w. 8](queries/jackets-and-coats/vests_queries.csv#L8)

### `trench coat with a wool-blend shell and nylon lining`

- **Kategoria** — `Trench Coats`
- **Filtry** — `main_composition contains_any ["Wool"]` · `lining_composition contains_any ["Nylon"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `wool-blend shell` do residualu. Zachowaj osobne filtry dla wełny w materiale zewnętrznym i nylonu w podszewce. [CSV, w. 30](queries/jackets-and-coats/trench_coats_queries.csv#L30)

### `cashmere-blend vest with no hood`

- **Kategoria** — `Vests`
- **Filtry** — `main_composition contains_any ["Cashmere"]` · `hood in ["Without Hood"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `cashmere-blend` do residualu. Filtr obecności kaszmiru dopuszcza też produkty ze 100% kaszmiru. [CSV, w. 33](queries/jackets-and-coats/vests_queries.csv#L33)

### `krótka bomberka z zamkiem na koncert`

- **Kategoria** — `Bombers`
- **Filtry** — `length in ["Cropped"]` · `closure_type contains_any ["Zip"]`
- **Residual** — `["na koncert"]`

**Sugestia** — Usuń `Cropped` i dodaj `krótka` do residualu, jeśli `Cropped` ma oznaczać długość do talii lub krótszą. Do testu tego filtra można użyć jednoznacznej frazy `bomberka do talii`. [CSV, w. 28](queries/jackets-and-coats/bombers_queries.csv#L28)

### `full length wool coat women`

- **Kategoria** — `Classic Coats`
- **Filtry** — `length in ["Long"]` · `main_composition contains_any ["Wool"]` · `coat_style in ["Standard"]` · `gender in ["Women"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `full length` do residualu. `Long` obejmuje również modele kończące się powyżej kostki. [CSV, w. 28](queries/jackets-and-coats/classic_coats_queries.csv#L28)

### `men's pinstriped coat`

- **Kategoria** — `Classic Coats`
- **Filtry** — `gender in ["Men"]` · `pattern in ["Striped"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `pinstriped` do residualu. `Striped` obejmuje też inne rodzaje pasków. [CSV, w. 34](queries/jackets-and-coats/classic_coats_queries.csv#L34)

## 5. Pants

Przejrzano 208 zapytań.

### `000 black jeans not ripped`

- **Kategoria** — `Jeans`
- **Filtry** — `colors contains_any ["Black"]` · `distressing contains_none ["Distressed"]`
- **Residual** — `["000"]`

**Sugestia** — Usuń `contains_none [Distressed]` i dodaj `not ripped` do residualu. Użytkownik wyklucza rozdarcia, a filtr obejmuje też inne rodzaje uszkodzeń. [CSV, w. 2](queries/pants/jeans_queries.csv#L2)

### `faded jeans with no rips`

- **Kategoria** — `Jeans`
- **Filtry** — `distressing contains_any ["Faded"]` · `distressing contains_none ["Distressed"]`
- **Residual** — `[]`

**Sugestia** — Zachowaj `Faded`. Usuń `contains_none [Distressed]` i dodaj `with no rips` do residualu. [CSV, w. 23](queries/pants/jeans_queries.csv#L23)

### `jasnoniebieskie dżinsy bez przetarć`

- **Kategoria** — `Jeans`
- **Filtry** — `colors contains_any ["Blue"]` · `distressing contains_none ["Distressed"]`
- **Residual** — `["jasnoniebieskie"]`

**Sugestia** — Zachowaj kolor i odcień. Rozważ przeniesienie `bez przetarć` do residualu zamiast wykluczania całej klasy `Distressed`. [CSV, w. 30](queries/pants/jeans_queries.csv#L30)

### `floral cargo pants with a drawstring waist`

- **Kategoria** — `Cargo Pants`
- **Filtry** — `pattern in ["Floral"]` · `waistband_type in ["Elasticized"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with a drawstring waist` do residualu. `Elasticized` obejmuje też pasy bez sznurka. [CSV, w. 30](queries/pants/cargo_pants_queries.csv#L30)

### `low-rise flared lounge pants with a drawstring waistband`

- **Kategoria** — `Sweatpants & Lounge Pants`
- **Filtry** — `rise in ["Low-Rise"]` · `leg_shape in ["Flared"]` · `waistband_type in ["Elasticized"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with a drawstring waistband` do residualu i zachowaj `Elasticized`. [CSV, w. 23](queries/pants/sweatpants_and_lounge_pants_queries.csv#L23)

### `lavender lounge pants with a ribbed waistband`

- **Kategoria** — `Sweatpants & Lounge Pants`
- **Filtry** — `colors contains_any ["Purple"]` · `waistband_type in ["Elasticized"]`
- **Residual** — `["lavender"]`

**Sugestia** — Dodaj `with a ribbed waistband` do residualu obok `lavender`. Sam filtr `Elasticized` nie gwarantuje ściągacza. [CSV, w. 27](queries/pants/sweatpants_and_lounge_pants_queries.csv#L27)

### `cargo pants with a zip fly, no ankle zips`

- **Kategoria** — `Cargo Pants`
- **Filtry** — `waistband_type in ["Structured"]` · `cuff_style not_in ["Zippered Cuff"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with a zip fly` do residualu i zachowaj wykluczenie zamków przy kostkach. Rozważ pominięcie `Structured`, bo sam rozporek nie określa konstrukcji pasa. [CSV, w. 21](queries/pants/cargo_pants_queries.csv#L21)

### `camo jeans with a button fly`

- **Kategoria** — `Jeans`
- **Filtry** — `pattern in ["Camo"]` · `waistband_type in ["Structured"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with a button fly` do residualu. Rozważ pominięcie `Structured`, jeśli sam rozporek nie wystarcza do przypisania typu pasa. [CSV, w. 37](queries/pants/jeans_queries.csv#L37)

### `joggers with belt loops`

- **Kategoria** — `Sweatpants & Lounge Pants`
- **Filtry** — `leg_shape in ["Tapered"]` · `waistband_type in ["Structured"]`
- **Residual** — `["joggers"]`

**Sugestia** — Dodaj `with belt loops` do residualu. `Structured` nie gwarantuje szlufek. Zachowaj obecną kategorię jako domyślną dla `joggers`. [CSV, w. 17](queries/pants/sweatpants_and_lounge_pants_queries.csv#L17)

## 6. Shorts

Przejrzano 53 zapytań.

### `tailored shorts with a drawstring waistband`

- **Kategoria** — `Shorts`
- **Filtry** — `shorts_type in ["Tailored"]` · `waistband_type in ["Elasticized"]`
- **Residual** — `[]`

**Sugestia** — Zachowaj `waistband_type in [Elasticized]` i przenieś `tailored` do residualu. Definicja `Tailored` zakłada pas `Structured`, więc obecne wymagania są niezgodne. [CSV, w. 26](queries/shorts/shorts_queries.csv#L26)

### `american eagle shorts for men longer length`

- **Kategoria** — `Shorts`
- **Filtry** — `brand in ["American Eagle"]` · `gender in ["Men"]` · `length in ["Long"]`
- **Residual** — `[]`

**Sugestia** — Usuń filtr długości i dodaj `longer length` do residualu. Samo porównanie nie wskazuje, że dół sięga co najmniej do kolana. [CSV, w. 10](queries/shorts/shorts_queries.csv#L10)

### `short high-rise denim shorts with a zip fly`

- **Kategoria** — `Shorts`
- **Filtry** — `length in ["Short"]` · `rise in ["High-Rise"]` · `shorts_type in ["Denim"]` · `waistband_type in ["Structured"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with a zip fly` do residualu. Rozważ usunięcie `Structured`, jeśli sam rozporek nie wystarcza do przypisania typu pasa. [CSV, w. 19](queries/shorts/shorts_queries.csv#L19)

### `regular-fit cargo shorts with belt loops`

- **Kategoria** — `Shorts`
- **Filtry** — `fit in ["Regular"]` · `shorts_type in ["Cargo"]` · `waistband_type in ["Structured"]`
- **Residual** — `[]`

**Sugestia** — Dodaj `with belt loops` do residualu. `Structured` obejmuje też modele bez szlufek. [CSV, w. 23](queries/shorts/shorts_queries.csv#L23)

### `bike shorts for men without padding`

- **Kategoria** — `Shorts`
- **Filtry** — `shorts_type in ["Athletic"]` · `gender in ["Men"]`
- **Residual** — `["bike", "without padding"]`

**Sugestia** — Rozważ usunięcie `Athletic` i pozostawienie `bike` oraz `without padding` w residualu. `Bike shorts` może określać fason również w ubraniach niesportowych. [CSV, w. 18](queries/shorts/shorts_queries.csv#L18)

### `swim shorts with a quick-dry lining`

- **Kategoria** — `Shorts`
- **Filtry** — `[]`
- **Residual** — `["swim", "with a quick-dry lining"]`

**Sugestia** — Zostaw `Shorts`, jeśli kategoria ma obejmować szorty kąpielowe. Jeżeli wyłączymy kąpielówki z zakresu parsera, ustaw `category: null` oraz puste listy filtrów i residualu. [CSV, w. 27](queries/shorts/shorts_queries.csv#L27)

### `best cargo shorts for men`

- **Kategoria** — `Shorts`
- **Filtry** — `shorts_type in ["Cargo"]` · `gender in ["Men"]`
- **Residual** — `[]`

**Sugestia** — Zostaw pusty residual, jeśli ogólne superlatywy uznajemy za słowa bez konkretnej preferencji. Dopisz tę konwencję do reguł. [CSV, w. 15](queries/shorts/shorts_queries.csv#L15)

### `orange shorts that packs easily for a weekend trip`

- **Kategoria** — `Shorts`
- **Filtry** — `colors contains_any ["Orange"]`
- **Residual** — `["that packs easily", "for a weekend trip"]`

**Sugestia** — Popraw `packs` na `pack` w syntetycznym zapytaniu i w odpowiadającym mu elemencie residualu. [CSV, w. 54](queries/shorts/shorts_queries.csv#L54)

## 7. Skirts

Przejrzano 100 zapytań.

### `edwardian walking skirt`

- **Kategoria** — `Skirts`
- **Filtry** — `[]`
- **Residual** — `["edwardian", "walking"]`

**Sugestia** — Zapisz `["edwardian walking skirt"]` jako residual. Pełna fraza nazywa fason, a rozdzielenie może zasugerować współczesną odzież do spacerowania. [CSV, w. 24](queries/skirts/skirts_queries.csv#L24)

### `flair maxi skirt`

- **Kategoria** — `Skirts`
- **Filtry** — `length in ["Maxi"]`
- **Residual** — `["flair"]`

**Sugestia** — Jeśli `flair` to literówka od `flared`, zamień residual na `["flared"]` i rozważ `skirt_silhouette in [A-Line]`. [CSV, w. 27](queries/skirts/skirts_queries.csv#L27)

### `long skirts with pockets for women`

- **Kategoria** — `Skirts`
- **Filtry** — `length in ["Maxi"]` · `gender in ["Women"]`
- **Residual** — `["with pockets"]`

**Sugestia** — Rozważ przeniesienie `long` do residualu zamiast twardego `Maxi`. Użytkownik może akceptować również dłuższe `Midi`. [CSV, w. 44](queries/skirts/skirts_queries.csv#L44)

### `snakeskin skirt`

- **Kategoria** — `Skirts`
- **Filtry** — `pattern in ["Animal Print"]`
- **Residual** — `["snakeskin"]`

**Sugestia** — Zostaw `Animal Print`, jeśli przyjmujemy odczytanie `snakeskin` jako wzoru. Przy ostrożniejszej interpretacji zachowaj samo `snakeskin` w residualu, bo może też oznaczać materiał. [CSV, w. 66](queries/skirts/skirts_queries.csv#L66)

### `magenta ruffle skirt`

- **Kategoria** — `Skirts`
- **Filtry** — `colors contains_any ["Pink"]` · `skirt_type contains_any ["Ruffled"]`
- **Residual** — `["magenta"]`

**Sugestia** — Zostaw `Pink` i `magenta` w residualu, jeśli tak normalizujemy ten odcień. Dopisz wtedy `magenta → Pink` do mapowania kolorów. [CSV, w. 45](queries/skirts/skirts_queries.csv#L45)

### `navy or beige skirt, no white`

- **Kategoria** — `Skirts`
- **Filtry** — `colors contains_any ["Blue", "Beige"]` · `colors contains_none ["White"]`
- **Residual** — `["navy"]`

**Sugestia** — Zachowaj oba filtry kolorów i zastąp `navy` przez `navy or beige` w residualu. [CSV, w. 87](queries/skirts/skirts_queries.csv#L87)

## 8. Dresses

Przejrzano 100 zapytań.

### `faux wrap dress for women`

- **Kategoria** — `Dresses`
- **Filtry** — `gender in ["Women"]` · `dress_type contains_any ["Wrap"]`
- **Residual** — `["faux wrap"]`

**Sugestia** — Rozważ usunięcie filtra `Wrap` i pozostawienie `faux wrap` w residualu. Symulowany efekt kopertowy może nie spełniać definicji rzeczywistego kopertowego przodu. [CSV, w. 47](queries/dress/dresses_queries.csv#L47)

### `sun dresses petite`

- **Kategoria** — `Dresses`
- **Filtry** — `[]`
- **Residual** — `["sun", "petite"]`

**Sugestia** — Zastąp `sun` przez `sundress` w residualu. Zachowaj `petite`. [CSV, w. 71](queries/dress/dresses_queries.csv#L71)

### `champagne wedding dress`

- **Kategoria** — `Dresses`
- **Filtry** — `colors contains_any ["Beige"]`
- **Residual** — `["champagne", "wedding"]`

**Sugestia** — Zastąp `wedding` przez `wedding dress` w residualu. Pełna fraza odróżnia suknię ślubną od sukienki dla gościa. [CSV, w. 32](queries/dress/dresses_queries.csv#L32)

### `red or navy dress, no white`

- **Kategoria** — `Dresses`
- **Filtry** — `colors contains_any ["Red", "Blue"]` · `colors contains_none ["White"]`
- **Residual** — `["navy"]`

**Sugestia** — Zachowaj oba filtry kolorów i zastąp `navy` przez `red or navy` w residualu. [CSV, w. 81](queries/dress/dresses_queries.csv#L81)

## Walidacja

Test schematu przeszedł. Przegląd automatyczny potwierdził zgodność CSV z dokumentami do przeglądu i sprawdził operatory, duplikaty oraz sprzeczne warunki na tej samej cesze.
