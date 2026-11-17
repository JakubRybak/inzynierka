# Zapytania dla Bombers — przegląd oczekiwanych odpowiedzi

50 zapytań z [pliku CSV](bombers_queries.csv) w tej samej kolejności. Każdy wpis na liście filtrów to osobny warunek, który musi być spełniony. Fragmenty zapytania przeznaczone do rankingu są wypisane jako residual.

**Przejdź do zapytań**

[001–025](#zapytania-001-025) · [026–050](#zapytania-026-050)

## Zapytania 001-025

### 001. `A bomber jacket with inner warming lining, preferrably black`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `colors equals_set ["Black"]`
- `lining_composition contains_none ["Unlined"]`

**Residual** — `inner warming lining`

### 002. `The jacket I would try to replace with the one I wear daily is a top gun bomber jacket.`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — `top gun`

### 003. `bomber flight jacket men`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — `flight`

### 004. `bomber jacket leather men`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `main_composition contains_any ["Leather"]`
- `gender in ["Men"]`

**Residual** — brak

### 005. `bomber jacket men`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`

**Residual** — brak

### 006. `bomber jackets`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry** — brak

**Residual** — brak

### 007. `bomber roja mujer`

**Kategoria** — `Bombers` · hiszpański · Amazon ESCI

**Filtry**

- `colors equals_set ["Red"]`
- `gender in ["Women"]`

**Residual** — brak

### 008. `calvin klein men classic bomber jacket`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `brand in ["Calvin Klein"]`
- `gender in ["Men"]`

**Residual** — `classic`

### 009. `mens floral bomber jacket`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `pattern in ["Floral"]`

**Residual** — brak

### 010. `mens lightweight bomber jacket white`

**Kategoria** — `Bombers` · angielski · Amazon ESCI

**Filtry**

- `gender in ["Men"]`
- `colors equals_set ["White"]`

**Residual** — `lightweight`

### 011. `cropped hooded bomber with a front zip`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Cropped"]`
- `hood in ["With Hood"]`
- `closure_type contains_any ["Zip"]`

**Residual** — brak

### 012. `regular-length bomber with a regular fit and no hood`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `length in ["Regular"]`
- `fit in ["Regular"]`
- `hood in ["Without Hood"]`

**Residual** — brak

### 013. `oversized longline bomber with press studs`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `fit in ["Oversized"]`
- `length in ["Longline"]`
- `closure_type contains_any ["Press-Stud"]`

**Residual** — brak

### 014. `varsity bomber with buttons`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Button"]`

**Residual** — `varsity`

### 015. `bomber with a front zip and snap closure`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_all ["Zip", "Press-Stud"]`

**Residual** — brak

### 016. `open-front satin bomber`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Open Front"]`

**Residual** — `satin`

### 017. `belted bomber jacket with oversized pockets`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Belted"]`

**Residual** — `with oversized pockets`

### 018. `double-breasted bomber jacket with buttons`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_all ["Double-Breasted", "Button"]`

**Residual** — brak

### 019. `fleece-lined bomber with a hood`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Fleece Lined"]`
- `hood in ["With Hood"]`

**Residual** — brak

### 020. `shearling-lined leather bomber`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Shearling Lined"]`
- `main_composition contains_any ["Leather"]`

**Residual** — brak

### 021. `down-filled bomber with a nylon shell`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Down"]`
- `main_composition contains_any ["Nylon"]`

**Residual** — brak

### 022. `bomber with synthetic padding and a cotton lining`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Synthetic Padding"]`
- `lining_composition contains_any ["Cotton"]`

**Residual** — brak

### 023. `unlined bomber for summer`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition equals_set ["Unlined"]`

**Residual** — `for summer`

### 024. `uninsulated bomber in plain grey`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `insulation in ["Uninsulated"]`
- `pattern in ["Solid"]`
- `colors equals_set ["Grey"]`

**Residual** — brak

### 025. `bomber with a stand collar and zip pockets`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry** — brak

**Residual** — `with a stand collar` · `with zip pockets`

## Zapytania 026-050

### 026. `czarna bomberka bez kaptura do 300 zł`

**Kategoria** — `Bombers` · polski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Black"]`
- `hood in ["Without Hood"]`
- `price lte 300`

**Residual** — brak

### 027. `krótka bomberka z zamkiem na koncert`

**Kategoria** — `Bombers` · polski · przykład syntetyczny

**Filtry**

- `length in ["Cropped"]`
- `closure_type contains_any ["Zip"]`

**Residual** — `na koncert`

### 028. `striped bomber jacket with ribbed cuffs`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Striped"]`

**Residual** — `with ribbed cuffs`

### 029. `plaid wool bomber jacket`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Plaid"]`
- `main_composition contains_any ["Wool"]`

**Residual** — brak

### 030. `camouflage bomber with a detachable hood`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Camo"]`
- `hood in ["With Hood"]`

**Residual** — `detachable hood`

### 031. `leopard-print bomber with silk lining`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Animal Print"]`
- `lining_composition contains_any ["Silk"]`

**Residual** — `leopard print`

### 032. `bomber jacket with a viscose lining and a polyester shell`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `lining_composition contains_any ["Viscose"]`
- `main_composition contains_any ["Polyester"]`

**Residual** — brak

### 033. `brown suede bomber jacket`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Brown"]`
- `main_composition contains_any ["Leather"]`

**Residual** — `suede`

### 034. `bomber with a zip or snaps, no buttons`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `closure_type contains_any ["Zip", "Press-Stud"]`
- `closure_type contains_none ["Button"]`

**Residual** — brak

### 035. `black or white bomber jacket, no red or pink`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_any_set ["Black", "White"]`
- `colors contains_none ["Red", "Pink"]`

**Residual** — brak

### 036. `yellow and black bomber jacket with no blue`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Yellow", "Black"]`
- `colors contains_none ["Blue"]`

**Residual** — brak

### 037. `all-white bomber jacket`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["White"]`

**Residual** — brak

### 038. `bomber jacket in grey and purple only`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Grey", "Purple"]`

**Residual** — brak

### 039. `turquoise bomber jacket around 89.99 euros`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `price around 89.99`

**Residual** — `turquoise`

### 040. `cotton or linen bomber jacket without polyester or nylon`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_any ["Cotton", "Linen"]`
- `main_composition contains_none ["Polyester", "Nylon"]`

**Residual** — brak

### 041. `cotton and elastane bomber jacket without acrylic`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `main_composition contains_all ["Cotton", "Elastane"]`
- `main_composition contains_none ["Acrylic"]`

**Residual** — brak

### 042. `bomber jacket made only from cotton and polyester`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `main_composition equals_set ["Cotton", "Polyester"]`

**Residual** — brak

### 043. `bomber jacket by Zara or Mango, between 50 and 100 euros`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `brand in ["Zara", "Mango"]`
- `price gte 50`
- `price lte 100`

**Residual** — brak

### 044. `navy bomber jacket, any brand except Zara or H&M`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Blue"]`
- `brand not_in ["Zara", "H&M"]`

**Residual** — `navy`

### 045. `beige bomber jacket for work at least $35`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Beige"]`
- `price gte 35`

**Residual** — `for work`

### 046. `green bomber jacket with roomy pockets, up to $85`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Green"]`
- `price lte 85`

**Residual** — `with roomy pockets`

### 047. `multicolor bomber jacket for a music festival`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Multicolor"]`

**Residual** — `for a music festival`

### 048. `pink polka-dot bomber jacket`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Pink"]`
- `pattern in ["Polka Dot"]`

**Residual** — brak

### 049. `plain brown bomber jacket for travel`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `pattern in ["Solid"]`
- `colors equals_set ["Brown"]`

**Residual** — `for travel`

### 050. `orange bomber jacket that packs easily for a weekend trip`

**Kategoria** — `Bombers` · angielski · przykład syntetyczny

**Filtry**

- `colors equals_set ["Orange"]`

**Residual** — `that packs easily` · `for a weekend trip`
