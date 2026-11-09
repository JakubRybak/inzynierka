# Zapytania dla Vests — przegląd oczekiwanych odpowiedzi

48 zapytań z [pliku CSV](vests_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–048](#zapytania-026-048)

## Zapytania 001-025

### 001. `black vest women`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `gender in ["Women"]`

**Residual** — brak

### 002. `carhartt men's brookville quilted nylon vest`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Carhartt"]`
- `gender in ["Men"]`
- `main_composition contains_any ["Nylon"]`

**Residual** — `brookville` · `quilted`

### 003. `chaleco amarillo hombre`

**Kategoria** — `Vests` · hiszpański · Amazon ESCI

**Filtry**

- `colors contains_any ["Yellow"]`
- `gender in ["Men"]`

**Residual** — brak

### 004. `columbia vest women`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Columbia"]`
- `gender in ["Women"]`

**Residual** — brak

### 005. `cutter & buck vest`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Cutter & Buck"]`

**Residual** — brak

### 006. `fringe vest`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `fringe`

### 007. `chaleco acolchado largo mujer`

**Kategoria** — `Vests` · hiszpański · Amazon ESCI

**Filtry**

- `length in ["Longline"]`
- `gender in ["Women"]`

**Residual** — `acolchado`

### 008. `chaleco deportivo con capucha`

**Kategoria** — `Vests` · hiszpański · Amazon ESCI

**Filtry**

- `hood in ["With Hood"]`

**Residual** — `deportivo`

### 009. `hooded down vest with a front zip`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `hood in ["With Hood"]`
- `insulation in ["Down"]`
- `closure_type contains_any ["Zip"]`

**Residual** — brak

### 010. `cropped gilet with press studs`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Cropped"]`
- `closure_type contains_any ["Press-Stud"]`

**Residual** — brak

### 011. `regular-length uninsulated vest with button closure`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Regular"]`
- `insulation in ["Uninsulated"]`
- `closure_type contains_any ["Button"]`

**Residual** — brak

### 012. `regular-fit quilted vest with synthetic padding`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Regular"]`
- `insulation in ["Synthetic Padding"]`

**Residual** — `quilted`

### 013. `oversized longline open-front vest`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Oversized"]`
- `length in ["Longline"]`
- `closure_type contains_any ["Open Front"]`

**Residual** — brak

### 014. `belted gilet without a hood`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Belted"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 015. `double-breasted wool vest with buttons`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_all ["Double-Breasted", "Button"]`
- `main_composition contains_any ["Wool"]`

**Residual** — brak

### 016. `gilet with zip and snap closure`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_all ["Zip", "Press-Stud"]`

**Residual** — brak

### 017. `gilet with buttons or snaps, no zipper`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Button", "Press-Stud"]`
- `closure_type contains_none ["Zip"]`

**Residual** — brak

### 018. `gilet with a fleece lining and hand-warmer pockets`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Fleece Lined"]`

**Residual** — `with hand-warmer pockets`

### 019. `shearling-lined leather vest`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Shearling Lined"]`
- `main_composition contains_any ["Leather"]`

**Residual** — brak

### 020. `unlined cotton vest for summer`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition equals_set ["Unlined"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `for summer`

### 021. `wool gilet with a viscose lining`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Wool"]`
- `lining_composition contains_any ["Viscose"]`

**Residual** — brak

### 022. `vest with a stand collar and no hood`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `hood in ["Without Hood"]`

**Residual** — `with a stand collar`

### 023. `pink plaid gilet`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Pink"]`
- `pattern in ["Plaid"]`

**Residual** — brak

### 024. `długa kamizelka puchowa z kapturem`

**Kategoria** — `Vests` · polski · przykład syntetyczny

**Filtry**

- `length in ["Longline"]`
- `insulation in ["Down"]`
- `hood in ["With Hood"]`

**Residual** — brak

### 025. `czarna kamizelka na zatrzaski do 200 zł`

**Kategoria** — `Vests` · polski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Black"]`
- `closure_type contains_any ["Press-Stud"]`
- `price lte 200`

**Residual** — brak

## Zapytania 026-048

### 026. `plaid vest for women`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Plaid"]`
- `gender in ["Women"]`

**Residual** — brak

### 027. `girls down vest`

**Kategoria** — `Vests` · angielski · Amazon ESCI

**Filtry**

- `insulation in ["Down"]`

**Residual** — `girls`

### 028. `striped cotton gilet for layering`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Striped"]`
- `main_composition contains_any ["Cotton"]`

**Residual** — `for layering`

### 029. `floral silk vest with an open front`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`
- `main_composition contains_any ["Silk"]`
- `closure_type contains_any ["Open Front"]`

**Residual** — brak

### 030. `camouflage gilet with chest pockets`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Camo"]`

**Residual** — `with chest pockets`

### 031. `leopard-print vest with cotton lining`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Animal Print"]`
- `lining_composition contains_any ["Cotton"]`

**Residual** — `leopard print`

### 032. `cashmere-blend vest with no hood`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cashmere"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 033. `black or white gilet, no red or pink`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 034. `yellow and black gilet with no blue`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_all ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 035. `all-white gilet`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 036. `gilet in grey and purple only`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 037. `turquoise gilet around 89.99 euros`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 038. `cotton or linen gilet without polyester or nylon`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 039. `cotton and elastane gilet without acrylic`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 040. `gilet made only from cotton and polyester`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 041. `gilet by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 042. `navy gilet, any brand except Zara or H&M`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 043. `beige gilet for work at least $35`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 044. `green gilet with roomy pockets, up to $85`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 045. `multicolor gilet for a music festival`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Multicolor"]`

**Residual** — `for a music festival`

### 046. `pink polka-dot gilet`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 047. `plain brown gilet for travel`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors contains_any ["Brown"]`

**Residual** — `for travel`

### 048. `orange gilet that packs easily for a weekend trip`

**Kategoria** — `Vests` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
