# Mapowanie konstrukcji pasa (`waistband_type`)

Dokument definiuje ujednoliconą listę **2 kanonicznych typów pasa** używanych w cesze `waistband_type` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `waistband_type`

Cecha `waistband_type` występuje w **3 kategoriach**, w których konstrukcja pasa odróżnia modele eleganckie/klasyczne od modeli sportowych/wciąganych:
* **Dział `5. Pants`** *(2 z 4 kategorii)*: `Trousers`, `Cargo Pants` *(brak w `Jeans`, gdzie niemal 100% ma klasyczny pas ze szlufkami i rozporkiem, oraz w `Sweatpants & Lounge Pants`, gdzie niemal 100% ma elastyczny pas na gumce/sznurku)*
* **Dział `6. Shorts`** *(1 kategoria)*: `Shorts` *(odróżnia eleganckie szorty chino/tailored od szortów dresowych i kąpielowych)*

---

## 2. Tabela mapowania 2 wartości `waistband_type`

| # | Wartość docelowa (`waistband_type`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Tailored`** | `Tailored / Belt Loops (Zip/Button Fly)` | Klasyczny, nierozciągliwy pas garniturowy/spodniowy wyposażony w szlufki na pasek oraz rozporek na zamek lub guziki (`belt loops`, `zip-fly`, `button-fly`, `concealed hook-eye fastening`, `tailored waistband`, `structured waist`) |
| 2 | **`Elasticized`** | `Elasticized / Drawstring (Pull-On)`, `Elasticized / Drawstring (Jogger)` | Elastyczny pas na gumce lub ze sznurkiem ściągającym (w tym spodnie wciągane `pull-on` oraz modele z elastycznym tyłem pasa) – `elasticized waistband`, `elastic waist`, `drawstring at waist`, `bungee-style drawstring`, `rib-knit waistband`, `pull-on` |
