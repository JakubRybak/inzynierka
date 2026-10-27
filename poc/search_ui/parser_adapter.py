"""
Query parsers and the adapter from parser output to the condition tree in conditions.py.
A parser is a function f(query) -> dict in the QueryParser.to_dict() format of poc/scripts/query_parser.py.

    --parser llm              poc/scripts/query_parser.py (Vertex AI)
    --parser mock             parser_mock.yaml + simple word matching
    --parser module:function  any function returning the same format
"""
import copy
import importlib
import re
import sys
from pathlib import Path

import yaml

import conditions

HERE = Path(__file__).resolve().parent
MOCK_FILE = HERE / "parser_mock.yaml"

# parser operator -> (leaf match mode, negated)
OPERATORS = {
    "in": ("any", False),
    "contains_any": ("any", False),
    "not_in": ("any", True),
    "contains_none": ("any", True),
    "contains_all": ("all", False),
    "equals_set": ("exact", False),
}


class OutOfCatalog(Exception):
    pass


def to_condition(raw):
    if not isinstance(raw, dict) or "category" not in raw:
        raise conditions.ConditionError("parser output has no category field")
    if raw["category"] is None:
        raise OutOfCatalog("The parser returned no category: the query is outside the catalog or too general.")
    filters = raw.get("filters") or []
    if not isinstance(filters, list):
        raise conditions.ConditionError("filters must be a list")
    args = [{"feature": "category", "values": [raw["category"]]}]
    for i, f in enumerate(filters):
        if isinstance(f, dict) and f.get("feature") == "price":
            args.append(conditions.validate(f, f"filters[{i}]"))
            continue
        if not isinstance(f, dict) or f.get("operator") not in OPERATORS:
            raise conditions.ConditionError(f"filters[{i}]: unknown operator {f.get('operator') if isinstance(f, dict) else f!r}")
        mode, negated = OPERATORS[f["operator"]]
        leaf = {"feature": f.get("feature"), "values": f.get("values")}
        if mode == "exact" or (mode == "all" and len(f.get("values") or []) > 1):
            leaf["match"] = mode
        args.append({"op": "not", "arg": leaf} if negated else leaf)
    return conditions.validate({"op": "and", "args": args})


def parser_info(raw):
    """Category, residual, step latencies and cost for the UI."""
    if not isinstance(raw, dict):
        return {}
    meta = raw.get("metadata") or {}
    return dict(category=raw.get("category"), residual=raw.get("residual") or "",
                step1_s=raw.get("step1_latency_seconds"), step2_s=raw.get("step2_latency_seconds"),
                cost_usd=meta.get("estimated_cost_usd"), model=meta.get("model"), source=raw.get("_mock"))


class Parser:
    def __init__(self, name, function):
        self.name, self.function = name, function

    def __call__(self, q):
        return self.function(q)


def load_parser(spec, vocabulary=None, mock_file=MOCK_FILE):
    if spec == "mock":
        return Parser("mock (parser_mock.yaml + index vocabulary)", MockParser(vocabulary, mock_file))
    if spec == "llm":
        spec = "llm_parser:parse"
    module, _, function = spec.partition(":")
    if not module or not function:
        raise SystemExit(f"--parser: expected llm, mock or module:function, got {spec!r}")
    for p in (HERE.parents[1], HERE, Path.cwd()):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    mod = importlib.import_module(module)
    return Parser(getattr(mod, "NAME", None) or spec, getattr(mod, function))


def normalize_text(s):
    s = str(s).casefold().replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", s)).strip()


def _singular(s):
    if re.search(r"(ss|sh|ch|x)es$", s):
        return s[:-2]
    return s[:-1] if s.endswith("s") and not s.endswith("ss") else s


def phrases_from_vocabulary(vocabulary):
    """phrase -> [(feature, value)]; category names also in singular."""
    phrases = {}
    for f, values in vocabulary.values.items():
        if f == "brand":
            continue
        for v in values.values():
            if v in conditions.MOCK_SKIP:
                continue
            forms = {normalize_text(v)}
            if f == "category":
                for part in re.split(r"&|,", v):
                    forms |= {normalize_text(part), _singular(normalize_text(part))}
            for form in filter(None, forms):
                phrases.setdefault(form, [])
                if (f, v) not in phrases[form]:
                    phrases[form].append((f, v))
    return phrases


class MockParser:
    """parser_mock.yaml first, then plain matching of query words against index values.
    Returns the same format as the LLM parser."""

    def __init__(self, vocabulary, path=MOCK_FILE):
        self.path = Path(path)
        self.phrases = phrases_from_vocabulary(vocabulary) if vocabulary else {}
        self.multi_valued = vocabulary.multi_valued if vocabulary else set()

    def __call__(self, q):
        examples = yaml.safe_load(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        for query, result in (examples or {}).items():
            if normalize_text(query) == normalize_text(q):
                return {"query": q, "filters": [], "residual": ""} | copy.deepcopy(result) | {"_mock": "parser_mock.yaml"}
        text = f" {normalize_text(q)} "
        category, filters = None, {}
        for phrase in sorted(self.phrases, key=len, reverse=True):
            targets = self.phrases[phrase]
            if f" {phrase} " not in text or len({f for f, _ in targets}) > 1:
                continue
            text = text.replace(f" {phrase} ", " ")
            f, v = targets[0]
            if f == "category":
                category = category or v
            else:
                op = "contains_any" if f in self.multi_valued else "in"
                filters.setdefault((f, op), []).append(v)
        return {"query": q, "category": category,
                "filters": [{"feature": f, "operator": op, "values": v} for (f, op), v in filters.items()],
                "residual": text.strip(), "_mock": "vocabulary"}
