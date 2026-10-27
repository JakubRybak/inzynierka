"""
Condition tree that the parser output is converted to:

    {"op": "and" | "or", "args": [...]}   {"op": "not", "arg": ...}
    {"feature": "colors", "values": ["Black", "White"], "match": "any" | "all" | "exact"}

A product's feature value is treated as a set (main_composition: the materials in it). match: any – non-empty
intersection (default), all – the product has every value, exact – exactly these values. A missing feature never
matches. category is compared with both category and section, brand with product metadata.
"""
from collections import defaultdict
import math
import operator

PRICE_OPERATORS = {"lt": operator.lt, "lte": operator.le, "gt": operator.gt,
                   "gte": operator.ge, "eq": operator.eq}
PRICE_SYMBOLS = {"lt": "<", "lte": "≤", "gt": ">", "gte": "≥", "eq": "="}


def product_price(p):
    """Positive finite catalog price; zero and invalid source values mean unknown."""
    raw = p.get("msrpUSD")
    if isinstance(raw, bool):
        return None
    try:
        value = float(raw)
    except (ValueError, TypeError, OverflowError):
        return None
    return value if math.isfinite(value) and value > 0 else None

OPERATORS = {"and", "or", "not"}
MATCH_MODES = {"any", "all", "exact"}
MOCK_SKIP = {"Other", "Not Applicable"}


class ConditionError(ValueError):
    pass


def validate(c, path="condition"):
    if c is None:
        return None
    if not isinstance(c, dict):
        raise ConditionError(f"{path}: expected an object, got {type(c).__name__}")
    if "feature" in c:
        if c["feature"] == "price":
            v = c.get("value")
            if (set(c) != {"feature", "operator", "value"}
                    or c.get("operator") not in PRICE_OPERATORS
                    or type(v) not in (int, float) or not math.isfinite(v) or v < 0):
                raise ConditionError(f"{path}: price requires a numeric nonnegative value and lt/lte/gt/gte/eq")
            return c
        if set(c) - {"feature", "values", "match"}:
            raise ConditionError(f"{path}: unknown keys {sorted(set(c) - {'feature', 'values', 'match'})}")
        v = c.get("values")
        if not isinstance(c["feature"], str) or not c["feature"].strip():
            raise ConditionError(f"{path}: feature must be a non-empty string")
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x.strip() for x in v):
            raise ConditionError(f"{path}: values must be a non-empty list of strings")
        if c.get("match", "any") not in MATCH_MODES:
            raise ConditionError(f"{path}: match must be one of {sorted(MATCH_MODES)}")
        return c
    op = c.get("op")
    if op not in OPERATORS:
        raise ConditionError(f"{path}: unknown operator {op!r}")
    if op == "not":
        if set(c) != {"op", "arg"}:
            raise ConditionError(f"{path}: not requires arg")
        validate(c["arg"], f"{path}.arg")
    else:
        if set(c) != {"op", "args"} or not isinstance(c["args"], list) or not c["args"]:
            raise ConditionError(f"{path}: {op} requires a non-empty args list")
        for i, a in enumerate(c["args"]):
            validate(a, f"{path}.args[{i}]")
    return c


def describe(c, top=True):
    if c is None:
        return "no conditions"
    if "feature" in c:
        if c["feature"] == "price":
            return f"price {PRICE_SYMBOLS[c['operator']]} {c['value']:g}"
        v, mode = c["values"], c.get("match", "any")
        if mode == "exact":
            return f"{c['feature']} = only {{{', '.join(v)}}}"
        if len(v) == 1:
            return f"{c['feature']} = {v[0]}"
        return f"{c['feature']} {'⊇' if mode == 'all' else '∈'} {{{', '.join(v)}}}"
    if c["op"] == "not":
        return f"NOT {describe(c['arg'], False)}"
    text = f" {c['op'].upper()} ".join(describe(a, False) for a in c["args"])
    return text if top or len(c["args"]) == 1 else f"({text})"


def _product_values(p):
    out = {"category": [p["category"], p["section"]]}
    if isinstance(p.get("brand"), str) and p["brand"]:
        out["brand"] = [p["brand"]]
    g = p["features"].get("gender") or p.get("gender")
    if g:
        out["gender"] = [g]
    for f, v in p["features"].items():
        if f == "gender" or v is None:
            continue
        out[f] = list(v) if isinstance(v, (list, dict)) else [v]
    return out


