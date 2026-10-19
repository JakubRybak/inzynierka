# Skirt Style Standardization & Mapping (`skirt_style`)

Standardization of the **`skirt_style`** attribute across **`Skirts`** (`7.1`) in the Fashion-Gen dataset.

---

## 1. Where `skirt_style` Is Included vs. Omitted

### Included In (1 Category)
| Section | Category | Allowed Values |
| :--- | :--- | :--- |
| **7. Skirts** | `7.1 Skirts` | `Pencil`, `A-Line`, `Pleated`, `Wrap`, `Asymmetric` |

### Omitted From (21 Categories)
- **`8.1 Dresses`**: Uses **`dress_style`** (`Bodycon`, `A-Line`, `Shift`, `Slip`, `Shirt Dress`, `Wrap`, `Sweater Dress`).
- **All other categories**: Not applicable.

---

## 2. Canonical Values & Mapping Table (`skirt_style`)

Instead of compound slash labels (`Pencil / Straight`, `Asymmetric / Draped`), **`skirt_style`** uses **5 clean canonical values**:

| Canonical Enum Value | Mapped Keywords / Phrases (`input_name` & `input_description`) | Notes & Detection Rules |
| :--- | :--- | :--- |
| **`Pencil`** | `pencil skirt`, `straight skirt`, `tube skirt`, `column skirt`, `bodycon skirt`, `fitted skirt`, `slim-fit skirt` | Narrow, straight, or form-fitting silhouette that hugs the hips and thighs (often with a back vent or slit for movement). |
| **`A-Line`** | `a-line`, `flared skirt`, `skater skirt`, `circle skirt`, `full skirt`, `bell skirt`, `tiered skirt`, `trapeze`, `denim mini skirt` | Fitted at the waist and gradually widening toward the hem in an "A" or flared silhouette. |
| **`Pleated`** | `pleated`, `knife-pleated`, `accordion-pleated`, `box-pleated`, `sunray pleats`, `plissé` | Defined by structured vertical folds or pleats (accordion, knife, box, or plissé) throughout the body of the skirt. |
| **`Wrap`** | `wrap skirt`, `pareo`, `sarong`, `overlap front`, `tie-waist wrap`, `kilt-style wrap` | Overlapping front panel secured by tying, buttoning, or buckling at the waist/hip. |
| **`Asymmetric`** | `asymmetric`, `asymmetrical`, `draped`, `high-low hem`, `handkerchief hem`, `ruched asymmetric`, `bias-cut draped` | Skirts defined by uneven/diagonal hemlines, handkerchief hems, or sculptural side draping/ruching. |
