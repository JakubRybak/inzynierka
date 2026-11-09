# Query Extraction Rules

## Purpose and Language

- Query extraction turns a shopping query into one product category, hard filters, and a list of residual concepts.
- English is the main language, followed by Polish and Spanish. The intended weighting is 94% English, 5% Polish, and 1% Spanish.
- Category, feature, and value names follow the [taxonomy](../categories_and_features.md). Filters reflect requirements expressed in the query.

## Category

- The category describes the product the user wants to buy. `t-shirt to wear with jeans` refers to `T-shirts`. `t-shirt dress` refers to `Dresses` when that category is supported.
- When the query identifies no supported category, the result is `category: null` and extraction stops.
- A bare `t-shirt` gives `T-shirts` with empty filter and residual lists.
- Use `Tank tops & Camisoles` for generic `top` queries such as `top`, `black top`, and `crop top` when the query does not identify a more specific supported garment.
- Use `Polos` for a collared tee, such as `tee with a collar`.

**Outside scope**

- Requests for alternative product categories, such as `t-shirt or dress`.

## Output Format

The parser returns one JSON object with exactly three fields.

| Field | Type | Allowed values |
| --- | --- | --- |
| `category` | string or null | One supported category using its exact taxonomy name, or `null`. |
| `filters` | array of objects | One object per filter clause. All clauses combine with `AND`, including clauses on the same feature. |
| `residual` | array of strings | One string per independent concept, in query order. |

Use an empty array when there are no filters or residual concepts. When no category is found, return `{"category":null,"filters":[],"residual":[]}`.

Each categorical filter has exactly `feature`, `operator`, and `values`. Use a feature key available for the selected category, or `brand`. The `values` field is a non-empty array of distinct strings using exact taxonomy labels. Exclude `Other`, `Not Applicable`, and `Unknown` from all taxonomy filters, including exclusions. For `brand`, use the explicitly requested brand name. Omit features that have no filter.

A request for a strapless garment uses `strap_style = Strapless` when the category supports it.

Each price filter has exactly `feature` (always `"price"`), `operator`, and `value` (a finite, nonnegative JSON number). The amount has no currency field.

| Feature | Allowed `operator` | Meaning |
| --- | --- | --- |
| Single-choice features, including `gender`, and `brand` | `in` | Matches any listed value (OR). |
| Single-choice features, including `gender`, and `brand` | `not_in` | Matches only if the value is absent from the list. |
| `colors` and other multi-choice features | `contains_any` | Contains at least one listed value (OR). Also used for a single requested value. |
| `colors` and other multi-choice features | `contains_all` | Contains every listed value (AND). |
| `colors` and other multi-choice features | `contains_none` | Contains none of the listed values. |
| `colors` and other multi-choice features | `equals_set` | Contains exactly the listed values, in any order. |
| `main_composition` | `contains_any` | Contains at least one listed material. Also used for a single requested material. |
| `main_composition` | `contains_all` | Contains every listed material. |
| `main_composition` | `contains_none` | Contains none of the listed materials. |
| `main_composition` | `equals_set` | Contains exactly the listed materials. For `100% wool`, use `["Wool"]`. |
| `price` | `gte` | Price is greater than or equal to `value`. |
| `price` | `lte` | Price is less than or equal to `value`. |
| `price` | `around` | Price is approximately `value`. The tolerance is still open. |

Encode `between X and Y` as two price clauses, `gte` for X and `lte` for Y.

**Example** — `women’s turquoise Nike T-shirt, cotton without polyester, between 50 and 100 PLN, for hiking`

```json
{
  "category": "T-shirts",
  "filters": [
    {"feature": "gender", "operator": "in", "values": ["Women"]},
    {"feature": "brand", "operator": "in", "values": ["Nike"]},
    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
    {"feature": "main_composition", "operator": "contains_any", "values": ["Cotton"]},
    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
    {"feature": "price", "operator": "gte", "value": 50},
    {"feature": "price", "operator": "lte", "value": 100}
  ],
  "residual": ["turquoise", "for hiking"]
}
```

## Filters

### Combining Requirements

