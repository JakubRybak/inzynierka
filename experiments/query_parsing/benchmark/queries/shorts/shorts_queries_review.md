# Zapytania dla Shorts — przegląd oczekiwanych odpowiedzi

53 zapytań z [pliku CSV](shorts_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050) · [051–053](#zapytania-051-053)

## Zapytania 001-025

### 001. `100% cotton shorts women`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `main_composition equals_set ["Cotton"]`
- `gender in ["Women"]`

**Residual** — brak

### 002. `2x linen shorts mens`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Linen"]`
- `gender in ["Men"]`

**Residual** — `2x`

### 003. `3 inseam volleyball shorts women`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `shorts_type in ["Athletic"]`
- `gender in ["Women"]`

**Residual** — `3 inseam` · `volleyball`

### 004. `3x shorts for men big and tall`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `3x` · `big and tall`

### 005. `addidas grey shorts`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Adidas"]`
- `colors equals_set ["Grey"]`

**Residual** — brak

### 006. `adidas tech fit compression shorts men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Adidas"]`
- `gender in ["Men"]`
- `shorts_type in ["Athletic"]`

**Residual** — `tech fit` · `compression`

### 007. `adidas ultimate 365 golf shorts`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Adidas"]`

**Residual** — `ultimate 365` · `golf`

### 008. `all white nike shorts men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["White"]`
- `brand in ["Nike"]`
- `gender in ["Men"]`

**Residual** — brak

### 009. `american eagle shorts for men longer length`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["American Eagle"]`
- `gender in ["Men"]`
- `length in ["Long"]`

**Residual** — brak

### 010. `asics women running shorts purple`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `brand in ["ASICS"]`
- `gender in ["Women"]`
- `shorts_type in ["Athletic"]`
- `colors equals_set ["Purple"]`

**Residual** — `running`

### 011. `athletic shorts men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `shorts_type in ["Athletic"]`
- `gender in ["Men"]`

**Residual** — brak

### 012. `bermuda ripped shorts`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Long"]`

**Residual** — `bermuda` · `ripped`

### 013. `bermuda shorts for women`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `length in ["Long"]`
- `gender in ["Women"]`

**Residual** — `bermuda`

### 014. `best cargo shorts for men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `shorts_type in ["Cargo"]`
- `gender in ["Men"]`

**Residual** — brak

### 015. `big and tall cotton cargo shorts for men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Cotton"]`
- `shorts_type in ["Cargo"]`
- `gender in ["Men"]`

**Residual** — `big and tall`

### 016. `bicycling shorts padded men 3xl`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `shorts_type in ["Athletic"]`
- `gender in ["Men"]`

**Residual** — `bicycling` · `padded` · `3xl`

### 017. `bike shorts for men without padding`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `shorts_type in ["Athletic"]`
- `gender in ["Men"]`

**Residual** — `bike` · `without padding`

### 018. `short high-rise denim shorts with a zip fly`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Short"]`
- `rise in ["High-Rise"]`
- `shorts_type in ["Denim"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 019. `mid-length sweatshorts with an elastic waistband`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Mid-Length"]`
- `shorts_type in ["Sweatshorts"]`
- `waistband_type in ["Elasticized"]`

**Residual** — brak

### 020. `long low-rise tailored shorts in a slim fit`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Long"]`
- `rise in ["Low-Rise"]`
- `shorts_type in ["Tailored"]`
- `fit in ["Slim"]`

**Residual** — brak

### 021. `skinny-fit mid-rise shorts`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Skinny"]`
- `rise in ["Mid-Rise"]`

**Residual** — brak

### 022. `regular-fit cargo shorts with belt loops`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Regular"]`
- `shorts_type in ["Cargo"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 023. `relaxed-fit sweatshorts for lounging`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Relaxed"]`
- `shorts_type in ["Sweatshorts"]`

**Residual** — `for lounging`

### 024. `denim or cargo shorts, but no sweatshorts`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `shorts_type in ["Denim", "Cargo"]`
- `shorts_type not_in ["Sweatshorts"]`

**Residual** — brak

### 025. `tailored shorts with a drawstring waistband`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `shorts_type in ["Tailored"]`
- `waistband_type in ["Elasticized"]`

**Residual** — brak

## Zapytania 026-050

### 026. `swim shorts with a quick-dry lining`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry** — brak

**Residual** — `swim` · `with a quick-dry lining`

### 027. `women's mid-thigh shorts with pockets`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `gender in ["Women"]`
- `length in ["Mid-Length"]`

**Residual** — `with pockets`

### 028. `krótkie spodenki do biegania bez poliestru`

**Kategoria** — `Shorts` · polski · przykład syntetyczny

**Filtry**

- `shorts_type in ["Athletic"]`
- `main_composition contains_none ["Polyester"]`

**Residual** — `do biegania`

### 029. `czarne szorty z wysokim stanem do 120 zł`

**Kategoria** — `Shorts` · polski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `rise in ["High-Rise"]`
- `price lte 120`

**Residual** — brak

### 030. `bermudas de lino para hombre`

**Kategoria** — `Shorts` · hiszpański · przykład syntetyczny

**Filtry**

- `length in ["Long"]`
- `main_composition contains_any ["Linen"]`
- `gender in ["Men"]`

**Residual** — `bermudas`

### 031. `leopard shorts`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Animal Print"]`

**Residual** — `leopard`

### 032. `pinstripe shorts men`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Striped"]`
- `gender in ["Men"]`

**Residual** — `pinstripe`

### 033. `white linen shorts for women`

**Kategoria** — `Shorts` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["White"]`
- `main_composition contains_any ["Linen"]`
- `gender in ["Women"]`

**Residual** — brak

### 034. `floral silk shorts for a beach holiday`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`
- `main_composition contains_any ["Silk"]`

**Residual** — `for a beach holiday`

### 035. `plaid wool shorts with a high waist`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Plaid"]`
- `main_composition contains_any ["Wool"]`
- `rise in ["High-Rise"]`

**Residual** — brak

### 036. `camo cargo shorts with belt loops`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Camo"]`
- `shorts_type in ["Cargo"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 037. `black leather shorts with a zip fly`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `main_composition contains_any ["Leather"]`
- `waistband_type in ["Structured"]`

**Residual** — brak

### 038. `black or white shorts, no red or pink`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_any_set ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 039. `yellow and black shorts with no blue`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 040. `all-white shorts`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 041. `shorts in grey and purple only`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 042. `turquoise shorts around 89.99 euros`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 043. `cotton or linen shorts without polyester or nylon`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 044. `cotton and elastane shorts without acrylic`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 045. `shorts made only from cotton and polyester`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 046. `shorts by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 047. `navy shorts, any brand except Zara or H&M`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 048. `beige shorts for work at least $35`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 049. `green shorts with roomy pockets, up to $85`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 050. `multicolor shorts for a music festival`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Multicolor"]`

**Residual** — `for a music festival`

## Zapytania 051-053

### 051. `pink polka-dot shorts`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 052. `plain brown shorts for travel`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors equals_set ["Brown"]`

**Residual** — `for travel`

### 053. `orange shorts that packs easily for a weekend trip`

**Kategoria** — `Shorts` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
