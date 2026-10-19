# Kategorie i Cechy (Categories & Features)

## 1. Tops

### T-shirts
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Polos
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Tank tops & Camisoles
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`strap_style`**: `Wide Straps`, `Spaghetti Straps`, `Racerback`, `Halter`, `Strapless`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Bodysuits
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`

### Wspólne cechy dla całego działu `Tops`

#### 1. Cechy w 100% wspólne (występują we wszystkich 4 kategoriach `Tops`):
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`

#### 2. Cechy częściowo wspólne (w 3 z 4 kategorii):
- **`sleeve_length`** (`Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`): obecna w `T-shirts`, `Polos`, `Bodysuits` *(brak w `Tank tops & Camisoles`, gdzie wszystko jest bez rękawów i zastępuje ją `strap_style`)*
- **`neckline`** (`Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`): obecna w `T-shirts`, `Tank tops & Camisoles`, `Bodysuits` *(brak w `Polos`, które z definicji mają kołnierzyk)*
- **`fit`** (`Slim`, `Regular`, `Relaxed`): obecna w `T-shirts`, `Polos`, `Tank tops & Camisoles` *(brak w `Bodysuits`, które z definicji są dopasowane)*

#### 3. Cechy specyficzne dla wybranych kategorii:
- **`length`** (`Cropped`, `Regular`, `Longline`): obecna w `T-shirts` oraz `Tank tops & Camisoles`
- **`strap_style`** (`Wide Straps`, `Spaghetti Straps`, `Racerback`, `Halter`, `Strapless`): specyficzna wyłącznie dla `Tank tops & Camisoles`

---

## 2. Shirts & Blouses

### Shirts
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`collar_type`**: `Point Collar`, `Camp Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Blouses
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Wspólne cechy dla całego działu `Shirts & Blouses`

#### 1. Cechy w 100% wspólne (występują w obu kategoriach `Shirts` i `Blouses`):
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve` *(identyczne 4 wartości)*
- **`fit`**: `Slim`, `Regular`, `Relaxed` *(identyczne 3 wartości)*

#### 2. Cechy specyficzne dla wybranych kategorii:
- **`collar_type`** (`Point Collar`, `Camp Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`): w `Shirts`
- **`neckline`** (`Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`): w `Blouses`
- **`length`** (`Cropped`, `Regular`, `Longline`): w `Blouses`

---

## 3. Sweaters

### Knit Sweaters
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Sweatshirts
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Hoodies & Zipups
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`hood`**: `With Hood`, `Without Hood`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Cardigans
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Wspólne cechy dla całego działu `Sweaters`

