# Concept scoring: user message

System instruction: [score_system.txt](score_system.txt). The user message is the block below, followed by two
product images (source poses `id_gridfs_1` and `id_gridfs_3`). `score_products.py` fills in the placeholders:
`{product}` is JSON with category, name, brand, description, composition and extracted features; `{concepts}` is
one line `- id: name (type)` per concept to rate. The response schema has one integer 0–10 per concept id.

```text
PRODUCT
{product}

CONCEPTS
{concepts}

Rate the product for every concept above.
```
