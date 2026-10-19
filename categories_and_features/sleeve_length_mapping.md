# Mapowanie długości rękawa (`sleeve_length`)

Dokument definiuje ujednoliconą listę **4 kanonicznych długości rękawa** używanych w cesze `sleeve_length` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `sleeve_length`

Cecha `sleeve_length` występuje we wszystkich **10 kategoriach**, w których długość rękawa wykazuje realną wariancję w zbiorze Fashion-Gen:
* **Dział `1. Tops`** *(3 z 4 kategorii)*: `T-shirts`, `Polos`, `Bodysuits` *(brak w `Tank tops & Camisoles`, które z definicji są w 100% bez rękawów i posiadają cechę `strap_style`)*
* **Dział `2. Shirts & Blouses`** *(wszystkie 2 kategorie)*: `Shirts`, `Blouses`
* **Dział `3. Sweaters`** *(wszystkie 4 kategorie)*: `Knit Sweaters`, `Sweatshirts`, `Hoodies & Zipups`, `Cardigans`
* **Dział `8. Dresses`** *(1 kategoria)*: `Dresses`

*(W okryciach wierzchnich `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers` niemal 100% produktów posiada długi rękaw, a bezrękawniki są wydzielone do osobnej kategorii `Vests`; w kategoriach dolnych `Pants`, `Shorts`, `Skirts` cecha nie dotyczy).*

---

## 2. Tabela mapowania 4 wartości `sleeve_length`

| # | Wartość docelowa (`sleeve_length`) | Dotychczasowe warianty zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Sleeveless`** | `Sleeveless`, `Sleeveless / Strappy`, `Strapless / Off-Shoulder` | Ubrania całkowicie pozbawione rękawów, na ramiączkach lub z odkrytymi ramionami (`sleeveless`, `tank`, `camisole`, `strappy`, `spaghetti straps`, `strapless`, `bandeau`, `halterneck`, `racerback`, `cut-out shoulders` bez rękawów) |
| 2 | **`Short Sleeve`** | `Short Sleeve` | Krótki rękaw sięgający przed łokieć oraz bardzo krótki rękawek (`short sleeve`, `short-sleeve`, `short-sleeved`, `cap sleeve`, `cap-sleeve`, `flutter short sleeve`) |
| 3 | **`Elbow Sleeve`** | `3/4 / Elbow Sleeve` | Rękaw sięgający w okolice łokcia lub 3/4 długości przedramienia (`elbow sleeve`, `elbow-length sleeve`, `three-quarter sleeve`, `3/4 sleeve`, `3/4-length sleeve`, `half sleeve`, `mid-length sleeve`, `cropped sleeve`) |
| 4 | **`Long Sleeve`** | `Long Sleeve` | Pełny, długi rękaw sięgający do nadgarstka lub dłoni (`long sleeve`, `long-sleeve`, `long-sleeved`, `full-length sleeve`, `extra-long sleeve`, `bell long sleeve`, `bishop sleeve`) |
