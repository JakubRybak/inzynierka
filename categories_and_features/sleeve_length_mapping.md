# Mapowanie długości rękawa (`sleeve_length`)

Dokument definiuje kanoniczne wartości używane w cesze `sleeve_length` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu). Zakres wartości jest zależny od kategorii.

---

## 1. Zakres kategorii posiadających cechę `sleeve_length`

Cecha `sleeve_length` występuje we wszystkich **10 kategoriach**, w których długość rękawa wykazuje realną wariancję w zbiorze Fashion-Gen:
* **Dział `1. Tops`** *(3 z 4 kategorii)*: `T-shirts`, `Polos`, `Bodysuits` *(brak w `Tank tops & Camisoles`, które z definicji są w 100% bez rękawów i posiadają cechę `strap_style`)*
* **Dział `2. Shirts & Blouses`** *(wszystkie 2 kategorie)*: `Shirts`, `Blouses`
* **Dział `3. Sweaters`** *(wszystkie 4 kategorie)*: `Knit Sweaters`, `Sweatshirts`, `Hoodies & Zipups`, `Cardigans`
* **Dział `8. Dresses`** *(1 kategoria)*: `Dresses`

*(W okryciach wierzchnich `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers` niemal 100% produktów posiada długi rękaw, a bezrękawniki są wydzielone do osobnej kategorii `Vests`; w kategoriach dolnych `Pants`, `Shorts`, `Skirts` cecha nie dotyczy).*

---

## 2. Tabela mapowania wartości `sleeve_length`

| # | Wartość docelowa (`sleeve_length`) | Dotychczasowe warianty zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Sleeveless`** | `Sleeveless` | Brak rękawów (`sleeveless`, `sleeveless body`, `no sleeves`, `without sleeves`). Wartość używana w `Bodysuits`, `Shirts`, `Blouses`, `Dresses` i wszystkich czterech kategoriach `Sweaters`; w `Tank tops & Camisoles` brak rękawów opisuje `strap_style`. |
| 2 | **`Short Sleeve`** | `Short Sleeve` | Krótki rękaw sięgający przed łokieć oraz bardzo krótki rękawek (`short sleeve`, `short-sleeve`, `short-sleeved`, `cap sleeve`, `cap-sleeve`, `flutter short sleeve`) |
| 3 | **`Long Sleeve`** | `Long Sleeve` | Długi rękaw sięgający do nadgarstka lub dłoni (`long sleeve`, `long-sleeve`, `long-sleeved`, `full-length sleeve`, `extra-long sleeve`, `bell long sleeve`, `bishop sleeve`) |
| 4 | **`Three-Quarter Sleeve`** | `Three-Quarter Sleeve` | Rękaw 3/4 kończący się na przedramieniu, między łokciem a nadgarstkiem (`three-quarter sleeve`, `3/4 sleeve`). Wartość dostępna w `Shirts`, `Blouses`, `Dresses` i wszystkich czterech kategoriach `Sweaters`. |

Dla `Dresses` obowiązują także reguły z [dresses_mapping.md](dresses_mapping.md).

> Produkty z rękawem do łokcia lub z nieustaloną długością rękawa nie otrzymują wartości `sleeve_length` i są wykluczane z docelowego indeksu dla kategorii używających tej cechy. Produkty bez rękawów otrzymują `Sleeveless` wyłącznie w `Bodysuits`, `Shirts`, `Blouses`, `Dresses` i wszystkich czterech kategoriach `Sweaters`; w pozostałych kategoriach obowiązują zasady zakresu danej kategorii.
