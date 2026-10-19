# Mapowanie typu zapięcia (`closure_type`)

Dokument definiuje ujednoliconą listę **7 kanonicznych typów zapięcia** używanych w cesze `closure_type` we wszystkich kategoriach rozpinanej odzieży górnej oraz okryć wierzchnich, wraz z zasadami mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `closure_type`

Cecha `closure_type` występuje w **7 kategoriach** posiadających wariancję sposobu zakładania i zapinania:
* **Dział `3. Sweaters`** *(2 z 4 kategorii)*: `Hoodies & Zipups`, `Cardigans` *(brak w `Knit Sweaters` oraz `Sweatshirts`, które z definicji są wkładane przez głowę – `Pullover`)*
* **Dział `4. Jackets & Coats`** *(wszystkie 5 kategorii)*: `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`

---

## 2. Tabela mapowania 7 wartości `closure_type`

| # | Wartość docelowa (`closure_type`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Zip`** | `Zip`, `Full-Zip` | Zapięcie na pełny zamek błyskawiczny na całej długości przodu (prosty lub asymetryczny jak w ramoneskach) – `zip closure`, `two-way zip`, `full-zip`, `zip-up`, `front zip`, `exposed zip`, `concealed zip`, `offset zip` |
| 2 | **`Half-Zip`** | `Half-Zip / Quarter-Zip`, `Pullover / Half-Zip` | Częściowy zamek błyskawiczny (lub krótkie zapięcie pod szyją na 1/4–1/2 długości) w bluzach, swetrach i anorakach – `half-zip`, `quarter-zip`, `1/4-zip`, `1/2-zip`, `half zip closure at collar`, `partial zip` |
| 3 | **`Button`** | `Button`, `Button / Snap`, `Single-Breasted (Button / Zip)` | Zapięcie jednorzędowe na guziki, napy/zatrzaski, haftki lub kołki (budrysówki) – `button closure`, `front button placket`, `single-breasted`, `snap-button`, `press-stud closure`, `concealed button placket`, `toggle closure`, `hook-eye closure` |
| 4 | **`Double-Breasted`** | `Double-Breasted` | Konstrukcja dwurzędowa zapinana na dwa rzędy guzików lub nap (klasyczne trencze, płaszcze dyplomatki, bosmanki `peacoat`, dwurzędowe kurtki i kamizelki) – `double-breasted`, `double breasted button closure` |
| 5 | **`Belted`** | `Belted / Wrap / Tie`, `Open Front / Belted`, `Open Front / Belted / Wrap` | Zapięcie kopertowe lub szlafrokowe wiązane paskiem w talii (bez głównego zamka lub rzędu guzików) – `self-tie belt`, `wrap closure`, `belted wrap`, `tie-front`, `robe coat`, `belted cardigan` |
| 6 | **`Open Front`** | `Open Front`, `Belted / Wrap / Open Front (No Buttons)` | Ubranie całkowicie otwarte z przodu, bez zamka, guzików i paska – `open front`, `open-front`, `unfastened`, `no closure`, `draped open front` |
| 7 | **`Pullover`** | `Pullover` | Ubranie wkładane przez głowę bez rozpięcia pod szyją (klasyczne bluzy z kapturem `pullover hoodie`, kurtki kangurki / wiatrówki wkładane przez głowę) – `pullover`, `slip-on`, brak zapięcia z przodu w bluzach `Hoodies` i anorakach |

---

## 3. Reguły rozstrzygania przypadków złożonych (np. zamek + plisa na napy)

1. **`Double-Breasted` ma priorytet nad `Button`:**
   * Jeśli płaszcz, trencz lub kurtka jest dwurzędowa (`double-breasted`), zawsze przypisujemy **`Double-Breasted`** (ponieważ użytkownicy szukający płaszczy bardzo często filtrują wprost `Double-Breasted` vs jednorzędowy `Button`).
2. **Kurtki z zamkiem krytym plisą na guziki/napy (`zip closure with button/press-stud storm flap`):**
   * Jeśli głównym mechanizmem zapinającym kurtkę jest zamek błyskawiczny (`zip closure`), a napy pełnią rolę listwy przeciwwiatrowej (`storm flap` / `placket`), przypisujemy **`Zip`** (lub obie wartości `["Zip", "Button"]`, jeśli indeks dopuszcza listę).
3. **`Pullover` vs `Half-Zip`:**
   * Jeśli bluza z kapturem lub kurtka anorak jest wkładana przez głowę, ale ma zamek pod szyją (`half-zip` / `quarter-zip`), przypisujemy **`Half-Zip`**. Jeśli nie ma żadnego zamka – przypisujemy **`Pullover`**.
