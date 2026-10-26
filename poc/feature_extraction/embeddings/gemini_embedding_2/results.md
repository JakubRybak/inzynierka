# Embedding run results

Completed: 900 image embeddings and 900 description embeddings. Each vector has 3072 dimensions, stored as L2-normalized float32 in Parquet.

| Modality | Products | Input tokens | Estimated USD |
| --- | ---: | ---: | ---: |
| image | 900 | 232200 | 0.1044900 |
| text | 900 | 31959 | 0.0063918 |

Successful requests: **$0.1108818**. Retained conservative reservations for one HTTP 429 and two connections closed without a response: **$0.0069632**. Total including those reservations: **$0.1178450**, below the $0.25 guard. These are token-based estimates, not a billing invoice.

All 1800 successful results were checked for exact pilot ID coverage, dimension, finite values, unit norm and matching source hashes. Successful results were reused after interruption; only the three failed/uncertain requests were explicitly retried. No product feature-extraction calls were made.