- Filters on different features combine with `AND`. A `short-sleeve tee in white or black` must have short sleeves and can be either color.
- Multiple acceptable values for a single-choice feature combine with `OR`. A `long- or 3/4-sleeve tee` can have either sleeve length.
- Multi-choice features preserve `AND` or `OR` as requested. In a category with closure filters, `zip and button bomber` requires both closures and `zip or button bomber` accepts either.

**Outside scope**

- Alternatives across different features, such as `short sleeve or white`.

### Exclusions

- All categories support explicit exclusions for the single-choice and multi-choice features they expose as filters, as well as for brand. Exclusions use the same allowed values as positive filters. A category must still be selected from the product the user wants.
- Positive and negative requirements can apply to the same feature. Return separate clauses combined with `AND`.
- `slim or regular T-shirt, but not oversized` gives `fit in ["Slim", "Regular"]` and `fit not_in ["Oversized"]`.
- `white T-shirt with no red` gives `colors contains_any ["White"]` and `colors contains_none ["Red"]`.

**Outside scope**

- Excluding a category or excluding only a combination of values, such as `anything but a red-and-white tee`.

### Brand and Gender

**Allowed values**

- Brand — any explicitly requested brand name.
- Gender — `Men` or `Women` for any category with a `gender` feature, when specified in the query.

**Examples**

- `women’s Nike tee` gives `Women` and `Nike`.
- `tee by Off-White` specifies a brand. `off-white tee` specifies a color shade.

### Price

**Allowed forms**

- `>= X` — at least X.
- `<= X` — up to X.
- `between X and Y` — a price range.
- `around X` — an approximate amount. The tolerance is still open.

**Amount handling**

- The parser preserves decimal amounts and ignores currency names and symbols without conversion.
- `2-pack of size 42 tees up to 99,99 PLN` gives one price constraint, `<= 99.99`.

### Colors

- A query can name any number of colors. `Multicolor` can appear alongside other colors in the query.

**Allowed operators**

- `AND` — all named colors. `white and black and red` extracts all three.
- `OR` — any named color. `white or black` extracts both alternatives.
- `contains_none` — excludes every listed color. `no red or black` excludes both colors individually.
- `equals_set` — requires exactly the specified colors. `all-black T-shirt` gives `equals_set ["Black"]`. `black T-shirt` gives `contains_any ["Black"]`.

**Outside scope**

- Mixed color expressions, such as `white and black or red`.

### Materials

- Material filters apply to the main composition.

**Allowed operations**

- `contains Wool` — wool is present. A 70% wool, 30% cotton blend matches.
- `contains only Wool` — wool is the sole material. The same blend fails this filter.
- `only wool and cotton` gives `{"feature":"main_composition","operator":"equals_set","values":["Wool","Cotton"]}`. A 70% wool, 30% cotton blend matches. Pure wool and any blend that also contains elastane fail this filter.
- `without polyester` — polyester is absent.
- `cotton and wool` requires both materials. `cotton or linen` accepts either.
- Positive requirements can combine with exclusions. `cotton and wool without polyester` requires both cotton and wool and excludes polyester.

**Material percentages**

- `0% wool` → exclude `Wool` from the main composition.
- `30% wool` → `contains Wool`. Any percentage above 0% and below 100% means the material must be present, regardless of its share.
- `100% wool` → `contains only Wool`.

## Residual

- Residual is a list with one item per independent concept. Items use the query’s language and keep the original wording or a very close variant.
- Modifiers, negation, and alternatives stay with the concept they qualify. The category and requirements fully captured by filters are omitted.
- `cotton tee with a mountain print for a family reunion` gives a Cotton filter and `["mountain print", "for a family reunion"]`.
- `dress shirt` gives `Shirts` and residual `["dress"]`.

### Color Shades

- A named shade gives a color family filter and keeps the exact shade in residual. `turquoise tee` gives `Blue` and `["turquoise"]`. `blue tee` gives `Blue` and `[]`.
- An excluded shade stays in residual with its negation. `tee, but not turquoise` gives `["not turquoise"]` with no color filter.

**Language examples**

- `turkusowa koszulka z nadrukiem gór` gives `T-shirts`, `Blue`, and `["turkusowa", "z nadrukiem gór"]`.
- `camiseta de algodón para una reunión familiar` gives `T-shirts`, `contains Cotton`, and `["para una reunión familiar"]`.
