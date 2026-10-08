# Architektura Pipeline'u Query Understanding w Modzie E-Commerce

Kompaktowy przewodnik po obecnym stanie systemu ekstrakcji semantycznej.

---

## 1. Dozwolone Kategorie (Krok 1)
System klasyfikuje zapytanie do dokładnie **jednej z 8 kategorii odzieżowych** lub zwraca **`None`** (dla akcesoriów, biżuterii, bielizny czy toreb):
1. **Jackets & Coats** (Kurtki, płaszcze, wiatrówki)
2. **Hoodies & Sweatshirts** (Bluzy z kapturem i bez, bluzy sportowe)
3. **Sweaters & Cardigans** (Swetry, kardigany, golfy)
4. **Shirts & Blouses** (Koszule eleganckie, koszule zapinane na guziki, bluzki)
5. **T-Shirts & Tops** (T-shirty, koszulki polo, tank topy)
6. **Pants & Trousers** (Spodnie, jeansy, szorty, dresy, legginsy)
7. **Dresses** (Sukienki codzienne, wieczorowe, koszulowe)
8. **Footwear** (Sneakersy, botki, sandały, szpilki, mokasyny)

---

## 2. Obsługiwane Cechy (Krok 2 – Guided Decoding)

### Cechy Globalne (dla każdej kategorii):
- **`department_gender`**: `Women`, `Men`, `Kids`, `Unisex`
- **`colors`** (14 barw): `Black`, `White`, `Blue`, `Navy`, `Grey`, `Beige / Cream`, `Brown`, `Red`, `Pink`, `Green`, `Yellow`, `Orange`, `Purple`, `Multicolor`
- **`materials`** (9 tkanin): `Cotton`, `Denim`, `Leather / Faux Leather`, `Linen`, `Wool`, `Fleece`, `Silk / Satin`, `Synthetic / Polyester`, `Corduroy`
- **`pattern`** (6 wzorów): `Solid`, `Striped`, `Plaid / Checked`, `Floral`, `Graphic / Print`, `Animal Print`

### Cechy Specyficzne dla Kategorii:
- **Jackets & Coats**: `hood` (`Yes` / `No`), `insulation` (`Lightweight / Transitional`, `Insulated / Winter`), `closure`
- **Footwear**: `shoe_style` (`Sneakers`, `Boots`, `Sandals`, `Loafers`, `Heels`, `Flats`), `shaft_height`, `fastening`, `toe_style`, `heel_sole_type`
- **Dresses**: `dress_style`, `length` (`Mini`, `Midi`, `Maxi`), `sleeve_length`, `neckline`
- **Pants & Trousers**: `pant_type` (`Jeans`, `Chinos`, `Cargo`, `Leggings`, `Sweatpants`, `Shorts`), `waist_rise`, `fit_cut`, `length`
- **Shirts & Blouses**: `sleeve_length`, `fit_cut`, `neckline_collar`
- **Hoodies & Sweatshirts**: `hood` (`Yes` / `No`), `closure_type` (`Pullover`, `Zip-up`)
- **Sweaters & Cardigans**: `sweater_style` (`Cardigan`, `Pullover`, `Turtleneck`), `neckline`

---

## 3. Logika Boolowska: Co i jak łączymy (AND / OR)

Wielowartościowość jest jawnie rozstrzygana przez operatory boolowskie:

1. **Kolory (`color_operator`):**
   - **`AND`** $\rightarrow$ wielokolorowy pojedynczy produkt (np. *"black and white shirt"* $\rightarrow$ `colors: ["Black", "White"], color_operator: "AND"`).
   - **`OR`** $\rightarrow$ alternatywa zakupowa (np. *"black or navy jacket"* $\rightarrow$ `colors: ["Black", "Navy"], color_operator: "OR"`).
2. **Materiały (`material_operator`):**
   - **`AND`** $\rightarrow$ mieszanka włókien / tkanina z podszewką (np. *"cotton polyester blend"*).
   - **`OR`** $\rightarrow$ alternatywa (np. *"linen or cotton dress"*).