class Vocabulary:
    """Features and values present in the index."""

    def __init__(self, products):
        self.values = defaultdict(dict)          # feature -> {casefolded: canonical}
        self.multi_valued = set()
        for p in products:
            for f, vals in _product_values(p).items():
                for v in vals:
                    self.values[f].setdefault(str(v).casefold(), str(v))
            self.multi_valued |= {f for f, v in p["features"].items() if isinstance(v, (list, dict))}

    def canonical(self, feature, value):
        return self.values.get(feature, {}).get(str(value).casefold())


def prune(c, vocabulary):
    """Drops leaves whose feature or value is not in the index. Returns (tree, warnings)."""
    warnings = []

    def walk(c):
        if c is None:
            return None
        if "feature" in c:
            f = c["feature"]
            if f == "price":
                return validate(c)
            if f not in vocabulary.values:
                warnings.append(f"unsupported feature: {f} (dropped {describe(c)})")
                return None
            vals = []
            for v in c["values"]:
                k = vocabulary.canonical(f, v)
                if k is None:
                    warnings.append(f"unsupported value: {f} = {v}")
                elif k not in vals:
                    vals.append(k)
            if not vals:
                return None
            return {"feature": f, "values": vals} | ({"match": c["match"]} if "match" in c else {})
        if c["op"] == "not":
            a = walk(c["arg"])
            return None if a is None else {"op": "not", "arg": a}
        args = [a for a in map(walk, c["args"]) if a is not None]
        if not args:
            return None
        return args[0] if len(args) == 1 and c["op"] == "or" else {"op": c["op"], "args": args}

    return walk(c), warnings


def prepare_product(p):
    """Adds p["_v"]: feature -> casefolded value set."""
    v = {"category": frozenset({p["category"].casefold(), p["section"].casefold()})}
    if isinstance(p.get("brand"), str) and p["brand"]:
        v["brand"] = frozenset({p["brand"].casefold()})
    g = p["features"].get("gender") or p.get("gender")
    if isinstance(g, str) and g:
        v["gender"] = frozenset({g.casefold()})
    for f, val in p["features"].items():
        if f == "gender" or val is None or val == [] or val == {}:
            continue
        if isinstance(val, dict):
            v[f] = frozenset(m.casefold() for m, share in val.items() if share > 0)
        elif isinstance(val, list):
            v[f] = frozenset(str(x).casefold() for x in val)
        else:
            v[f] = frozenset({str(val).casefold()})
    p["_v"] = v
    p["_price"] = product_price(p)
    return p


def compile_condition(c):
    if c is None:
        return lambda p: True
    if "feature" in c:
        if c["feature"] == "price":
            compare, value = PRICE_OPERATORS[c["operator"]], c["value"]
            return lambda p: p.get("_price") is not None and compare(p["_price"], value)
        f, vals, mode = c["feature"], frozenset(v.casefold() for v in c["values"]), c.get("match", "any")
        if mode == "all":
            return lambda p: f in p["_v"] and vals <= p["_v"][f]
        if mode == "exact":
            return lambda p: p["_v"].get(f) == vals
        return lambda p: not p["_v"].get(f, frozenset()).isdisjoint(vals)
    if c["op"] == "not":
        a = compile_condition(c["arg"])
        return lambda p: not a(p)
    fs = [compile_condition(a) for a in c["args"]]
    if c["op"] == "and":
        return lambda p: all(f(p) for f in fs)
    return lambda p: any(f(p) for f in fs)


def matches(c, p):
    return compile_condition(c)(p)


def matched_features(c, p):
    """Features that satisfied a non-negated leaf (highlighted in the UI)."""
    out = []

    def walk(c, positive):
        if c is None:
            return
        if "feature" in c:
            if positive and matches(c, p) and c["feature"] not in out:
                out.append(c["feature"])
        elif c["op"] == "not":
            walk(c["arg"], not positive)
        else:
            for a in c["args"]:
                walk(a, positive)

    walk(c, True)
    return out


def filter_products(c, products):
    """Indexes of the products meeting the condition, with the features each of them matched."""
    if c is None:
        return dict(candidates=list(range(len(products))), matched={})
    f = compile_condition(c)
    candidates = [i for i, p in enumerate(products) if f(p)]
    return dict(candidates=candidates, matched={i: matched_features(c, products[i]) for i in candidates})
