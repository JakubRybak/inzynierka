# Mapowanie wykończenia dołu nogawki (`cuff_style`)

Dokument definiuje ujednoliconą listę **3 kanonicznych typów wykończenia nogawki** używanych w cesze `cuff_style` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `cuff_style`

Cecha `cuff_style` występuje w **2 kategoriach** działu `5. Pants`, w których sposób zakończenia nogawki (luźna nogawka vs ściągacz typu jogger vs zamek przy kostce) jest kluczowym elementem fasonu:
* `Cargo Pants`
* `Sweatpants & Lounge Pants`

---

## 2. Tabela mapowania 3 wartości `cuff_style`

| # | Wartość docelowa (`cuff_style`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Straight Hem`** | `Open / Straight Hem` | Klasyczna, otwarta nogawka bez ściągacza ani gumki na dole (`straight hem`, `open cuffs`, `raw edge at cuffs`, `vented cuffs`, `flared hem`, brak wzmianki o ściągaczu na dole nogawki) |
| 2 | **`Elasticized Cuff`** | `Elasticized / Ribbed / Bungee Cuff`, `Elasticized / Ribbed Cuff (Jogger)` | Nogawka zwężana na dole prążkowanym ściągaczem, gumką, stoperem (`bungee`) lub paskiem na rzep/guzik (styl jogger) – `rib-knit cuffs`, `ribbed cuffs`, `elasticized cuffs`, `elastic cuffs`, `bungee-style drawstring at cuffs`, `gathered cuffs`, `cinched cuffs`, `button-tab at cuffs` |
| 3 | **`Zippered Cuff`** | `Zippered Cuff` | Nogawka wyposażona w pionowy zamek błyskawiczny przy kostce (`zippered cuffs`, `zip vent at cuffs`, `ankle zips`, `zipper at hem`) |
