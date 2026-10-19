# Belt Standardization & Mapping (`belt`)

Standardization of the **`belt`** attribute across **`Trench Coats`** (`4.2`) in the Fashion-Gen dataset.

---

## 1. Where `belt` Is Included vs. Omitted

### Included In (1 Category)
| Section | Category | Allowed Values |
| :--- | :--- | :--- |
| **4. Jackets & Coats** | `4.2 Trench Coats` | `Belted`, `Unbelted` |

### Omitted From (21 Categories)
- **`4.1 Classic Coats`**: Belted wrap coats (`robe coat`) are captured via `closure_type: Belted`, whereas Trench Coats frequently combine `closure_type: Double-Breasted` or `Button` with a separate waist belt (`belt: Belted` vs. `Unbelted`).
- **All other categories**: Not a primary structural discriminator.

---

## 2. Canonical Values & Mapping Table (`belt`)

| Canonical Enum Value | Mapped Keywords / Phrases (`input_name` & `input_description`) | Notes & Detection Rules |
| :--- | :--- | :--- |
| **`Belted`** | `belted`, `self-tie belt`, `detachable belt`, `pin-buckle belt at waist`, `belt loops at waist`, `cinched waist`, `storm flap` (with waist belt) | Trench coat featuring a waist belt (buckle belt, D-ring belt, or self-tie sash belt). |
| **`Unbelted`** | `unbelted`, `loose trench`, `A-line trench`, `mac coat`, `mackintosh`, *(absence of belt keywords in description)* | Clean-lined trench or mac raincoat without a waist belt. |
