# Mapowanie dekoltu / wykończenia pod szyją (`neckline`)

Dokument definiuje ujednoliconą listę **7 kanonicznych typów dekoltu** używanych w cesze `neckline` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description`, `input_subcategory` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `neckline`

Cecha `neckline` występuje w **8 kategoriach**, w których kształt dekoltu / wykończenia pod szyją wykazuje istotną wariancję:
* **Dział `1. Tops`** *(3 z 4 kategorii)*: `T-shirts`, `Tank tops & Camisoles`, `Bodysuits` *(brak w `Polos`, które z definicji posiadają kołnierzyk polo)*
* **Dział `2. Shirts & Blouses`** *(1 z 2 kategorii)*: `Blouses` *(w `Shirts` zastępuje ją bardziej szczegółowa cecha `collar_type`)*
* **Dział `3. Sweaters`** *(3 z 4 kategorii)*: `Knit Sweaters`, `Sweatshirts`, `Cardigans` *(brak w `Hoodies & Zipups`, gdzie wykończenie góry opisuje `hood` oraz `closure_type`)*
* **Dział `8. Dresses`** *(1 kategoria)*: `Dresses`

---

## 2. Tabela mapowania 7 wartości `neckline`

| # | Wartość docelowa (`neckline`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description` / `input_subcategory`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Crewneck`** | `Crewneck`, `Crewneck / Round Neck`, `Crewneck / High Neck` | Klasyczny, okrągły dekolt blisko szyi (`crewneck`, `crew-neck`, `rib-knit crewneck`, `round neck`, subkategoria `CREWNECKS`) |
| 2 | **`Scoop Neck`** | `Scoop / Wide Neck`, `Scoop / Round Neck` | Głębszy lub szerszy zaokrąglony dekolt (`scoop neck`, `scoopneck`, `scoop-neck`, `wide neck`, `u-neck`, `deep round neck`, `ballet neck`) |
| 3 | **`V-Neck`** | `V-Neck`, `V-Neck / Plunge`, `V-Neck / Plunging`, `V-Neck / Wrap`, `V-Neck / Y-Neck` | Dekolt w serek – klasyczny, głęboki, kopertowy lub Y-neck (`v-neck`, `v neck`, `plunging neck`, `plunge`, `surplice`, `wrap neck`, `y-neck`, `sweetheart neck`, `keyhole v-neck`, subkategoria `V-NECKS`) |
| 4 | **`Turtleneck`** | `High / Mock Neck`, `High / Turtleneck`, `Turtleneck / High / Mock Neck`, `Turtleneck / High Neck`, `High / Tie-Neck / Keyhole` | Golf, półgolf, stójka, lejący wysoki kołnierz lub wysoka szyja z wiązaniem (`turtleneck`, `roll neck`, `mock neck`, `mockneck`, `high neck`, `funnel neck`, `stand collar`, `cowl neck`, `tie-neck`, `pussy-bow`, subkategoria `TURTLENECKS`) |
| 5 | **`Collared`** | `Collared / Button-Down`, `Collar / Shirt Neck`, `Shawl / Open Collar` | Wykładany kołnierzyk koszulowy, polo, szalowy lub klapy (`spread collar`, `point collar`, `shirt collar`, `polo collar`, `button-down collar`, `shawl collar`, `notched lapel collar`, `peter pan collar`, `camp collar`) |
| 6 | **`Square Neck`** | `Square / Straight Neck`, `Scoop / Square / Boat Neck` | Dekolt kwadratowy, prosty lub szeroka łódka (`square neck`, `straight neck`, `boat neck`, `bateau neck`, `slash neck`) |
| 7 | **`Off-Shoulder`** | `Strapless / Halter`, `Halter / Strapless / Off-Shoulder`, `Scoop / Boat / Off-Shoulder` | Odkryte ramiona, dekolt gorsetowy bez ramiączek, jedno ramię lub halter wiązany na szyi (`off-shoulder`, `off-the-shoulder`, `strapless`, `bandeau`, `one-shoulder`, `asymmetric shoulder`, `halter`, `halterneck`, `bardot`, `cold-shoulder`) |
