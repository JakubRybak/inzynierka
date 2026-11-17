# Zapytania dla Jeans — przegląd oczekiwanych odpowiedzi

53 zapytań z [pliku CSV](jeans_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050) · [051–053](#zapytania-051-053)

## Zapytania 001-025

### 001. `000 black jeans not ripped`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `distressing contains_none ["Distressed"]`

**Residual** — `000`

### 002. `20 womens jeans elastic waist`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `waistband_type in ["Elasticized"]`

**Residual** — `20`

### 003. `34 x 28 slim fit stretch jeans`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Slim"]`

**Residual** — `34 x 28` · `stretch`

### 004. `501 levis jeans for men`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Levi's"]`
- `gender in ["Men"]`

**Residual** — `501`

### 005. `ag jeans women`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["AG Jeans"]`
- `gender in ["Women"]`

**Residual** — brak

### 006. `ariat jeans m4 low rise bootcut`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Ariat"]`
- `rise in ["Low-Rise"]`
- `leg_shape in ["Flared"]`

**Residual** — `m4` · `bootcut`

### 007. `baggy jeans`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Relaxed"]`

**Residual** — brak

### 008. `bell bottom jeans for women`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `leg_shape in ["Flared"]`
- `gender in ["Women"]`

**Residual** — `bell bottom`

### 009. `big and tall wrangler jeans men relaxed fit`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Wrangler"]`
- `gender in ["Men"]`
- `fit in ["Relaxed"]`

**Residual** — `big and tall`

### 010. `biker jeans for men skinny fit`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `fit in ["Skinny"]`

**Residual** — `biker`

### 011. `black jeans for women high waist`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `gender in ["Women"]`
- `rise in ["High-Rise"]`

**Residual** — brak

### 012. `black wide jeans for women`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `leg_shape in ["Wide-Leg"]`
- `gender in ["Women"]`

**Residual** — brak

### 013. `brown jeans`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Brown"]`

**Residual** — brak

### 014. `calvin klein mens jeans slim straight`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Calvin Klein"]`
- `gender in ["Men"]`
- `fit in ["Slim"]`
- `leg_shape in ["Straight"]`

**Residual** — brak

### 015. `carpenter jeans for men`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `carpenter`

### 016. `regular-fit full-length jeans with open hems`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Regular"]`
- `length in ["Full-Length"]`
- `cuff_style in ["Open Hem"]`

**Residual** — brak

### 017. `mid-rise cropped tapered jeans with zippered ankle cuffs`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `rise in ["Mid-Rise"]`
- `length in ["Cropped"]`
- `leg_shape in ["Tapered"]`
- `cuff_style in ["Zippered Cuff"]`

**Residual** — brak

### 018. `jeans with elastic ankle cuffs and a zip fly`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `cuff_style in ["Elasticized Cuff"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 019. `raw denim jeans with no fading`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_any ["Clean"]`
- `distressing contains_none ["Faded"]`

**Residual** — `raw denim`

### 020. `faded and ripped jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_all ["Faded", "Distressed"]`

**Residual** — brak

### 021. `faded or ripped jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_any ["Faded", "Distressed"]`

**Residual** — brak

### 022. `faded jeans with no rips`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_any ["Faded"]`
- `distressing contains_none ["Distressed"]`

**Residual** — brak

### 023. `jeans with fading and distressing only`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing equals_set ["Faded", "Distressed"]`

**Residual** — brak

### 024. `jeans without fading or distressing`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_none ["Faded", "Distressed"]`

**Residual** — brak

### 025. `jeans with a clean finish and no distressing`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_any ["Clean"]`
- `distressing contains_none ["Distressed"]`

**Residual** — brak

## Zapytania 026-050

### 026. `acid-wash grey jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `distressing contains_any ["Faded"]`
- `colors equals_set ["Grey"]`

**Residual** — `acid-wash`

### 027. `bootcut jeans with a raw hem`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `leg_shape in ["Flared"]`
- `cuff_style in ["Open Hem"]`

**Residual** — `bootcut` · `raw hem`

### 028. `dżinsy z wysokim stanem i prostą nogawką do 250 zł`

**Kategoria** — `Jeans` · polski · przykład syntetyczny

**Filtry**

- `rise in ["High-Rise"]`
- `leg_shape in ["Straight"]`
- `price lte 250`

**Residual** — brak

### 029. `jasnoniebieskie dżinsy bez przetarć`

**Kategoria** — `Jeans` · polski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `distressing contains_none ["Distressed"]`

**Residual** — `jasnoniebieskie`

### 030. `vaqueros negros de tiro medio y pierna ancha`

**Kategoria** — `Jeans` · hiszpański · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `rise in ["Mid-Rise"]`
- `leg_shape in ["Wide-Leg"]`

**Residual** — brak

### 031. `carhartt bootcut jeans for men`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Carhartt"]`
- `leg_shape in ["Flared"]`
- `gender in ["Men"]`

**Residual** — `bootcut`

### 032. `black skinny jeans women`

**Kategoria** — `Jeans` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `fit in ["Skinny"]`
- `gender in ["Women"]`

**Residual** — brak

### 033. `floral jeans with a high rise`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`
- `rise in ["High-Rise"]`

**Residual** — brak

### 034. `striped jeans with an elastic waistband`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Striped"]`
- `waistband_type in ["Elasticized"]`

**Residual** — brak

### 035. `plaid jeans with an open hem`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Plaid"]`
- `cuff_style in ["Open Hem"]`

**Residual** — brak

### 036. `camo jeans with a button fly`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Camo"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 037. `leopard-print straight-leg jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Animal Print"]`
- `leg_shape in ["Straight"]`

**Residual** — `leopard print`

### 038. `black or white jeans, no red or pink`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_any_set ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 039. `yellow and black jeans with no blue`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 040. `all-white jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 041. `jeans in grey and purple only`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 042. `turquoise jeans around 89.99 euros`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 043. `cotton or linen jeans without polyester or nylon`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 044. `cotton and elastane jeans without acrylic`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 045. `jeans made only from cotton and polyester`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 046. `jeans by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 047. `navy jeans, any brand except Zara or H&M`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 048. `beige jeans for work at least $35`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 049. `green jeans with roomy pockets, up to $85`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 050. `multicolor jeans for a music festival`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Multicolor"]`

**Residual** — `for a music festival`

## Zapytania 051-053

### 051. `pink polka-dot jeans`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 052. `plain brown jeans for travel`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors equals_set ["Brown"]`

**Residual** — `for travel`

### 053. `orange jeans that packs easily for a weekend trip`

**Kategoria** — `Jeans` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
