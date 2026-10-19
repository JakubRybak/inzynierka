# Mapowanie obecności kaptura (`hood`)

Dokument definiuje ujednoliconą listę **2 kanonicznych wartości** używanych w cesze `hood` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `hood`

Cecha `hood` występuje w **4 kategoriach**, w których obecność kaptura jest kluczowym kryterium wyszukiwania i wykazuje wariancję:
* **Dział `3. Sweaters`** *(1 z 4 kategorii)*: `Hoodies & Zipups` *(łączy bluzy z kapturem `hoodies` oraz rozpinane bluzy ze stójką `zip-ups` bez kaptura)*
* **Dział `4. Jackets & Coats`** *(3 z 5 kategorii)*: `Classic Coats`, `Jackets`, `Vests` *(brak w `Trench Coats` oraz `Bombers`, gdzie kaptur występuje w mniej niż 3.2% produktów)*

---

## 2. Tabela mapowania 2 wartości `hood`

| # | Wartość docelowa (`hood`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`With Hood`** | `With Hood` | Ubrania wyposażone w kaptur – stały, odpinany, chowany w kołnierzu lub ze ściągaczem (`hood`, `hoodie`, `hooded`, `drawstring hood`, `detachable hood`, `removable hood`, `stowaway hood`, `concealed hood`, `bungee-style drawstring at hood`, `snorkel hood`) |
| 2 | **`Without Hood`** | `Without Hood`, `Without Hood / Stand Collar` | Ubrania bez kaptura – np. rozpinane bluzy ze stójką (`zip-up sweatshirt` bez kaptura) oraz płaszcze, kurtki i kamizelki bez kaptura (wartość domyślna, gdy w opisie i na zdjęciu brak kaptura) |
