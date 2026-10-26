# LLM extraction pilot: 900 products

Fixed selection of 300 products per category from train only. Products with
`status = excluded` or nonempty `exclusion_reasons` were not eligible.
Join `products.csv` to source data and keyword extraction results by `product_id`.
No features were changed; no LLM or embedding requests were made.
The 20 reference products per category have not been selected yet.

Selection preserves eligible gender proportions and, for Dresses, length
proportions. Quotas use the largest remainder method. Within each stratum,
products are ordered by SHA-256 of `seed|category|product_id`, taking the first
quota entries. Brand and color are not balanced. This is an integration sample,
not a balanced benchmark. Keep these IDs fixed for subsequent experiments.

Seed: `fashiongen-llm-pilot-900-v1`.

Keyword input: `extraction/results/products_train.jsonl`.
Input SHA-256: `61dddc1ff1ba71e84eab14060df7282169ad6660a44094a59782f59135295a77`.

| Category | Gender | Length | Eligible | Selected |
| --- | --- | --- | ---: | ---: |
| T-shirts | Men | — | 4922 | 190 |
| T-shirts | Women | — | 2863 | 110 |
| Dresses | Women | Maxi | 177 | 26 |
| Dresses | Women | Midi | 825 | 122 |
| Dresses | Women | Mini | 1034 | 152 |
| Tank tops & Camisoles | Men | — | 149 | 55 |
| Tank tops & Camisoles | Women | — | 659 | 245 |
