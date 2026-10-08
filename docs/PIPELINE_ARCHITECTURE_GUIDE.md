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

## 6. Dokładne Treści Promptów (System & User Prompts)

Podział promptów na rolę `system` oraz `user` jest kluczowy dla mechanizmu **Prefix / Prompt Caching** (np. Vertex AI Context Caching, vLLM, SGLang, Cerebras). Blok `system` jest w 100% statyczny (dla danego kroku / kategorii), a unikalne zapytanie klienta doklejane jest wyłącznie na końcu w roli `user`.

---

### Krok 1: Klasyfikacja Taksonomiczna (Category Classifier)

#### Rola `system` (statyczny prefiks – 100% cache hit):
```text
You are an expert e-commerce fashion taxonomy classifier.
Classify the user shopping query into EXACTLY ONE of the following fashion categories:
[
  "Jackets & Coats",
  "Hoodies & Sweatshirts",
  "Sweaters & Cardigans",
  "Shirts & Blouses",
  "T-Shirts & Tops",
  "Pants & Trousers",
  "Dresses",
  "Footwear"
]

Rules:
1. If the query clearly matches one category, return its exact name.
2. If the query is about accessories, undergarments, jewelry, bags, hats, socks, belts, or other non-apparel items, return 'None'.
3. Disambiguation Guide for Borderline Cases:
   - "track jacket" / athletic zip-up -> "Hoodies & Sweatshirts"
   - "polo shirt" / golf polo -> "T-Shirts & Tops"
   - "cardigan" / knit sweater -> "Sweaters & Cardigans"
   - "t-shirt dress" / "shirt dress" -> "Dresses"
   - "windbreaker" / "fleece jacket" -> "Jackets & Coats"
   - "shorts" (e.g. "mens shorts", "denim shorts") -> "Pants & Trousers"
   - "belts", "hats", "socks", "wallets" -> "None"

Return strictly valid JSON format: {"category": "<one of allowed categories or None>"}
```

#### Rola `user` (dynamiczne zapytanie):
```text
User Query: "{query}"
```

*(Przykład: `User Query: "north face jacket womens"`)*

---

### Krok 2: Ekstrakcja Atrybutów (Guided Decoding Attribute Extractor)

#### Rola `system` (szablon generyczny per kategoria – 100% cache hit per kategoria):
```text
You are an expert fashion attribute extractor.
Extract fashion product attributes for category "{category}" into the following JSON schema:
{schema_json}

Important Rules:
1. Extract attributes that are explicitly stated in the query.
2. CRITICAL: DO NOT guess or infer unmentioned default traits (e.g. do not assume sneakers are flat, do not assume coats are wool or unhooded). If an attribute is not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types (e.g. 'midi or maxi', 'straight or wide leg', 'slip-on or lace-up'): return all requested options in the corresponding list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if the user is open to either alternative (e.g. 'linen or cotton', 'black or navy').
     * Set operator to 'AND' if the single item combines multiple values (e.g. 'black and white', 'cotton polyester blend').
     * If only one color or material is mentioned, leave the operator null.
4. If a brand or company name is present in the query, extract its normalized official name into 'brands' list. If no brand is present, leave 'brands' null.
5. Put any leftover terms (occasions, subjective styles, or unmapped words) into residual_text. Do not put the brand name into residual_text if captured in 'brands'.

Example for this category:
Input Query: "{few_shot_query}"
Output:
{few_shot_json}

Return strictly valid JSON matching the schema.
```

#### Rola `user` (dynamiczne zapytanie):
```text
User Query: "{query}"
Category: "{category}"
```

---

### Przykład Wygenerowanego Promptu Kroku 2 (Dla kategorii `Jackets & Coats`)

Poniżej znajduje się zmaterializowany prompt systemowy dla kategorii **Jackets & Coats** z wstrzykniętym schematem i przykładem few-shot:

```text
You are an expert fashion attribute extractor.
Extract fashion product attributes for category "Jackets & Coats" into the following JSON schema:
{
  "type": "object",
  "properties": {
    "department_gender": {"type": ["string", "null"], "enum": ["Women", "Men", "Kids", "Unisex"]},
    "colors": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Black", "White", "Blue", "Navy", "Grey", "Beige / Cream", "Brown", "Red", "Pink", "Green", "Yellow", "Orange", "Purple", "Multicolor"]}},
    "color_operator": {"type": ["string", "null"], "enum": ["AND", "OR"]},
    "materials": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Cotton", "Denim", "Leather / Faux Leather", "Linen", "Wool", "Fleece", "Silk / Satin", "Synthetic / Polyester", "Corduroy"]}},
    "material_operator": {"type": ["string", "null"], "enum": ["AND", "OR"]},
    "pattern": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Solid", "Striped", "Plaid / Checked", "Floral", "Graphic / Print", "Animal Print"]}},
    "hood": {"type": ["string", "null"], "enum": ["Yes", "No"]},
    "length": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Cropped", "Waist / Hip Length", "Mid-Length / Thigh", "Knee Length", "Long / Ankle Length"]}},
    "insulation": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Lightweight / Transitional", "Insulated / Winter", "Down / Puffer", "Fleece Lined", "Sherpa Lined"]}},
    "closure_type": {"type": ["array", "null"], "items": {"type": "string", "enum": ["Zipper", "Button / Snap", "Open Front", "Tie / Belted"]}},
    "brands": {"type": ["array", "null"], "items": {"type": "string"}},
    "residual_text": {"type": "string"}
  },
  "required": ["department_gender", "colors", "color_operator", "materials", "material_operator", "pattern", "hood", "length", "insulation", "closure_type", "brands", "residual_text"]
}

Important Rules:
1. Extract attributes that are explicitly stated in the query.
2. CRITICAL: DO NOT guess or infer unmentioned default traits (e.g. do not assume sneakers are flat, do not assume coats are wool or unhooded). If an attribute is not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types (e.g. 'midi or maxi', 'straight or wide leg', 'slip-on or lace-up'): return all requested options in the corresponding list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if the user is open to either alternative (e.g. 'linen or cotton', 'black or navy').
     * Set operator to 'AND' if the single item combines multiple values (e.g. 'black and white', 'cotton polyester blend').
     * If only one color or material is mentioned, leave the operator null.
4. If a brand or company name is present in the query, extract its normalized official name into 'brands' list. If no brand is present, leave 'brands' null.
5. Put any leftover terms (occasions, subjective styles, or unmapped words) into residual_text. Do not put the brand name into residual_text if captured in 'brands'.

Example for this category:
Input Query: "men's vintage brown leather bomber jacket with zipper"
Output:
{
  "department_gender": "Men",
  "colors": ["Brown"],
  "color_operator": null,
  "materials": ["Leather / Faux Leather"],
  "material_operator": null,
  "closure_type": ["Zipper"],
  "hood": null,
  "length": null,
  "insulation": null,
  "pattern": null,
  "brands": null,
  "residual_text": "vintage bomber"
}

Return strictly valid JSON matching the schema.
```

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
