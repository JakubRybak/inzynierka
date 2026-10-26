# Test integracji LLM — 6 produktów

Po 2 nowe produkty z T-shirts, Dresses i Tank tops & Camisoles. Oceniono opisy i wszystkie zdjęcia po wybraniu próbki. Poniższy przegląd jest oceną Codexa, nie niezależnym pomiarem accuracy.

Gemini Flash-Lite 3.5, thinking MEDIUM, media resolution MEDIUM. Jeden produkt na wywołanie, wszystkie zdjęcia celu i zdjęcia 1 oraz 3 każdego z dwóch sąsiadów.

## Wynik techniczny

- 6/6 odpowiedzi kompletnych, ze STOP, poprawnych według walidacji lokalnej.
- 6/6 produktów ma komplet cech. Brak outside_schema i problemów całego produktu w tej próbce.
- Każdy sąsiad ma tę samą kategorię i płeć; sąsiedzi są różni od celu i od siebie.
- Pola przypisane keywordami zachowane; etykiety przykładów i schema obejmują tylko brakujące cechy.
- Faktycznie wysłano zdjęcia 1 i 3 referencji; 8 obrazów na wywołanie, a w jednym przypadku 9, bo cel miał 5 zdjęć.
- JSONL i Parquet zawierają równoważne dane. Bank urósł z 60 do 66 produktów.

## Koszt

| Produkt | Kategoria | Input tokens | Output | Thinking | USD | Czas [s] |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2071147 | T-shirts | 6544 | 65 | 228 | 0.0026957 | 2.50 |
| 2029773 | T-shirts | 6277 | 75 | 0 | 0.0020706 | 1.70 |
| 1170223 | Dresses | 7328 | 118 | 547 | 0.0038609 | 10.04 |
| 101979 | Dresses | 7395 | 119 | 492 | 0.0037460 | 3.07 |
| 96701 | Tank tops & Camisoles | 6589 | 86 | 456 | 0.0033317 | 2.95 |
| 110446 | Tank tops & Camisoles | 6854 | 97 | 528 | 0.0036187 | 3.37 |

Łącznie **0.0193236 USD** według tokenów i stawek $0.30/M input oraz $2.50/M output (w tym thinking). To oszacowanie, nie odczyt faktury. Nie doliczono wcześniejszych embeddingów.

[Cennik Google Cloud](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing).

## Przegląd produktów

### 2071147 — Navy Knight T-Shirt

Short sleeve cotton jersey t-shirt in navy featuring multicolor graphic pattern printed throughout. Logo patch at rib knit crewneck collar. Tonal stitching.

**Sąsiedzi:** image: 2174687 (cosine 0.7104), text: 2278407 (cosine 0.7066).

| Cecha | Wynik LLM |
| --- | --- |
| `pattern` | Other |
| `fit` | Regular |
| `length` | Regular |

Other pasuje do nadruku imitującego dekoracje munduru. Regular/Regular wyglądają rozsądnie. Blue zachowane z keywordów mimo wielobarwnej grafiki — to oczekiwane zachowanie blokady.

![2071147_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2071147/2071147_id_gridfs_1.png)
![2071147_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2071147/2071147_id_gridfs_2.png)
![2071147_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2071147/2071147_id_gridfs_3.png)
![2071147_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2071147/2071147_id_gridfs_4.png)
![2071147_id_gridfs_5](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2071147/2071147_id_gridfs_5.png)

---

### 2029773 — White 'All is Love' T-Shirt

Short sleeve cotton jersey t-shirt in 'pure' white. Embroidered appliqu� in white and black at bust. Rolled cuffs. Tonal stitching.

**Sąsiedzi:** image: 1409733 (cosine 0.7688), text: 2556848 (cosine 0.8011).

| Cecha | Wynik LLM |
| --- | --- |
| `pattern` | Other |
| `neckline` | Crewneck |
| `fit` | Regular |
| `length` | Regular |

Other odpowiada napisowi/aplikacji. Crewneck, Regular i Regular są zgodne ze zdjęciami.

![2029773_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2029773/2029773_id_gridfs_1.png)
![2029773_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2029773/2029773_id_gridfs_2.png)
![2029773_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2029773/2029773_id_gridfs_3.png)
![2029773_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/2029773/2029773_id_gridfs_4.png)

---

### 1170223 — Black Woven V-Back Dress

Textured-weave dress in black. Funnel collar. Zip closure at side seam. Padded and pleated details at shoulders. Tonal wrapped belt detail at waist. Draping panel at back waist. Pockets at side seam. Vented at back hem. Tonal stitching.