3. **Fasony i kroje (listy stylów):**
   - Domyślna unia / alternatywa (np. *"midi or maxi dress"* $\rightarrow$ `length: ["Midi", "Maxi"]`).

---

## 4. Wyodrębnianie Marki (`brands`)
- **Otwarte pole tekstowe:** `brands: Optional[List[str]]` (nie jest sztywnym enumem, co pozwala wykrywać dowolne marki z rynku).
- **Automatyczna normalizacja:** np. `"the north face"` $\rightarrow$ `["The North Face"]`, `"32 degrees"` $\rightarrow$ `["32 Degrees"]`.
- **Zasada czystości:** Jeśli nazwa marki zostanie wykryta, jest usuwana z tekstu resztkowego.

---

## 5. Tekst Resztkowy (`residual_text`)
Wszystko, co **nie jest twardym atrybutem filtrowalnym SQL**, trafia do `residual_text`:
- **Okazje i przeznaczenie:** *"wedding"*, *"funeral"*, *"party"*, *"work"*
- **Styl i estetyka subiektywna:** *"casual"*, *"motorcycle"*, *"running"*, *"comfortable"*
- **Rola w systemie:** `residual_text` jest wektoryzowany (embedding) i przekazywany do gęstego wyszukiwania semantycznego (Dense Vector Search / CLIP).

---

## 6. Architektura Promptów (Podział na System i User)

### Krok 1 (Klasyfikacja):
- **`system`**: Definicja roli klasyfikatora, 8 kategorii, disambiguation guide, format JSON. *(100% statyczny cache)*
- **`user`**: `User Query: "north face jacket womens"`

### Krok 2 (Ekstrakcja Atrybutów):
- **`system`**: Schemat Pydantic JSON dla wybranej kategorii, reguły AND/OR, few-shot demonstration. *(100% statyczny cache per kategoria)*
- **`user`**: `User Query: "north face jacket womens"`

---

## 7. Przykłady Udanych Zapytań (Success Cases)

1. **Marka + Płeć:**
   - *Query:* `"north face jacket womens"`
   - *Output:* `Category: Jackets & Coats` | `{"department_gender": "Women", "brands": ["The North Face"]}` | `residual: ""`
2. **Cecha Negatywna + Ocieplenie:**
   - *Query:* `"womens lightweight jacket without hood"`
   - *Output:* `{"department_gender": "Women", "hood": "No", "insulation": ["Lightweight / Transitional"]}`
3. **Logika AND dla Multikoloru + Wzór:**
   - *Query:* `"mens black and white striped shirt"`
   - *Output:* `{"department_gender": "Men", "colors": ["Black", "White"], "color_operator": "AND", "pattern": ["Striped"]}`
4. **Wielowartościowa Alternatywa Fasonów:**
   - *Query:* `"summer linen or cotton midi dress"`
   - *Output:* `{"materials": ["Linen", "Cotton"], "material_operator": "OR", "length": ["Midi"]}` | `residual: "summer"`

---

## 8. Przykłady Typowych Błędów i Wyzwań (Failure Cases / Edge Cases)

1. **Domyślne / Niejawne cechy semantyczne:**
   - *Query:* `"ski coat women"`
   - *Problem:* Model wyciąga `department_gender: "Women"`, ale czasami pomija `insulation: "Insulated / Winter"` (bo słowo "ski" ląduje w `residual_text`, a nie jest wprost słowem "winter").
2. **Pogranicza taksonomiczne (Borderline Categories):**
   - *Query:* `"golf polo shirt"`
   - *Problem:* Czy to `T-Shirts & Tops` czy `Shirts & Blouses`? (Rozwiązane disambiguation guidem, ale modele miewają wahania).
3. **Modyfikatory sylwetki (poza schematem):**
   - *Query:* `"petite high waisted jeans"`
   - *Problem:* `"high waisted"` wpada do `waist_rise: "High Rise"`, ale `"petite"` musi lądować w `residual_text`, bo brak dedykowanego pola `size_modifier`.
