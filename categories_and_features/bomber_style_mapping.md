# Bomber Style Standardization & Mapping (`bomber_style`)

Standardization of the **`bomber_style`** attribute across **`Bombers`** (`4.4`) in the Fashion-Gen dataset.

---

## 1. Where `bomber_style` Is Included vs. Omitted

### Included In (1 Category)
| Section | Category | Allowed Values |
| :--- | :--- | :--- |
| **4. Jackets & Coats** | `4.4 Bombers` | `Flight`, `Varsity`, `Quilted`, `Blouson` |

### Omitted From (21 Categories)
- **`4.3 Jackets`**: Uses the broader **`jacket_style`** attribute (`Biker`, `Trucker`, `Puffer`, `Windbreaker`, `Utility`, `Casual`).
- **All other categories**: Not applicable.

---

## 2. Canonical Values & Mapping Table (`bomber_style`)

Instead of slash-separated labels (`Classic / MA-1 Flight`, `Varsity / Letterman`, `Quilted`, `Minimalist / Blouson`), **`bomber_style`** uses **4 clean canonical values**:

| Canonical Enum Value | Mapped Keywords / Phrases (`input_name` & `input_description`) | Notes & Detection Rules |
| :--- | :--- | :--- |
| **`Flight`** | `ma-1`, `flight jacket`, `aviator bomber`, `pilot bomber`, `utility pocket at sleeve`, `zip pocket at upper sleeve`, `nylon bomber`, `satin bomber`, `souvenir jacket`, `sukajan` | Classic military/aviator MA-1 bomber silhouette featuring ribbed stand collar, cuffs, and hem, often with a zippered utility/pen pocket on the sleeve or satin/nylon shell. |
| **`Varsity`** | `varsity`, `letterman`, `baseball jacket`, `contrast sleeves`, `contrast leather sleeves`, `chenille patch`, `striped rib knit collar` | Collegiate/athletic baseball or letterman silhouette, typically featuring contrasting sleeves, striped rib-knit trim, or snap-button front. |
| **`Quilted`** | `quilted bomber`, `diamond-quilted`, `padded bomber`, `channel-quilted`, `puffer bomber`, `matelassé bomber` | Bomber jacket with visible stitched quilting (diamond, channel, onion, or baffle stitching) across the body and sleeves. |
| **`Blouson`** | `blouson`, `minimalist bomber`, `suede bomber`, `leather bomber`, `wool bomber`, `clean bomber`, `harrington bomber` | Clean, tailored, or minimalist blouson without sleeve utility pockets, varsity contrast trims, or visible quilting (often crafted from suede, wool, leather, or structured crepe). |
