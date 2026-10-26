# Pilot extraction complete

900 products: 60 manual references, 6 smoke-test results and 834 new synchronous requests.

Counts: {'ready': 893, 'needs_review': 3, 'pending': 4}.

All 900 IDs match the fixed pilot, each category contains 300 products, all keyword assignments are preserved, and JSONL/Parquet read-back agrees.

New run usage-based estimate: $2.7843707; including retained reservations: $2.9257325. Prior smoke test: $0.0193236. These are estimates, not billing invoices.

The run stopped after 791 products on an authentication error (HTTP 401) during countTokens. It resumed with fresh credentials and skipped all saved products. All 834 new products have a saved result.

## Products requiring review

| ID | Category | Name | Status | Reason |
| --- | --- | --- | --- | --- |
| 2236107 | T-shirts | Pink Rib Basic T-Shirt | needs_review | The record contains unrelated garments mixed together, showing both a pink t-shirt and a yellow hoodie. |
| 1738493 | Dresses | Black Wool Cape Dress | pending | {"sleeve_length": "The garment combines a sleeveless base dress with a detachable long-sleeve overlay."} |
| 1829603 | Dresses | Pink Carabiner Dress | pending | {"sleeve_length": "The dress features a single sleeve on one side and a strap on the other, making standard sleeve length categories inapplicable."} |
| 1164223 | Tank tops & Camisoles | Peach Woven Silk Tank Top | needs_review | HTTP 429 |
| 1492963 | Dresses | White & Red Layered Shirt Dress | needs_review | Strap dependency conflict: flag for review; never overwrite keywords |
| 443203 | T-shirts | Silver Foil T-Shirt | pending | {"colors": "Silver is a metallic color not represented in the standard color families."} |
| 2014513 | Dresses | Black Dash Dress | pending | {"sleeve_length": "The garment has a single sleeve design, which is incompatible with standard single-length categories."} |

No review flags were automatically relabelled. These products stay outside the example bank. One additional ready product has no image 3 and is also excluded from the bank; it remains in the final dataset.
