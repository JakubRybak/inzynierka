# Pilot 9922 product selection

The [selection CSV](../../data/processed/fashiongen/pilot_9922/selection.csv) lists one row per product. The selection keeps fewer than 10,000 products and follows these rules:

- Only the train split is used. Products that keyword extraction marks as `excluded`
  are not eligible, so the selection matches the searchable catalog.
- Bodysuits, Cargo Pants, Dresses, Polos, Trench Coats and Vests are complete. Dresses
  is the complete large category, so ranking can be evaluated on a full candidate set.
- T-shirts have 1,000 products, Blouses and Cardigans 300, Tank tops & Camisoles 309
  and every other category 400.
- Within a category, the products are stratified by gender and price tercile with
  proportional allocation. Products are drawn in the order of the SHA-256 hash of
  `pilot-2026-11|<product_id>`, so the selection is deterministic.
- All 900 products from the original pilot are included. They follow the catalog distribution
  of gender, price and season, so they do not bias the selection. In Tank tops & Camisoles,
  9 products were added to the original 300 to restore the proportions.
- 228 reference products are part of the selection. The pipeline reuses their manual
  labels, so they cost nothing and must be left out when measuring extraction accuracy.

| Section | Category | Eligible | Selected | Share |
| --- | --- | ---: | ---: | ---: |
| Tops | T-shirts | 7,797 | 1,000 | 13% |
| Tops | Polos | 496 | 496 | 100% |
| Tops | Tank tops & Camisoles | 825 | 309 | 37% |
| Tops | Bodysuits | 103 | 103 | 100% |
| Shirts & Blouses | Shirts | 3,724 | 400 | 11% |
| Shirts & Blouses | Blouses | 824 | 300 | 36% |
| Sweaters | Knit Sweaters | 4,186 | 400 | 10% |
| Sweaters | Sweatshirts | 2,845 | 400 | 14% |
| Sweaters | Hoodies & Zipups | 2,317 | 400 | 17% |
| Sweaters | Cardigans | 766 | 300 | 39% |
| Jackets & Coats | Classic Coats | 1,646 | 400 | 24% |
| Jackets & Coats | Trench Coats | 140 | 140 | 100% |
| Jackets & Coats | Jackets | 2,876 | 400 | 14% |
| Jackets & Coats | Bombers | 1,138 | 400 | 35% |
| Jackets & Coats | Vests | 233 | 233 | 100% |
| Pants | Trousers | 3,198 | 400 | 13% |
| Pants | Cargo Pants | 156 | 156 | 100% |
| Pants | Sweatpants & Lounge Pants | 1,757 | 400 | 23% |
| Pants | Jeans | 3,176 | 400 | 13% |
| Shorts | Shorts | 1,704 | 400 | 23% |
| Skirts | Skirts | 1,549 | 400 | 26% |
| Dresses | Dresses | 2,085 | 2,085 | 100% |
| | **Total** | **43,541** | **9,922** | **23%** |

Eligible counts are train products that are not excluded.

### Running

Set `selection: data/processed/fashiongen/pilot_9922/selection.csv` and list all 22
categories in `categories`. Keep `splits: [train, validation]`: the selection contains
only train products, but six Sweaters references come from the validation split and
the reference bank loads every reference of the selected categories.

### Limitations

The share of each category differs, from 10% of Knit Sweaters to complete categories. Results
that combine several categories, such as a query for a whole section, over-represent the
complete categories: Trench Coats and Vests are complete, Jackets are not. Evaluate such
results per category or weight products by the inverse of their category share.
