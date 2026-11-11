# Zapytania dla Jackets — przegląd oczekiwanych odpowiedzi

53 zapytań z [pliku CSV](jackets_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050) · [051–053](#zapytania-051-053)

## Zapytania 001-025

### 001. `80s windbreaker jacket`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `jacket_style in ["Windbreaker"]`

**Residual** — `80s`

### 002. `90s jacket for women`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Women"]`

**Residual** — `90s`

### 003. `A basic, denim jacket that has a slightly oversized fit.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `jacket_style in ["Denim"]`
- `fit in ["Oversized"]`

**Residual** — `basic`

### 004. `A new jacket which is green in colour and lightweight`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Green"]`

**Residual** — `new` · `lightweight`

### 005. `A warm jacket that feels comfy. Also probably one with plaid.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `pattern in ["Plaid"]`

**Residual** — `warm` · `comfy`

### 006. `Black leather jacket with a removable hood insert. Similar to a biker jacket.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `main_composition contains_any ["Leather"]`
- `hood in ["With Hood"]`
- `jacket_style in ["Biker"]`

**Residual** — `removable hood insert`

### 007. `Black leather jacket with dark leopard print and black patent leather detailing.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `main_composition contains_any ["Leather"]`
- `pattern in ["Animal Print"]`

**Residual** — `dark leopard print` · `black patent leather detailing`

### 008. `I am looking to purchase a black leather biker jacket, which has to be real leather`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `main_composition contains_any ["Leather"]`
- `jacket_style in ["Biker"]`

**Residual** — `real leather`

### 009. `I want a black leather jacket with gold zips and pocket buttons`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `main_composition contains_any ["Leather"]`

**Residual** — `gold zips` · `pocket buttons`

### 010. `I want a jacket without a hood that is fairly slim-fitting, but warm.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `hood in ["Without Hood"]`

**Residual** — `slim-fitting` · `warm`

### 011. `I would buy a vintage jean jacket, with a shearling lined interior.`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `jacket_style in ["Denim"]`
- `insulation in ["Shearling Lined"]`

**Residual** — `vintage`

### 012. `cropped zip-up biker jacket with lapels`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Cropped"]`
- `closure_type contains_any ["Zip"]`
- `jacket_style in ["Biker"]`
- `collar_type in ["Lapel Collar"]`

**Residual** — brak

### 013. `regular-length, regular-fit denim jacket with a point collar`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Regular"]`
- `fit in ["Regular"]`
- `jacket_style in ["Denim"]`
- `collar_type in ["Point Collar"]`

**Residual** — brak

### 014. `longline double-breasted jacket with buttons and a belt`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Longline"]`
- `closure_type contains_all ["Double-Breasted", "Button", "Belted"]`

**Residual** — brak

### 015. `windbreaker with a stand collar and no hood`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `jacket_style in ["Windbreaker"]`
- `collar_type in ["Stand Collar"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 016. `jacket with a front zip and press studs`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_all ["Zip", "Press-Stud"]`

**Residual** — brak

### 017. `open-front jacket for indoor wear`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Open Front"]`

**Residual** — `for indoor wear`

### 018. `orange down-filled jacket with a nylon shell`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Orange"]`
- `insulation in ["Down"]`
- `main_composition contains_any ["Nylon"]`

**Residual** — brak

### 019. `lightly padded jacket with synthetic insulation`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Synthetic Padding"]`

**Residual** — `lightly padded`

### 020. `fleece-lined jacket without a hood`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Fleece Lined"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 021. `unlined denim jacket`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition equals_set ["Unlined"]`
- `jacket_style in ["Denim"]`

**Residual** — brak

### 022. `uninsulated cotton jacket with silk lining`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Uninsulated"]`
- `main_composition contains_any ["Cotton"]`
- `lining_composition contains_any ["Silk"]`

**Residual** — brak

### 023. `denim or biker jacket, no windbreakers`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `jacket_style in ["Denim", "Biker"]`
- `jacket_style not_in ["Windbreaker"]`

**Residual** — brak

### 024. `khaki camo jacket with zip pockets`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Green"]`
- `pattern in ["Camo"]`

**Residual** — `khaki` · `with zip pockets`

### 025. `kurtka dżinsowa bez kaptura do 250 zł`

**Kategoria** — `Jackets` · polski · przykład syntetyczny

**Filtry**

- `jacket_style in ["Denim"]`
- `hood in ["Without Hood"]`
- `price lte 250`

**Residual** — brak

## Zapytania 026-050

### 026. `skórzana kurtka motocyklowa na wiosnę`

**Kategoria** — `Jackets` · polski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Leather"]`
- `jacket_style in ["Biker"]`

**Residual** — `na wiosnę`

### 027. `chaqueta negra con cierre de cremallera`

**Kategoria** — `Jackets` · hiszpański · przykład syntetyczny

**Filtry**

- `colors contains_any ["Black"]`
- `closure_type contains_any ["Zip"]`

**Residual** — brak

### 028. `black denim jacket mens`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Black"]`
- `jacket_style in ["Denim"]`
- `gender in ["Men"]`

**Residual** — brak

### 029. `cropped distressed denim jacket`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `length in ["Cropped"]`
- `jacket_style in ["Denim"]`

**Residual** — `distressed`

### 030. `denim jacket plus size oversized`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `jacket_style in ["Denim"]`
- `fit in ["Oversized"]`

**Residual** — `plus size`

### 031. `red denim jacket for men`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Red"]`
- `jacket_style in ["Denim"]`
- `gender in ["Men"]`

**Residual** — brak

### 032. `tan denim jacket`

**Kategoria** — `Jackets` · angielski · Amazon ESCI

**Filtry**

- `colors contains_any ["Beige"]`
- `jacket_style in ["Denim"]`

**Residual** — `tan`

### 033. `floral jacket with silk lining`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Floral"]`
- `lining_composition contains_any ["Silk"]`

**Residual** — brak

### 034. `striped jacket with a wool shell`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Striped"]`
- `main_composition contains_any ["Wool"]`

**Residual** — brak

### 035. `rain jacket with waterproof pockets`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry** — brak

**Residual** — `rain` · `with waterproof pockets`

### 036. `jacket with a zip and press studs only`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `closure_type equals_set ["Zip", "Press-Stud"]`

**Residual** — brak

### 037. `jacket with a zip or press studs, no buttons`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Zip", "Press-Stud"]`
- `closure_type contains_none ["Button"]`

**Residual** — brak

### 038. `black or white jacket, no red or pink`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 039. `yellow and black jacket with no blue`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_all ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 040. `all-white jacket`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 041. `jacket in grey and purple only`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 042. `turquoise jacket around 89.99 euros`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 043. `cotton or linen jacket without polyester or nylon`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 044. `cotton and elastane jacket without acrylic`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 045. `jacket made only from cotton and polyester`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 046. `jacket by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 047. `navy jacket, any brand except Zara or H&M`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 048. `beige jacket for work at least $35`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 049. `green jacket with roomy pockets, up to $85`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 050. `multicolor jacket for a music festival`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Multicolor"]`

**Residual** — `for a music festival`

## Zapytania 051-053

### 051. `pink polka-dot jacket`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 052. `plain brown jacket for travel`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors contains_any ["Brown"]`

**Residual** — `for travel`

### 053. `orange jacket that packs easily for a weekend trip`

**Kategoria** — `Jackets` · angielski · przykład syntetyczny

**Filtry**

- `colors contains_any ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
