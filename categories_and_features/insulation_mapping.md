# Mapowanie stopnia ocieplenia (`insulation`)

Dokument definiuje ujednoliconą listę **4 kanonicznych stopni ocieplenia** używanych w cesze `insulation` we wszystkich 5 kategoriach działu `4. Jackets & Coats` (`Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`) oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description`, `input_composition` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `insulation`

Cecha `insulation` jest w 100% wspólna dla wszystkich **5 kategorii działu `4. Jackets & Coats`**:
* `Classic Coats`, `Trench Coats`, `Jackets`, `Bombers`, `Vests`

---

## 2. Tabela mapowania 4 wartości `insulation`

| # | Wartość docelowa (`insulation`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description` / `input_composition`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Lightweight`** | `Unlined / Lightweight / Rain Shell`, `Unlined / Lightweight`, `Lightweight / Unpadded` | Cienkie kurtki, płaszcze i kamizelki bez ocieplenia – wiatrówki, kurtki przeciwdeszczowe, cienkie płaszcze bez podszewki, modele letnie (`unlined`, `lightweight`, `unpadded`, `rain shell`, `windbreaker`, `packable`, `water-repellent shell`, `semi-sheer`, brak podszewki i wypełnienia) |
| 2 | **`Midweight`** | `Standard / Midweight (Wool/Tailored)`, `Standard / Midweight`, `Standard / Tailored (Unpadded)` | Klasyczne okrycia przejściowe (wiosenno-jesienne) ze standardową podszewką materiałową (np. wiskozową, satynową lub bawełnianą), ale bez grubego wypełnienia puchowego czy kożucha – klasyczne wełniane płaszcze, trencze z podszewką, kurtki jeansowe (`denim jacket`), skórzane ramoneski (`leather biker jacket`), klasyczne bomberki `MA-1` bez grubego puchu |
| 3 | **`Padded`** | `Padded / Quilted / Down`, `Heavy / Padded / Down`, `Padded / Quilted / Down (Warm)` | Ciepłe okrycia zimowe i przejściowe z wypełnieniem puchowym (`down` / `feathers`) lub syntetycznym (`polyester fill` / `padding`), w tym kurtki puchowe i pikowane (`padded`, `quilted`, `down-filled`, `down jacket`, `puffer`, `insulated`, `polyfill`, `primaloft`, `fill:` w `input_composition`) |
| 4 | **`Shearling`** | `Fur / Shearling Lined`, `Fur / Shearling / Fleece Lined`, `Fur / Shearling / Fleece` | Okrycia ocieplane kożuchem, futrem (naturalnym lub sztucznym) albo grubym polarem typu sherpa/borg (`shearling`, `shearling-lined`, `fur-lined`, `faux-fur lining`, `fleece-lined`, `sherpa-lined`, `borg collar/lining`, `pile lining`, `lambskin shearling`) |
