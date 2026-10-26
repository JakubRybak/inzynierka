#!/usr/bin/env python3
"""
Benchmark runner to evaluate query parser accuracy, latency, and logical extraction.
Runs 26 diverse queries (none of which are present in the few-shot examples).
"""

import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "poc/scripts"))

from query_parser import QueryParser

TEST_CASES = [
    # --- T-SHIRTS ---
    {
        "id": "T1",
        "query": "oversized vintage graphic tee for men",
        "expected_category": "T-shirts",
        "expected_features": {"gender": "Men", "fit": "Oversized"},
        "expected_residual_contains": "vintage",
    },
    {
        "id": "T2",
        "query": "blue or navy crewneck t-shirt 100% cotton",
        "expected_category": "T-shirts",
        "expected_features": {"colors": ["Blue"], "neckline": "Crewneck", "main_composition": ["Cotton"]},
        "color_operator": "contains_any",
    },
    {
        "id": "T3",
        "query": "white long sleeve t-shirt without polyester",
        "expected_category": "T-shirts",
        "expected_features": {"colors": ["White"], "sleeve_length": "Long Sleeve"},
        "exclusion": ("main_composition", "Polyester"),
    },
    {
        "id": "T4",
        "query": "men's Adidas running t-shirt in grey",
        "expected_category": "T-shirts",
        "expected_features": {"brand": "Adidas", "gender": "Men", "colors": ["Grey"]},
        "expected_residual_contains": "running",
    },
    {
        "id": "T5",
        "query": "green and yellow striped tee",
        "expected_category": "T-shirts",
        "expected_features": {"colors": ["Green", "Yellow"], "pattern": "Striped"},
        "color_operator": "contains_all",
    },
    {
        "id": "T6",
        "query": "męska czarna koszulka bawełniana z krótkim rękawem",
        "expected_category": "T-shirts",
        "expected_features": {"gender": "Men", "colors": ["Black"], "main_composition": ["Cotton"], "sleeve_length": "Short Sleeve"},
    },
    {
        "id": "T7",
        "query": "only black slim fit t-shirt",
        "expected_category": "T-shirts",
        "expected_features": {"colors": ["Black"], "fit": "Slim"},
        "color_operator": "equals_set",
    },

    # --- DRESSES ---
    {
        "id": "D1",
        "query": "emerald green maxi dress for prom",
        "expected_category": "Dresses",
        "expected_features": {"colors": ["Green"], "length": "Maxi"},
        "expected_residual_contains": "prom",
    },
    {
        "id": "D2",
        "query": "long sleeve floral wrap dress",
        "expected_category": "Dresses",
        "expected_features": {"sleeve_length": "Long Sleeve", "pattern": "Floral", "dress_type": ["Wrap"]},
    },
    {
        "id": "D3",
        "query": "czarna sukienka midi bez ramiączek na imprezę",
        "expected_category": "Dresses",
        "expected_features": {"colors": ["Black"], "length": "Midi", "strap_style": "Strapless"},
        "expected_residual_contains": "imprez",
    },
    {
        "id": "D4",
        "query": "women's knitted sweater dress in beige or brown",
        "expected_category": "Dresses",
        "expected_features": {"gender": "Women", "dress_type": ["Sweater Dress"], "colors": ["Beige", "Brown"]},
        "color_operator": "contains_any",
    },
    {
        "id": "D5",
        "query": "red and white polka dot mini dress",
        "expected_category": "Dresses",
        "expected_features": {"colors": ["Red", "White"], "pattern": "Polka Dot", "length": "Mini"},
        "color_operator": "contains_all",
    },
    {
        "id": "D6",
        "query": "Gucci silk slip dress",
        "expected_category": "Dresses",
        "expected_features": {"brand": "Gucci", "main_composition": ["Silk"], "dress_type": ["Slip"]},
    },
    {
        "id": "D7",
        "query": "fitted cocktail dress with V-neck",
        "expected_category": "Dresses",
        "expected_features": {"dress_silhouette": "Fitted", "neckline": "V-Neck"},
        "expected_residual_contains": "cocktail",
    },
    {
        "id": "D8",
        "query": "sukienka letnia w kwiaty z lnu",
        "expected_category": "Dresses",
        "expected_features": {"pattern": "Floral", "main_composition": ["Linen"]},
        "expected_residual_contains": "letnia",
    },

    # --- TANK TOPS & CAMISOLES ---
    {
        "id": "K1",
        "query": "white ribbed racerback tank top for workout",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"colors": ["White"], "strap_style": "Racerback"},
        "expected_residual_contains": "workout",
    },
    {
        "id": "K2",
        "query": "czarny damski top na cienkich ramiączkach bez wzoru",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"gender": "Women", "colors": ["Black"], "strap_width": "Spaghetti", "pattern": "Solid"},
    },
    {
        "id": "K3",
        "query": "silk camisole with scoop neck in pink",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"main_composition": ["Silk"], "neckline": "Scoop Neck", "colors": ["Pink"]},
    },
    {
        "id": "K4",
        "query": "men's Under Armour gym singlet in black or grey",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"brand": "Under Armour", "gender": "Men", "colors": ["Black", "Grey"]},
        "color_operator": "contains_any",
    },
    {
        "id": "K5",
        "query": "cropped halter top without polyester",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"length": "Cropped", "strap_style": "Halter"},
        "exclusion": ("main_composition", "Polyester"),
    },
    {
        "id": "K6",
        "query": "loose cotton camisole with wide straps",
        "expected_category": "Tank tops & Camisoles",
        "expected_features": {"fit": "Oversized", "main_composition": ["Cotton"], "strap_width": "Wide"},
    },

    # --- OUT OF CATALOG / UNSUPPORTED / AMBIGUOUS ---
    {
        "id": "O1",
        "query": "czarne skórzane botki na obcasie",
        "expected_category": None,
    },
    {
        "id": "O2",
        "query": "blue denim jeans slim fit for men",
        "expected_category": None,
    },
    {
        "id": "O3",
        "query": "leather jacket for winter",
        "expected_category": None,
    },
    {
        "id": "O4",
        "query": "cute summer tops for women",
        "expected_category": None,
    },
    {
        "id": "O5",
        "query": "mens dress shirts slim fit",
        "expected_category": None,
    },
]


