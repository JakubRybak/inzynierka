# Guided decoding and structured outputs

Guided decoding constrains generation to an allowed response structure and value vocabulary. In the Gemini API, this parser uses structured outputs: the application supplies `responseMimeType: application/json` and a `responseSchema` separately from the prompt. A prompt asking for JSON alone does not enable this constraint.

## Prompt and schema pairs

| Step | System prompt | API response schema |
| --- | --- | --- |
| 1: category | [category.md](prompts/category.md) | [category.json](schemas/category.json) |
| 2: T-shirts | [t-shirts.md](prompts/t-shirts.md) | [t-shirts.json](schemas/t-shirts.json) |
| 2: Tank tops & Camisoles | [tank-tops-and-camisoles.md](prompts/tank-tops-and-camisoles.md) | [tank-tops-and-camisoles.json](schemas/tank-tops-and-camisoles.json) |
| 2: Dresses | [dresses.md](prompts/dresses.md) | [dresses.json](schemas/dresses.json) |

The fenced system-prompt blocks include the few-shot examples. Send the original query in a separate user message. For step 2, also supply the selected category using the user-message template at the top of its prompt file. Only the chosen category's prompt and schema are used in the second call.

## Step 1 definition

The response has one required field, `category`. It is one of `T-shirts`, `Tank tops & Camisoles`, or `Dresses`, or JSON null. An array of categories, an unsupported category name, a confidence score, or an explanation is invalid. When category is null, do not call step 2 and do not search the catalog.

## Step 2 definition

The response has two required fields, `filters` and `residual`. `filters` may be empty; `residual` may be an empty string. Each filter has exactly `feature`, `operator`, and `values`.

Each category schema uses `anyOf` to pair every supported feature with its own operators and value vocabulary. This prevents mixing a valid feature with another feature's labels, such as `neckline: Mini`. Supported features include `brand` (single choice with operators `in` and `not_in` accepting open string brand names) across all categories. Every value list has at least one entry. Only the schema for Dresses includes `dress_type` and `dress_silhouette`; Tank tops & Camisoles has no `sleeve_length`. Collared and Standard Sleeved appear only where supported.

| Product feature type | Operators |
| --- | --- |
| Single choice | `in`, `not_in` |
| Multi choice or material set | `contains_any`, `contains_all`, `equals_set`, `contains_none` |

The query schema does not apply the product's two-color limit to the list of query alternatives. For example, three alternatives are valid with `contains_any`. Likewise, `Other` may be one of several alternatives in a query, even though it occurs alone in a product's `dress_type` list. Product cardinality and exclusivity rules must not be copied onto query alternatives.

## API configuration

The JSON files use the Google Cloud `responseSchema` format, including uppercase type names and `nullable`. They are not raw prompt fragments or generic Draft 2020-12 JSON Schemas.

The following Python code only prepares request settings; it performs no API calls:

```python
import json
from pathlib import Path

parser_dir = Path("poc/query_parsing")  # Relative to the repository root.
category_config = {
    "responseMimeType": "application/json",
    "responseSchema": json.loads(
        (parser_dir / "schemas/category.json").read_text()
    ),
}

feature_schema_paths = {
    "T-shirts": "t-shirts.json",
    "Tank tops & Camisoles": "tank-tops-and-camisoles.json",
    "Dresses": "dresses.json",
}

# After step 1, reject extra fields and validate the category value locally.
# selected_category is the validated category value from that response.
if selected_category is not None:
    feature_config = {
        "responseMimeType": "application/json",
        "responseSchema": json.loads(
            (parser_dir / "schemas" / feature_schema_paths[selected_category]).read_text()
        ),
    }
    # Use feature_config and the corresponding category-specific system prompt
    # in the second generateContent request.
```

## Local validation requirements

Before using a result, the application must check:

- The response is complete JSON, the expected root keys are present, and no extra keys occur at any level.
- Category is a supported scalar or null, and step 2 uses exactly the category chosen in step 1.
- Every filter has a category-supported feature, a compatible operator, and values from that feature's enum.
- Value lists are nonempty, contain strings, and have no duplicates.
- `residual` is a string and the full original query remains available to ranking.
- Refusals, truncated outputs, HTTP errors, or validation failures are retained as errors rather than converted to valid empty-filter searches.

The schema does not establish semantic correctness: the model may still misread OR as AND, miss a requirement, or put the wrong meaning in residual. Dedicated contradiction detection remains deferred. The schemas omit unsupported constraints such as `uniqueItems` and `additionalProperties`; uniqueness and extra-key rejection must be checked locally.

The prompts and schema definitions are prepared here. A query API runner and local response validator have not yet been implemented or tested against live requests.

Source: [Google Cloud structured output documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output).
