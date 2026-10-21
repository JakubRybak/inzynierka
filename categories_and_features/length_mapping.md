# Mapowanie długości ubrań (`length`)

Dokument definiuje ujednolicone słowniki wartości używanych w cesze `length` w 4 naturalnych grupach odzieży oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description`, `input_subcategory` oraz analiza obrazu).

---

## 1. Cztery standardy cechy `length` (bez ukośników `/`)

Ponieważ długość góry odzieży, płaszczy/szortów, spodni oraz spódnic/sukienek opisuje się w modzie odmiennymi terminami, cecha `length` stosuje **4 czyste standardy**:

| Grupa kategorii | Kategorie wchodzące w skład grupy | Wartości `length` (bez `/`) |
| :--- | :--- | :--- |
| **1. Góra odzieży i kurtki** *(11 kategorii)* | `T-shirts`, `Tank tops & Camisoles`, `Shirts`, `Blouses`, `Knit Sweaters`, `Sweatshirts`, `Hoodies & Zipups`, `Cardigans`, `Jackets`, `Bombers`, `Vests` | `Cropped`, `Regular`, `Longline` |
| **2. Płaszcze i szorty** *(3 kategorie)* | `Classic Coats`, `Trench Coats`, `Shorts` | `Short`, `Mid-Length`, `Long` |
| **3. Spodnie (`5. Pants`)** *(4 kategorie)* | `Trousers`, `Cargo Pants`, `Sweatpants & Lounge Pants`, `Jeans` | `Cropped`, `Full-Length` |
| **4. Spódnice i sukienki** *(2 kategorie)* | `Skirts`, `Dresses` | `Mini`, `Midi`, `Maxi` |

---

## 2. Tabele mapowania dla poszczególnych grup

### Grupa 1: Góra odzieży i kurtki (`Cropped`, `Regular`, `Longline`)

| # | Wartość docelowa (`length`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Cropped`** | `Cropped` | Ubrania krótkie, odsłaniające brzuch lub kończące się na wysokości talii (`cropped`, `crop`, `short-length`, `bolero`, `shrug`, `midriff-baring`, `waist-cropped`) |
| 2 | **`Regular`** | `Regular`, `Regular / Hip-Length`, `Regular / Waist-Length` | Standardowa długość sięgająca do pasa lub bioder (`regular`, `hip-length`, `waist-length`, standardowa długość koszulki/bluzy/kurtki) |
| 3 | **`Longline`** | `Longline`, `Longline / Tunic`, `Longline / Duster`, `Longline / Sleeveless Coat` | Ubrania przedłużane poniżej bioder, tuniki, długie kardigany i kamizelki (`longline`, `long-length`, `elongated`, `extended hem`, `tunic`, `duster`, `long cardigan`, `sleeveless coat`, `thigh-length top/jacket`) |

---

### Grupa 2: Płaszcze i szorty (`Short`, `Mid-Length`, `Long`)

| # | Wartość docelowa (`length`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Short`** | `Short / Thigh-Length` *(płaszcze)*, `Short / Mini (Upper Thigh)` *(szorty)* | **W płaszczach:** krótkie płaszcze i budrysówki do bioder lub połowy uda (`short coat`, `pea coat`, `peacoat`, `car coat`, `thigh-length`).<br>**W szortach:** bardzo krótkie szorty kończące się wysoko na udzie (`short`, `mini shorts`, `hot pants`, `dolphin shorts`, `running shorts`). |
| 2 | **`Mid-Length`** | `Mid-Length / Knee-Length` *(płaszcze)*, `Mid-Thigh / Regular` *(szorty)* | **W płaszczach:** klasyczna długość w okolice kolan (`mid-length`, `knee-length`, `three-quarter length coat`).<br>**W szortach:** standardowe szorty do połowy uda (`mid-thigh`, `regular length shorts`, `classic chino shorts`). |
| 3 | **`Long`** | `Long / Maxi` *(płaszcze)*, `Knee-Length / Bermuda / Long` *(szorty)* | **W płaszczach:** długie płaszcze sięgające do łydki lub kostek (`long coat`, `maxi coat`, `full-length coat`, `ankle-length`, `duster coat`, `floor-length`).<br>**W szortach:** długie szorty sięgające do kolan lub tuż za kolano (`bermuda`, `knee-length shorts`, `long shorts`, `basketball shorts`, `boardshorts`). |

---

### Grupa 3: Spodnie – Dział `5. Pants` (`Cropped`, `Full-Length`)

| # | Wartość docelowa (`length`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Cropped`** | `Cropped / Ankle / Culotte`, `Cropped / Ankle`, `Cropped / Capri / 3/4` | Spodnie o skróconej nogawce – przed kostkę, 7/8, rybaczki, capri lub culotte (`cropped`, `ankle-length`, `ankle-cropped`, `capri`, `3/4 length`, `seven-eighth`, `7/8`, `culotte`, `calf-length`, `pedal pusher`) |
| 2 | **`Full-Length`** | `Regular / Full-Length` | Pełna, standardowa długość nogawki sięgająca do kostki/buta (`full-length`, `regular length`, `long-length`, `floor-length`, `stacked hem`, wartość domyślna dla spodni) |

---

### Grupa 4: Spódnice i sukienki (`Mini`, `Midi`, `Maxi`)

| # | Wartość docelowa (`length`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description` / `input_subcategory`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Mini`** | `Mini / Short` | Długość przed kolano (`mini`, `miniskirt`, `minidress`, `short`, `micro-mini`, `above-knee`, `thigh-length`, subkategorie `SHORT SKIRTS` oraz `SHORT DRESSES`) |
| 2 | **`Midi`** | `Midi / Knee-Length` | Długość w kolano lub do połowy łydki (`midi`, `mid-length`, `knee-length`, `below-knee`, `calf-length`, `tea-length`, subkategorie `MID LENGTH SKIRTS` oraz `MID LENGTH DRESSES`) |
| 3 | **`Maxi`** | `Maxi / Long` | Długość do kostek lub do ziemi (`maxi`, `long`, `full-length`, `ankle-length`, `floor-length`, `gown`, `evening gown`, subkategorie `LONG SKIRTS`, `LONG DRESSES` oraz `GOWNS`) |
