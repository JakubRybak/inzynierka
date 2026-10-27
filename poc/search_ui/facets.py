"""Filter panel: features, operators and values per category, taken from the query parser response schemas."""
import json
import re
from collections import Counter
from pathlib import Path

import common

SCHEMAS = common.REPO / "poc/query_parsing/schemas"


def _schema_file(category):
    return re.sub(r"[^a-z0-9]+", "-", category.lower().replace("&", "and")).strip("-") + ".json"


def load(products, schemas=SCHEMAS):
    """-> {category: [{feature, kind, operators, values: [[value, count], ...]}]} for indexed categories.
    products must already have p["_v"] (conditions.prepare_product)."""
    out = {}
    for category in sorted({p["category"] for p in products}):
        path = Path(schemas) / _schema_file(category)
        if not path.exists():
            continue
        in_category = [p for p in products if p["category"] == category]
        features = []
        for option in json.loads(path.read_text(encoding="utf-8"))["properties"]["filters"]["items"]["anyOf"]:
            props = option["properties"]
            feature, operators = props["feature"]["enum"][0], props["operator"]["enum"]
            if feature == "price":
                features.append(dict(feature=feature, kind="number", operators=operators, values=[]))
                continue
            allowed = props["values"]["items"].get("enum")
            if allowed is None:
                # open vocabulary (brand): the values present in the index
                values = Counter(p[feature] for p in in_category if p.get(feature)).most_common()
            else:
                values = [(v, sum(v.casefold() in p["_v"].get(feature, ()) for p in in_category)) for v in allowed]
            features.append(dict(feature=feature, kind="multi" if "contains_any" in operators else "single",
                                 operators=operators, values=[list(v) for v in values]))
        features.sort(key=lambda f: f["feature"] == "brand")
        out[category] = features
    return out
