# Mapowanie kroju i dopasowania (`fit`)

Dokument definiuje ujednolicone słowniki wartości używanych w cesze `fit` we wszystkich kategoriach posiadających wariancję dopasowania oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description`, `input_subcategory` oraz analiza obrazu).

---

## 1. Dwa standardy cechy `fit` w systemie

Aby zachować maksymalną prostotę dla odzieży górnej/wierzchniej oraz pełną precyzję dla spodni, cecha `fit` wykorzystuje dokładnie **dwa czyste standardy (bez ukośników `/`)**:

1. **Standard ogólny – 3 wartości (`Slim`, `Regular`, `Relaxed`):**
   * Obowiązuje w **15 kategoriach**:
     * `1. Tops`: `T-shirts`, `Polos`, `Tank tops & Camisoles` *(brak w `Bodysuits`, które z definicji są ściśle dopasowane)*
     * `2. Shirts & Blouses`: `Shirts`, `Blouses`
     * `3. Sweaters`: `Knit Sweaters`, `Sweatshirts`, `Hoodies & Zipups`, `Cardigans`
     * `4. Jackets & Coats`: `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`
     * `6. Shorts`: `Shorts`
2. **Standard dla spodni – 4 wartości (`Skinny`, `Slim`, `Regular`, `Relaxed`):**
   * Obowiązuje we wszystkich **4 kategoriach działu `5. Pants`**:
     * `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans`

---

## 2. Tabela mapowania – Standard ogólny (`fit` w 15 kategoriach)

| # | Wartość docelowa (`fit`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Slim`** | `Slim / Fitted`, `Slim / Tailored`, `Slim / Fitted / Bodycon / Sheath` | Krój dopasowany do ciała, obcisły lub mocno taliowany (`slim`, `slim-fit`, `slim-fitting`, `fitted`, `form-fitting`, `figure-hugging`, `tailored fit`, `skinny fit`, `bodycon`, `sheath`, `contours`) |
| 2 | **`Regular`** | `Regular`, `Regular / Straight`, `Shift / Straight / Regular` | Klasyczny, standardowy, prosty krój – ani obcisły, ani oversize (`regular`, `regular-fit`, `classic fit`, `standard fit`, `straight-cut`, `tailored regular`, wartość domyślna gdy krój jest standardowy) |
| 3 | **`Relaxed`** | `Oversized / Relaxed`, `Oversized / Relaxed / Cocoon`, `Relaxed / Loose / Wide` | Krój luźny, swobodny, szeroki, pudełkowy lub oversize (`relaxed`, `relaxed-fit`, `oversized`, `oversize`, `loose`, `loose-fit`, `boxy`, `cocoon`, `slouchy`, `boyfriend`, `dropped-shoulder`, `wide-cut`, `dolman`) |

---

## 3. Dopasowanie spodni (`fit`, single choice)

Obowiązuje w `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans`. Opisuje dopasowanie w biodrach i udach; kształt nogawki opisuje osobne `leg_shape`.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Skinny` | Bardzo obcisłe dopasowanie (`skinny`, `super skinny`, `spray-on`, `second-skin`). |
| `Slim` | Dopasowane, ale bez bardzo obcisłego efektu skinny (`slim`, `slim-fit`, `fitted`). |
| `Regular` | Standardowe dopasowanie, pomiędzy dopasowanym a luźnym (`regular-fit`, `classic fit`). |
| `Relaxed` | Luźne dopasowanie w biodrach i udach (`relaxed-fit`, `loose`, `baggy`, `boyfriend`). |

`Straight`, `Tapered`, `Wide-Leg` i `Flared` nie są wartościami `fit`; należą do `leg_shape`. Sam prosty krój nogawki nie wymusza `Regular`. Przykładowo `relaxed-fit tapered trousers` oznacza `fit = Relaxed` oraz `leg_shape = Tapered`.

W `Dresses` zamiast `fit` i `dress_style` stosujemy `dress_silhouette` oraz `dress_type`; patrz [dresses_mapping.md](dresses_mapping.md).
