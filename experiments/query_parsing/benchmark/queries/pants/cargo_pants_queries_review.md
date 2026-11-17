# Zapytania dla Cargo Pants — przegląd oczekiwanych odpowiedzi

50 zapytań z [pliku CSV](cargo_pants_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050)

## Zapytania 001-025

### 001. `black cargo pants women`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `gender in ["Women"]`

**Residual** — brak

### 002. `cargo pants for men`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — brak

### 003. `cargo pants for women`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — brak

### 004. `cargo pants men big and tall`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `big and tall`

### 005. `cargo pants wrangler`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Wrangler"]`

**Residual** — brak

### 006. `dickies cargo pants for men`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Dickies"]`
- `gender in ["Men"]`

**Residual** — brak

### 007. `g star cargo pants men`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `brand in ["G-Star"]`
- `gender in ["Men"]`

**Residual** — brak

### 008. `loose high waist cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `fit in ["Relaxed"]`
- `rise in ["High-Rise"]`

**Residual** — brak

### 009. `tactical cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `tactical`

### 010. `union bay mens cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Unionbay"]`
- `gender in ["Men"]`

**Residual** — brak

### 011. `womens army cargo pants with pockets`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `army` · `with pockets`

### 012. `womens green cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `colors equals_set ["Green"]`

**Residual** — brak

### 013. `skinny low-rise cargo pants with zippered ankle cuffs`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Skinny"]`
- `rise in ["Low-Rise"]`
- `cuff_style in ["Zippered Cuff"]`

**Residual** — brak

### 014. `slim-fit cropped cargo pants with tapered legs`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Slim"]`
- `length in ["Cropped"]`
- `leg_shape in ["Tapered"]`

**Residual** — brak

### 015. `regular-fit full-length straight cargo pants`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Regular"]`
- `length in ["Full-Length"]`
- `leg_shape in ["Straight"]`

**Residual** — brak

### 016. `mid-rise wide-leg cargo pants with an elastic waistband`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `rise in ["Mid-Rise"]`
- `leg_shape in ["Wide-Leg"]`
- `waistband_type in ["Elasticized"]`

**Residual** — brak

### 017. `flared cargo pants with a structured waistband and open hems`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `leg_shape in ["Flared"]`
- `waistband_type in ["Structured"]`
- `cuff_style in ["Open Hem"]`

**Residual** — brak

### 018. `tapered cargo pants with elastic ankle cuffs`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `leg_shape in ["Tapered"]`
- `cuff_style in ["Elasticized Cuff"]`

**Residual** — brak

### 019. `slim or relaxed cargo pants, no skinny fit`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Slim", "Relaxed"]`
- `fit not_in ["Skinny"]`

**Residual** — brak

### 020. `cargo pants with a zip fly, no ankle zips`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `waistband_type in ["Structured"]`
- `cuff_style not_in ["Zippered Cuff"]`

**Residual** — brak

### 021. `cotton cargo pants with hook-and-loop ankle tabs`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton"]`

**Residual** — `with hook-and-loop ankle tabs`

### 022. `bright orange camo cargo pants`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`
- `pattern in ["Camo"]`

**Residual** — `bright orange`

### 023. `czarne bojówki z gumką w pasie do 200 zł`

**Kategoria** — `Cargo Pants` · polski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `waistband_type in ["Elasticized"]`
- `price lte 200`

**Residual** — brak

### 024. `długie bojówki z prostą nogawką na wycieczkę`

**Kategoria** — `Cargo Pants` · polski · przykład syntetyczny

**Filtry**

- `length in ["Full-Length"]`
- `leg_shape in ["Straight"]`

**Residual** — `na wycieczkę`

### 025. `pantalones cargo negros de tiro alto`

**Kategoria** — `Cargo Pants` · hiszpański · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `rise in ["High-Rise"]`

**Residual** — brak

## Zapytania 026-050

### 026. `cargo pants men`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — brak

### 027. `mens cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — brak

### 028. `womens cargo pants`

**Kategoria** — `Cargo Pants` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — brak

### 029. `floral cargo pants with a drawstring waist`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`
- `waistband_type in ["Elasticized"]`

**Residual** — brak

### 030. `plaid cargo pants with deep side pockets`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Plaid"]`

**Residual** — `with deep side pockets`

### 031. `striped cargo pants for skating`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Striped"]`

**Residual** — `for skating`

### 032. `leopard-print cargo pants with ankle zips`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Animal Print"]`
- `cuff_style in ["Zippered Cuff"]`

**Residual** — `leopard print`

### 033. `black leather cargo pants with a high rise`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `main_composition contains_any ["Leather"]`
- `rise in ["High-Rise"]`

**Residual** — brak

### 034. `khaki cargo pants with a tapered leg`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `leg_shape in ["Tapered"]`

**Residual** — `khaki`

### 035. `black or white cargo pants, no red or pink`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_any_set ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 036. `yellow and black cargo pants with no blue`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 037. `all-white cargo pants`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 038. `cargo pants in grey and purple only`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 039. `turquoise cargo pants around 89.99 euros`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 040. `cotton or linen cargo pants without polyester or nylon`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 041. `cotton and elastane cargo pants without acrylic`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 042. `cargo pants made only from cotton and polyester`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 043. `cargo pants by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 044. `navy cargo pants, any brand except Zara or H&M`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 045. `beige cargo pants for work at least $35`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 046. `green cargo pants with roomy pockets, up to $85`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 047. `multicolor cargo pants for a music festival`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Multicolor"]`

**Residual** — `for a music festival`

### 048. `pink polka-dot cargo pants`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 049. `plain brown cargo pants for travel`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors equals_set ["Brown"]`

**Residual** — `for travel`

### 050. `orange cargo pants that packs easily for a weekend trip`

**Kategoria** — `Cargo Pants` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
