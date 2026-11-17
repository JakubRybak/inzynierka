# Zapytania dla Classic Coats — przegląd oczekiwanych odpowiedzi

54 zapytań z [pliku CSV](classic_coats_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050) · [051–054](#zapytania-051-054)

## Zapytania 001-025

### 001. `I choose a navy wool pea coat that is long and warm`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Blue"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`
- `length in ["Long"]`

**Residual** — `navy` · `pea coat` · `warm`

### 002. `black peacoat womens`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `coat_style in ["Standard"]`
- `gender in ["Women"]`

**Residual** — `peacoat`

### 003. `blue long coat formal`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Blue"]`
- `length in ["Long"]`

**Residual** — `formal`

### 004. `boho parka for women`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `coat_style in ["Parka"]`
- `gender in ["Women"]`

**Residual** — `boho`

### 005. `abrigo azul marino mujer invierno rebajas`

**Kategoria** — `Classic Coats` · hiszpański · Amazon ESCI

**Filtry**

- `colors equals_set ["Blue"]`
- `gender in ["Women"]`

**Residual** — `azul marino` · `invierno` · `rebajas`

### 006. `abrigo de pelo de mujer de invierno`

**Kategoria** — `Classic Coats` · hiszpański · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Fur"]`
- `gender in ["Women"]`

**Residual** — `invierno`

### 007. `abrigo plumas mujer largo`

**Kategoria** — `Classic Coats` · hiszpański · Amazon ESCI

**Filtry**

- `insulation in ["Down"]`
- `gender in ["Women"]`
- `length in ["Long"]`

**Residual** — brak

### 008. `short classic coat with a point collar`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Short"]`
- `coat_style in ["Standard"]`
- `collar_type in ["Point Collar"]`

**Residual** — brak

### 009. `mid-length double-breasted wool overcoat with buttons and lapels`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Mid-Length"]`
- `closure_type contains_all ["Double-Breasted", "Button"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`
- `collar_type in ["Lapel Collar"]`

**Residual** — brak

### 010. `black parka with a hood, front zip and snap closure`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `coat_style in ["Parka"]`
- `hood in ["With Hood"]`
- `closure_type contains_all ["Zip", "Press-Stud"]`

**Residual** — brak

### 011. `women's belted classic coat with no hood`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `gender in ["Women"]`
- `closure_type contains_any ["Belted"]`
- `coat_style in ["Standard"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 012. `open-front wool coat for work`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Open Front"]`
- `main_composition contains_any ["Wool"]`

**Residual** — `for work`

### 013. `regular-fit coat with a stand collar and synthetic insulation`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Regular"]`
- `collar_type in ["Stand Collar"]`
- `insulation in ["Synthetic Padding"]`

**Residual** — brak

### 014. `oversized shearling-lined coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Oversized"]`
- `insulation in ["Shearling Lined"]`

**Residual** — brak

### 015. `fleece-lined parka with a detachable hood`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Fleece Lined"]`
- `coat_style in ["Parka"]`
- `hood in ["With Hood"]`

**Residual** — `detachable hood`

### 016. `unpadded wool coat with cotton lining`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Uninsulated"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`
- `lining_composition contains_any ["Cotton"]`

**Residual** — brak

### 017. `unlined linen coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition equals_set ["Unlined"]`
- `main_composition contains_any ["Linen"]`

**Residual** — brak

### 018. `fur-trimmed hood on a wool coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `hood in ["With Hood"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`

**Residual** — `fur-trimmed hood`

### 019. `down-filled coat with a nylon shell`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Down"]`
- `main_composition contains_any ["Nylon"]`

**Residual** — brak

### 020. `plain coat with oversized buttons`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `closure_type contains_any ["Button"]`

**Residual** — `oversized buttons`

### 021. `coat with a zip or buttons, no snaps`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Zip", "Button"]`
- `closure_type contains_none ["Press-Stud"]`

**Residual** — brak

### 022. `orange plaid winter coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`
- `pattern in ["Plaid"]`

**Residual** — `winter`

### 023. `wełniany płaszcz bez kaptura do 500 zł`

**Kategoria** — `Classic Coats` · polski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Wool"]`
- `hood in ["Without Hood"]`
- `price lte 500`

**Residual** — brak

### 024. `długi płaszcz na guziki na zimę`

**Kategoria** — `Classic Coats` · polski · przykład syntetyczny

**Filtry**

- `length in ["Long"]`
- `closure_type contains_any ["Button"]`

**Residual** — `na zimę`

### 025. `calvin klein wool coats for women`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Calvin Klein"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`
- `gender in ["Women"]`

**Residual** — brak

## Zapytania 026-050

### 026. `champion coats for men`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Champion"]`
- `gender in ["Men"]`

**Residual** — brak

### 027. `full length wool coat women`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `length in ["Long"]`
- `main_composition contains_any ["Wool"]`
- `coat_style in ["Standard"]`
- `gender in ["Women"]`

**Residual** — brak

### 028. `fur coat for men`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Fur"]`
- `gender in ["Men"]`

**Residual** — brak

### 029. `goosedown coat men`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `insulation in ["Down"]`
- `gender in ["Men"]`

**Residual** — `goose down`

### 030. `men's car coat`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `coat_style in ["Standard"]`

**Residual** — `car coat`

### 031. `women parkas winter coat`

**Kategoria** — `Classic Coats` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`
- `coat_style in ["Parka"]`

**Residual** — `winter`

### 032. `cashmere overcoat with striped lining`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cashmere"]`
- `coat_style in ["Standard"]`

**Residual** — `with striped lining`

### 033. `men's pinstriped coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `gender in ["Men"]`
- `pattern in ["Striped"]`

**Residual** — brak

### 034. `women's leopard-print coat with a stand collar`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `gender in ["Women"]`
- `pattern in ["Animal Print"]`
- `collar_type in ["Stand Collar"]`

**Residual** — `leopard print`

### 035. `floral coat for a garden party`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`

**Residual** — `for a garden party`

### 036. `camo parka with a hood`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Camo"]`
- `coat_style in ["Parka"]`
- `hood in ["With Hood"]`

**Residual** — brak

### 037. `coat with a cotton and viscose lining`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition contains_all ["Cotton", "Viscose"]`

**Residual** — brak

### 038. `coat with a 100% silk lining`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition equals_set ["Silk"]`

**Residual** — brak

### 039. `black or white coat, no red or pink`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_any_set ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 040. `yellow and black coat with no blue`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 041. `all-white coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 042. `coat in grey and purple only`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 043. `turquoise coat around 89.99 euros`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 044. `cotton or linen coat without polyester or nylon`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 045. `cotton and elastane coat without acrylic`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 046. `coat made only from cotton and polyester`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 047. `coat by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 048. `navy coat, any brand except Zara or H&M`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 049. `beige coat for work at least $35`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 050. `green coat with roomy pockets, up to $85`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

## Zapytania 051-054

### 051. `multicolor coat for a music festival`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Multicolor"]`

**Residual** — `for a music festival`

### 052. `pink polka-dot coat`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 053. `plain brown coat for travel`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors equals_set ["Brown"]`

**Residual** — `for travel`

### 054. `orange coat that packs easily for a weekend trip`

**Kategoria** — `Classic Coats` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
