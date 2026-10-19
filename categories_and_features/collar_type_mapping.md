# Mapowanie typu kołnierza (`collar_type`)

Dokument definiuje ujednoliconą listę **6 kanonicznych typów kołnierza** używanych w cesze `collar_type` (w kategoriach `Shirts` oraz `Classic Coats`) oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `collar_type`

Cecha `collar_type` występuje w kategoriach, w których szczegółowa konstrukcja kołnierza stanowi kluczowy element fasonu:
* **`Shirts`** (w dziale `2. Shirts & Blouses`)
* **`Classic Coats`** (w dziale `4. Jackets & Coats`)

*(W pozostałych kategoriach odzieży górnej oraz w sukienkach wykończenie pod szyją opisuje ujednolicona cecha `neckline`, gdzie wszystkie wykładane kołnierzyki mapowane są do wartości `Collared`).*

---

## 2. Tabela mapowania 6 wartości `collar_type`

| # | Wartość docelowa (`collar_type`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Point Collar`** | `Classic / Point / Spread Collar` | Klasyczny wykładany kołnierzyk koszulowy lub płaszczowy (zwykły, szeroki włoski `spread` lub zapinany na guziczki `button-down`) – `point collar`, `spread collar`, `button-down collar`, `classic collar`, `cutaway collar`, `wingtip collar`, `shirt collar`, `club collar`, `peter pan collar`, `polo collar` |
| 2 | **`Camp Collar`** | `Camp / Cuban Collar` | Płasko rozkładany, otwarty kołnierzyk kubański / hawajski bez stójki – `camp collar`, `cuban collar`, `revere collar`, `convertible collar`, `bowling shirt collar`, `open collar` |
| 3 | **`Lapel Collar`** | `Lapel / Classic Collar` | Klasyczne klapy marynarkowe i płaszczowe (otwarte `notched` lub ostre `peak`) – `notched lapel`, `peak lapel`, `lapel collar`, `tailored lapels`, `wide lapels`, `ulster collar` |
| 4 | **`Stand Collar`** | `Band / Stand / Collarless`, `Stand / Funnel Neck` | Stójka, kołnierz mandaryński lub wysoki kołnierz kominowy bez wykładanych rożków – `stand collar`, `band collar`, `mandarin collar`, `mao collar`, `grandad collar`, `nehru collar`, `funnel neck`, `mock collar`, `high stand collar` |
| 5 | **`Shawl Collar`** | `Shawl / Wrap Collar` | Zaokrąglony, płynnie przechodzący w zapięcie kołnierz szalowy lub kopertowy – `shawl collar`, `shawl lapel`, `wrap collar`, `draped collar` |
| 6 | **`Collarless`** | `Collarless / Round Neck`, `Hooded (No Lapel)` | Całkowity brak kołnierza i stójki (gładkie wycięcie pod szyją lub kaptur wszyty bezpośrednio w dekolt bez klap) – `collarless`, `no collar`, `round neck coat`, `crewneck shirt`, `hooded without collar` |