#### 1. Cechy w 100% wspólne (występują we wszystkich 4 kategoriach `Sweaters`):
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve` *(identyczne 4 wartości we wszystkich 4 kategoriach)*
- **`fit`**: `Slim`, `Regular`, `Relaxed` *(identyczne 3 wartości we wszystkich 4 kategoriach)*
- **`length`**: `Cropped`, `Regular`, `Longline` *(identyczne 3 wartości we wszystkich 4 kategoriach)*

#### 2. Cechy częściowo wspólne (w 2–3 z 4 kategorii):
- **`neckline`** (`Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`): obecna w `Knit Sweaters`, `Sweatshirts` oraz `Cardigans` *(brak wyłącznie w `Hoodies & Zipups`, gdzie zastępuje ją `hood`)*
- **`closure_type`** (`Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`): obecna w `Hoodies & Zipups` oraz `Cardigans`

#### 3. Cechy specyficzne dla pojedynczych kategorii:
- **`hood`** (`With Hood`, `Without Hood`): w `Hoodies & Zipups`

---

## 4. Jackets & Coats

### Classic Coats
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`hood`**: `With Hood`, `Without Hood`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`collar_type`**: `Point Collar`, `Camp Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling`
- **`length`**: `Short`, `Mid-Length`, `Long`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Trench Coats
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`belt`**: `Belted`, `Unbelted`
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling`
- **`length`**: `Short`, `Mid-Length`, `Long`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Jackets
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`jacket_style`**: `Biker`, `Trucker`, `Puffer`, `Windbreaker`, `Utility`, `Casual`
- **`hood`**: `With Hood`, `Without Hood`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling`
- **`length`**: `Cropped`, `Regular`, `Longline`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Bombers
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`bomber_style`**: `Flight`, `Varsity`, `Quilted`, `Blouson`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`length`**: `Cropped`, `Regular`, `Longline`

### Vests
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`hood`**: `With Hood`, `Without Hood`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover`
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling`
- **`length`**: `Cropped`, `Regular`, `Longline`
- **`fit`**: `Slim`, `Regular`, `Relaxed`

### Wspólne cechy dla całego działu `Jackets & Coats`

#### 1. Cechy w 100% wspólne (występują we wszystkich 5 kategoriach `Jackets & Coats`):
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`closure_type`**: `Zip`, `Half-Zip`, `Button`, `Double-Breasted`, `Belted`, `Open Front`, `Pullover` *(identyczne 7 wartości we wszystkich 5 kategoriach)*
- **`insulation`**: `Lightweight`, `Midweight`, `Padded`, `Shearling` *(identyczne 4 wartości we wszystkich 5 kategoriach)*
- **`length`**: obecna we wszystkich 5 kategoriach (`Short`, `Mid-Length`, `Long` dla płaszczy i trenczy oraz `Cropped`, `Regular`, `Longline` dla kurtek, bomberek i kamizelek)
- **`fit`**: `Slim`, `Regular`, `Relaxed` *(identyczne 3 wartości we wszystkich 5 kategoriach)*

#### 2. Cechy częściowo wspólne:
- **`hood`** (`With Hood`, `Without Hood`): obecna w **3 z 5 kategorii** (`Classic Coats`, `Jackets`, `Vests` – brak w `Trench Coats` i `Bombers`, gdzie kaptur występuje w <3.2% produktów)

#### 3. Cechy specyficzne dla pojedynczych kategorii:
- **`collar_type`**: w `Classic Coats` (`Point Collar`, `Camp Collar`, `Lapel Collar`, `Stand Collar`, `Shawl Collar`, `Collarless`)
- **`belt`**: w `Trench Coats` (`Belted`, `Unbelted`)
- **`jacket_style`**: w `Jackets` (`Biker`, `Trucker`, `Puffer`, `Windbreaker`, `Utility`, `Casual`)
- **`bomber_style`**: w `Bombers` (`Flight`, `Varsity`, `Quilted`, `Blouson`)

---

## 5. Pants

### Trousers
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared`
- **`length`**: `Cropped`, `Full-Length`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`
- **`waistband_type`**: `Tailored`, `Elasticized`

### Cargo Pants
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared`
- **`length`**: `Cropped`, `Full-Length`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`
- **`waistband_type`**: `Tailored`, `Elasticized`
- **`cuff_style`**: `Straight Hem`, `Elasticized Cuff`, `Zippered Cuff`

### Sweatpants & Lounge Pants
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared`
- **`length`**: `Cropped`, `Full-Length`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`
- **`cuff_style`**: `Straight Hem`, `Elasticized Cuff`, `Zippered Cuff`

### Jeans
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared`
- **`length`**: `Cropped`, `Full-Length`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`
- **`distressing`**: `Clean`, `Faded`, `Distressed`

### Wspólne cechy dla całego działu `Pants`

#### 1. Cechy w 100% wspólne (występują we wszystkich 4 kategoriach `Pants`):
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Skinny`, `Slim`, `Straight`, `Tapered`, `Relaxed`, `Wide-Leg`, `Flared` *(identyczne 7 wartości we wszystkich 4 kategoriach)*
- **`length`**: `Cropped`, `Full-Length` *(identyczne 2 wartości we wszystkich 4 kategoriach)*
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise` *(identyczne 3 wartości we wszystkich 4 kategoriach)*

#### 2. Cechy częściowo wspólne (w 2 z 4 kategorii):
- **`waistband_type`** (`Tailored`, `Elasticized`): obecna w `Trousers` oraz `Cargo Pants`
- **`cuff_style`** (`Straight Hem`, `Elasticized Cuff`, `Zippered Cuff`): obecna w `Cargo Pants` oraz `Sweatpants & Lounge Pants`

#### 3. Cechy specyficzne dla pojedynczych kategorii:
- **`distressing`** (`Clean`, `Faded`, `Distressed`): w `Jeans`

---

## 6. Shorts

### Shorts
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`waistband_type`**: `Tailored`, `Elasticized`
- **`length`**: `Short`, `Mid-Length`, `Long`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`

---

## 7. Skirts

### Skirts
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`length`**: `Mini`, `Midi`, `Maxi`
- **`skirt_style`**: `Pencil`, `A-Line`, `Pleated`, `Wrap`, `Asymmetric`
- **`rise`**: `High-Rise`, `Mid-Rise`, `Low-Rise`

---

## 8. Dresses

### Dresses
- **`gender`**: `Men`, `Women`
- **`colors`**: `Black`, `White`, `Grey`, `Navy`, `Blue`, `Red`, `Green`, `Pink`, `Beige`, `Brown`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`main_composition`**: `Cotton`, `Polyester`, `Wool`, `Viscose`, `Elastane`, `Nylon`, `Silk`, `Leather`, `Cashmere`, `Linen`, `Down`, `Fur`
- **`full_composition_text`**: pełny tekst składu surowcowego z `input_composition`
- **`pattern`**: `Solid`, `Striped`, `Plaid`, `Graphic`, `Logo`, `Floral`, `Colorblock`, `Camo`, `Animal Print`, `Polka Dot`, `Tie-Dye`
- **`length`**: `Mini`, `Midi`, `Maxi`
- **`sleeve_length`**: `Sleeveless`, `Short Sleeve`, `Elbow Sleeve`, `Long Sleeve`
- **`neckline`**: `Crewneck`, `Scoop Neck`, `V-Neck`, `Turtleneck`, `Collared`, `Square Neck`, `Off-Shoulder`
- **`fit`**: `Slim`, `Regular`, `Relaxed`
- **`dress_style`**: `Bodycon`, `A-Line`, `Shift`, `Slip`, `Shirt Dress`, `Wrap`, `Sweater Dress`
