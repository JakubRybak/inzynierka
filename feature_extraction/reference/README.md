# Reference products

`products.jsonl` contains the 60 original manually annotated products, 20 per category.
The extraction job starts its example bank from these records. They remain manual
references and are not sent for feature completion.

`review.md` and `review_images/` are historical material for reviewing these labels.
The original rendering script is preserved in
`archive/extraction_clean_previous/poc/scripts/render_reference_review.py`.

References must be ready, complete, have no product-level problem, and include
image poses `id_gridfs_1` and `id_gridfs_3`. Image and text embeddings must exist
for every reference. New ready LLM results can extend the bank during a run.
