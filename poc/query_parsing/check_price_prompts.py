"""Bounded prompt experiment: offline examples, optionally 15 live Vertex calls.

Calls the model directly; does not exercise the downstream parser or search UI.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from query_parser import QueryParser, CATEGORY_FILE_MAP, INPUT_RATE, OUTPUT_RATE


def clause(feature, operator, value):
    return {"feature": feature, "operator": operator,
            "value" if feature == "price" else "values": value}


def price(operator, value):
    return clause("price", operator, value)


CASES = [
    {"category": "T-shirts", "query": f"black cotton tee below 175 {currency}",
     "filters": [clause("colors", "contains_any", ["Black"]),
                 clause("main_composition", "contains_any", ["Cotton"]), price("lt", 175)],
     "residual": ""}
    for currency in ("dollars", "euros", "PLN")
] + [
    {"category": "Dresses", "query": "sukienka do 399,99 zl",
     "filters": [price("lte", 399.99)], "residual": ""},
    {"category": "Dresses", "query": "dress costing at least 75 euros",
     "filters": [price("gte", 75)], "residual": ""},
    {"category": "Tank tops & Camisoles", "query": "tank top costing more than 40 PLN",
     "filters": [price("gt", 40)], "residual": ""},
    {"category": "Tank tops & Camisoles", "query": "camisole priced at exactly 89.50 dollars",
     "filters": [price("eq", 89.5)], "residual": ""},
    {"category": "Dresses", "query": "dress priced between 110 and 230 euros",
     "filters": [price("gte", 110), price("lte", 230)], "residual": ""},
    {"category": "T-shirts", "query": "tee above 70 but below 180 PLN",
     "filters": [price("gt", 70), price("lt", 180)], "residual": ""},
    {"category": "T-shirts", "query": "100% cotton T-shirt size 42",
     "filters": [clause("main_composition", "contains_any", ["Cotton"])],
     "residual_contains": ["42"]},
    {"category": "Tank tops & Camisoles", "query": "cheap tank top around 80 euros",
     "filters": [], "residual_contains": ["cheap", "80"]},
    {"category": "Dresses", "query": "blue dress below 275 dollars for a wedding",
     "filters": [clause("colors", "contains_any", ["Blue"]), price("lt", 275)],
     "residual_contains": ["wedding"], "residual_excludes": ["275", "dollar", "blue"]},
]


def validate(value, schema):
    """Validate the schema subset used here, including local extra-key checks."""
    if value is None and schema.get("nullable"):
        return True
    if "anyOf" in schema:
        return any(validate(value, branch) for branch in schema["anyOf"])
    kind = schema["type"]
    if kind == "OBJECT":
        props = schema["properties"]
        return (isinstance(value, dict) and set(schema.get("required", [])) <= set(value)
                and set(value) <= set(props)
                and all(validate(v, props[k]) for k, v in value.items()))
    if kind == "ARRAY":
        return (isinstance(value, list)
                and schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", math.inf)
                and all(validate(v, schema["items"]) for v in value))
    if kind == "NUMBER":
        return (type(value) in (float, int) and math.isfinite(value)
                and value >= schema.get("minimum", -math.inf))
    if kind == "STRING":
        return isinstance(value, str) and ("enum" not in schema or value in schema["enum"])
    raise ValueError(f"Unsupported type: {kind}")


def canonical(filters):
    normalized = [dict(f, values=sorted(f["values"])) if "values" in f else f for f in filters]
    return sorted(json.dumps(f, sort_keys=True) for f in normalized)


def main():
    args_parser = argparse.ArgumentParser(description=__doc__)
    args_parser.add_argument("--live", action="store_true", help="Authorize 15 paid API calls")
    args = args_parser.parse_args()
    parser = QueryParser(project="project-3a86f100-1aae-4780-84b",
                         model="gemini-3.5-flash-lite", location="global", thinking="NONE", timeout=60)
    count = 0
    for slug in ["category", *CATEGORY_FILE_MAP.values()]:
        schema = json.loads((HERE / "schemas" / f"{slug}.json").read_text())
        for line in (HERE / "prompts" / f"{slug}.md").read_text().splitlines():
            if line.startswith("Output: "):
                assert validate(json.loads(line[8:]), schema), (slug, line)
                count += 1
    print(f"Offline: {count} few-shot outputs passed schema validation", flush=True)
    if not args.live:
        return
    output = HERE / "results" / ("price_prompts_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {"model": parser.model, "thinking": parser.thinking, "location": parser.location,
              "scope": "Raw structured model responses only; no parser normalization or UI filtering",
              "input_usd_per_million_assumed": INPUT_RATE * 1e6,
              "output_usd_per_million_assumed": OUTPUT_RATE * 1e6,
              "results": []}
    tasks = [("features", case) for case in CASES]
    tasks += [("category", CASES[i]) for i in (0, 3, 5)]
    for stage, case in tasks:
        category = case["category"]
        if stage == "features":
            prompt, schema = parser.feature_prompts[category], parser.feature_schemas[category]
            user = f"Category: {category}\nQuery: {case['query']}"
        else:
            prompt, schema, user = parser.category_system_instruction, parser.category_schema, case["query"]
        actual, usage, seconds = parser._call_api(prompt, user, schema)
        valid = validate(actual, schema)
        if stage == "category":
            passed = valid and actual == {"category": category}
        else:
            residual = actual.get("residual", "")
            passed = (valid and canonical(actual["filters"]) == canonical(case["filters"])
                      and ("residual" not in case or residual == case["residual"])
                      and all(s in residual.lower() for s in case.get("residual_contains", []))
                      and all(s not in residual.lower() for s in case.get("residual_excludes", [])))
        estimated = (usage.get("promptTokenCount", 0) * INPUT_RATE
                     + (usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)) * OUTPUT_RATE)
        report["results"].append({"stage": stage, "case": case, "actual": actual,
                                  "schema_valid": valid, "passed": passed, "usage": usage,
                                  "seconds": seconds, "estimated_cost_usd": estimated})
        report["estimated_cost_usd"] = sum(r["estimated_cost_usd"] for r in report["results"])
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(f"{stage}: {'PASS' if passed else 'FAIL'} | {case['query']} | {json.dumps(actual, ensure_ascii=False)}", flush=True)
    print(f"Passed {sum(r['passed'] for r in report['results'])}/{len(tasks)}; estimated ${report['estimated_cost_usd']:.6f}; {output}")


if __name__ == "__main__":
    main()
