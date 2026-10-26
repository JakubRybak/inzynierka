# Amazon query corpus

The parser uses [category extraction](prompts/category.md), followed by one category-specific feature prompt: [T-shirts](prompts/t-shirts.md), [Dresses](prompts/dresses.md), or [Tank tops & Camisoles](prompts/tank-tops-and-camisoles.md). Every prompt includes few-shot examples. Step 2 runs only after step 1 identifies exactly one supported category.

The corresponding guided-decoding definitions are in [schemas/](schemas/). See [structured_output.md](structured_output.md) for their response contracts, API configuration, and local validation requirements. Examples are manually authored illustrations, not labeled Amazon evaluation cases.

`amazon_clothing_queries.csv` is the cleaned query corpus generated from Amazon Science's ESCI Shopping Queries Dataset. The public source repository is https://github.com/amazon-science/esci-data.

## Processing

The source file `shopping_queries_dataset_examples.parquet` was downloaded to the ignored `archive/data/` directory. The archived script `archive/scripts/export_clothing_queries.py` filtered rows to `product_locale == "us"`, grouped repeated query strings, removed queries containing Chinese, Japanese, or Korean characters, selected queries matching its clothing-related keyword list, assigned its legacy category labels, and sorted by the number of query-product rows. The generated CSV was copied here.

The output has 10,454 unique query strings and four columns:

| Column | Meaning |
| --- | --- |
| `Query_ID` | Query ID from the first matching source row. |
| `Query_Text` | User's query text. |
| `Category` | Legacy keyword-based broad category assignment. |
| `Product_Count` | Number of US-locale source rows grouped under this exact query string. |

## Important for parser work

`Category` is not ground truth for the current parser. It uses the archived taxonomy, includes broad and out-of-scope labels such as `Footwear`, `Accessories`, and `Underwear & Sleepwear`, and may assign multiple categories to one query. The file has 42 distinct category strings, including combinations; 299 rows contain more than one category. Current rules require exactly one supported category, so use `Query_Text` as real query material and treat `Category` only as a legacy heuristic until queries are relabeled against the current taxonomy.

The source script filters for the US locale and removes queries containing CJK characters; it does not otherwise verify that every remaining query is written in English. It also ignores the source ESCI relevance labels.

The original Parquet is 51,286,808 bytes and is stored under `archive/data/`, which is gitignored. The cleaned CSV in this directory is the artifact intended for query parsing work.
