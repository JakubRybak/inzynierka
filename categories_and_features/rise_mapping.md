# Mapowanie wysokości stanu (`rise`)

Dokument definiuje ujednoliconą listę **3 kanonicznych wysokości stanu** używanych w cesze `rise` we wszystkich kategoriach odzieży dolnej (`Pants`, `Shorts`, `Skirts`) oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `rise`

Cecha `rise` jest w 100% wspólna dla wszystkich **6 kategorii odzieży dolnej**:
* **Dział `5. Pants`** *(wszystkie 4 kategorie)*: `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans`
* **Dział `6. Shorts`** *(1 kategoria)*: `Shorts`
* **Dział `7. Skirts`** *(1 kategoria)*: `Skirts`

---

## 2. Tabela mapowania 3 wartości `rise`

| # | Wartość docelowa (`rise`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`High-Rise`** | `High-Rise / High-Waisted` | Wysoki stan sięgający talii lub pępka (`high-rise`, `high rise`, `high-waisted`, `high waist`, `paperbag waist`, `corset waist`) |
| 2 | **`Mid-Rise`** | `Mid-Rise / Regular` | Standardowy, średni stan układający się naturalnie poniżej talii (`mid-rise`, `mid rise`, `regular rise`, `medium rise`, `classic rise`, wartość domyślna gdy stan jest standardowy) |
| 3 | **`Low-Rise`** | `Low-Rise` | Niski stan opadający na biodra (`low-rise`, `low rise`, `low-waisted`, `low waist`, `hip-hugger`, `dropped waist`) |