def run_benchmark():
    parser = QueryParser()
    results = []

    print(f"Running benchmark on {len(TEST_CASES)} diverse queries with {parser.model}...")
    print("=" * 80)

    category_correct = 0
    total_time_step1 = 0.0
    total_time_step2 = 0.0
    total_cost = 0.0

    for i, tc in enumerate(TEST_CASES, 1):
        q = tc["query"]
        expected_cat = tc["expected_category"]
        res = parser.parse(q)

        cat_match = (res.category == expected_cat)
        if cat_match:
            category_correct += 1

        total_time_step1 += res.step1_latency_seconds
        total_time_step2 += res.step2_latency_seconds
        total_cost += res.metadata.get("estimated_cost_usd", 0.0)

        # Evaluate features
        filter_map = {}
        for f in res.filters:
            filter_map[f.feature] = (f.operator, f.values)

        feature_eval = []
        if expected_cat is not None:
            for feat, expected_val in tc.get("expected_features", {}).items():
                if feat in filter_map:
                    op, vals = filter_map[feat]
                    if isinstance(expected_val, list):
                        match = all(v in vals for v in expected_val)
                    else:
                        match = expected_val in vals
                    feature_eval.append((feat, match, f"got {op} {vals}"))
                else:
                    feature_eval.append((feat, False, "MISSING"))

            if "color_operator" in tc and "colors" in filter_map:
                op, vals = filter_map["colors"]
                op_match = (op == tc["color_operator"])
                feature_eval.append(("color_op", op_match, f"got {op}, expected {tc['color_operator']}"))

            if "exclusion" in tc:
                feat, val = tc["exclusion"]
                ex_match = False
                if feat in filter_map:
                    op, vals = filter_map[feat]
                    if op in ("not_in", "contains_none") and val in vals:
                        ex_match = True
                feature_eval.append((f"exclude_{val}", ex_match, f"got {filter_map.get(feat)}"))

        status = "PASS" if cat_match and (not feature_eval or all(m[1] for m in feature_eval)) else "CHECK"
        cat_str = f"{res.category}" if res.category else "null"
        exp_str = f"{expected_cat}" if expected_cat else "null"

        print(f"[{i:02d}/{len(TEST_CASES)}] {status} | \"{q}\"")
        print(f"      Category: {cat_str} (expected: {exp_str}) | Step 1: {res.step1_latency_seconds:.2f}s | Step 2: {res.step2_latency_seconds:.2f}s | Total: {res.total_latency_seconds:.2f}s")
        if res.filters:
            print(f"      Filters : {[[f.feature, f.operator, f.values] for f in res.filters]}")
        if res.residual:
            print(f"      Residual: \"{res.residual}\"")
        if feature_eval:
            failed_feats = [f"{m[0]}: {m[2]}" for m in feature_eval if not m[1]]
            if failed_feats:
                print(f"      Issues  : {', '.join(failed_feats)}")
        print("-" * 80)

        results.append({
            "test_case": tc,
            "parsed": res.to_dict(),
            "cat_match": cat_match,
            "feature_eval": feature_eval,
        })

    avg_step1 = total_time_step1 / len(TEST_CASES)
    avg_step2 = total_time_step2 / sum(1 for r in results if r["parsed"]["category"] is not None)
    avg_total = (total_time_step1 + total_time_step2) / len(TEST_CASES)

    summary = {
        "total_queries": len(TEST_CASES),
        "category_accuracy": category_correct / len(TEST_CASES),
        "avg_step1_latency": round(avg_step1, 3),
        "avg_step2_latency": round(avg_step2, 3),
        "avg_total_latency": round(avg_total, 3),
        "total_cost_usd": round(total_cost, 6),
    }

    print("\nBENCHMARK SUMMARY:")
    print(f"Total queries      : {summary['total_queries']}")
    print(f"Category accuracy  : {summary['category_accuracy']*100:.1f}% ({category_correct}/{len(TEST_CASES)})")
    print(f"Avg Step 1 Latency : {summary['avg_step1_latency']}s")
    print(f"Avg Step 2 Latency : {summary['avg_step2_latency']}s")
    print(f"Avg Total Latency  : {summary['avg_total_latency']}s")
    print(f"Total Cost         : ${summary['total_cost_usd']:.4f}")

    out_file = ROOT / "poc/feature_extraction/results/benchmark_eval.json"
    out_file.write_text(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False))
    print(f"\nDetailed report saved to {out_file}")


if __name__ == "__main__":
    run_benchmark()
