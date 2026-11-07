# Zapytania o T-shirty — przegląd oczekiwanych odpowiedzi

206 zapytań z [pliku CSV](t-shirt_queries.csv) w tej samej kolejności. Każdy punkt na liście filtrów to osobny warunek, który musi być spełniony. Nazwy cech i operatorów odpowiadają kluczom parsera. Wartości filtrów są zapisane w formacie JSON. Fragmenty zapytania przeznaczone do rankingu są wypisane osobno jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050) · [051–075](#zapytania-051-075) · [076–100](#zapytania-076-100) · [101–125](#zapytania-101-125) · [126–150](#zapytania-126-150) · [151–175](#zapytania-151-175) · [176–200](#zapytania-176-200) · [201–206](#zapytania-201-206)

## Zapytania 001-025

### 001. `hippie tshirt tie dyed`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `hippie` · `tie dyed`

### 002. `white cotton tee to wear with jeans`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `to wear with jeans`

### 003. `nirvana long sleeve t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`

**Residual** — `nirvana`

### 004. `miękka koszulka z bawełny albo lnu bez poliestru`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester"]`

**Residual** — `miękka`

### 005. `pink unisex tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Pink"]`

**Residual** — `unisex`

### 006. `retro blue and red retro champion t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_all ["Blue", "Red"]`
- `brand in ["Champion"]`

**Residual** — `retro`

### 007. `amazon essential long sleeve tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Amazon Essentials"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — brak

### 008. `100% cotton long sleeve t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `main_composition equals_set ["Cotton"]`
- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Women"]`

**Residual** — brak

### 009. `heather tshirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `heather`

### 010. `fishing tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `fishing`

### 011. `t-shirts for men with pocket`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `with pocket`

### 012. `plain cotton tee around $25`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `pattern in ["Solid"]`
- `main_composition contains_any ["Cotton"]`
- `price around 25`

**Residual** — brak

### 013. `soft heather grey tshirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Grey"]`
- `gender in ["Women"]`

**Residual** — `soft` · `heather grey`

### 014. `large gray tshirt soft`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Grey"]`

**Residual** — `large` · `soft`

### 015. `women's t shirts with a cross`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `with a cross`

### 016. `yellow tee shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Yellow"]`

**Residual** — brak

### 017. `floral baseball tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Floral"]`

**Residual** — `baseball`

### 018. `star wars tee shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `star wars`

### 019. `champion long sleeve t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Champion"]`
- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Men"]`

**Residual** — brak

### 020. `2x womens v neck tshirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `neckline in ["V-Neck"]`

**Residual** — `2x`

### 021. `womens cotton tshirts short sleeve`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `main_composition contains_any ["Cotton"]`
- `sleeve_length in ["Short Sleeve"]`

**Residual** — brak

### 022. `slim fit white crew neck t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Slim"]`
- `colors contains_any ["White"]`
- `neckline in ["Crewneck"]`
- `gender in ["Men"]`

**Residual** — brak

### 023. `blue tee but not turquoise`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["Blue"]`

**Residual** — `not turquoise`

### 024. `womens hiking tees`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `hiking`

### 025. `forest green tee shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Green"]`
- `gender in ["Men"]`

**Residual** — `forest green`

## Zapytania 026-050

### 026. `pink and blue tshirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_all ["Pink", "Blue"]`
- `gender in ["Women"]`

**Residual** — brak

### 027. `3d long-sleeve t-shirt for man`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Men"]`

**Residual** — `3d`

### 028. `gładki biały t-shirt, ale nie oversize`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `pattern in ["Solid"]`
- `colors contains_any ["White"]`
- `fit not_in ["Oversized"]`

**Residual** — brak

### 029. `crop tshirt for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Cropped"]`
- `gender in ["Women"]`

**Residual** — brak

### 030. `rose pink tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Pink"]`

**Residual** — `rose pink`

### 031. `amazon basics v neck tshirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Amazon Basics"]`
- `neckline in ["V-Neck"]`
- `gender in ["Men"]`

**Residual** — brak

### 032. `crewneck tshirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `neckline in ["Crewneck"]`
- `gender in ["Men"]`

**Residual** — brak

### 033. `vineyard vines women long sleeve tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Vineyard Vines"]`
- `gender in ["Women"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — brak

### 034. `jeep t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `jeep`

### 035. `hanes pocket t-shirts men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Hanes"]`
- `gender in ["Men"]`

**Residual** — `pocket`

### 036. `bawełniana koszulka na rodzinny zjazd`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `main_composition contains_any ["Cotton"]`

**Residual** — `na rodzinny zjazd`

### 037. `men's striped t-shirt for at least $25`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `pattern in ["Striped"]`
- `price gte 25`

**Residual** — brak

### 038. `men's white graphic tee under 19.99 euros`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors contains_any ["White"]`
- `price lte 19.99`

**Residual** — `graphic`

### 039. `guns n roses t shirt womens`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `guns n roses`

### 040. `adidas yellow t-shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Adidas"]`
- `colors contains_any ["Yellow"]`

**Residual** — brak

### 041. `tshirt with thumb holes men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `with thumb holes`

### 042. `womens fitted t shirt ivory`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `fit in ["Slim"]`
- `colors contains_any ["White"]`

**Residual** — `ivory`

### 043. `gb gb girls big girls 7-16 striped rib knit tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["GB GB"]`
- `pattern in ["Striped"]`

**Residual** — `big girls 7-16` · `rib knit`

### 044. `sleep tees for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `sleep`

### 045. `outdoor research echo tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Outdoor Research"]`

**Residual** — `echo`

### 046. `labor and delivery nurse tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `labor and delivery nurse`

### 047. `plain long sleeve t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Solid"]`
- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Women"]`

**Residual** — brak

### 048. `orange graphic tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Orange"]`

**Residual** — `graphic`

### 049. `mens v neck tee shirts 2xl tall`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `neckline in ["V-Neck"]`

**Residual** — `2xl tall`

### 050. `nursing tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `nursing`

## Zapytania 051-075

### 051. `tshirt women yellow cotton`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `colors contains_any ["Yellow"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — brak

### 052. `extra long t shirts for tall men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Longline"]`
- `gender in ["Men"]`

**Residual** — `tall`

### 053. `#try not to suck tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `#try not to suck`

### 054. `womens graphic tees vintage shein`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `brand in ["SHEIN"]`

**Residual** — `graphic` · `vintage`

### 055. `różowo-niebieski t-shirt damski bez czerwieni`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_all ["Pink", "Blue"]`
- `gender in ["Women"]`
- `colors contains_none ["Red"]`

**Residual** — brak

### 056. `baseball tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `baseball`

### 057. `long sleeve t shirt us army women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Women"]`

**Residual** — `us army`

### 058. `not today satan not today t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `not today satan not today`

### 059. `custom t shirts design your own`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `custom design your own`

### 060. `women's short or long sleeve tee for hiking`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `sleeve_length in ["Short Sleeve", "Long Sleeve"]`

**Residual** — `for hiking`

### 061. `t shirts for women graphic faith`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `faith graphic`

### 062. `long sleeve cotton t shirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `main_composition contains_any ["Cotton"]`
- `gender in ["Women"]`

**Residual** — brak

### 063. `plus size long sleeve v neck t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `neckline in ["V-Neck"]`
- `gender in ["Women"]`

**Residual** — `plus size`

### 064. `big and tall logo t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `big and tall` · `logo`

### 065. `august burns red t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `august burns red`

### 066. `men's crew neck tee, not oversized`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `neckline in ["Crewneck"]`
- `fit not_in ["Oversized"]`

**Residual** — brak

### 067. `tshirts extra long women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Longline"]`
- `gender in ["Women"]`

**Residual** — brak

### 068. `men's black tee, any brand except Nike`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors contains_any ["Black"]`
- `brand not_in ["Nike"]`

**Residual** — brak

### 069. `hi-vis safety tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `hi-vis safety`

### 070. `matching family group t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `matching family group`

### 071. `wool t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Wool"]`

**Residual** — brak

### 072. `football tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `football`

### 073. `off the shoulder tshirt plus size`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `off the shoulder` · `plus size`

### 074. `long sleeve ivory t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `colors contains_any ["White"]`
- `gender in ["Women"]`

**Residual** — `ivory`

### 075. `gildan white t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Gildan"]`
- `colors contains_any ["White"]`

**Residual** — brak

## Zapytania 076-100

### 076. `męska koszulka z kieszonką, około 80 zł`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `price around 80`

**Residual** — `z kieszonką`

### 077. `men t shirts v neck cheap price`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `neckline in ["V-Neck"]`

**Residual** — `cheap price`

### 078. `pugs not drugs tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `pugs not drugs`

### 079. `personalized christmas graphic raglan t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `personalized` · `christmas graphic` · `raglan`

### 080. `t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — brak

### 081. `tommy hilfiger men tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Tommy Hilfiger"]`
- `gender in ["Men"]`

**Residual** — brak

### 082. `colorful graphic tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Multicolor"]`

**Residual** — `graphic`

### 083. `bella canvas tshirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Bella Canvas"]`

**Residual** — brak

### 084. `tie dyed tshirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `tie dyed`

### 085. `russell athletic t shirt big and tall`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Russell Athletic"]`

**Residual** — `big and tall`

### 086. `black or navy t-shirt with a front pocket`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["Black", "Blue"]`

**Residual** — `navy` · `with a front pocket`

### 087. `lululemon tee shirts women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Lululemon"]`
- `gender in ["Women"]`

**Residual** — brak

### 088. `twisted navy and brown tees`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_all ["Blue", "Brown"]`

**Residual** — `twisted` · `navy`

### 089. `next level t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Next Level"]`

**Residual** — brak

### 090. `white nautica t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`
- `brand in ["Nautica"]`
- `gender in ["Men"]`

**Residual** — brak

### 091. `konflic mens all over print mma muscle tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Konflic"]`
- `gender in ["Men"]`

**Residual** — `all over print` · `mma` · `muscle`

### 092. `camo woodland t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Camo"]`

**Residual** — `woodland camo`

### 093. `30% wool t-shirt for winter layering`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `main_composition contains_any ["Wool"]`

**Residual** — `for winter layering`

### 094. `plain black t shirts men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Solid"]`
- `colors contains_any ["Black"]`
- `gender in ["Men"]`

**Residual** — brak

### 095. `fruit of the loom xlt black t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Fruit of the Loom"]`
- `colors contains_any ["Black"]`

**Residual** — `xlt`

### 096. `pink and blue graphic tee, no red`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_all ["Pink", "Blue"]`
- `colors contains_none ["Red"]`

**Residual** — `graphic`

### 097. `32 degrees cool mens v neck t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["32 Degrees"]`
- `gender in ["Men"]`
- `neckline in ["V-Neck"]`

**Residual** — `cool`

### 098. `casual graphic tees for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `casual` · `graphic`

### 099. `women's tee made only from wool and cotton`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `main_composition equals_set ["Wool", "Cotton"]`

**Residual** — brak

### 100. `nasa t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `nasa`

## Zapytania 101-125

### 101. `motherhood maternity nursing tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Motherhood Maternity"]`

**Residual** — `nursing`

### 102. `striped tee shirt men long sleeve`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Striped"]`
- `gender in ["Men"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — brak

### 103. `saying spanish tshirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `spanish sayings`

### 104. `camiseta blanca de algodón con cuello en V para mujer`

**Kategoria** — `T-shirts` · hiszpański · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`
- `main_composition contains_any ["Cotton"]`
- `neckline in ["V-Neck"]`
- `gender in ["Women"]`

**Residual** — brak

### 105. `t shirt men simple`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `simple`

### 106. `women's slim or regular fit white tee`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `fit in ["Slim", "Regular"]`
- `colors contains_any ["White"]`

**Residual** — brak

### 107. `retirement t shirts for women that say not my problem`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `retirement` · `that say not my problem`

### 108. `cooling tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `cooling`

### 109. `free mom hugs pride lgbt t shirt gift`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `free mom hugs pride lgbt` · `gift`

### 110. `women's long sleeve ivory t-shirt between £20 and £40`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `sleeve_length in ["Long Sleeve"]`
- `colors contains_any ["White"]`
- `price gte 20`
- `price lte 40`

**Residual** — `ivory`

### 111. `thick long sleeve t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Men"]`

**Residual** — `thick`

### 112. `under armour tech tee 407`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Under Armour"]`

**Residual** — `tech 407`

### 113. `superman tshirt slim fit men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Slim"]`
- `gender in ["Men"]`

**Residual** — `superman`

### 114. `soft cotton tshirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Cotton"]`
- `gender in ["Women"]`

**Residual** — `soft`

### 115. `black t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `gender in ["Men"]`

**Residual** — brak

### 116. `long sleeve tee shirts pack mens`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Men"]`

**Residual** — `pack`

### 117. `life is good mens tshirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Life is Good"]`
- `gender in ["Men"]`

**Residual** — brak

### 118. `adidas t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Adidas"]`
- `gender in ["Men"]`

**Residual** — brak

### 119. `long tshirt for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Longline"]`
- `gender in ["Women"]`

**Residual** — brak

### 120. `womens vneck tshirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `neckline in ["V-Neck"]`

**Residual** — brak

### 121. `purple tshirts unisex`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Purple"]`

**Residual** — `unisex`

### 122. `mens basic striped t-shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `pattern in ["Striped"]`

**Residual** — `basic`

### 123. `i've decided i'm not old snoopy t-shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `i've decided i'm not old snoopy`

### 124. `gildan t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Gildan"]`

**Residual** — brak

### 125. `mens cotton elvis tees`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `elvis`

## Zapytania 126-150

### 126. `mens under armour short sleeve t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `brand in ["Under Armour"]`
- `sleeve_length in ["Short Sleeve"]`

**Residual** — brak

### 127. `distressed disney tee white`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`

**Residual** — `distressed` · `disney`

### 128. `mens rock tee shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `rock`

### 129. `powerhouse gym t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `powerhouse gym`

### 130. `camiseta negra de manga larga para hombre hasta 30 euros`

**Kategoria** — `T-shirts` · hiszpański · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Men"]`
- `price lte 30`

**Residual** — brak

### 131. `women's neck tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — brak

### 132. `butterfly peace sign t shirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `butterfly peace sign`

### 133. `women's Off-White t-shirt with a small logo`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `brand in ["Off-White"]`

**Residual** — `with a small logo`

### 134. `tuxedo t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `tuxedo`

### 135. `lacoste t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Lacoste"]`

**Residual** — brak

### 136. `graphic tees for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `graphic`

### 137. `v neck white t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `neckline in ["V-Neck"]`
- `colors contains_any ["White"]`
- `gender in ["Women"]`

**Residual** — brak

### 138. `bcba gifts tshirt vneck`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `neckline in ["V-Neck"]`

**Residual** — `bcba gifts`

### 139. `freedom is not free t-shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `freedom is not free`

### 140. `mens nike t shirts dri fit`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `brand in ["Nike"]`

**Residual** — `dri fit`

### 141. `ladies petite v neck cotton t shirts soft`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `neckline in ["V-Neck"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `petite` · `soft`

### 142. `tight t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Slim"]`

**Residual** — brak

### 143. `big and tall printed t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `big and tall` · `printed`

### 144. `mens white graphic t-shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors contains_any ["White"]`

**Residual** — `graphic`

### 145. `chevron tshirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `chevron`

### 146. `the white stripes t shirt band`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `the white stripes band`

### 147. `pro club heavyweight t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Pro Club"]`

**Residual** — `heavyweight`

### 148. `aesthetic t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `aesthetic`

### 149. `i cannot live without books tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `i cannot live without books`

### 150. `mens 100% polyester t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `main_composition equals_set ["Polyester"]`

**Residual** — brak

## Zapytania 151-175

### 151. `mens elongated t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `length in ["Longline"]`

**Residual** — brak

### 152. `breast cancer awareness tshirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `breast cancer awareness`

### 153. `mens+organic+cotton+long+sleeve+tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `main_composition contains_any ["Cotton"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — `organic cotton`

### 154. `soft cotton or linen t-shirt without polyester`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester"]`

**Residual** — `soft`

### 155. `turkusowa koszulka na wakacje`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["Blue"]`

**Residual** — `turkusowa` · `na wakacje`

### 156. `men's nike tee shirts 3xl`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `brand in ["Nike"]`

**Residual** — `3xl`

### 157. `off-white cotton tee with no graphics`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `off-white` · `with no graphics`

### 158. `daisies t-shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `daisies`

### 159. `men's black crew neck t-shirt up to $30`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors contains_any ["Black"]`
- `neckline in ["Crewneck"]`
- `price lte 30`

**Residual** — brak

### 160. `men's round neck tee shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `neckline in ["Crewneck"]`

**Residual** — brak

### 161. `100% cotton tee for a family reunion`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `main_composition equals_set ["Cotton"]`

**Residual** — `for a family reunion`

### 162. `disney halloween tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `disney` · `halloween`

### 163. `'thou shalt not try me' relaxed-fit tee - women & plus`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Oversized"]`
- `gender in ["Women"]`

**Residual** — `thou shalt not try me` · `plus`

### 164. `plain tunic t shirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Solid"]`
- `length in ["Longline"]`
- `gender in ["Women"]`

**Residual** — `tunic`

### 165. `goodthreads tshirt pack`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Goodthreads"]`

**Residual** — `pack`

### 166. `oversized tshirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Oversized"]`
- `gender in ["Women"]`

**Residual** — brak

### 167. `biała lub szara koszulka Nike`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["White", "Grey"]`
- `brand in ["Nike"]`

**Residual** — brak

### 168. `work tshirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `work`

### 169. `fruit of the loom mens t shirts`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Fruit of the Loom"]`
- `gender in ["Men"]`

**Residual** — brak

### 170. `tshirt for women with sayings`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `with sayings`

### 171. `damski t-shirt w paski do noszenia z jeansami`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `pattern in ["Striped"]`

**Residual** — `do noszenia z jeansami`

### 172. `white lace tshirt juniors`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`

**Residual** — `lace` · `juniors`

### 173. `soft wash tee shirts men cotton`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `soft wash`

### 174. `graphic tees for women plus size boss`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `graphic` · `plus size` · `boss`

### 175. `glow in the dark tee`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `glow in the dark`

## Zapytania 176-200

### 176. `boys tshirts size 8`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `boys` · `size 8`

### 177. `4th july tees 12 mo`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `4th july` · `12 mo`

### 178. `80s lip print tshirt for plus size women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `80s lip print` · `plus size`

### 179. `peplum t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `peplum`

### 180. `v neck t shirts women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `neckline in ["V-Neck"]`
- `gender in ["Women"]`

**Residual** — brak

### 181. `bowling tshirts for women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `bowling`

### 182. `this is not a drill tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `this is not a drill`

### 183. `white or grey long sleeve tee for women`

**Kategoria** — `T-shirts` · angielski · inspirowane Amazon ESCI

**Filtry**

- `colors contains_any ["White", "Grey"]`
- `sleeve_length in ["Long Sleeve"]`
- `gender in ["Women"]`

**Residual** — brak

### 184. `calvin klein t shirt men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Calvin Klein"]`
- `gender in ["Men"]`

**Residual** — brak

### 185. `koszulka damska z długim rękawem`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — brak

### 186. `cream v neck t shirt women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["White"]`
- `neckline in ["V-Neck"]`
- `gender in ["Women"]`

**Residual** — `cream`

### 187. `graffic tees women`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `graphic`

### 188. `hanes red t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Hanes"]`
- `colors contains_any ["Red"]`

**Residual** — brak

### 189. `jerzees long sleeve t shirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Jerzees"]`
- `sleeve_length in ["Long Sleeve"]`

**Residual** — brak

### 190. `męski czarny t-shirt z okrągłym dekoltem do 120 zł`

**Kategoria** — `T-shirts` · polski · inspirowane Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors contains_any ["Black"]`
- `neckline in ["Crewneck"]`
- `price lte 120`

**Residual** — brak

### 191. `3xl tshirts for men big and tall`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `3xl` · `big and tall`

### 192. `carhartt t shirts for men`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Carhartt"]`
- `gender in ["Men"]`

**Residual** — brak

### 193. `womens snug tshirt`

**Kategoria** — `T-shirts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `fit in ["Slim"]`

**Residual** — brak

### 194. `all-black T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`

**Residual** — brak

### 195. `T-shirt in black and white only`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black", "White"]`

**Residual** — brak

### 196. `black or white T-shirt, no red`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Black", "White"]`
- `colors contains_none ["Red"]`

**Residual** — brak

### 197. `cotton and silk T-shirt without polyester`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Silk"]`
- `main_composition contains_none ["Polyester"]`

**Residual** — brak

### 198. `slim or regular fit T-shirt, but not oversized`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Slim", "Regular"]`
- `fit not_in ["Oversized"]`

**Residual** — brak

### 199. `beige scoop-neck T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Beige"]`
- `neckline in ["Scoop Neck"]`

**Residual** — brak

### 200. `high-neck T-shirt with 3/4 sleeves`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `neckline in ["High Neck"]`
- `sleeve_length in ["Three-Quarter Sleeve"]`

**Residual** — brak

## Zapytania 201-206

### 201. `sleeveless polka-dot T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `sleeve_length in ["Sleeveless"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 202. `regular-length leopard-print T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Regular"]`
- `pattern in ["Animal Print"]`

**Residual** — brak

### 203. `plaid T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Plaid"]`

**Residual** — brak

### 204. `viscose T-shirt with elastane`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Viscose", "Elastane"]`

**Residual** — brak

### 205. `nylon T-shirt for running`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Nylon"]`

**Residual** — `for running`

### 206. `cashmere-blend T-shirt`

**Kategoria** — `T-shirts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cashmere"]`

**Residual** — brak
