# Audyt słów kluczowych: kategorie, cechy i wartości

Zakres: **wszystkie 17 kategorii poza Jackets & Coats**. Łącznie **44 645 unikalnych produktów** z `train` i `validation`.

## Jak czytać wyniki

- **Procent = produkty z co najmniej jednym trafieniem / wszystkie produkty danej kategorii.** Każdy `input_productID` liczy się raz, niezależnie od liczby zdjęć i liczby trafień.
- To częstości **wzmianek i szerokich wskazówek w tekście**, nie gotowe etykiety produktów. Nie analizujemy zdjęć ani nie uruchamiamy LLM.
- Kategorie wynikają z etykiet źródłowych. Cechy: `input_name` + `input_description`; `gender`: pola `input_gender` i `input_department`; materiały: `input_composition`. Nie dopisujemy wzmianki o cesze na podstawie samej nazwy podkategorii źródłowej.
- Każdą wartość liczymy niezależnie. Trafienia mogą się nakładać, również w cechach single choice; sumy procentów mogą przekroczyć 100%. Nie stosujemy limitu dwóch kolorów ani priorytetów klasyfikacji.
- **Brak trafienia nie oznacza `Other`, `Solid`, `Regular`, `Without Hood` ani braku cechy.** Wiersz „bez trafienia” jest osobną miarą pokrycia tekstu. `Other` ma wyłącznie dodatnie wskazówki dla części konstrukcji poza nazwanymi klasami; nie mierzy całej pozostałej grupy.
- `0,00%` = reguła istnieje, ale niczego nie znalazła; **n/d** = brak sensownej reguły dodatniej. Oba wyniki nie dowodzą, że dana konstrukcja nie występuje. Szczególnie ostrożnie czytaj neutralne i domyślne wartości: `Regular`, `Standard`, `Clean`, `Solid`, `Full-Length`, `Open Hem`, `Pullover`, `Without Hood`.
- **Materiały:** szeroka kolumna bazuje na obecnych grupowaniach w `materials_mapping.md`. Kolumna „konkretna nazwa” ogranicza się do nazw danego surowca i jego bliskich synonimów. Różnica pokazuje skutki grupowań, np. przypisania `polyurethane` do `Polyester`. Obie kolumny liczą wzmianki w całym składzie, także podszewce i wykończeniach; **nie ustalają głównej części ani procentowego udziału włókna**.
- Szeroki słownik może łapać kolor guzika, nazwę wzoru, detale lub części produktu. Sama niska częstość w tekście nie wystarcza do usunięcia wartości. Najpierw porównaj pokrycie cechy, przykłady i użyteczność filtra.
- Kolory są liczone bez rozstrzygania kontekstu: np. `khaki` trafia do `Green` i `Beige`, `navy blue` do `Navy` i `Blue`. `Multicolor` to jawne określenia wielobarwności i szeroki sygnał `tie-dye`; nie wyliczamy go z trzech trafień innych kolorów.
- Pełne reguły, uwagi dla poszczególnych wartości i przykładowe trafienia z ID znajdują się w JSON-ie. Przyjęte grupowania składów obejmują szersze rodziny surowców w `Polyester`, `Viscose` i `Wool`, `hemp/ramie` w `Linen`, pióra w `Down`, imitacje skóry/futra. Kolumna „konkretna nazwa” zawęża te grupy, ale nadal jest tekstowym przybliżeniem (np. `rayon` bywa nazwą szerszej rodziny).

[Pierwotny przegląd z perspektywy klienta](taxonomy_customer_review.md) przedstawia stan sprzed ostatnich zmian taksonomii. Poniższe tabele odpowiadają aktualnemu dokumentowi kategorii.

## Zakres i liczebności