**Sąsiedzi:** image: 626003 (cosine 0.8204), text: 1924363 (cosine 0.7522).

| Cecha | Wynik LLM |
| --- | --- |
| `pattern` | Solid |
| `sleeve_length` | Sleeveless |
| `neckline` | High Neck |
| `dress_silhouette` | Straight |
| `dress_type` | ["Other"] |
| `strap_style` | Standard |
| `strap_width` | Wide |

Solid, brak rękawów, High Neck i Straight są zgodne z opisem i zdjęciami. Dekoracyjne drapowanie nie zmienia zasadniczo kolumnowej sylwetki.

![1170223_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/1170223/1170223_id_gridfs_1.png)
![1170223_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/1170223/1170223_id_gridfs_2.png)
![1170223_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/1170223/1170223_id_gridfs_3.png)
![1170223_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/1170223/1170223_id_gridfs_4.png)

---

### 101979 — Metallic Silver Trapeze Maxi Cami Dress

Unstructured relaxed-fit dress in metallic silver. Scoopneck collar. Tonal stitching.

**Sąsiedzi:** image: 2186517 (cosine 0.7801), text: 626003 (cosine 0.7034).

| Cecha | Wynik LLM |
| --- | --- |
| `colors` | ["Grey"] |
| `pattern` | Solid |
| `sleeve_length` | Sleeveless |
| `neckline` | Scoop Neck |
| `dress_silhouette` | A-Line |
| `strap_style` | Standard |
| `strap_width` | Wide |

Srebrny materiał przypisano do rodziny Grey. Solid, Sleeveless, Scoop Neck, A-Line i Standard są rozsądne. Wide dla szerokich tekstylnych ramiączek jest akceptowalne.

![101979_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/101979/101979_id_gridfs_1.png)
![101979_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/101979/101979_id_gridfs_2.png)
![101979_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/101979/101979_id_gridfs_3.png)
![101979_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/101979/101979_id_gridfs_4.png)

---

### 96701 — Grey Twist Hem Tank Top

Scoop neck twist hem cotton jersey tank top in mineral grey. Trimmed collar and large arm holes. Vented side seams. Curled hem. Tonal stitching.

**Sąsiedzi:** image: 2441428 (cosine 0.8495), text: 91849 (cosine 0.7737).

| Cecha | Wynik LLM |
| --- | --- |
| `pattern` | Solid |
| `fit` | Regular |
| `length` | Longline |
| `strap_style` | Standard |
| `strap_width` | Wide |

Solid, Standard i Wide są przekonujące. Regular fit jest rozsądny; Longline jest graniczną, subiektywną oceną — wydłużony dół sięga wyraźnie poniżej pasa, ale można bronić Regular.

![96701_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/96701/96701_id_gridfs_1.png)
![96701_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/96701/96701_id_gridfs_2.png)
![96701_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/96701/96701_id_gridfs_3.png)
![96701_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/96701/96701_id_gridfs_4.png)

---

### 110446 — Navy Twist Knot Jersey Tank Top

Jersey tank top in navy. Scoopneck collar. Twist knot detail at front. Tonal stitching.

**Sąsiedzi:** image: 868803 (cosine 0.8105), text: 1891073 (cosine 0.7560).

| Cecha | Wynik LLM |
| --- | --- |
| `pattern` | Solid |
| `neckline` | Scoop Neck |
| `fit` | Regular |
| `length` | Regular |
| `strap_style` | Standard |
| `strap_width` | Wide |

Solid, Scoop Neck i Standard zgadzają się z konstrukcją. Wide, Regular fit i Regular length są rozsądne, z typową niejednoznacznością granic szerokości i dopasowania.

![110446_id_gridfs_1](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/110446/110446_id_gridfs_1.png)
![110446_id_gridfs_2](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/110446/110446_id_gridfs_2.png)
![110446_id_gridfs_3](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/110446/110446_id_gridfs_3.png)
![110446_id_gridfs_4](/Users/jakubrybak/Projekty/Test/data/processed/fashiongen/images/train/110446/110446_id_gridfs_4.png)

---

## Ograniczenia

Te sześć produktów nie sprawdza częstości pomyłek modelu ani jakości wszystkich kategorii. Ścieżki problemu produktu i outside_schema sprawdzono lokalnie na odpowiedziach syntetycznych, ponieważ model nie zwrócił ich w tym teście. Nie wymuszano prowokacyjnych odpowiedzi dodatkowymi płatnymi wywołaniami.

Najbardziej niejednoznaczna etykieta w przeglądzie to Longline dla 96701. Nie zmieniano automatycznie odpowiedzi modelu ani wcześniejszych keywordów.
