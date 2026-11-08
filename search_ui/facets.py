"""Filter panel: features, value counts and price per category, taken from the feature extraction schemas."""
import sys
from collections import Counter

import common

sys.path.insert(0, str(common.REPO))
from feature_extraction.schema.loader import load_schemas  # noqa: E402

HIDDEN = {"Other", "Not Applicable", "Unknown"}
OPERATORS = {"single_choice": ["in", "not_in"],
             "multi_choice": ["contains_any", "contains_all", "contains_none", "equals_set"],
             "composition": ["contains_any", "contains_all", "contains_none", "equals_set"]}


def category_schemas():
    """-> {category: {feature: definition}} for every configured category."""
    return {category: features for (_, category), features in load_schemas()[0].items()}


def load(products, schemas=None):
    """-> {category: [{feature, kind, operators, values: [[value, count], ...]}]} for indexed categories.
    products must already have p["_v"] (conditions.prepare_product). Other, Not Applicable and Unknown are left out,
    as the query parser never filters on them."""
    schemas = category_schemas() if schemas is None else schemas
    out = {}
    for category in sorted({p["category"] for p in products}):
        if category not in schemas:
            continue
        in_category = [p for p in products if p["category"] == category]
        features = []
        for feature, definition in schemas[category].items():
            values = [(v, sum(v.casefold() in p["_v"].get(feature, ()) for p in in_category))
                      for v in definition["values"] if v not in HIDDEN]
            features.append(dict(feature=feature, kind="single" if definition["type"] == "single_choice" else "multi",
                                 operators=OPERATORS[definition["type"]], values=[list(v) for v in values]))
        features.append(dict(feature="price", kind="number", operators=["lt", "lte", "gt", "gte", "eq"], values=[]))
        brands = Counter(p["brand"] for p in in_category if p.get("brand")).most_common()
        features.append(dict(feature="brand", kind="single", operators=["in", "not_in"], values=[list(b) for b in brands]))
        out[category] = features
    return out
