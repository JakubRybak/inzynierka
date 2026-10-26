# Query parsing rules

1. **Language.** Write all prompts, feature and value definitions, schema descriptions, and model-facing examples in English. Use the current taxonomy keys and values.

2. **Exactly one category.** A valid parsed query must contain exactly one supported category. Never return a list of categories. If the request cannot be assigned to one category, or is outside the supported catalog, do not run the search.

3. **Single-choice product features.** A query may contain several accepted values for a feature that has one value per product. Always combine these query values with `OR`: “short- and long-sleeve T-shirts” means `Short Sleeve OR Long Sleeve`.

4. **Multi-choice product features.** Distinguish combinations within one product (`AND`) from alternatives (`OR`). “Black and white T-shirt” requires both colors; “black or white T-shirt” requires at least one. Interpret a conjunction of color names as `AND` by default.

5. **Different features.** Combine requirements on different features with `AND`. A red cotton long-sleeve T-shirt must satisfy the color, material, and sleeve requirements together. Explicitly requested garment brands (e.g. Nike, Zara, Kenzo) are extracted into the `brand` single-choice filter.

6. **Unmentioned features.** Create no filter for a feature the user did not specify. Do not assume default colors, materials, fits, sleeve lengths, or other properties.

7. **Negation.** Support exclusions such as “without polyester,” “not oversized,” and “no red.” A product containing an excluded multi-choice value fails the filter even if it also contains other values.

8. **Presence versus exact set.** A named value normally means membership. “Black T-shirt” accepts both `[Black]` and `[Black, White]`. An explicit “only” requires the exact set: “only black” accepts `[Black]` alone. “Black and white” requires both values; “only black and white” additionally forbids other values. Respect the catalog's existing value limits and exclusivity rules. `Multicolor` does not identify its component colors and cannot satisfy a positive filter for a specific named color.

9. **Composition as a material set.** For now, ignore percentages in queries and create no percentage thresholds. Treat materials with a positive percentage in `main_composition` as a multi-choice set:
   - “Cotton T-shirt”: cotton is present, whether its share is 1% or 100%.
   - “Cotton and polyester”: both are present; additional materials are allowed.
   - “Cotton or polyester”: at least one is present.
   - “Only cotton”: cotton is the only material present.
   - “Without polyester”: polyester is absent.

10. **Residual.** Extract the meaning that could not be mapped to a category or supported hard filters into `residual`. For example, “black dress for a wedding” produces category `Dresses`, color `Black`, and residual `for a wedding`. Do not repeat the successfully mapped category or filters in residual. Return an empty string when no unmatched meaning remains. Preserve unsupported requirements here for ranking and explanation. Do not replace a specific unsupported value with `Other`: a request for a boat neckline must not match every product labeled `Other`. Keep the full original query available to ranking as well.

11. **Deferred decisions.** Dedicated contradiction detection and clarification behavior are postponed.

12. **Query dataset.** Base parser development and evaluation on real shopping queries from the Amazon Shopping Queries Dataset (ESCI). The cleaned query corpus is `poc/query_parsing/amazon_clothing_queries.csv`; its source, processing, columns, and limitations are documented in `poc/query_parsing/README.md`. The source Parquet is kept in the gitignored `archive/data/`. The legacy benchmark CSV, `archive/data/fashion_test_benchmark.csv`, remains empty. The JSON files in `archive/results/` retain 109 benchmark queries with old expected categories, attributes, and residuals. This benchmark mixes Amazon queries with additional cases such as Polish and slang queries; it is not the complete Amazon dataset, and its labels use the old taxonomy. The download and clothing-query selection code is in `archive/scripts/analyze_clothing_queries.py` and `archive/scripts/export_clothing_queries.py`.

These are query interpretation rules. They do not change the feature values assigned to products or the product extraction rules. Parsing uses two sequential model calls: category extraction, followed by one of three category-specific feature prompts. Prompts with few-shot examples are in `poc/query_parsing/prompts/`, response schemas are in `poc/query_parsing/schemas/`, and their API configuration is documented in `poc/query_parsing/structured_output.md`. The model and query API runner have not yet been selected or implemented.