| Dział | Kategoria | Train | Validation | Razem |
| :--- | :--- | ---: | ---: | ---: |
| Tops | [T-shirts](#t-shirts) | 7988 | 973 | 8961 |
| Tops | [Polos](#polos) | 512 | 78 | 590 |
| Tops | [Tank tops & Camisoles](#tank-tops-camisoles) | 904 | 116 | 1020 |
| Tops | [Bodysuits](#bodysuits) | 107 | 11 | 118 |
| Shirts & Blouses | [Shirts](#shirts) | 3854 | 485 | 4339 |
| Shirts & Blouses | [Blouses](#blouses) | 885 | 117 | 1002 |
| Sweaters | [Knit Sweaters](#knit-sweaters) | 4454 | 536 | 4990 |
| Sweaters | [Sweatshirts](#sweatshirts) | 3027 | 405 | 3432 |
| Sweaters | [Hoodies & Zipups](#hoodies-zipups) | 2464 | 315 | 2779 |
| Sweaters | [Cardigans](#cardigans) | 815 | 89 | 904 |
| Pants | [Trousers](#trousers) | 3495 | 421 | 3916 |
| Pants | [Cargo Pants](#cargo-pants) | 165 | 23 | 188 |
| Pants | [Sweatpants & Lounge Pants](#sweatpants-lounge-pants) | 1883 | 253 | 2136 |
| Pants | [Jeans](#jeans) | 3292 | 412 | 3704 |
| Shorts | [Shorts](#shorts) | 1825 | 228 | 2053 |
| Skirts | [Skirts](#skirts) | 1700 | 213 | 1913 |
| Dresses | [Dresses](#dresses) | 2311 | 289 | 2600 |

Produkty występujące w obu splitach w tym zakresie: **0**. Przy wielu wariantach tekstu jednego produktu uwzględniamy trafienie w dowolnym wariancie.

## Pokrycie najważniejszych cech

Procent produktów z co najmniej jednym trafieniem dowolnej dopuszczalnej wartości. Niskie pokrycie oznacza, że słowa kluczowe słabo opisują rozkład tej cechy; „—” oznacza brak cechy w schemacie.

| Kategoria | pattern | fit | length | neckline | sleeve_length | rise |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| T-shirts | 64,66% | 10,11% | 1,19% | 97,76% | 95,35% | — |
| Polos | 71,86% | 6,78% | — | — | 98,31% | — |
| Tank tops & Camisoles | 31,86% | 16,86% | 8,53% | 84,90% | — | — |
| Bodysuits | 19,49% | — | — | 86,44% | 95,76% | — |
| Shirts | 48,19% | 10,07% | 1,82% | — | 97,67% | — |
| Blouses | 26,25% | 18,16% | 7,68% | 88,22% | 91,12% | — |
| Knit Sweaters | 36,93% | 13,13% | 4,11% | 97,78% | 96,13% | — |
| Sweatshirts | 65,71% | 10,40% | 1,37% | 98,19% | 98,60% | — |
| Hoodies & Zipups | 62,86% | 12,74% | 1,84% | — | 97,30% | — |
| Cardigans | 40,27% | 10,29% | 7,52% | 81,64% | 92,92% | — |
| Trousers | 22,91% | 57,02% | 18,54% | — | — | 20,61% |
| Cargo Pants | 35,64% | 82,98% | 7,98% | — | — | 18,09% |
| Sweatpants & Lounge Pants | 45,60% | 73,13% | 8,33% | — | — | 8,94% |
| Jeans | 66,12% | 81,37% | 13,20% | — | — | 52,59% |
| Shorts | 42,67% | 62,59% | 5,11% | — | — | 16,80% |
| Skirts | 30,16% | — | 60,32% | — | — | 8,47% |
| Dresses | 29,54% | — | 6,04% | 88,15% | 91,73% | — |

<a id="t-shirts"></a>

## T-shirts

**Dział:** Tops. **Mianownik każdej tabeli: 8961 produktów.**

Źródło: `TOPS / T-SHIRTS` (8961).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 5683 | 63,42% | men, man, male, menswear |
| `Women` | 3278 | 36,58% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 8961 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 5552 | 61,96% | black, ebony, onyx, coal |
| `White` | 4902 | 54,70% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 1678 | 18,73% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 721 | 8,05% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 910 | 10,16% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 945 | 10,55% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 509 | 5,68% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 365 | 4,07% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 307 | 3,43% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 169 | 1,89% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 531 | 5,93% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 193 | 2,15% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 176 | 1,96% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 675 | 7,53% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 8960 (99,99%); **bez trafienia:** 1 (0,01%); **trafienia ≥2 wartości:** 5819 (64,94%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 8049 | 89,82% | 8049 / 89,82% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 833 | 9,30% | 748 / 8,35% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 52 | 0,58% | 52 / 0,58% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 192 | 2,14% | 190 / 2,12% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 900 | 10,04% | 634 / 7,08% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 570 | 6,36% | 570 / 6,36% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 352 | 3,93% | 352 / 3,93% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 336 | 3,75% | 336 / 3,75% | silk, slik |
| `Leather` | 68 | 0,76% | 64 / 0,71% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 76 | 0,85% | 76 / 0,85% | cashmere, cashmire |
| `Linen` | 224 | 2,50% | 209 / 2,33% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 3 | 0,03% | 3 / 0,03% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 8957 (99,96%); **bez trafienia:** 4 (0,04%); **trafienia ≥2 wartości:** 2048 (22,85%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 16 | 0,18% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 725 | 8,09% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 73 | 0,81% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 234 | 2,61% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 74 | 0,83% | camo, camouflage, camouflaged |
| `Animal Print` | 195 | 2,18% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 56 | 0,62% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 5134 | 57,29% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 5794 (64,66%); **bez trafienia:** 3167 (35,34%); **trafienia ≥2 wartości:** 689 (7,69%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Short Sleeve` | 7358 | 82,11% | short sleeve, short-sleeved, cap sleeve |
| `Long Sleeve` | 1195 | 13,34% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 8544 (95,35%); **bez trafienia:** 417 (4,65%); **trafienia ≥2 wartości:** 9 (0,10%).

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 8172 | 91,20% | crewneck, crew neck, round/rounded neck, jewel neck |
| `Scoop Neck` | 216 | 2,41% | scoop/scooped neck, u-neck, deep round neck |
| `V-Neck` | 141 | 1,57% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 149 | 1,66% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Other` | 112 | 1,25% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 8760 (97,76%); **bez trafienia:** 201 (2,24%); **trafienia ≥2 wartości:** 30 (0,33%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Collared, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 143 | 1,60% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 40 | 0,45% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 725 | 8,09% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 906 (10,11%); **bez trafienia:** 8055 (89,89%); **trafienia ≥2 wartości:** 2 (0,02%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 73 | 0,81% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 1 | 0,01% | regular/standard length, hip-length, waist-length |
| `Longline` | 33 | 0,37% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 107 (1,19%); **bez trafienia:** 8854 (98,81%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

<a id="polos"></a>

## Polos

**Dział:** Tops. **Mianownik każdej tabeli: 590 produktów.**

Źródło: `TOPS / POLOS` (590).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 484 | 82,03% | men, man, male, menswear |
| `Women` | 106 | 17,97% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 590 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 310 | 52,54% | black, ebony, onyx, coal |
| `White` | 288 | 48,81% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 116 | 19,66% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 117 | 19,83% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 81 | 13,73% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 105 | 17,80% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 33 | 5,59% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 23 | 3,90% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 15 | 2,54% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 15 | 2,54% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 30 | 5,08% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 11 | 1,86% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 9 | 1,53% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 36 | 6,10% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 590 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 390 (66,10%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 514 | 87,12% | 514 / 87,12% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 91 | 15,42% | 72 / 12,20% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 3 | 0,51% | 3 / 0,51% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 32 | 5,42% | 30 / 5,08% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 54 | 9,15% | 48 / 8,14% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 37 | 6,27% | 37 / 6,27% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 56 | 9,49% | 56 / 9,49% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 26 | 4,41% | 26 / 4,41% | silk, slik |
| `Leather` | 5 | 0,85% | 5 / 0,85% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 10 | 1,69% | 10 / 1,69% | cashmere, cashmire |
| `Linen` | 6 | 1,02% | 5 / 0,85% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 590 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 168 (28,47%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 0 | 0,00% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 197 | 33,39% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 9 | 1,53% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 6 | 1,02% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 12 | 2,03% | camo, camouflage, camouflaged |
| `Animal Print` | 59 | 10,00% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 0 | 0,00% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 328 | 55,59% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 424 (71,86%); **bez trafienia:** 166 (28,14%); **trafienia ≥2 wartości:** 167 (28,31%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Short Sleeve` | 498 | 84,41% | short sleeve, short-sleeved, cap sleeve |
| `Long Sleeve` | 83 | 14,07% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 580 (98,31%); **bez trafienia:** 10 (1,69%); **trafienia ≥2 wartości:** 1 (0,17%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 12 | 2,03% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 3 | 0,51% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 25 | 4,24% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 40 (6,78%); **bez trafienia:** 550 (93,22%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

<a id="tank-tops-camisoles"></a>

## Tank tops & Camisoles

**Dział:** Tops. **Mianownik każdej tabeli: 1020 produktów.**

Źródło: `TOPS / TANK TOPS` (177); `TOPS / TANK TOPS & CAMISOLES` (843).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 177 | 17,35% | men, man, male, menswear |
| `Women` | 843 | 82,65% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 1020 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 581 | 56,96% | black, ebony, onyx, coal |
| `White` | 442 | 43,33% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 160 | 15,69% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 94 | 9,22% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 102 | 10,00% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 57 | 5,59% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 41 | 4,02% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 56 | 5,49% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 53 | 5,20% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 14 | 1,37% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 58 | 5,69% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 19 | 1,86% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 12 | 1,18% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 26 | 2,55% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 1020 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 451 (44,22%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 535 | 52,45% | 535 / 52,45% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 244 | 23,92% | 235 / 23,04% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 19 | 1,86% | 19 / 1,86% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 61 | 5,98% | 60 / 5,88% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 348 | 34,12% | 276 / 27,06% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 215 | 21,08% | 215 / 21,08% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 206 | 20,20% | 206 / 20,20% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 230 | 22,55% | 230 / 22,55% | silk, slik |
| `Leather` | 21 | 2,06% | 21 / 2,06% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 21 | 2,06% | 21 / 2,06% | cashmere, cashmire |
| `Linen` | 42 | 4,12% | 41 / 4,02% | linen, flax, ramie, hemp |
| `Down` | 1 | 0,10% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 1020 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 567 (55,59%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 8 | 0,78% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 80 | 7,84% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 17 | 1,67% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 55 | 5,39% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 3 | 0,29% | camo, camouflage, camouflaged |
| `Animal Print` | 18 | 1,76% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 8 | 0,78% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 197 | 19,31% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 325 (31,86%); **bez trafienia:** 695 (68,14%); **trafienia ≥2 wartości:** 55 (5,39%).

### `strap_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Standard` | 59 | 5,78% | two/twin/parallel straps, shoulder straps, adjustable straps |
| `Racerback` | 88 | 8,63% | racerback, racer-back, T-back, Y-back |
| `Halter` | 16 | 1,57% | halter, halterneck, halter neck |
| `One-Shoulder` | 23 | 2,25% | one-shoulder, single-shoulder, one-sleeve |
| `Strapless` | 17 | 1,67% | strapless, bandeau, tube top/dress/bodysuit |
| `Off-Shoulder` | 9 | 0,88% | off-shoulder, off-the-shoulder, Bardot |
| `Other` | 19 | 1,86% | jawnie nazwane rękawy, cold-shoulder, cross/criss-cross back |

**Co najmniej jedno trafienie:** 214 (20,98%); **bez trafienia:** 806 (79,02%); **trafienia ≥2 wartości:** 14 (1,37%).

Uwagi: `Standard`: Szeroki, niepełny wskaźnik ramiączek; może współwystępować np. z Racerback/Halter. Nie jest rozpoznaniem standardowego układu. `Other`: Rękawy są przybliżeniem zwykłej konstrukcji; mogą współwystępować z Off-Shoulder/One-Shoulder. Nie jest to pełna klasa Other.

### `strap_width`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Wide` | 3 | 0,29% | wide/broad/thick (shoulder) straps |
| `Spaghetti` | 8 | 0,78% | spaghetti, thin/narrow/delicate/fine/skinny/string straps |
| `Other` | 1 | 0,10% | medium/intermediate/regular-width straps, mixed/different/unequal-width straps; wzmianki o szerokim i cienkim ramiączku w jednym tekście |
| `Not Applicable` | 17 | 1,67% | strapless, bandeau, tube top/dress/bodysuit |

**Co najmniej jedno trafienie:** 29 (2,84%); **bez trafienia:** 991 (97,16%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Other`: Tylko jawne wskazówki pośredniej lub mieszanej szerokości. Brak informacji o szerokości nie daje Other; szerokie dopasowania mogą dotyczyć wariantów konstrukcji. `Not Applicable`: Tylko jawne wskaźniki braku ramiączek; brak informacji o szerokości nie jest Not Applicable.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 411 | 40,29% | crewneck, crew neck, round/rounded neck, jewel neck |
| `Scoop Neck` | 275 | 26,96% | scoop/scooped neck, u-neck, deep round neck |
| `V-Neck` | 104 | 10,20% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 25 | 2,45% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Other` | 55 | 5,39% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 866 (84,90%); **bez trafienia:** 154 (15,10%); **trafienia ≥2 wartości:** 4 (0,39%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Collared, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 26 | 2,55% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 1 | 0,10% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 146 | 14,31% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 172 (16,86%); **bez trafienia:** 848 (83,14%); **trafienia ≥2 wartości:** 1 (0,10%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 78 | 7,65% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 9 | 0,88% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 87 (8,53%); **bez trafienia:** 933 (91,47%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

<a id="bodysuits"></a>

## Bodysuits

**Dział:** Tops. **Mianownik każdej tabeli: 118 produktów.**

Źródło: `TOPS / BODYSUITS` (118).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 0 | 0,00% | men, man, male, menswear |
| `Women` | 118 | 100,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 118 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 81 | 68,64% | black, ebony, onyx, coal |
| `White` | 41 | 34,75% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 13 | 11,02% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 3 | 2,54% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 2 | 1,69% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 6 | 5,08% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 4 | 3,39% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 4 | 3,39% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 15 | 12,71% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 0 | 0,00% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 7 | 5,93% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 0 | 0,00% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 1 | 0,85% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 0 | 0,00% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 118 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 48 (40,68%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 29 | 24,58% | 29 / 24,58% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 19 | 16,10% | 19 / 16,10% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 0 | 0,00% | 0 / 0,00% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 9 | 7,63% | 9 / 7,63% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 44 | 37,29% | 23 / 19,49% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 97 | 82,20% | 97 / 82,20% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 59 | 50,00% | 59 / 50,00% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 13 | 11,02% | 13 / 11,02% | silk, slik |
| `Leather` | 0 | 0,00% | 0 / 0,00% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 1 | 0,85% | 1 / 0,85% | cashmere, cashmire |
| `Linen` | 0 | 0,00% | 0 / 0,00% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 118 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 108 (91,53%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 0 | 0,00% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 3 | 2,54% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 0 | 0,00% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 5 | 4,24% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 0 | 0,00% | camo, camouflage, camouflaged |
| `Animal Print` | 0 | 0,00% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 0 | 0,00% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 18 | 15,25% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 23 (19,49%); **bez trafienia:** 95 (80,51%); **trafienia ≥2 wartości:** 3 (2,54%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 47 | 39,83% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 14 | 11,86% | short sleeve, short-sleeved, cap sleeve |
| `Long Sleeve` | 52 | 44,07% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 113 (95,76%); **bez trafienia:** 5 (4,24%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 41 | 34,75% | crewneck, crew neck, round/rounded neck, jewel neck |
| `Scoop Neck` | 18 | 15,25% | scoop/scooped neck, u-neck, deep round neck |
| `V-Neck` | 22 | 18,64% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 13 | 11,02% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Other` | 8 | 6,78% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 102 (86,44%); **bez trafienia:** 16 (13,56%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Collared, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

### `strap_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Standard` | 4 | 3,39% | two/twin/parallel straps, shoulder straps, adjustable straps |
| `Racerback` | 3 | 2,54% | racerback, racer-back, T-back, Y-back |
| `Halter` | 4 | 3,39% | halter, halterneck, halter neck |
| `One-Shoulder` | 0 | 0,00% | one-shoulder, single-shoulder, one-sleeve |
| `Strapless` | 1 | 0,85% | strapless, bandeau, tube top/dress/bodysuit |
| `Off-Shoulder` | 1 | 0,85% | off-shoulder, off-the-shoulder, Bardot |
| `Other` | 67 | 56,78% | jawnie nazwane rękawy, cold-shoulder, cross/criss-cross back |

**Co najmniej jedno trafienie:** 79 (66,95%); **bez trafienia:** 39 (33,05%); **trafienia ≥2 wartości:** 1 (0,85%).

Uwagi: `Standard`: Szeroki, niepełny wskaźnik ramiączek; może współwystępować np. z Racerback/Halter. Nie jest rozpoznaniem standardowego układu. `Other`: Rękawy są przybliżeniem zwykłej konstrukcji; mogą współwystępować z Off-Shoulder/One-Shoulder. Nie jest to pełna klasa Other.

### `strap_width`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Wide` | 0 | 0,00% | wide/broad/thick (shoulder) straps |
| `Spaghetti` | 0 | 0,00% | spaghetti, thin/narrow/delicate/fine/skinny/string straps |
| `Other` | 0 | 0,00% | medium/intermediate/regular-width straps, mixed/different/unequal-width straps; wzmianki o szerokim i cienkim ramiączku w jednym tekście |
| `Not Applicable` | 68 | 57,63% | strapless, bandeau, tube; jawnie nazwane rękawy |

**Co najmniej jedno trafienie:** 68 (57,63%); **bez trafienia:** 50 (42,37%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Other`: Tylko jawne wskazówki pośredniej lub mieszanej szerokości. Brak informacji o szerokości nie daje Other; szerokie dopasowania mogą dotyczyć wariantów konstrukcji. `Not Applicable`: Rękawy są szerokim przybliżeniem konstrukcji bez ramiączek; konstrukcje z rękawami i dodatkowymi ramiączkami mogą zawyżać wynik.

<a id="shirts"></a>

## Shirts

**Dział:** Shirts & Blouses. **Mianownik każdej tabeli: 4339 produktów.**

Źródło: `SHIRTS / SHIRTS` (3124); `TOPS / SHIRTS` (1215).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 3124 | 72,00% | men, man, male, menswear |
| `Women` | 1215 | 28,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 4339 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1847 | 42,57% | black, ebony, onyx, coal |
| `White` | 2517 | 58,01% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 745 | 17,17% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 540 | 12,45% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 1044 | 24,06% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 478 | 11,02% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 283 | 6,52% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 123 | 2,83% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 223 | 5,14% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 133 | 3,07% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 259 | 5,97% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 80 | 1,84% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 72 | 1,66% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 176 | 4,06% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 4338 (99,98%); **bez trafienia:** 1 (0,02%); **trafienia ≥2 wartości:** 2587 (59,62%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 3719 | 85,71% | 3719 / 85,71% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 422 | 9,73% | 339 / 7,81% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 27 | 0,62% | 26 / 0,60% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 235 | 5,42% | 235 / 5,42% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 390 | 8,99% | 265 / 6,11% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 337 | 7,77% | 335 / 7,72% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 263 | 6,06% | 263 / 6,06% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 360 | 8,30% | 360 / 8,30% | silk, slik |
| `Leather` | 44 | 1,01% | 44 / 1,01% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 15 | 0,35% | 15 / 0,35% | cashmere, cashmire |
| `Linen` | 149 | 3,43% | 141 / 3,25% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 4339 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 1186 (27,33%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 17 | 0,39% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 422 | 9,73% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 598 | 13,78% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 161 | 3,71% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 35 | 0,81% | camo, camouflage, camouflaged |
| `Animal Print` | 78 | 1,80% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 78 | 1,80% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 1142 | 26,32% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 2091 (48,19%); **bez trafienia:** 2248 (51,81%); **trafienia ≥2 wartości:** 418 (9,63%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 101 | 2,33% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 492 | 11,34% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 38 | 0,88% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 3612 | 83,24% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 4238 (97,67%); **bez trafienia:** 101 (2,33%); **trafienia ≥2 wartości:** 5 (0,12%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 130 | 3,00% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 25 | 0,58% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 284 | 6,55% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 437 (10,07%); **bez trafienia:** 3902 (89,93%); **trafienia ≥2 wartości:** 2 (0,05%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 46 | 1,06% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 1 | 0,02% | regular/standard length, hip-length, waist-length |
| `Longline` | 35 | 0,81% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 79 (1,82%); **bez trafienia:** 4260 (98,18%); **trafienia ≥2 wartości:** 3 (0,07%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `collar_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Point Collar` | 3689 | 85,02% | point/pointed/spread/cutaway/shirt/classic collar, button-down collar |
| `Camp Collar` | 42 | 0,97% | camp/cuban/revere/convertible collar |
| `Stand Collar` | 310 | 7,14% | stand/stand-up/band/mandarin/funnel/Nehru/grandad collar |
| `Collarless` | 19 | 0,44% | collarless, no/without collar |
| `Other` | 45 | 1,04% | lapels, shawl collar, Peter Pan, ruffled/sailor/bow/tie collar |

**Co najmniej jedno trafienie:** 4086 (94,17%); **bez trafienia:** 253 (5,83%); **trafienia ≥2 wartości:** 19 (0,44%).

Uwagi: `Other`: Tylko pozytywne przykłady kołnierzy poza słownikiem Shirts.

<a id="blouses"></a>

## Blouses

**Dział:** Shirts & Blouses. **Mianownik każdej tabeli: 1002 produktów.**

Źródło: `TOPS / BLOUSES` (1002).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 0 | 0,00% | men, man, male, menswear |
| `Women` | 1002 | 100,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 1002 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 452 | 45,11% | black, ebony, onyx, coal |
| `White` | 465 | 46,41% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 111 | 11,08% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 118 | 11,78% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 143 | 14,27% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 65 | 6,49% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 50 | 4,99% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 46 | 4,59% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 54 | 5,39% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 18 | 1,80% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 47 | 4,69% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 15 | 1,50% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 23 | 2,30% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 33 | 3,29% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 1002 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 399 (39,82%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 491 | 49,00% | 491 / 49,00% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 242 | 24,15% | 231 / 23,05% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 7 | 0,70% | 6 / 0,60% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 70 | 6,99% | 69 / 6,89% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 268 | 26,75% | 214 / 21,36% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 152 | 15,17% | 152 / 15,17% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 174 | 17,37% | 174 / 17,37% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 320 | 31,94% | 320 / 31,94% | silk, slik |
| `Leather` | 22 | 2,20% | 20 / 2,00% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 2 | 0,20% | 2 / 0,20% | cashmere, cashmire |
| `Linen` | 48 | 4,79% | 43 / 4,29% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 1002 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 486 (48,50%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 7 | 0,70% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 103 | 10,28% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 28 | 2,79% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 59 | 5,89% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 2 | 0,20% | camo, camouflage, camouflaged |
| `Animal Print` | 7 | 0,70% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 13 | 1,30% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 85 | 8,48% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 263 (26,25%); **bez trafienia:** 739 (73,75%); **trafienia ≥2 wartości:** 38 (3,79%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 100 | 9,98% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 344 | 34,33% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 49 | 4,89% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 430 | 42,91% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 913 (91,12%); **bez trafienia:** 89 (8,88%); **trafienia ≥2 wartości:** 10 (1,00%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 6 | 0,60% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 0 | 0,00% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 177 | 17,66% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 182 (18,16%); **bez trafienia:** 820 (81,84%); **trafienia ≥2 wartości:** 1 (0,10%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 37 | 3,69% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 41 | 4,09% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 77 (7,68%); **bez trafienia:** 925 (92,32%); **trafienia ≥2 wartości:** 1 (0,10%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 477 | 47,60% | crewneck, crew neck, round/rounded neck, jewel neck |
| `Scoop Neck` | 24 | 2,40% | scoop/scooped neck, u-neck, deep round neck |
| `V-Neck` | 95 | 9,48% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 148 | 14,77% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Collared` | 87 | 8,68% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels |
| `Other` | 67 | 6,69% | square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 884 (88,22%); **bez trafienia:** 118 (11,78%); **trafienia ≥2 wartości:** 14 (1,40%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Collared`: Nie liczymy samego collar, ponieważ rib-knit crewneck collar nie oznacza wykładanego kołnierza. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

<a id="knit-sweaters"></a>

## Knit Sweaters

**Dział:** Sweaters. **Mianownik każdej tabeli: 4990 produktów.**

Źródło: `SWEATERS / CREWNECKS` (3645); `SWEATERS / V-NECKS` (339); `SWEATERS / TURTLENECKS` (1006).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 2290 | 45,89% | men, man, male, menswear |
| `Women` | 2700 | 54,11% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 4990 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 2543 | 50,96% | black, ebony, onyx, coal |
| `White` | 1720 | 34,47% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 1066 | 21,36% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 776 | 15,55% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 529 | 10,60% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 536 | 10,74% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 310 | 6,21% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 249 | 4,99% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 337 | 6,75% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 131 | 2,63% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 298 | 5,97% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 118 | 2,36% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 86 | 1,72% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 208 | 4,17% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 4990 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 2512 (50,34%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 1496 | 29,98% | 1496 / 29,98% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 713 | 14,29% | 633 / 12,69% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 261 | 5,23% | 261 / 5,23% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 2969 | 59,50% | 2857 / 57,25% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 712 | 14,27% | 635 / 12,73% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 481 | 9,64% | 480 / 9,62% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 1418 | 28,42% | 1418 / 28,42% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 266 | 5,33% | 266 / 5,33% | silk, slik |
| `Leather` | 68 | 1,36% | 66 / 1,32% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 754 | 15,11% | 754 / 15,11% | cashmere, cashmire |
| `Linen` | 80 | 1,60% | 71 / 1,42% | linen, flax, ramie, hemp |
| `Down` | 3 | 0,06% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 13 | 0,26% | 11 / 0,22% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 4987 (99,94%); **bez trafienia:** 3 (0,06%); **trafienia ≥2 wartości:** 2790 (55,91%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 23 | 0,46% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 677 | 13,57% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 102 | 2,04% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 85 | 1,70% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 21 | 0,42% | camo, camouflage, camouflaged |
| `Animal Print` | 66 | 1,32% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 21 | 0,42% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 1145 | 22,95% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 1843 (36,93%); **bez trafienia:** 3147 (63,07%); **trafienia ≥2 wartości:** 271 (5,43%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 94 | 1,88% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 182 | 3,65% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 73 | 1,46% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 4457 | 89,32% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 4797 (96,13%); **bez trafienia:** 193 (3,87%); **trafienia ≥2 wartości:** 9 (0,18%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 73 | 1,46% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 12 | 0,24% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 574 | 11,50% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 655 (13,13%); **bez trafienia:** 4335 (86,87%); **trafienia ≥2 wartości:** 4 (0,08%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 177 | 3,55% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 29 | 0,58% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 205 (4,11%); **bez trafienia:** 4785 (95,89%); **trafienia ≥2 wartości:** 1 (0,02%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `hood`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `With Hood` | 8 | 0,16% | hood, hooded, hoodie |
| `Without Hood` | 0 | 0,00% | without/no hood, hoodless, non-hooded |

**Co najmniej jedno trafienie:** 8 (0,16%); **bez trafienia:** 4982 (99,84%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `With Hood`: Liczymy również kaptur odpinany/chowany; szeroka reguła może trafić rzadką frazę without hood. `Without Hood`: Brak słowa hood nie jest potwierdzeniem braku kaptura.

### `closure_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Zip` | 12 | 0,24% | zip-up, full zip, zip front/placket, front zip, zip closure at front, two-way zip |
| `Half-Zip` | 8 | 0,16% | half-zip, quarter-zip, partial zip, 1/2 zip, 1/4 zip, short zip placket |
| `Button` | 57 | 1,14% | button front/down/up/placket, front button/snap/toggle, button/snap/hook closure at front |
| `Belted` | 38 | 0,76% | belted, self-tie/tie/belt closure, self-tie belt/waist, tie belt, detachable belt |
| `Open Front` | 1 | 0,02% | open front, no/without closure/fastening, closure-free |
| `Pullover` | 1036 | 20,76% | pullover, pull-over, pull-on, slip-on, over-the-head |
| `Other` | 3 | 0,06% | double-breasted, lace-up front/closure, front buckle/velcro closure |

**Co najmniej jedno trafienie:** 1113 (22,30%); **bez trafienia:** 3877 (77,70%); **trafienia ≥2 wartości:** 40 (0,80%).

Uwagi: `Zip`: Zamek kieszeni lub przy karku nie wystarcza; częściowy zamek może nakładać się z Half-Zip. `Button`: Guziki kieszeni/mankietów i pomocnicze zapięcie z tyłu nie wystarczają. `Belted`: Szeroka obecność paska; audyt nie rozstrzyga, czy jest głównym zapięciem. `Pullover`: Nie przypisujemy automatycznie wszystkim sweaters/sweatshirts ani na podstawie braku zapięcia w tekście. `Other`: Dla Sweaters double-breasted należy do Other; audyt nadal dopuszcza równoległe trafienie Button.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 3221 | 64,55% | crewneck, crew neck, round/rounded neck, jewel neck |
| `V-Neck` | 352 | 7,05% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 1170 | 23,45% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Collared` | 27 | 0,54% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels |
| `Other` | 153 | 3,07% | scoop/scooped neck, u-neck, deep round neck; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 4879 (97,78%); **bez trafienia:** 111 (2,22%); **trafienia ≥2 wartości:** 43 (0,86%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Collared`: Nie liczymy samego collar, ponieważ rib-knit crewneck collar nie oznacza wykładanego kołnierza. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Scoop Neck, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

<a id="sweatshirts"></a>

## Sweatshirts

**Dział:** Sweaters. **Mianownik każdej tabeli: 3432 produktów.**

Źródło: `SWEATERS / SWEATSHIRTS` (3432).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 2140 | 62,35% | men, man, male, menswear |
| `Women` | 1292 | 37,65% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 3432 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 2181 | 63,55% | black, ebony, onyx, coal |
| `White` | 1258 | 36,66% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 1063 | 30,97% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 408 | 11,89% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 465 | 13,55% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 342 | 9,97% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 258 | 7,52% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 248 | 7,23% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 147 | 4,28% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 69 | 2,01% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 243 | 7,08% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 118 | 3,44% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 93 | 2,71% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 288 | 8,39% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 3432 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 2315 (67,45%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 3183 | 92,74% | 3183 / 92,74% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 922 | 26,86% | 809 / 23,57% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 49 | 1,43% | 49 / 1,43% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 139 | 4,05% | 138 / 4,02% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 377 | 10,98% | 304 / 8,86% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 598 | 17,42% | 598 / 17,42% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 355 | 10,34% | 355 / 10,34% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 66 | 1,92% | 66 / 1,92% | silk, slik |
| `Leather` | 84 | 2,45% | 83 / 2,42% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 22 | 0,64% | 22 / 0,64% | cashmere, cashmire |
| `Linen` | 14 | 0,41% | 13 / 0,38% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 2 | 0,06% | 1 / 0,03% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 3428 (99,88%); **bez trafienia:** 4 (0,12%); **trafienia ≥2 wartości:** 1552 (45,22%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 6 | 0,17% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 257 | 7,49% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 31 | 0,90% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 87 | 2,53% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 35 | 1,02% | camo, camouflage, camouflaged |
| `Animal Print` | 158 | 4,60% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 11 | 0,32% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 2036 | 59,32% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 2255 (65,71%); **bez trafienia:** 1177 (34,29%); **trafienia ≥2 wartości:** 339 (9,88%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 10 | 0,29% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 100 | 2,91% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 9 | 0,26% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 3265 | 95,13% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 3384 (98,60%); **bez trafienia:** 48 (1,40%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 15 | 0,44% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 6 | 0,17% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 337 | 9,82% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 357 (10,40%); **bez trafienia:** 3075 (89,60%); **trafienia ≥2 wartości:** 1 (0,03%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 46 | 1,34% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 1 | 0,03% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 47 (1,37%); **bez trafienia:** 3385 (98,63%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `hood`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `With Hood` | 16 | 0,47% | hood, hooded, hoodie |
| `Without Hood` | 0 | 0,00% | without/no hood, hoodless, non-hooded |

**Co najmniej jedno trafienie:** 16 (0,47%); **bez trafienia:** 3416 (99,53%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `With Hood`: Liczymy również kaptur odpinany/chowany; szeroka reguła może trafić rzadką frazę without hood. `Without Hood`: Brak słowa hood nie jest potwierdzeniem braku kaptura.

### `closure_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Zip` | 3 | 0,09% | zip-up, full zip, zip front/placket, front zip, zip closure at front, two-way zip |
| `Half-Zip` | 3 | 0,09% | half-zip, quarter-zip, partial zip, 1/2 zip, 1/4 zip, short zip placket |
| `Button` | 7 | 0,20% | button front/down/up/placket, front button/snap/toggle, button/snap/hook closure at front |
| `Belted` | 7 | 0,20% | belted, self-tie/tie/belt closure, self-tie belt/waist, tie belt, detachable belt |
| `Open Front` | 0 | 0,00% | open front, no/without closure/fastening, closure-free |
| `Pullover` | 1169 | 34,06% | pullover, pull-over, pull-on, slip-on, over-the-head |
| `Other` | 1 | 0,03% | double-breasted, lace-up front/closure, front buckle/velcro closure |

**Co najmniej jedno trafienie:** 1180 (34,38%); **bez trafienia:** 2252 (65,62%); **trafienia ≥2 wartości:** 10 (0,29%).

Uwagi: `Zip`: Zamek kieszeni lub przy karku nie wystarcza; częściowy zamek może nakładać się z Half-Zip. `Button`: Guziki kieszeni/mankietów i pomocnicze zapięcie z tyłu nie wystarczają. `Belted`: Szeroka obecność paska; audyt nie rozstrzyga, czy jest głównym zapięciem. `Pullover`: Nie przypisujemy automatycznie wszystkim sweaters/sweatshirts ani na podstawie braku zapięcia w tekście. `Other`: Dla Sweaters double-breasted należy do Other; audyt nadal dopuszcza równoległe trafienie Button.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 3293 | 95,95% | crewneck, crew neck, round/rounded neck, jewel neck |
| `High Neck` | 49 | 1,43% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Other` | 31 | 0,90% | scoop/scooped neck, u-neck, deep round neck; v-neck, vneck, plunge/plunging, surplice, y-neck; collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 3370 (98,19%); **bez trafienia:** 62 (1,81%); **trafienia ≥2 wartości:** 3 (0,09%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Scoop Neck, V-Neck, Collared, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

<a id="hoodies-zipups"></a>

## Hoodies & Zipups

**Dział:** Sweaters. **Mianownik każdej tabeli: 2779 produktów.**

Źródło: `SWEATERS / HOODIES & ZIPUPS` (2779).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 1965 | 70,71% | men, man, male, menswear |
| `Women` | 814 | 29,29% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 2779 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1938 | 69,74% | black, ebony, onyx, coal |
| `White` | 1072 | 38,58% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 1129 | 40,63% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 277 | 9,97% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 262 | 9,43% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 369 | 13,28% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 167 | 6,01% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 94 | 3,38% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 149 | 5,36% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 62 | 2,23% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 241 | 8,67% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 49 | 1,76% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 29 | 1,04% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 199 | 7,16% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 2779 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 2035 (73,23%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 2378 | 85,57% | 2378 / 85,57% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 779 | 28,03% | 692 / 24,90% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 57 | 2,05% | 57 / 2,05% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 212 | 7,63% | 209 / 7,52% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 296 | 10,65% | 242 / 8,71% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 420 | 15,11% | 419 / 15,08% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 334 | 12,02% | 334 / 12,02% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 44 | 1,58% | 44 / 1,58% | silk, slik |
| `Leather` | 66 | 2,37% | 65 / 2,34% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 53 | 1,91% | 53 / 1,91% | cashmere, cashmire |
| `Linen` | 13 | 0,47% | 12 / 0,43% | linen, flax, ramie, hemp |
| `Down` | 4 | 0,14% | 4 / 0,14% | down, feather, feathers |
| `Fur` | 2 | 0,07% | 1 / 0,04% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 2777 (99,93%); **bez trafienia:** 2 (0,07%); **trafienia ≥2 wartości:** 1249 (44,94%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 5 | 0,18% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 292 | 10,51% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 27 | 0,97% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 26 | 0,94% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 25 | 0,90% | camo, camouflage, camouflaged |
| `Animal Print` | 34 | 1,22% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 4 | 0,14% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 1588 | 57,14% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 1747 (62,86%); **bez trafienia:** 1032 (37,14%); **trafienia ≥2 wartości:** 245 (8,82%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 35 | 1,26% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 20 | 0,72% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 6 | 0,22% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 2646 | 95,21% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 2704 (97,30%); **bez trafienia:** 75 (2,70%); **trafienia ≥2 wartości:** 3 (0,11%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 23 | 0,83% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 2 | 0,07% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 332 | 11,95% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 354 (12,74%); **bez trafienia:** 2425 (87,26%); **trafienia ≥2 wartości:** 3 (0,11%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 48 | 1,73% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 3 | 0,11% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 51 (1,84%); **bez trafienia:** 2728 (98,16%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `hood`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `With Hood` | 2400 | 86,36% | hood, hooded, hoodie |
| `Without Hood` | 0 | 0,00% | without/no hood, hoodless, non-hooded |

**Co najmniej jedno trafienie:** 2400 (86,36%); **bez trafienia:** 379 (13,64%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `With Hood`: Liczymy również kaptur odpinany/chowany; szeroka reguła może trafić rzadką frazę without hood. `Without Hood`: Brak słowa hood nie jest potwierdzeniem braku kaptura.

### `closure_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Zip` | 1035 | 37,24% | zip-up, full zip, zip front/placket, front zip, zip closure at front, two-way zip |
| `Half-Zip` | 91 | 3,27% | half-zip, quarter-zip, partial zip, 1/2 zip, 1/4 zip, short zip placket |
| `Button` | 28 | 1,01% | button front/down/up/placket, front button/snap/toggle, button/snap/hook closure at front |
| `Belted` | 18 | 0,65% | belted, self-tie/tie/belt closure, self-tie belt/waist, tie belt, detachable belt |
| `Open Front` | 6 | 0,22% | open front, no/without closure/fastening, closure-free |
| `Pullover` | 88 | 3,17% | pullover, pull-over, pull-on, slip-on, over-the-head |
| `Other` | 6 | 0,22% | double-breasted, lace-up front/closure, front buckle/velcro closure |

**Co najmniej jedno trafienie:** 1147 (41,27%); **bez trafienia:** 1632 (58,73%); **trafienia ≥2 wartości:** 101 (3,63%).

Uwagi: `Zip`: Zamek kieszeni lub przy karku nie wystarcza; częściowy zamek może nakładać się z Half-Zip. `Button`: Guziki kieszeni/mankietów i pomocnicze zapięcie z tyłu nie wystarczają. `Belted`: Szeroka obecność paska; audyt nie rozstrzyga, czy jest głównym zapięciem. `Pullover`: Nie przypisujemy automatycznie wszystkim sweaters/sweatshirts ani na podstawie braku zapięcia w tekście. `Other`: Dla Sweaters double-breasted należy do Other; audyt nadal dopuszcza równoległe trafienie Button.

<a id="cardigans"></a>

## Cardigans

**Dział:** Sweaters. **Mianownik każdej tabeli: 904 produktów.**

Źródło: `SWEATERS / CARDIGANS` (904).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 401 | 44,36% | men, man, male, menswear |
| `Women` | 503 | 55,64% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 904 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 432 | 47,79% | black, ebony, onyx, coal |
| `White` | 316 | 34,96% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 259 | 28,65% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 182 | 20,13% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 92 | 10,18% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 100 | 11,06% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 34 | 3,76% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 32 | 3,54% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 56 | 6,19% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 25 | 2,77% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 61 | 6,75% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 6 | 0,66% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 6 | 0,66% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 39 | 4,31% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 904 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 493 (54,54%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 211 | 23,34% | 211 / 23,34% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 88 | 9,73% | 82 / 9,07% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 43 | 4,76% | 43 / 4,76% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 594 | 65,71% | 567 / 62,72% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 90 | 9,96% | 71 / 7,85% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 49 | 5,42% | 49 / 5,42% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 210 | 23,23% | 210 / 23,23% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 70 | 7,74% | 70 / 7,74% | silk, slik |
| `Leather` | 9 | 1,00% | 9 / 1,00% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 163 | 18,03% | 163 / 18,03% | cashmere, cashmire |
| `Linen` | 12 | 1,33% | 11 / 1,22% | linen, flax, ramie, hemp |
| `Down` | 2 | 0,22% | 2 / 0,22% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 902 (99,78%); **bez trafienia:** 2 (0,22%); **trafienia ≥2 wartości:** 421 (46,57%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 2 | 0,22% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 179 | 19,80% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 22 | 2,43% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 24 | 2,65% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 0 | 0,00% | camo, camouflage, camouflaged |
| `Animal Print` | 11 | 1,22% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 11 | 1,22% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 183 | 20,24% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 364 (40,27%); **bez trafienia:** 540 (59,73%); **trafienia ≥2 wartości:** 61 (6,75%).

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 5 | 0,55% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 11 | 1,22% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 6 | 0,66% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 820 | 90,71% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 840 (92,92%); **bez trafienia:** 64 (7,08%); **trafienia ≥2 wartości:** 2 (0,22%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 4 | 0,44% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 2 | 0,22% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 88 | 9,73% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 93 (10,29%); **bez trafienia:** 811 (89,71%); **trafienia ≥2 wartości:** 1 (0,11%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 29 | 3,21% | cropped/crop, bolero, shrug, midriff-baring, short-length |
| `Regular` | 0 | 0,00% | regular/standard length, hip-length, waist-length |
| `Longline` | 39 | 4,31% | longline, long-length, elongated, extended hem, tunic, duster, long cardigan, thigh-length |

**Co najmniej jedno trafienie:** 68 (7,52%); **bez trafienia:** 836 (92,48%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Cropped sleeve nie jest długością całego ubrania; złożone opisy nadal mogą dawać fałszywe trafienia. `Regular`: Nie wynika z braku cropped/longline; granica waist-length vs Cropped jest przybliżona.

### `hood`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `With Hood` | 16 | 1,77% | hood, hooded, hoodie |
| `Without Hood` | 0 | 0,00% | without/no hood, hoodless, non-hooded |

**Co najmniej jedno trafienie:** 16 (1,77%); **bez trafienia:** 888 (98,23%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `With Hood`: Liczymy również kaptur odpinany/chowany; szeroka reguła może trafić rzadką frazę without hood. `Without Hood`: Brak słowa hood nie jest potwierdzeniem braku kaptura.

### `closure_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Zip` | 24 | 2,65% | zip-up, full zip, zip front/placket, front zip, zip closure at front, two-way zip |
| `Half-Zip` | 0 | 0,00% | half-zip, quarter-zip, partial zip, 1/2 zip, 1/4 zip, short zip placket |
| `Button` | 574 | 63,50% | button front/down/up/placket, front button/snap/toggle, button/snap/hook closure at front |
| `Belted` | 34 | 3,76% | belted, self-tie/tie/belt closure, self-tie belt/waist, tie belt, detachable belt |
| `Open Front` | 84 | 9,29% | open front, no/without closure/fastening, closure-free |
| `Pullover` | 3 | 0,33% | pullover, pull-over, pull-on, slip-on, over-the-head |
| `Other` | 10 | 1,11% | double-breasted, lace-up front/closure, front buckle/velcro closure |

**Co najmniej jedno trafienie:** 701 (77,54%); **bez trafienia:** 203 (22,46%); **trafienia ≥2 wartości:** 27 (2,99%).

Uwagi: `Zip`: Zamek kieszeni lub przy karku nie wystarcza; częściowy zamek może nakładać się z Half-Zip. `Button`: Guziki kieszeni/mankietów i pomocnicze zapięcie z tyłu nie wystarczają. `Belted`: Szeroka obecność paska; audyt nie rozstrzyga, czy jest głównym zapięciem. `Pullover`: Nie przypisujemy automatycznie wszystkim sweaters/sweatshirts ani na podstawie braku zapięcia w tekście. `Other`: Dla Sweaters double-breasted należy do Other; audyt nadal dopuszcza równoległe trafienie Button.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 124 | 13,72% | crewneck, crew neck, round/rounded neck, jewel neck |
| `V-Neck` | 513 | 56,75% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 25 | 2,77% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Collared` | 83 | 9,18% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels |
| `Other` | 3 | 0,33% | scoop/scooped neck, u-neck, deep round neck; square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 738 (81,64%); **bez trafienia:** 166 (18,36%); **trafienia ≥2 wartości:** 10 (1,11%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Collared`: Nie liczymy samego collar, ponieważ rib-knit crewneck collar nie oznacza wykładanego kołnierza. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Scoop Neck, Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

<a id="trousers"></a>

## Trousers

**Dział:** Pants. **Mianownik każdej tabeli: 3916 produktów.**

Źródło: `PANTS / TROUSERS` (3744); `PANTS / LEATHER PANTS` (172).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 2293 | 58,55% | men, man, male, menswear |
| `Women` | 1623 | 41,45% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 3916 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 2535 | 64,73% | black, ebony, onyx, coal |
| `White` | 580 | 14,81% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 805 | 20,56% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 641 | 16,37% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 308 | 7,87% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 133 | 3,40% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 246 | 6,28% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 62 | 1,58% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 243 | 6,21% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 108 | 2,76% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 171 | 4,37% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 35 | 0,89% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 26 | 0,66% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 32 | 0,82% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 3915 (99,97%); **bez trafienia:** 1 (0,03%); **trafienia ≥2 wartości:** 1474 (37,64%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 1926 | 49,18% | 1926 / 49,18% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 1067 | 27,25% | 913 / 23,31% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 34 | 0,87% | 34 / 0,87% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 1583 | 40,42% | 1578 / 40,30% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 1154 | 29,47% | 759 / 19,38% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 977 | 24,95% | 973 / 24,85% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 517 | 13,20% | 517 / 13,20% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 292 | 7,46% | 292 / 7,46% | silk, slik |
| `Leather` | 217 | 5,54% | 214 / 5,46% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 46 | 1,17% | 46 / 1,17% | cashmere, cashmire |
| `Linen` | 202 | 5,16% | 191 / 4,88% | linen, flax, ramie, hemp |
| `Down` | 1 | 0,03% | 1 / 0,03% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 3910 (99,85%); **bez trafienia:** 6 (0,15%); **trafienia ≥2 wartości:** 2568 (65,58%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 8 | 0,20% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 242 | 6,18% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 125 | 3,19% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 73 | 1,86% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 24 | 0,61% | camo, camouflage, camouflaged |
| `Animal Print` | 18 | 0,46% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 18 | 0,46% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 449 | 11,47% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 897 (22,91%); **bez trafienia:** 3019 (77,09%); **trafienia ≥2 wartości:** 58 (1,48%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Skinny` | 200 | 5,11% | skinny, spray-on, second-skin, skin-tight |
| `Slim` | 1506 | 38,46% | slim, fitted, form-fitting |
| `Regular` | 5 | 0,13% | regular/classic/standard fit |
| `Relaxed` | 545 | 13,92% | relaxed, loose, baggy, boyfriend, slouchy, oversized |

**Co najmniej jedno trafienie:** 2233 (57,02%); **bez trafienia:** 1683 (42,98%); **trafienia ≥2 wartości:** 23 (0,59%).

Uwagi: `Slim`: Audyt nie rozstrzyga, czy określenie dotyczy bioder/ud, czy nogawki. `Regular`: Nie utożsamiamy straight-leg z Regular. `Relaxed`: Nie utożsamiamy wide-leg z luźnym dopasowaniem w biodrach.

### `leg_shape`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Straight` | 258 | 6,59% | straight, straight-leg/cut/fit |
| `Tapered` | 360 | 9,19% | tapered/tapering, carrot |
| `Wide-Leg` | 667 | 17,03% | wide-leg, palazzo, hakama, culottes |
| `Flared` | 86 | 2,20% | flare/flared/flaring, bootcut, bell-bottom, kick-flare |

**Co najmniej jedno trafienie:** 1340 (34,22%); **bez trafienia:** 2576 (65,78%); **trafienia ≥2 wartości:** 30 (0,77%).

Uwagi: `Straight`: Szerokie straight może dotyczyć innego fragmentu opisu. `Wide-Leg`: Culottes są szerokim wskaźnikiem; nie każdy taki produkt ma szeroką nogawkę.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 723 | 18,46% | cropped, ankle-length/cropped, capri, 3/4 length, seven-eighths, 7/8, culotte, calf-length, pedal pusher |
| `Full-Length` | 4 | 0,10% | full-length, regular/standard/long length, floor-length, stacked hem |

**Co najmniej jedno trafienie:** 726 (18,54%); **bez trafienia:** 3190 (81,46%); **trafienia ≥2 wartości:** 1 (0,03%).

Uwagi: `Cropped`: Ankle-length/culotte są szerokimi wskaźnikami zgodnie z obecnym mappingiem. `Full-Length`: Tylko jawna wzmianka; standardowa długość spodni często nie jest opisywana.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 365 | 9,32% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 385 | 9,83% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 57 | 1,46% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 807 (20,61%); **bez trafienia:** 3109 (79,39%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

### `waistband_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Structured` | 2977 | 76,02% | structured/tailored/fixed/rigid waist, non-elastic/non-stretch waistband, belt loops, zip fly, button fly |
| `Elasticized` | 816 | 20,84% | elastic/elasticated/elasticized waistband, elasticized back waist, rib-knit/ribbed/stretch/smocked waistband |
| `Other` | n/d | n/d | — |

**Co najmniej jedno trafienie:** 3427 (87,51%); **bez trafienia:** 489 (12,49%); **trafienia ≥2 wartości:** 366 (9,35%).

Uwagi: `Structured`: Szlufki i rozporek są tutaj celowo szerokimi sygnałami zastępczymi; występują również przy elastycznym pasie. W audycie mogą jednocześnie trafić do Structured i Elasticized; nie stanowią reguły produkcyjnej ekstrakcji. `Other`: Brak wiarygodnego pozytywnego keywordu rozdzielającego Other od Structured/Elasticized; samo wiązanie nie wystarcza.

### `cuff_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Open Hem` | 403 | 10,29% | open/plain/straight/raw/unfinished/frayed hem, unhemmed, rolled/turned-up cuff |
| `Elasticized Cuff` | 188 | 4,80% | elasticized/elasticated cuffs/hem/ankle, rib-knit/ribbed cuffs |
| `Zippered Cuff` | 90 | 2,30% | zippered cuff/hem, ankle zip, zip vent/opening at cuff, zip at hem |
| `Other` | 17 | 0,43% | drawstring/drawcord/bungee/toggle/velcro cuff/hem, regulacja przy kostce |

**Co najmniej jedno trafienie:** 696 (17,77%); **bez trafienia:** 3220 (82,23%); **trafienia ≥2 wartości:** 2 (0,05%).

Uwagi: `Open Hem`: Szerokie dodatnie wskazówki zwykłego dołu; nie zastępujemy brakujących informacji domyślnym Open Hem. `Other`: Nie liczymy sznurka w pasie; gumka może jednocześnie dać trafienie Elasticized Cuff.

<a id="cargo-pants"></a>

## Cargo Pants

**Dział:** Pants. **Mianownik każdej tabeli: 188 produktów.**

Źródło: `PANTS / CARGO PANTS` (188).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 188 | 100,00% | men, man, male, menswear |
| `Women` | 0 | 0,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 188 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 133 | 70,74% | black, ebony, onyx, coal |
| `White` | 11 | 5,85% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 64 | 34,04% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 23 | 12,23% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 7 | 3,72% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 2 | 1,06% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 33 | 17,55% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 0 | 0,00% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 29 | 15,43% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 6 | 3,19% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 9 | 4,79% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 0 | 0,00% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 1 | 0,53% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 1 | 0,53% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 188 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 98 (52,13%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 164 | 87,23% | 164 / 87,23% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 48 | 25,53% | 29 / 15,43% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 3 | 1,60% | 3 / 1,60% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 26 | 13,83% | 26 / 13,83% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 27 | 14,36% | 25 / 13,30% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 67 | 35,64% | 67 / 35,64% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 26 | 13,83% | 26 / 13,83% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 4 | 2,13% | 4 / 2,13% | silk, slik |
| `Leather` | 1 | 0,53% | 1 / 0,53% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 0 | 0,00% | 0 / 0,00% | cashmere, cashmire |
| `Linen` | 6 | 3,19% | 6 / 3,19% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 188 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 132 (70,21%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 0 | 0,00% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 9 | 4,79% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 0 | 0,00% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 0 | 0,00% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 9 | 4,79% | camo, camouflage, camouflaged |
| `Animal Print` | 1 | 0,53% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 0 | 0,00% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 55 | 29,26% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 67 (35,64%); **bez trafienia:** 121 (64,36%); **trafienia ≥2 wartości:** 6 (3,19%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Skinny` | 12 | 6,38% | skinny, spray-on, second-skin, skin-tight |
| `Slim` | 110 | 58,51% | slim, fitted, form-fitting |
| `Regular` | 0 | 0,00% | regular/classic/standard fit |
| `Relaxed` | 34 | 18,09% | relaxed, loose, baggy, boyfriend, slouchy, oversized |

**Co najmniej jedno trafienie:** 156 (82,98%); **bez trafienia:** 32 (17,02%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Slim`: Audyt nie rozstrzyga, czy określenie dotyczy bioder/ud, czy nogawki. `Regular`: Nie utożsamiamy straight-leg z Regular. `Relaxed`: Nie utożsamiamy wide-leg z luźnym dopasowaniem w biodrach.

### `leg_shape`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Straight` | 5 | 2,66% | straight, straight-leg/cut/fit |
| `Tapered` | 9 | 4,79% | tapered/tapering, carrot |
| `Wide-Leg` | 4 | 2,13% | wide-leg, palazzo, hakama, culottes |
| `Flared` | 0 | 0,00% | flare/flared/flaring, bootcut, bell-bottom, kick-flare |

**Co najmniej jedno trafienie:** 18 (9,57%); **bez trafienia:** 170 (90,43%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Straight`: Szerokie straight może dotyczyć innego fragmentu opisu. `Wide-Leg`: Culottes są szerokim wskaźnikiem; nie każdy taki produkt ma szeroką nogawkę.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 15 | 7,98% | cropped, ankle-length/cropped, capri, 3/4 length, seven-eighths, 7/8, culotte, calf-length, pedal pusher |
| `Full-Length` | 0 | 0,00% | full-length, regular/standard/long length, floor-length, stacked hem |

**Co najmniej jedno trafienie:** 15 (7,98%); **bez trafienia:** 173 (92,02%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Ankle-length/culotte są szerokimi wskaźnikami zgodnie z obecnym mappingiem. `Full-Length`: Tylko jawna wzmianka; standardowa długość spodni często nie jest opisywana.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 5 | 2,66% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 26 | 13,83% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 3 | 1,60% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 34 (18,09%); **bez trafienia:** 154 (81,91%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

### `waistband_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Structured` | 161 | 85,64% | structured/tailored/fixed/rigid waist, non-elastic/non-stretch waistband, belt loops, zip fly, button fly |
| `Elasticized` | 40 | 21,28% | elastic/elasticated/elasticized waistband, elasticized back waist, rib-knit/ribbed/stretch/smocked waistband |
| `Other` | n/d | n/d | — |

**Co najmniej jedno trafienie:** 171 (90,96%); **bez trafienia:** 17 (9,04%); **trafienia ≥2 wartości:** 30 (15,96%).

Uwagi: `Structured`: Szlufki i rozporek są tutaj celowo szerokimi sygnałami zastępczymi; występują również przy elastycznym pasie. W audycie mogą jednocześnie trafić do Structured i Elasticized; nie stanowią reguły produkcyjnej ekstrakcji. `Other`: Brak wiarygodnego pozytywnego keywordu rozdzielającego Other od Structured/Elasticized; samo wiązanie nie wystarcza.

### `cuff_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Open Hem` | 6 | 3,19% | open/plain/straight/raw/unfinished/frayed hem, unhemmed, rolled/turned-up cuff |
| `Elasticized Cuff` | 46 | 24,47% | elasticized/elasticated cuffs/hem/ankle, rib-knit/ribbed cuffs |
| `Zippered Cuff` | 3 | 1,60% | zippered cuff/hem, ankle zip, zip vent/opening at cuff, zip at hem |
| `Other` | 4 | 2,13% | drawstring/drawcord/bungee/toggle/velcro cuff/hem, regulacja przy kostce |

**Co najmniej jedno trafienie:** 59 (31,38%); **bez trafienia:** 129 (68,62%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Open Hem`: Szerokie dodatnie wskazówki zwykłego dołu; nie zastępujemy brakujących informacji domyślnym Open Hem. `Other`: Nie liczymy sznurka w pasie; gumka może jednocześnie dać trafienie Elasticized Cuff.

<a id="sweatpants-lounge-pants"></a>

## Sweatpants & Lounge Pants

**Dział:** Pants. **Mianownik każdej tabeli: 2136 produktów.**

Źródło: `PANTS / SWEATPANTS` (1431); `PANTS / LOUNGE PANTS` (705).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 1431 | 66,99% | men, man, male, menswear |
| `Women` | 705 | 33,01% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 2136 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1436 | 67,23% | black, ebony, onyx, coal |
| `White` | 612 | 28,65% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 688 | 32,21% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 269 | 12,59% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 156 | 7,30% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 153 | 7,16% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 95 | 4,45% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 38 | 1,78% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 172 | 8,05% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 32 | 1,50% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 75 | 3,51% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 31 | 1,45% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 16 | 0,75% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 51 | 2,39% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 2136 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 1207 (56,51%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 1580 | 73,97% | 1580 / 73,97% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 715 | 33,47% | 629 / 29,45% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 53 | 2,48% | 52 / 2,43% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 243 | 11,38% | 240 / 11,24% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 327 | 15,31% | 243 / 11,38% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 410 | 19,19% | 409 / 19,15% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 370 | 17,32% | 370 / 17,32% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 56 | 2,62% | 56 / 2,62% | silk, slik |
| `Leather` | 38 | 1,78% | 35 / 1,64% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 31 | 1,45% | 31 / 1,45% | cashmere, cashmire |
| `Linen` | 22 | 1,03% | 22 / 1,03% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 2 | 0,09% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 2134 (99,91%); **bez trafienia:** 2 (0,09%); **trafienia ≥2 wartości:** 1133 (53,04%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 4 | 0,19% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 272 | 12,73% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 15 | 0,70% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 21 | 0,98% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 14 | 0,66% | camo, camouflage, camouflaged |
| `Animal Print` | 19 | 0,89% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 5 | 0,23% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 818 | 38,30% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 974 (45,60%); **bez trafienia:** 1162 (54,40%); **trafienia ≥2 wartości:** 188 (8,80%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Skinny` | 51 | 2,39% | skinny, spray-on, second-skin, skin-tight |
| `Slim` | 907 | 42,46% | slim, fitted, form-fitting |
| `Regular` | 2 | 0,09% | regular/classic/standard fit |
| `Relaxed` | 617 | 28,89% | relaxed, loose, baggy, boyfriend, slouchy, oversized |

**Co najmniej jedno trafienie:** 1562 (73,13%); **bez trafienia:** 574 (26,87%); **trafienia ≥2 wartości:** 15 (0,70%).

Uwagi: `Slim`: Audyt nie rozstrzyga, czy określenie dotyczy bioder/ud, czy nogawki. `Regular`: Nie utożsamiamy straight-leg z Regular. `Relaxed`: Nie utożsamiamy wide-leg z luźnym dopasowaniem w biodrach.

### `leg_shape`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Straight` | 41 | 1,92% | straight, straight-leg/cut/fit |
| `Tapered` | 107 | 5,01% | tapered/tapering, carrot |
| `Wide-Leg` | 57 | 2,67% | wide-leg, palazzo, hakama, culottes |
| `Flared` | 7 | 0,33% | flare/flared/flaring, bootcut, bell-bottom, kick-flare |

**Co najmniej jedno trafienie:** 212 (9,93%); **bez trafienia:** 1924 (90,07%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Straight`: Szerokie straight może dotyczyć innego fragmentu opisu. `Wide-Leg`: Culottes są szerokim wskaźnikiem; nie każdy taki produkt ma szeroką nogawkę.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 178 | 8,33% | cropped, ankle-length/cropped, capri, 3/4 length, seven-eighths, 7/8, culotte, calf-length, pedal pusher |
| `Full-Length` | 0 | 0,00% | full-length, regular/standard/long length, floor-length, stacked hem |

**Co najmniej jedno trafienie:** 178 (8,33%); **bez trafienia:** 1958 (91,67%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Ankle-length/culotte są szerokimi wskaźnikami zgodnie z obecnym mappingiem. `Full-Length`: Tylko jawna wzmianka; standardowa długość spodni często nie jest opisywana.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 45 | 2,11% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 137 | 6,41% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 9 | 0,42% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 191 (8,94%); **bez trafienia:** 1945 (91,06%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

### `waistband_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Structured` | 462 | 21,63% | structured/tailored/fixed/rigid waist, non-elastic/non-stretch waistband, belt loops, zip fly, button fly |
| `Elasticized` | 1795 | 84,04% | elastic/elasticated/elasticized waistband, elasticized back waist, rib-knit/ribbed/stretch/smocked waistband |
| `Other` | n/d | n/d | — |

**Co najmniej jedno trafienie:** 1911 (89,47%); **bez trafienia:** 225 (10,53%); **trafienia ≥2 wartości:** 346 (16,20%).

Uwagi: `Structured`: Szlufki i rozporek są tutaj celowo szerokimi sygnałami zastępczymi; występują również przy elastycznym pasie. W audycie mogą jednocześnie trafić do Structured i Elasticized; nie stanowią reguły produkcyjnej ekstrakcji. `Other`: Brak wiarygodnego pozytywnego keywordu rozdzielającego Other od Structured/Elasticized; samo wiązanie nie wystarcza.

### `cuff_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Open Hem` | 17 | 0,80% | open/plain/straight/raw/unfinished/frayed hem, unhemmed, rolled/turned-up cuff |
| `Elasticized Cuff` | 819 | 38,34% | elasticized/elasticated cuffs/hem/ankle, rib-knit/ribbed cuffs |
| `Zippered Cuff` | 25 | 1,17% | zippered cuff/hem, ankle zip, zip vent/opening at cuff, zip at hem |
| `Other` | 17 | 0,80% | drawstring/drawcord/bungee/toggle/velcro cuff/hem, regulacja przy kostce |

**Co najmniej jedno trafienie:** 877 (41,06%); **bez trafienia:** 1259 (58,94%); **trafienia ≥2 wartości:** 1 (0,05%).

Uwagi: `Open Hem`: Szerokie dodatnie wskazówki zwykłego dołu; nie zastępujemy brakujących informacji domyślnym Open Hem. `Other`: Nie liczymy sznurka w pasie; gumka może jednocześnie dać trafienie Elasticized Cuff.

<a id="jeans"></a>

## Jeans

**Dział:** Pants. **Mianownik każdej tabeli: 3704 produktów.**

Źródło: `JEANS / JEANS` (3704).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 2122 | 57,29% | men, man, male, menswear |
| `Women` | 1582 | 42,71% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 3704 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1718 | 46,38% | black, ebony, onyx, coal |
| `White` | 688 | 18,57% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 1434 | 38,71% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 217 | 5,86% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 2009 | 54,24% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 317 | 8,56% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 79 | 2,13% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 42 | 1,13% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 1213 | 32,75% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 523 | 14,12% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 644 | 17,39% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 168 | 4,54% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 10 | 0,27% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 33 | 0,89% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 3704 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 2890 (78,02%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 3694 | 99,73% | 3694 / 99,73% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 983 | 26,54% | 612 / 16,52% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 7 | 0,19% | 7 / 0,19% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 17 | 0,46% | 17 / 0,46% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 130 | 3,51% | 62 / 1,67% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 2029 | 54,78% | 2024 / 54,64% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 38 | 1,03% | 38 / 1,03% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 9 | 0,24% | 9 / 0,24% | silk, slik |
| `Leather` | 122 | 3,29% | 122 / 3,29% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 3 | 0,08% | 3 / 0,08% | cashmere, cashmire |
| `Linen` | 10 | 0,27% | 10 / 0,27% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 1 | 0,03% | 1 / 0,03% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 3704 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 2554 (68,95%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 1 | 0,03% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 30 | 0,81% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 18 | 0,49% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 16 | 0,43% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 10 | 0,27% | camo, camouflage, camouflaged |
| `Animal Print` | 12 | 0,32% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 6 | 0,16% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 2426 | 65,50% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 2449 (66,12%); **bez trafienia:** 1255 (33,88%); **trafienia ≥2 wartości:** 66 (1,78%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Skinny` | 1338 | 36,12% | skinny, spray-on, second-skin, skin-tight |
| `Slim` | 1527 | 41,23% | slim, fitted, form-fitting |
| `Regular` | 2 | 0,05% | regular/classic/standard fit |
| `Relaxed` | 292 | 7,88% | relaxed, loose, baggy, boyfriend, slouchy, oversized |

**Co najmniej jedno trafienie:** 3014 (81,37%); **bez trafienia:** 690 (18,63%); **trafienia ≥2 wartości:** 136 (3,67%).

Uwagi: `Slim`: Audyt nie rozstrzyga, czy określenie dotyczy bioder/ud, czy nogawki. `Regular`: Nie utożsamiamy straight-leg z Regular. `Relaxed`: Nie utożsamiamy wide-leg z luźnym dopasowaniem w biodrach.

### `leg_shape`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Straight` | 293 | 7,91% | straight, straight-leg/cut/fit |
| `Tapered` | 191 | 5,16% | tapered/tapering, carrot |
| `Wide-Leg` | 155 | 4,18% | wide-leg, palazzo, hakama, culottes |
| `Flared` | 139 | 3,75% | flare/flared/flaring, bootcut, bell-bottom, kick-flare |

**Co najmniej jedno trafienie:** 768 (20,73%); **bez trafienia:** 2936 (79,27%); **trafienia ≥2 wartości:** 10 (0,27%).

Uwagi: `Straight`: Szerokie straight może dotyczyć innego fragmentu opisu. `Wide-Leg`: Culottes są szerokim wskaźnikiem; nie każdy taki produkt ma szeroką nogawkę.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Cropped` | 489 | 13,20% | cropped, ankle-length/cropped, capri, 3/4 length, seven-eighths, 7/8, culotte, calf-length, pedal pusher |
| `Full-Length` | 0 | 0,00% | full-length, regular/standard/long length, floor-length, stacked hem |

**Co najmniej jedno trafienie:** 489 (13,20%); **bez trafienia:** 3215 (86,80%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Cropped`: Ankle-length/culotte są szerokimi wskaźnikami zgodnie z obecnym mappingiem. `Full-Length`: Tylko jawna wzmianka; standardowa długość spodni często nie jest opisywana.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 509 | 13,74% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 1179 | 31,83% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 265 | 7,15% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 1948 (52,59%); **bez trafienia:** 1756 (47,41%); **trafienia ≥2 wartości:** 5 (0,13%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

### `waistband_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Structured` | 3486 | 94,11% | structured/tailored/fixed/rigid waist, non-elastic/non-stretch waistband, belt loops, zip fly, button fly |
| `Elasticized` | 30 | 0,81% | elastic/elasticated/elasticized waistband, elasticized back waist, rib-knit/ribbed/stretch/smocked waistband |
| `Other` | n/d | n/d | — |

**Co najmniej jedno trafienie:** 3492 (94,28%); **bez trafienia:** 212 (5,72%); **trafienia ≥2 wartości:** 24 (0,65%).

Uwagi: `Structured`: Szlufki i rozporek są tutaj celowo szerokimi sygnałami zastępczymi; występują również przy elastycznym pasie. W audycie mogą jednocześnie trafić do Structured i Elasticized; nie stanowią reguły produkcyjnej ekstrakcji. `Other`: Brak wiarygodnego pozytywnego keywordu rozdzielającego Other od Structured/Elasticized; samo wiązanie nie wystarcza.

### `cuff_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Open Hem` | 93 | 2,51% | open/plain/straight/raw/unfinished/frayed hem, unhemmed, rolled/turned-up cuff |
| `Elasticized Cuff` | 13 | 0,35% | elasticized/elasticated cuffs/hem/ankle, rib-knit/ribbed cuffs |
| `Zippered Cuff` | 47 | 1,27% | zippered cuff/hem, ankle zip, zip vent/opening at cuff, zip at hem |
| `Other` | 0 | 0,00% | drawstring/drawcord/bungee/toggle/velcro cuff/hem, regulacja przy kostce |

**Co najmniej jedno trafienie:** 153 (4,13%); **bez trafienia:** 3551 (95,87%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Open Hem`: Szerokie dodatnie wskazówki zwykłego dołu; nie zastępujemy brakujących informacji domyślnym Open Hem. `Other`: Nie liczymy sznurka w pasie; gumka może jednocześnie dać trafienie Elasticized Cuff.

### `distressing`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Clean` | 148 | 4,00% | raw denim, unwashed, clean/uniform wash, dark rinse, selvedge, rigid denim |
| `Faded` | 2320 | 62,63% | faded/fading, whiskering, stonewashed, acid wash, bleached, vintage wash, worn-in, honeycombs, fade |
| `Distressed` | 1498 | 40,44% | distressed, ripped/rips, torn, slashed, destroyed, frayed, abrasion, knee slits, holes, paint splatter, patched |

**Co najmniej jedno trafienie:** 2651 (71,57%); **bez trafienia:** 1053 (28,43%); **trafienia ≥2 wartości:** 1279 (34,53%).

Uwagi: `Clean`: Selvedge/rigid są szerokimi proxy i mogą występować z przetarciami; brak słów o uszkodzeniach nie daje Clean. `Distressed`: Szerokie ślady uszkodzenia/napraw; bez pierwszeństwa nad Faded.

<a id="shorts"></a>

## Shorts

**Dział:** Shorts. **Mianownik każdej tabeli: 2053 produktów.**

Źródło: `SHORTS / SHORTS` (2053).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 1307 | 63,66% | men, man, male, menswear |
| `Women` | 746 | 36,34% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 2053 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1227 | 59,77% | black, ebony, onyx, coal |
| `White` | 543 | 26,45% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 522 | 25,43% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 276 | 13,44% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 382 | 18,61% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 148 | 7,21% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 135 | 6,58% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 73 | 3,56% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 284 | 13,83% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 72 | 3,51% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 146 | 7,11% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 53 | 2,58% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 31 | 1,51% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 51 | 2,48% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 2051 (99,90%); **bez trafienia:** 2 (0,10%); **trafienia ≥2 wartości:** 1162 (56,60%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 1452 | 70,73% | 1452 / 70,73% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 553 | 26,94% | 483 / 23,53% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 19 | 0,93% | 19 / 0,93% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 223 | 10,86% | 221 / 10,76% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 356 | 17,34% | 235 / 11,45% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 403 | 19,63% | 399 / 19,43% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 288 | 14,03% | 288 / 14,03% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 150 | 7,31% | 150 / 7,31% | silk, slik |
| `Leather` | 93 | 4,53% | 87 / 4,24% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 8 | 0,39% | 8 / 0,39% | cashmere, cashmire |
| `Linen` | 80 | 3,90% | 76 / 3,70% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 2052 (99,95%); **bez trafienia:** 1 (0,05%); **trafienia ≥2 wartości:** 1083 (52,75%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 6 | 0,29% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 178 | 8,67% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 54 | 2,63% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 69 | 3,36% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 17 | 0,83% | camo, camouflage, camouflaged |
| `Animal Print` | 20 | 0,97% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 11 | 0,54% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 652 | 31,76% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 876 (42,67%); **bez trafienia:** 1177 (57,33%); **trafienia ≥2 wartości:** 126 (6,14%).

### `fit`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slim` | 373 | 18,17% | slim, fitted, form-fitting, figure-hugging, bodycon, sheath, tailored fit, skinny |
| `Regular` | 14 | 0,68% | regular/classic/standard fit, straight-cut |
| `Relaxed` | 908 | 44,23% | relaxed, oversized, loose, boxy, slouchy, boyfriend, baggy, cocoon, dropped shoulder, wide-cut, dolman |

**Co najmniej jedno trafienie:** 1285 (62,59%); **bez trafienia:** 768 (37,41%); **trafienia ≥2 wartości:** 10 (0,49%).

Uwagi: `Regular`: Tylko jawne wskazówki; brak innych określeń nie oznacza Regular. `Relaxed`: Dropped shoulder i dolman są szerokimi wskaźnikami konstrukcji, nie dowodem luźnego dopasowania.

### `waistband_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Structured` | 1119 | 54,51% | structured/tailored/fixed/rigid waist, non-elastic/non-stretch waistband, belt loops, zip fly, button fly |
| `Elasticized` | 943 | 45,93% | elastic/elasticated/elasticized waistband, elasticized back waist, rib-knit/ribbed/stretch/smocked waistband |
| `Other` | n/d | n/d | — |

**Co najmniej jedno trafienie:** 1794 (87,38%); **bez trafienia:** 259 (12,62%); **trafienia ≥2 wartości:** 268 (13,05%).

Uwagi: `Structured`: Szlufki i rozporek są tutaj celowo szerokimi sygnałami zastępczymi; występują również przy elastycznym pasie. W audycie mogą jednocześnie trafić do Structured i Elasticized; nie stanowią reguły produkcyjnej ekstrakcji. `Other`: Brak wiarygodnego pozytywnego keywordu rozdzielającego Other od Structured/Elasticized; samo wiązanie nie wystarcza.

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Short` | 16 | 0,78% | short shorts, mini shorts, hot pants, dolphin shorts, upper-thigh, short-length, running shorts |
| `Mid-Length` | 13 | 0,63% | mid-length, mid-thigh, regular/standard length |
| `Long` | 77 | 3,75% | bermuda, knee/below-knee length, long shorts, basketball shorts, boardshorts |

**Co najmniej jedno trafienie:** 105 (5,11%); **bez trafienia:** 1948 (94,89%); **trafienia ≥2 wartości:** 1 (0,05%).

Uwagi: `Short`: Running/dolphin są szerokimi wskaźnikami; samo shorts nie mówi o długości. `Long`: Basketball/boardshorts są szerokimi wskaźnikami długości, nie gwarancją.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 161 | 7,84% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 167 | 8,13% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 17 | 0,83% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 345 (16,80%); **bez trafienia:** 1708 (83,20%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

### `shorts_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Denim` | 301 | 14,66% | denim, jean shorts, jorts |
| `Cargo` | 49 | 2,39% | cargo |
| `Sweatshorts` | 312 | 15,20% | sweatshorts, sweat shorts, French-terry/fleece shorts, french terry, fleece, lounge/jogger/jogging shorts |
| `Athletic` | 86 | 4,19% | athletic/sports/running/basketball/tennis/training/gym/track/cycling/biker shorts |
| `Tailored` | 53 | 2,58% | tailored, suit/suiting shorts, dress/formal shorts |
| `Other` | 62 | 3,02% | boxer shorts, bloomers, harem/sarouel shorts, skort |

**Co najmniej jedno trafienie:** 839 (40,87%); **bez trafienia:** 1214 (59,13%); **trafienia ≥2 wartości:** 24 (1,17%).

Uwagi: `Sweatshorts`: Szerokie wskazówki materiału i nazwy: obejmują też fleece lining i lounge shorts. Nie potwierdzają jednoznacznie konstrukcji Sweatshorts; nakładanie z innymi typami jest dozwolone. `Tailored`: Nie wnioskujemy wyłącznie z pasa Structured ani plis. `Other`: Tylko nazwane konstrukcje spoza obecnej listy; nie pełne dopełnienie pozostałych typów.

<a id="skirts"></a>

## Skirts

**Dział:** Skirts. **Mianownik każdej tabeli: 1913 produktów.**

Źródło: `SKIRTS / SHORT SKIRTS` (900); `SKIRTS / MID LENGTH SKIRTS` (882); `SKIRTS / LONG SKIRTS` (131).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 0 | 0,00% | men, man, male, menswear |
| `Women` | 1913 | 100,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 1913 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1102 | 57,61% | black, ebony, onyx, coal |
| `White` | 484 | 25,30% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 393 | 20,54% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 231 | 12,08% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 344 | 17,98% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 161 | 8,42% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 109 | 5,70% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 129 | 6,74% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 200 | 10,45% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 57 | 2,98% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 200 | 10,45% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 39 | 2,04% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 34 | 1,78% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 72 | 3,76% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 1912 (99,95%); **bez trafienia:** 1 (0,05%); **trafienia ≥2 wartości:** 979 (51,18%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 818 | 42,76% | 818 / 42,76% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 693 | 36,23% | 645 / 33,72% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 44 | 2,30% | 44 / 2,30% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 438 | 22,90% | 432 / 22,58% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 726 | 37,95% | 541 / 28,28% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 428 | 22,37% | 428 / 22,37% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 459 | 23,99% | 459 / 23,99% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 412 | 21,54% | 412 / 21,54% | silk, slik |
| `Leather` | 94 | 4,91% | 91 / 4,76% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 22 | 1,15% | 22 / 1,15% | cashmere, cashmire |
| `Linen` | 56 | 2,93% | 50 / 2,61% | linen, flax, ramie, hemp |
| `Down` | 1 | 0,05% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 1910 (99,84%); **bez trafienia:** 3 (0,16%); **trafienia ≥2 wartości:** 1287 (67,28%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 8 | 0,42% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 142 | 7,42% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 69 | 3,61% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 94 | 4,91% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 2 | 0,10% | camo, camouflage, camouflaged |
| `Animal Print` | 30 | 1,57% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 19 | 0,99% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 278 | 14,53% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 577 (30,16%); **bez trafienia:** 1336 (69,84%); **trafienia ≥2 wartości:** 62 (3,24%).

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Mini` | 571 | 29,85% | mini/minidress/miniskirt, short dress/skirt, above knee, thigh-length |
| `Midi` | 541 | 28,28% | midi, mid-length, knee/calf/tea-length, below knee |
| `Maxi` | 46 | 2,40% | maxi, long dress/skirt, full/ankle/floor-length, gown |

**Co najmniej jedno trafienie:** 1154 (60,32%); **bez trafienia:** 759 (39,68%); **trafienia ≥2 wartości:** 4 (0,21%).

Uwagi: `Maxi`: Gown jest szerokim wskaźnikiem; nie każda suknia ma długość maxi.

### `skirt_silhouette`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Fitted` | 203 | 10,61% | pencil, bodycon, fitted, slim, figure-hugging, form-fitting |
| `Straight` | 7 | 0,37% | straight, straight-cut/fit, column |
| `A-Line` | 248 | 12,96% | a-line, flare/flared, skater, circle skirt |
| `Other` | 9 | 0,47% | cocoon, balloon/bubble/tulip skirt, mermaid/fishtail/trumpet silhouette |

**Co najmniej jedno trafienie:** 466 (24,36%); **bez trafienia:** 1447 (75,64%); **trafienia ≥2 wartości:** 1 (0,05%).

Uwagi: `Other`: Tylko nazwane alternatywne sylwetki; część może wizualnie mieścić się także w Fitted/A-Line.

### `skirt_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Pleated` | 433 | 22,63% | pleat/pleated/pleating, plissé |
| `Wrap` | 168 | 8,78% | wrap/wraparound, pareo, sarong, overlapping front/panel |
| `Asymmetric` | 252 | 13,17% | asymmetric/asymmetrical, high-low, handkerchief |
| `Tiered` | 43 | 2,25% | tier, tiered, tiers |
| `Ruffled` | 115 | 6,01% | ruffle/ruffled, flounce/flounced |
| `Other` | 71 | 3,71% | draped/draping, ruched/ruching, smocked, bubble/balloon/tulip skirt |

**Co najmniej jedno trafienie:** 821 (42,92%); **bez trafienia:** 1092 (57,08%); **trafienia ≥2 wartości:** 223 (11,66%).

Uwagi: `Pleated`: Szeroko liczymy również pojedyncze zakładki; to może zawyżać plisowaną konstrukcję. `Other`: Tylko pozytywne przykłady innych konstrukcji; mogą współwystępować z nazwanym typem. Brak wzmianki nie daje Other.

### `rise`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `High-Rise` | 121 | 6,33% | high-rise, high waist/waisted, paperbag waist, corset waist |
| `Mid-Rise` | 39 | 2,04% | mid/medium/regular/classic rise, mid-waist |
| `Low-Rise` | 2 | 0,10% | low-rise, low waist/waisted, hip-hugger, dropped waist |

**Co najmniej jedno trafienie:** 162 (8,47%); **bez trafienia:** 1751 (91,53%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Mid-Rise`: Nie uzupełniamy przy braku wzmianki o wysokim/niskim stanie.

<a id="dresses"></a>

## Dresses

**Dział:** Dresses. **Mianownik każdej tabeli: 2600 produktów.**

Źródło: `DRESSES / SHORT DRESSES` (1340); `DRESSES / MID LENGTH DRESSES` (1036); `DRESSES / LONG DRESSES` (224).

### `gender`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Men` | 0 | 0,00% | men, man, male, menswear |
| `Women` | 2600 | 100,00% | women, woman, female, womenswear |

**Co najmniej jedno trafienie:** 2600 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 0 (0,00%).

### `colors`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Black` | 1534 | 59,00% | black, ebony, onyx, coal |
| `White` | 852 | 32,77% | white, ivory, cream, ecru, bone, alabaster, milk, pearl, chalk, eggshell, natural |
| `Grey` | 405 | 15,58% | grey, gray, charcoal, slate, ash, silver, gunmetal, graphite, anthracite, pewter, stone, smoke, cement |
| `Navy` | 336 | 12,92% | navy, midnight blue, marine, ink, deep indigo, dark indigo |
| `Blue` | 299 | 11,50% | blue, cobalt, indigo, teal, turquoise, aqua, cyan, cerulean, periwinkle, cornflower, petrol |
| `Red` | 174 | 6,69% | red, burgundy, maroon, wine, bordeaux, crimson, scarlet, cherry, ruby, oxblood, garnet, vermilion, cardinal, claret, berry |
| `Green` | 122 | 4,69% | green, olive, khaki, emerald, mint, sage, lime, jade, moss, pine, chartreuse, pistachio, seafoam |
| `Pink` | 165 | 6,35% | pink, blush, rose, magenta, fuchsia, salmon, bubblegum, peony, flamingo, mauve, raspberry, carnation |
| `Beige` | 123 | 4,73% | beige, tan, camel, sand, taupe, oatmeal, champagne, fawn, buff, nude, wheat, biscuit, khaki, latte, putty, parchment, sahara |
| `Brown` | 41 | 1,58% | brown, chocolate, cognac, espresso, chestnut, mahogany, rust, terracotta, bronze, copper, cinnamon, caramel, toffee, mocha, umber, sienna, walnut, sepia, tobacco, hazel, cocoa, tortoiseshell |
| `Yellow` | 214 | 8,23% | yellow, mustard, gold, golden, brass, lemon, canary, ochre, saffron, amber, honey, butter, marigold, citrine, daffodil, sunflower, banana, banan |
| `Orange` | 58 | 2,23% | orange, coral, peach, tangerine, apricot, papaya, mandarin, pumpkin, mango, persimmon, clementine |
| `Purple` | 56 | 2,15% | purple, violet, lavender, lilac, plum, eggplant, aubergine, amethyst, orchid, mulberry, grape, heliotrope, wisteria, periwinkle purple, indigo purple |
| `Multicolor` | 75 | 2,88% | multicolor, multicolour, multi-colored, multi-coloured, rainbow, tie-dye |

**Co najmniej jedno trafienie:** 2600 (100,00%); **bez trafienia:** 0 (0,00%); **trafienia ≥2 wartości:** 1226 (47,15%).

### `main_composition`

| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |
| :--- | ---: | ---: | ---: | :--- |
| `Cotton` | 1219 | 46,88% | 1219 / 46,88% | cotton, coton, cototn, supima, pima, cotto, cottom, cottoin, cottob |
| `Polyester` | 766 | 29,46% | 722 / 27,77% | polyester, poylester, polyurethane, polyethylene, polypropylene, pvc, polyvinyl chloride, polyetser, poliester, polyestger, polyeseter, polyerster, polyesters, polyster, polurethane, polyeurethane, polyutryhane, polyurethan, polyuretane, polypropelyne, polyproylene, polypropilene, polyethelyne, polyethyline, polyethene, polyvinylchloride |
| `Acrylic` | 38 | 1,46% | 38 / 1,46% | acrylic, modacrylic, polyacrylic, acryl, polyacryl |
| `Wool` | 458 | 17,62% | 457 / 17,58% | wool, merino, lambswool, lambs wool, lamb wool, fleecewool, mohair, alpaca, angora, camel, yak, kidmohair |
| `Viscose` | 981 | 37,73% | 775 / 29,81% | viscose, cupro, cupra, bemberg, rayon, acetate, triacetate, modal, micromodal, micro modal, lyocell, tencel, bamboo, viscsoe, visocse, viscoe, curpo, curpa, lyocel, tencell, tensel, tri acetate |
| `Elastane` | 641 | 24,65% | 639 / 24,58% | elastane, elastan, elastodiene, elastomultiester, spandex, lycra, elastene, elstane, elasthane, elatane, elsatane, ealstane, elastsane, elastne, elastant, lyrca |
| `Nylon` | 562 | 21,62% | 562 / 21,62% | nylon, polyamide, polyamid, poylamide, polymide, polyammide, polyamides, polyamdie |
| `Silk` | 522 | 20,08% | 522 / 20,08% | silk, slik |
| `Leather` | 60 | 2,31% | 60 / 2,31% | leather, lambskin, lamb skin, calfskin, calf skin, goatskin, goat skin, cowhide, cow hide, deerskin, deer skin, pigskin, pig skin, horsehide, horse hide, sheepskin, sheep skin, suede, nubuck, calf, lamb, goat, cow, buffalo, bull |
| `Cashmere` | 56 | 2,15% | 56 / 2,15% | cashmere, cashmire |
| `Linen` | 84 | 3,23% | 77 / 2,96% | linen, flax, ramie, hemp |
| `Down` | 0 | 0,00% | 0 / 0,00% | down, feather, feathers |
| `Fur` | 0 | 0,00% | 0 / 0,00% | fur, shearling, mink, fox, rabbit, raccoon, chinchilla, coyote, beaver, nutria, karakul |

**Co najmniej jedno trafienie:** 2596 (99,85%); **bez trafienia:** 4 (0,15%); **trafienia ≥2 wartości:** 1623 (62,42%).

### `pattern`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Solid` | 17 | 0,65% | solid, plain, monochrome, monochromatic, unpatterned, unprinted, single color, single colour, uniform color, uniform colour |
| `Striped` | 212 | 8,15% | stripe, stripes, striped, striping, pinstripe, pinstripes, pinstriped, chalk stripe, side stripe, breton, ticking stripe, variegated stripe, chevron stripe, candy stripe, pencil stripe, railroad stripe |
| `Plaid` | 66 | 2,54% | plaid, check, checks, checked, checkered, chequered, checkerboard, tartan, gingham, houndstooth, hounds tooth, herringbone, argyle, windowpane, prince of wales, madras, tattersall |
| `Floral` | 116 | 4,46% | floral, flower, flowers, flowered, botanical, tropical, hawaiian, leaf, leaves, foliage, palm, hibiscus, rose print, rose pattern, rose motif, daisy, daisies, blossom, blossoms, botanic |
| `Camo` | 5 | 0,19% | camo, camouflage, camouflaged |
| `Animal Print` | 46 | 1,77% | animal print, animal printed, animal pattern, leopard, cheetah, jaguar, panther, zebra, tiger, snake, snakeskin, python, reptile, crocodile, croc embossed, croc print, alligator, cow print, cow pattern, dalmatian, giraffe |
| `Polka Dot` | 19 | 0,73% | polka dot, polka dots, polka dotted, dotted, dot, dots, spotted, pin dot, micro dot, polkadot, polkadots |
| `Other` | 407 | 15,65% | graphic, graphics, graphical, artwork, photo print, photographic, portrait print, text print, text printed, text graphic, lettering, slogan, logo, logos, monogram, monogrammed, wordmark, branded, colorblock, colorblocked, colourblock, colourblocked, color block, colour block, two tone, bi color, bicolor, bi colour, bicolour, contrast panel, contrast panels, contrast paneling, contrast panelling, split color, split colour, tie dye, tie dyed, tiedye, acid wash, acid washed, bleached, dip dye, dip dyed, ombre, ombré, gradient, marbled, marble print, marble effect, shibori, cloud wash, paint splatter, paint splattered, splatter, splattered, patchwork, paisley, abstract, geometric, geometrical, zigzag, zig zag, chevron, ikat, aztec, tribal, psychedelic, baroque, damask, tapestry, kaleidoscope, kaleidoscopic |

**Co najmniej jedno trafienie:** 768 (29,54%); **bez trafienia:** 1832 (70,46%); **trafienia ≥2 wartości:** 110 (4,23%).

### `length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Mini` | 30 | 1,15% | mini/minidress/miniskirt, short dress/skirt, above knee, thigh-length |
| `Midi` | 74 | 2,85% | midi, mid-length, knee/calf/tea-length, below knee |
| `Maxi` | 53 | 2,04% | maxi, long dress/skirt, full/ankle/floor-length, gown |

**Co najmniej jedno trafienie:** 157 (6,04%); **bez trafienia:** 2443 (93,96%); **trafienia ≥2 wartości:** 0 (0,00%).

Uwagi: `Maxi`: Gown jest szerokim wskaźnikiem; nie każda suknia ma długość maxi.

### `sleeve_length`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Sleeveless` | 871 | 33,50% | sleeveless, no/without sleeves, strapless, bandeau, tube top/dress |
| `Short Sleeve` | 594 | 22,85% | short sleeve, short-sleeved, cap sleeve |
| `Three-Quarter Sleeve` | 80 | 3,08% | three-quarter sleeve, 3/4 sleeve, three-fourths sleeve |
| `Long Sleeve` | 854 | 32,85% | long sleeve, long-sleeved, full-length sleeve, extra-long sleeve |

**Co najmniej jedno trafienie:** 2385 (91,73%); **bez trafienia:** 215 (8,27%); **trafienia ≥2 wartości:** 13 (0,50%).

Uwagi: `Sleeveless`: Strapless/bandeau/tube są szerokimi wskaźnikami braku rękawów; nie wyciągamy wniosku z samej kategorii.

### `neckline`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Crewneck` | 1171 | 45,04% | crewneck, crew neck, round/rounded neck, jewel neck |
| `Scoop Neck` | 91 | 3,50% | scoop/scooped neck, u-neck, deep round neck |
| `V-Neck` | 355 | 13,65% | v-neck, vneck, plunge/plunging, surplice, y-neck |
| `High Neck` | 255 | 9,81% | turtleneck, mock neck, roll neck, funnel neck, high neck, stand/band/mandarin collar |
| `Collared` | 322 | 12,38% | collared, point/spread/polo/shirt/camp/shawl collar, foldover collar, button-down collar, lapels |
| `Other` | 132 | 5,08% | square neck, square neckline; boat neck, boatneck, bateau, slash neck; sweetheart, sweet-heart; cowl, cowl neck; straight neckline, straight-across neck, straight top edge; asymmetric/asymmetrical neckline |

**Co najmniej jedno trafienie:** 2292 (88,15%); **bez trafienia:** 308 (11,85%); **trafienia ≥2 wartości:** 34 (1,31%).

Uwagi: `Crewneck`: Round neck to szeroki wskaźnik: może obejmować także Scoop Neck. `V-Neck`: Plunging i surplice są szerokimi wskaźnikami; nie każdy głęboki dekolt ma kształt V. Y-neck to szeroki sygnał serka z przedłużeniem w listwę zapięcia, szczególnie w kardiganach. `Collared`: Nie liczymy samego collar, ponieważ rib-knit crewneck collar nie oznacza wykładanego kołnierza. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Square Neck, Boat Neck, Sweetheart, Cowl Neck, Straight Neck, Asymmetric. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

### `dress_silhouette`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Fitted` | 131 | 5,04% | bodycon, sheath, fitted, slim, figure-hugging, form-fitting |
| `Straight` | 97 | 3,73% | shift, straight/straight-cut, column |
| `A-Line` | 201 | 7,73% | a-line, flared, fit-and-flare, skater |
| `Other` | 4 | 0,15% | cocoon, balloon/bubble/tulip, mermaid/fishtail/trumpet dress |

**Co najmniej jedno trafienie:** 403 (15,50%); **bez trafienia:** 2197 (84,50%); **trafienia ≥2 wartości:** 27 (1,04%).

Uwagi: `Fitted`: Samo fitted może dotyczyć tylko góry sukienki; nakładanie się z A-Line jest zamierzone. `A-Line`: Flared może dotyczyć rękawów; szeroki audyt nie rozstrzyga całej sylwetki. `Other`: Tylko nazwane alternatywne sylwetki; część może wizualnie mieścić się także w Fitted/A-Line.

### `dress_type`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Slip` | 39 | 1,50% | slip dress/style, slip-inspired, chemise |
| `Shirt Dress` | 243 | 9,35% | shirt dress, shirtdress, shirt-style, polo dress |
| `Wrap` | 64 | 2,46% | wrap/wraparound, surplice, overlapping front |
| `Sweater Dress` | 53 | 2,04% | sweater dress/style, jumper dress |
| `Sweatshirt Dress` | 79 | 3,04% | sweatshirt dress/style, hoodie dress, hooded sweatshirt |
| `T-Shirt Dress` | 127 | 4,88% | t-shirt dress/style, tshirt dress, tee dress |
| `Other` | 51 | 1,96% | kaftan/caftan, pinafore, sundress, babydoll, tunic/smock/peasant dress; blazer dress/style, blazer-inspired, tuxedo dress |

**Co najmniej jedno trafienie:** 628 (24,15%); **bez trafienia:** 1972 (75,85%); **trafienia ≥2 wartości:** 28 (1,08%).

Uwagi: `Slip`: Nie liczymy samego slip-on, satyny ani cienkich ramiączek. `Shirt Dress`: T-shirt dress ma osobny typ; regex nie wymaga wyłączności wobec pozostałych konstrukcji. `Wrap`: Szeroko liczy również wrap detail w opisie. `Sweater Dress`: Jumper dress bywa nazwą sukienki na szelkach; samo knit nie wystarcza. `Other`: Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. Przeniesione do Other: Blazer Dress. Nie jest to pełna klasa Other; brak trafienia nie daje Other.

### `strap_style`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Standard` | 88 | 3,38% | two/twin/parallel straps, shoulder straps, adjustable straps |
| `Racerback` | 24 | 0,92% | racerback, racer-back, T-back, Y-back |
| `Halter` | 21 | 0,81% | halter, halterneck, halter neck |
| `One-Shoulder` | 30 | 1,15% | one-shoulder, single-shoulder, one-sleeve |
| `Strapless` | 24 | 0,92% | strapless, bandeau, tube top/dress/bodysuit |
| `Off-Shoulder` | 26 | 1,00% | off-shoulder, off-the-shoulder, Bardot |
| `Other` | 1538 | 59,15% | jawnie nazwane rękawy, cold-shoulder, cross/criss-cross back |

**Co najmniej jedno trafienie:** 1700 (65,38%); **bez trafienia:** 900 (34,62%); **trafienia ≥2 wartości:** 46 (1,77%).

Uwagi: `Standard`: Szeroki, niepełny wskaźnik ramiączek; może współwystępować np. z Racerback/Halter. Nie jest rozpoznaniem standardowego układu. `Other`: Rękawy są przybliżeniem zwykłej konstrukcji; mogą współwystępować z Off-Shoulder/One-Shoulder. Nie jest to pełna klasa Other.

### `strap_width`

| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |
| :--- | ---: | ---: | :--- |
| `Wide` | 3 | 0,12% | wide/broad/thick (shoulder) straps |
| `Spaghetti` | 11 | 0,42% | spaghetti, thin/narrow/delicate/fine/skinny/string straps |
| `Other` | 2 | 0,08% | medium/intermediate/regular-width straps, mixed/different/unequal-width straps; wzmianki o szerokim i cienkim ramiączku w jednym tekście |
| `Not Applicable` | 1557 | 59,88% | strapless, bandeau, tube; jawnie nazwane rękawy |

**Co najmniej jedno trafienie:** 1572 (60,46%); **bez trafienia:** 1028 (39,54%); **trafienia ≥2 wartości:** 1 (0,04%).

Uwagi: `Other`: Tylko jawne wskazówki pośredniej lub mieszanej szerokości. Brak informacji o szerokości nie daje Other; szerokie dopasowania mogą dotyczyć wariantów konstrukcji. `Not Applicable`: Rękawy są szerokim przybliżeniem konstrukcji bez ramiączek; konstrukcje z rękawami i dodatkowymi ramiączkami mogą zawyżać wynik.

## Dodatkowe sygnały do oceny zakresu

To pomocnicze zliczenia poza zestawem enumów. Nie dodają cech do taksonomii. Nazwy tkanin liczymy w opisach niezależnie od składu surowcowego.

| Kategoria | Rękaw 3/4 | Rękaw do łokcia / half | Denim | Koronka | Satyna | Aksamit / welur | Sztruks | Grafika / logo |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T-shirts | 55 / 0,61% | 11 / 0,12% | 31 / 0,35% | 76 / 0,85% | 50 / 0,56% | 45 / 0,50% | 1 / 0,01% | 4669 / 52,10% |
| Polos | 1 / 0,17% | 1 / 0,17% | 3 / 0,51% | 2 / 0,34% | 5 / 0,85% | 10 / 1,69% | 0 / 0,00% | 313 / 53,05% |
| Tank tops & Camisoles | 0 / 0,00% | 0 / 0,00% | 9 / 0,88% | 61 / 5,98% | 32 / 3,14% | 8 / 0,78% | 0 / 0,00% | 158 / 15,49% |
| Bodysuits | 1 / 0,85% | 0 / 0,00% | 0 / 0,00% | 19 / 16,10% | 2 / 1,69% | 2 / 1,69% | 0 / 0,00% | 16 / 13,56% |
| Shirts | 38 / 0,88% | 2 / 0,05% | 265 / 6,11% | 42 / 0,97% | 47 / 1,08% | 15 / 0,35% | 22 / 0,51% | 936 / 21,57% |
| Blouses | 49 / 4,89% | 3 / 0,30% | 19 / 1,90% | 97 / 9,68% | 48 / 4,79% | 7 / 0,70% | 0 / 0,00% | 48 / 4,79% |
| Knit Sweaters | 73 / 1,46% | 3 / 0,06% | 5 / 0,10% | 69 / 1,38% | 27 / 0,54% | 49 / 0,98% | 0 / 0,00% | 901 / 18,06% |
| Sweatshirts | 9 / 0,26% | 3 / 0,09% | 11 / 0,32% | 35 / 1,02% | 37 / 1,08% | 65 / 1,89% | 4 / 0,12% | 1869 / 54,46% |
| Hoodies & Zipups | 6 / 0,22% | 0 / 0,00% | 16 / 0,58% | 19 / 0,68% | 41 / 1,48% | 40 / 1,44% | 0 / 0,00% | 1479 / 53,22% |
| Cardigans | 6 / 0,66% | 0 / 0,00% | 1 / 0,11% | 13 / 1,44% | 4 / 0,44% | 4 / 0,44% | 1 / 0,11% | 129 / 14,27% |
| Trousers | 0 / 0,00% | 0 / 0,00% | 76 / 1,94% | 13 / 0,33% | 133 / 3,40% | 36 / 0,92% | 58 / 1,48% | 381 / 9,73% |
| Cargo Pants | 0 / 0,00% | 0 / 0,00% | 6 / 3,19% | 0 / 0,00% | 1 / 0,53% | 0 / 0,00% | 0 / 0,00% | 51 / 27,13% |
| Sweatpants & Lounge Pants | 0 / 0,00% | 0 / 0,00% | 13 / 0,61% | 18 / 0,84% | 70 / 3,28% | 33 / 1,54% | 4 / 0,19% | 764 / 35,77% |
| Jeans | 0 / 0,00% | 0 / 0,00% | 1777 / 47,98% | 4 / 0,11% | 8 / 0,22% | 6 / 0,16% | 12 / 0,32% | 2357 / 63,63% |
| Shorts | 0 / 0,00% | 0 / 0,00% | 295 / 14,37% | 18 / 0,88% | 78 / 3,80% | 7 / 0,34% | 3 / 0,15% | 588 / 28,64% |
| Skirts | 0 / 0,00% | 0 / 0,00% | 226 / 11,81% | 62 / 3,24% | 92 / 4,81% | 32 / 1,67% | 12 / 0,63% | 207 / 10,82% |
| Dresses | 80 / 3,08% | 5 / 0,19% | 87 / 3,35% | 126 / 4,85% | 100 / 3,85% | 52 / 2,00% | 1 / 0,04% | 308 / 11,85% |

W tej tabeli `lace` może też opisywać sznurowanie, a `graphic/logo` ma celowo szeroki zakres; to wskazówki do review, nie etykiety docelowe.

## Odtworzenie i kontrola

```sh
.venv/bin/python products_new/scripts/audit_taxonomy_keywords.py
```

- [Skrypt](../scripts/audit_taxonomy_keywords.py)
- [Słownik cech wspólnych](../scripts/taxonomy_audit_common_rules.json)
- [Słownik pozostałych cech i wyjątków kategorii](../scripts/taxonomy_audit_specific_rules.json)
- [Wyniki JSON, regexy i przykładowe trafienia z ID produktów](taxonomy_keyword_audit.json)

Wygenerowano (UTC): 2026-10-20T21:54:20.192771+00:00. JSON zawiera odciski SHA-256 taksonomii i słowników oraz metadane plików wejściowych.

Kontrole: pełne pokrycie wszystkich kombinacji kategoria–cecha–wartość z dokumentu; liczenie raz na ID; brak Jackets & Coats; osobne braki trafień; każda liczba w przedziale 0…liczba produktów; zgodność liczebności źródeł i kategorii.
