# Distressing Standardization & Mapping (`distressing`)

Standardization of the **`distressing`** attribute across **`Jeans`** (`5.4`) in the Fashion-Gen dataset.

---

## 1. Where `distressing` Is Included vs. Omitted

### Included In (1 Category)
| Section | Category | Allowed Values |
| :--- | :--- | :--- |
| **5. Pants** | `5.4 Jeans` | `Clean`, `Faded`, `Distressed` |

### Omitted From (21 Categories)
- **All other categories**: While occasional distressed knitwear or denim jackets exist, surface wash/ripping is a primary shopping filter specifically in **`5.4 Jeans`** (`input_subcategory == "JEANS"`, 6,850 unique products in Fashion-Gen).

---

## 2. Canonical Values & Mapping Table (`distressing`)

Instead of compound slash labels (`Clean / Unwashed`, `Faded / Whiskered`, `Ripped / Distressed`), **`distressing`** uses **3 clean canonical values** representing progressive levels of denim treatment:

| Canonical Enum Value | Mapped Keywords / Phrases (`input_name` & `input_description`) | Notes & Detection Rules |
| :--- | :--- | :--- |
| **`Clean`** | `raw denim`, `unwashed`, `selvedge`, `dark rinse`, `solid`, `uniform wash`, *(absence of fading, whiskering, or distressing keywords)* | Uniform, solid-colored, or raw/unwashed denim without visible fading, whiskering, abrasions, or rips (~3,491 jeans in Fashion-Gen). |
| **`Faded`** | `fading`, `faded`, `whiskering`, `whiskered`, `stonewashed`, `acid wash`, `bleached`, `vintage wash`, `worn-in`, `honeycombs` *(without rips/holes)* | Denim with tonal wash treatments (fading at thighs/knees, crease whiskering at hips, stonewash, or bleach wash) but **no** open rips, tears, or heavy abrasion (~1,796 jeans in Fashion-Gen). |
| **`Distressed`** | `distressing`, `distressed`, `ripped`, `rips`, `torn`, `slashed`, `destroyed`, `frayed`, `fraying`, `abrasions`, `knee slits`, `holes`, `paint splatter`, `patched` | Denim featuring physical surface damage such as rips, knee slashes, frayed edges, abrasions, or repair patches (~1,563 jeans in Fashion-Gen; takes precedence over `Faded` when both fading and distressing are present). |
