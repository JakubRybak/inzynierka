# Jacket Style Standardization & Mapping (`jacket_style`)

Standardization of the **`jacket_style`** attribute across **`Jackets`** (`4.3`) in the Fashion-Gen dataset.

---

## 1. Where `jacket_style` Is Included vs. Omitted

### Included In (1 Category)
| Section | Category | Allowed Values |
| :--- | :--- | :--- |
| **4. Jackets & Coats** | `4.3 Jackets` | `Biker`, `Trucker`, `Puffer`, `Windbreaker`, `Utility`, `Casual` |

### Omitted From (21 Categories)
- **`4.1 Classic Coats`** & **`4.2 Trench Coats`**: Tailored overcoats and raincoats defined by `collar_type`, `closure_type`, `belt`, and `insulation`.
- **`4.4 Bombers`**: Uses the dedicated **`bomber_style`** attribute (`Flight`, `Varsity`, `Quilted`, `Blouson`).
- **`4.5 Vests`**: Sleeveless outerwear defined by `hood`, `closure_type`, and `insulation`.
- **All Tops, Sweaters, Pants, Shorts, Skirts, Dresses**: Not applicable.

---

## 2. Canonical Values & Mapping Table (`jacket_style`)

Instead of compound slash labels (`Biker / Moto`, `Denim / Trucker`, `Puffer / Down`, `Windbreaker / Track`, `Field / Utility`), **`jacket_style`** uses **6 clean, single-concept values**:

| Canonical Enum Value | Mapped Keywords / Phrases (`input_name` & `input_description`) | Notes & Detection Rules |
| :--- | :--- | :--- |
| **`Biker`** | `biker`, `moto`, `motorcycle`, `perfecto`, `leather biker`, `asymmetric zip jacket`, `epaulettes` (with asymmetric zip) | Asymmetric zip closure or snap-tab band-collar motorcycle silhouette, typically in leather, suede, or coated denim. |
| **`Trucker`** | `trucker`, `denim jacket`, `jean jacket`, `type iii`, `western denim jacket`, `sherpa trucker` | Structured button-front casual jacket with dual chest flap pockets and vertical seam paneling (most commonly denim, corduroy, or suede). |
| **`Puffer`** | `puffer`, `down jacket`, `quilted down`, `padded jacket`, `baffle`, `puffer coat`, `feather-filled` | Quilted or baffled insulated jacket filled with down, feathers, or heavy synthetic padding. |
| **`Windbreaker`** | `windbreaker`, `track jacket`, `anorak`, `rain jacket`, `shell jacket`, `coach jacket`, `windrunner`, `packable jacket`, `technical shell` | Lightweight athletic, sporty, or weather-resistant nylon/polyester shell, track jacket, coach jacket, or pullover anorak. |
| **`Utility`** | `field jacket`, `utility jacket`, `military jacket`, `safari jacket`, `cargo jacket`, `m-65`, `bdu`, `chore jacket`, `workwear jacket`, `parka` (short/lightweight) | Multi-pocket utilitarian, military, safari, or French chore/workwear silhouette (typically 3–4 patch/flap front pockets). |
| **`Casual`** | `harrington`, `shirt jacket`, `overshirt`, `shacket`, `coach` (non-tech), `blouson`, `zip-up jacket`, `cropped jacket`, `tailored casual jacket` | Clean everyday zip or button jackets that do not fall into biker, trucker, puffer, athletic shell, or multi-pocket military/utility archetypes. |
