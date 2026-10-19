# Mapowanie kroju i dopasowania (`fit` oraz `dress_style`)

Dokument definiuje ujednolicone słowniki wartości używanych w cesze `fit` we wszystkich kategoriach posiadających wariancję dopasowania oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description`, `input_subcategory` oraz analiza obrazu).

---

## 1. Dwa standardy cechy `fit` w systemie

Aby zachować maksymalną prostotę dla odzieży górnej/wierzchniej oraz pełną precyzję dla spodni, cecha `fit` wykorzystuje dokładnie **dwa czyste standardy (bez ukośników `/`)**:

1. **Standard ogólny – 3 wartości (`Slim`, `Regular`, `Relaxed`):**
   * Obowiązuje w **16 kategoriach**:
     * `1. Tops`: `T-shirts`, `Polos`, `Tank tops & Camisoles` *(brak w `Bodysuits`, które z definicji są ściśle dopasowane)*
     * `2. Shirts & Blouses`: `Shirts`, `Blouses`
     * `3. Sweaters`: `Knit Sweaters`, `Sweatshirts`, `Hoodies & Zipups`, `Cardigans`
     * `4. Jackets & Coats`: `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`
     * `6. Shorts`: `Shorts`
     * `8. Dresses`: `Dresses` *(w połączeniu z dedykowaną cechą fasonu `dress_style`)*
2. **Standard dla spodni – 7 wartości (`Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared`):**
   * Obowiązuje we wszystkich **4 kategoriach działu `5. Pants`**:
     * `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans`

---

## 2. Tabela mapowania – Standard ogólny (`fit` w 16 kategoriach)

| # | Wartość docelowa (`fit`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Slim`** | `Slim / Fitted`, `Slim / Tailored`, `Slim / Fitted / Bodycon / Sheath` | Krój dopasowany do ciała, obcisły lub mocno taliowany (`slim`, `slim-fit`, `slim-fitting`, `fitted`, `form-fitting`, `figure-hugging`, `tailored fit`, `skinny fit`, `bodycon`, `sheath`, `contours`) |
| 2 | **`Regular`** | `Regular`, `Regular / Straight`, `Shift / Straight / Regular` | Klasyczny, standardowy, prosty krój – ani obcisły, ani oversize (`regular`, `regular-fit`, `classic fit`, `standard fit`, `straight-cut`, `tailored regular`, wartość domyślna gdy krój jest standardowy) |
| 3 | **`Relaxed`** | `Oversized / Relaxed`, `Oversized / Relaxed / Cocoon`, `Relaxed / Loose / Wide` | Krój luźny, swobodny, szeroki, pudełkowy lub oversize (`relaxed`, `relaxed-fit`, `oversized`, `oversize`, `loose`, `loose-fit`, `boxy`, `cocoon`, `slouchy`, `boyfriend`, `dropped-shoulder`, `wide-cut`, `dolman`) |

---

## 3. Tabela mapowania – Standard dla spodni (`fit` w dziale `5. Pants`)

| # | Wartość docelowa (`fit`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description` / `input_subcategory`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Skinny`** | `Skinny`, `Slim / Skinny` | Bardzo obcisłe spodnie przylegające na całej długości nogawki (`skinny`, `super skinny`, `spray-on`, `second-skin`, `legging-style`, subkategoria `SKINNY JEANS`) |
| 2 | **`Slim`** | `Slim`, `Slim / Skinny` | Spodnie wąskie, dopasowane, ale nie obcisłe jak legginsy (`slim`, `slim-fit`, `slim-leg`, `cigarette`, subkategoria `SLIM JEANS` / `SLIM PANTS`) |
| 3 | **`Straight`** | `Straight / Regular`, `Regular / Straight` | Prosta nogawka od uda do kostki, klasyczny krój regular (`straight`, `straight-leg`, `regular-fit`, `classic straight`, subkategoria `STRAIGHT JEANS` / `STRAIGHT PANTS`) |
| 4 | **`Tapered`** | `Tapered`, `Tapered / Jogger`, `Regular / Tapered (Jogger)` | Nogawka swobodniejsza w udzie i zwężająca się ku dołowi (`tapered`, `tapered-leg`, `carrot fit`, `jogger`, `track pant fit`, subkategoria `TAPERED JEANS` / `TAPERED PANTS`) |
| 5 | **`Relaxed`** | `Relaxed / Loose / Baggy`, `Relaxed / Loose / Baggy / Boyfriend`, `Drop-Crotch / Harem` | Luźny, swobodny krój, spodnie baggy, boyfriend lub z obniżonym krokiem (`relaxed`, `relaxed-fit`, `loose`, `baggy`, `boyfriend`, `slouchy`, `drop-crotch`, `harem`, `cargo loose`, subkategoria `RELAXED JEANS` / `DROP-CROTCH PANTS`) |
| 6 | **`Wide-Leg`** | `Wide-Leg`, `Wide-Leg / Loose / Palazzo` | Bardzo szeroka nogawka na całej długości (`wide-leg`, `wide leg`, `palazzo`, `culotte`, `hakama`, `flared wide`, subkategoria `WIDE-LEG PANTS` / `WIDE-LEG JEANS`) |
| 7 | **`Flared`** | `Flared / Bootcut` | Nogawka dopasowana w udzie i rozszerzająca się od kolana w dół (`flared`, `flare`, `bootcut`, `bell-bottom`, `kick-flare`, subkategoria `FLARED JEANS` / `FLARED PANTS`) |

---

## 4. Tabela mapowania fasonu sukienek (`dress_style` w `8. Dresses`)

Wydzielenie fasonu sukienki z ogólnego `fit` do osobnej cechy `dress_style` (analogicznie do `skirt_style` w spódnicach i `jacket_style` w kurtkach) pozwala niezależnie filtrować dopasowanie (`Slim`, `Regular`, `Relaxed`) oraz krój konstrukcyjny sukienki:

| # | Wartość docelowa (`dress_style`) | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- |
| 1 | **`Bodycon`** | Dopasowane sukienki ołówkowe, bandażowe i etui (`bodycon`, `bandage`, `sheath`, `pencil dress`, `figure-hugging`, ` bustier dress`) |
| 2 | **`A-Line`** | Sukienki rozkloszowane ku dołowi, trapezowe i skater (`a-line`, `flared`, `skater`, `fit-and-flare`, `tiered`, `pleated skirt dress`, `babydoll`) |
| 3 | **`Shift`** | Proste sukienki o kroju tuby / trapezu bez wcięcia w talii (`shift`, `straight-cut dress`, `tunic dress`, `column dress`, `tank dress`, `t-shirt dress`) |
| 4 | **`Slip`** | Bieliźniane sukienki na cienkich ramiączkach (`slip dress`, `camisole dress`, `satin slip`, `silk slip`) |
| 5 | **`Shirt Dress`** | Sukienki koszulowe zapinane na guziki / szmizjerki (`shirt dress`, `shirtdress`, `button-down dress`, `utility shirt dress`, `polo dress`) |
| 6 | **`Wrap`** | Sukienki kopertowe, wiązane lub drapowane (`wrap dress`, `draped dress`, `surplice dress`, `ruched wrap`, `sarong dress`) |
| 7 | **`Sweater Dress`** | Sukienki dzianinowe / swetrowe i dresowe (`sweater dress`, `knit dress`, `rib-knit dress`, `jumper dress`, `hoodie dress`, `sweatshirt dress`) |
