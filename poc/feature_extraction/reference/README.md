# Reference products

`products.jsonl` is the authoritative annotation file: one product per line,
20 per category, all included in `../samples/pilot_900/products.csv`.
These 60 products leave 840 for subsequent extraction.

- `features`: complete feature values, preserving every assigned preprocessing value.
- `feature_metadata`: original provenance retained; added values use
  `source: manual`, with the reviewed image IDs and text columns.
- `status: ready`: all required features have values; this is not a human approval.
- `review_status: assistant_reviewed`, `reviewer: Codex`, `user_verified: false`:
  labels were assigned by the assistant after viewing images and descriptions,
  not independently verified by the user.
- `review_notes`: ambiguous judgments and known limitations of preserved values.
- `images`: all image IDs and repository-relative source paths; originals are not copied.
- `main_image_id`: first source image, used for the future image embedding.
- `example_image_ids`: source images 1 and 3 (`id_gridfs_1`, `id_gridfs_3`).
  This fixed selection applies to every reference. Pose IDs do not guarantee
  semantic front/back views.

Selection was deliberate, not random: T-shirts include 10 Men and 10 Women;
Tank tops & Camisoles include 6 Men and 14 Women; Dresses include 6 Maxi,
7 Midi and 7 Mini. Construction, pattern and silhouette variety were considered.
This small bank does not cover every possible feature value.

The review preserves keyword assignments even when an image suggests a different
interpretation. It is a pipeline reference proposal, not an independent gold
standard for evaluating keyword accuracy. Subjective fit/length judgments remain
approximate. No paid LLM or embedding API was called.

`review.md` shows every source image, description, composition and final feature
with provenance. Regenerate it after editing annotations:

```sh
.venv/bin/python poc/scripts/render_reference_review.py
```

`review_images/` contains contact sheets used for the visual review.
