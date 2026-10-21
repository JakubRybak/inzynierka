"""Reproducible, deliberately overlapping keyword audit of the clothing taxonomy.

Reads textual HDF5 columns only. Never labels products for the production index.
Run from the repository: .venv/bin/python products_new/scripts/audit_taxonomy_keywords.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import h5py

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "products_new"
TAXONOMY = ROOT / "categories_and_features/categories_and_features.md"
RULE_FILES = [
    BASE / "scripts/taxonomy_audit_common_rules.json",
    BASE / "scripts/taxonomy_audit_specific_rules.json",
]
OUT = BASE / "reports"
SOURCE_PAIRS = {
    "T-shirts": [("TOPS", "T-SHIRTS")],
    "Polos": [("TOPS", "POLOS")],
    "Tank tops & Camisoles": [("TOPS", "TANK TOPS"), ("TOPS", "TANK TOPS & CAMISOLES")],
    "Bodysuits": [("TOPS", "BODYSUITS")],
    "Shirts": [("SHIRTS", "SHIRTS"), ("TOPS", "SHIRTS")],
    "Blouses": [("TOPS", "BLOUSES")],
    "Knit Sweaters": [("SWEATERS", "CREWNECKS"), ("SWEATERS", "V-NECKS"), ("SWEATERS", "TURTLENECKS")],
    "Sweatshirts": [("SWEATERS", "SWEATSHIRTS")],
    "Hoodies & Zipups": [("SWEATERS", "HOODIES & ZIPUPS")],
    "Cardigans": [("SWEATERS", "CARDIGANS")],
    "Trousers": [("PANTS", "TROUSERS"), ("PANTS", "LEATHER PANTS")],
    "Cargo Pants": [("PANTS", "CARGO PANTS")],
    "Sweatpants & Lounge Pants": [("PANTS", "SWEATPANTS"), ("PANTS", "LOUNGE PANTS")],
    "Jeans": [("JEANS", "JEANS")],
    "Shorts": [("SHORTS", "SHORTS")],
    "Skirts": [("SKIRTS", "SHORT SKIRTS"), ("SKIRTS", "MID LENGTH SKIRTS"), ("SKIRTS", "LONG SKIRTS")],
    "Dresses": [("DRESSES", "SHORT DRESSES"), ("DRESSES", "MID LENGTH DRESSES"), ("DRESSES", "LONG DRESSES")],
}
TEXT_FIELDS = ("input_name", "input_description", "input_composition", "input_gender", "input_department")
SOURCES = {
    "text": ("input_name", "input_description"),
    "composition": ("input_composition",),
    "gender": ("input_gender", "input_department"),
}


def normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[‐‑‒–—−]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def decode(value):
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)


def parse_taxonomy():
    result = {}
    department = category = None
    for line in TAXONOMY.read_text().splitlines():
        if line.startswith("## "):
            department = re.sub(r"^## \d+\.\s*", "", line).strip()
            category = None
        elif line.startswith("### "):
            category = line[4:].strip()
            if category == "Zasady" or department == "Jackets & Coats":
                category = None
            else:
                result[category] = {"department": department, "features": {}}
        elif category and line.startswith("- **`"):
            tokens = re.findall(r"`([^`]+)`", line)
            result[category]["features"][tokens[0]] = tokens[1:]
    if set(result) != set(SOURCE_PAIRS):
        raise ValueError(f"Category/source mapping mismatch: {set(result) ^ set(SOURCE_PAIRS)}")
    return result


def load_products():
    pair_target = {pair: target for target, pairs in SOURCE_PAIRS.items() for pair in pairs}
    products = {}
    all_ids = defaultdict(set)
    source_counts = defaultdict(set)
    files = []
    raw_selected_rows = Counter()
    for split in ("train", "validation"):
        path = BASE / "data/raw" / f"fashiongen_256_256_{split}.h5"
        with h5py.File(path, "r") as h5:
            names = ("input_productID", "input_category", "input_subcategory") + TEXT_FIELDS
            cols = {name: h5[name][:].reshape(-1) for name in names}
        files.append({
            "split": split, "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns,
            "image_rows": len(cols["input_productID"]),
        })
        for values in zip(*(cols[key] for key in names)):
            pid = int(values[0])
            all_ids[split].add(pid)
            pair = (decode(values[1]), decode(values[2]))
            source_counts[pair].add(pid)
            if pair not in pair_target:
                continue
            raw_selected_rows[split] += 1
            category = pair_target[pair]
            if pid not in products:
                products[pid] = {
                    "product_id": pid, "category": category, "splits": set(), "source_pairs": set(),
                    **{key: set() for key in TEXT_FIELDS},
                }
            product = products[pid]
            if category != product["category"]:
                raise ValueError(f"Product {pid} has conflicting target categories")
            product["splits"].add(split)
            product["source_pairs"].add(pair)
            for key, value in zip(TEXT_FIELDS, values[3:]):
                product[key].add(decode(value))
        del cols
    for product in products.values():
        for key in ("splits", "source_pairs") + TEXT_FIELDS:
            product[key] = sorted(product[key])
        product["texts"] = {
            source: [normalize(text) for field in fields for text in product[field] if text.strip()]
            for source, fields in SOURCES.items()
        }
    metadata = {
        "files": files,
        "all_unique_product_ids": len(set.union(*all_ids.values())),
        "unique_product_ids_by_split": {split: len(ids) for split, ids in all_ids.items()},
        "ids_in_both_splits": len(all_ids["train"] & all_ids["validation"]),
        "selected_unique_products": len(products),
        "selected_image_rows_by_split": dict(raw_selected_rows),
        "selected_ids_in_both_splits": sum(len(p["splits"]) > 1 for p in products.values()),
        "selected_metadata_variants": {
            field: sum(len(p[field]) > 1 for p in products.values()) for field in TEXT_FIELDS
        },
        "all_source_counts": [
            {"category": pair[0], "subcategory": pair[1], "products": len(ids)}
            for pair, ids in sorted(source_counts.items())
        ],
    }
    return sorted(products.values(), key=lambda p: p["product_id"]), metadata


def load_rules(taxonomy):
    features, overrides, other_policies = {}, {}, {}
    for path in RULE_FILES:
        data = json.loads(path.read_text())
        other_policies.update(data.get("other_from_excluded_values", {}))
        for feature, values in data["features"].items():
            if feature in features:
                raise ValueError(f"Duplicate feature rules: {feature}")
            features[feature] = values
        for category, category_rules in data.get("overrides", {}).items():
            for feature, values in category_rules.items():
                overrides.setdefault(category, {}).setdefault(feature, {}).update(values)
    resolved = {}
    for category, cat in taxonomy.items():
        resolved[category] = {}
        for feature, values in cat["features"].items():
            resolved[category][feature] = {}
            for value in values:
                rule = overrides.get(category, {}).get(feature, {}).get(value, features.get(feature, {}).get(value))
                if value == "Other" and feature in other_policies:
                    policy = other_policies[feature]
                    excluded = [name for name in features[feature] if name != "Other" and name not in values]
                    components = [features[feature][name] for name in excluded]
                    if policy.get("include_base"):
                        components.insert(0, features[feature]["Other"])
                    sources = {component.get("source", "text") for component in components}
                    if len(sources) > 1:
                        raise ValueError(f"Cannot combine different sources for {category}/{feature}/Other")
                    rule = {
                        "patterns": list(dict.fromkeys(pattern for component in components for pattern in component["patterns"])),
                        "keywords": "; ".join(component.get("keywords", "") for component in components) or "—",
                        "source": next(iter(sources), "text"),
                        "note": "Dodatnie wskazówki rozpoznanych konstrukcji poza bieżącą listą kategorii. "
                        + ("Przeniesione do Other: " + ", ".join(excluded) + ". " if excluded else "")
                        + "Nie jest to pełna klasa Other; brak trafienia nie daje Other.",
                        "grouped_values": excluded,
                    }
                if rule is None:
                    raise ValueError(f"Missing rule: {category}/{feature}/{value}")
                if rule.get("source", "text") not in SOURCES:
                    raise ValueError(f"Invalid source: {rule}")
                for pattern in rule["patterns"] + rule.get("strict_patterns", []):
                    re.compile(pattern, re.I)
                resolved[category][feature][value] = rule
    return resolved


def compile_patterns(patterns):
    return re.compile("|".join(f"(?:{p})" for p in patterns), re.I) if patterns else None


def count_matches(products, rule, pattern_key="patterns"):
    regex = compile_patterns(rule.get(pattern_key, []))
    if regex is None:
        return None, []
    matched_ids, examples = set(), []
    source = rule.get("source", "text")
    for product in products:
        matched = next(
            ((text, match) for text in product["texts"][source] if (match := regex.search(text))),
            None,
        )
        if matched is None:
            continue
        matched_ids.add(product["product_id"])
        if len(examples) < 3:
            text, match = matched
            examples.append({
                "product_id": product["product_id"],
                "name": product["input_name"][0], "matched": match.group(),
                "context": text[max(0, match.start() - 80):match.end() + 120],
            })
    return matched_ids, examples


def percentage(n, denominator):
    return round(100 * n / denominator, 6) if denominator else None


def audit(taxonomy, products, rules):
    groups = defaultdict(list)
    for product in products:
        groups[product["category"]].append(product)
    categories = {}
    for category, cat in taxonomy.items():
        group = groups[category]
        denominator = len(group)
        if denominator == 0:
            raise ValueError(f"Empty category: {category}")
        result = {
            "department": cat["department"], "products": denominator,
            "products_by_split": dict(Counter(split for p in group for split in p["splits"])),
            "source_pairs": [
                {"category": pair[0], "subcategory": pair[1],
                 "products": sum(list(pair) in [list(v) for v in p["source_pairs"]] for p in group)}
                for pair in SOURCE_PAIRS[category]
            ], "features": {},
        }
        for feature, values in cat["features"].items():
            rows, hit_counts = {}, Counter()
            for value in values:
                rule = rules[category][feature][value]
                ids, examples = count_matches(group, rule)
                count = len(ids) if ids is not None else None
                if ids is not None:
                    hit_counts.update(ids)
                row = {
                    "count": count, "percent": percentage(count, denominator) if count is not None else None,
                    "keywords": rule.get("keywords", ""), "note": rule.get("note", ""),
                    "source": rule.get("source", "text"), "patterns": rule["patterns"],
                    "examples": examples,
                }
                if "grouped_values" in rule:
                    row["grouped_values"] = rule["grouped_values"]
                if ids is not None:
                    row["count_by_split"] = dict(Counter(
                        split for p in group if p["product_id"] in ids for split in p["splits"]
                    ))
                if "strict_patterns" in rule:
                    strict_ids, strict_examples = count_matches(group, rule, "strict_patterns")
                    row.update({
                        "strict_count": len(strict_ids) if strict_ids is not None else None,
                        "strict_percent": percentage(len(strict_ids), denominator) if strict_ids is not None else None,
                        "strict_keywords": rule.get("strict_keywords", ""),
                        "strict_note": rule.get("strict_note", ""),
                        "strict_patterns": rule["strict_patterns"], "strict_examples": strict_examples,
                    })
                rows[value] = row
            result["features"][feature] = {
                "values": rows, "any_match": len(hit_counts),
                "no_match": denominator - len(hit_counts),
                "multiple_matches": sum(count > 1 for count in hit_counts.values()),
                "measurable_values": sum(row["count"] is not None for row in rows.values()),
            }
        categories[category] = result
        print(f"{category}: {denominator} products, {len(result['features'])} features", flush=True)
    return categories


def extra_signals(products):
    """Questions beyond the enums, useful for checking exclusions and blind spots."""
    checks = {
        "sleeve_three_quarter": (
            "Rękaw 3/4 (także tam, gdzie brak go w enumie)",
            r"\b(?:three[ -]quarter|3[ /-]4)(?:[ -]length)?[ -]sleeve",
        ),
        "sleeve_elbow": (
            "Rękaw do łokcia / half sleeve",
            r"\b(?:elbow(?:[ -]length)?[ -]sleeve|half[ -]sleeve|sleeve\w*(?:\s+\w+){0,3}\s+(?:to|at)\s+(?:the\s+)?elbow)",
        ),
        "denim": ("Denim (tkanina, osobno od składu)", r"\bdenim\b"),
        "lace": ("Koronka", r"\b(?:lace|lacy)\b"),
        "satin": ("Satyna", r"\bsatin\b"),
        "velvet": ("Aksamit / welur", r"\b(?:velvet|velour)\b"),
        "corduroy": ("Sztruks", r"\bcorduroy\b"),
        "graphic_logo": ("Grafika / logo", r"\b(?:graphic\w*|logo\w*|print(?:ed)? text|text print|slogan)\b"),
        "stretch": ("Stretch / elastyczność opisana wprost", r"\b(?:stretch\w*|elastic\w*)\b"),
        "loose_draped": ("Luźny / drapowany opis (w tym body)", r"\b(?:relaxed|loose|draped|blouson|oversized)\b"),
    }
    result = {}
    groups = defaultdict(list)
    for product in products:
        groups[product["category"]].append(product)
    for key, (label, pattern) in checks.items():
        result[key] = {"label": label, "pattern": pattern, "categories": {}}
        for category, group in groups.items():
            ids, examples = count_matches(group, {"patterns": [pattern], "source": "text"})
            result[key]["categories"][category] = {
                "count": len(ids), "percent": percentage(len(ids), len(group)), "examples": examples,
            }
    return result


def cell(value):
    return str(value).replace("|", r"\|").replace("\n", " ")


def pct(value):
    return "n/d" if value is None else f"{value:.2f}%".replace(".", ",")


def anchor(category):
    return re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")


def markdown_report(report):
    cats = report["categories"]
    md = [
        "# Audyt słów kluczowych: kategorie, cechy i wartości",
        "",
        f"Zakres: **wszystkie {len(cats)} kategorii poza Jackets & Coats**. "
        f"Łącznie **{report['metadata']['selected_unique_products']:,} unikalnych produktów** ".replace(",", " ")
        + "z `train` i `validation`.",
        "",
        "## Jak czytać wyniki",
        "",
        "- **Procent = produkty z co najmniej jednym trafieniem / wszystkie produkty danej kategorii.** "
        "Każdy `input_productID` liczy się raz, niezależnie od liczby zdjęć i liczby trafień.",
        "- To częstości **wzmianek i szerokich wskazówek w tekście**, nie gotowe etykiety produktów. "
        "Nie analizujemy zdjęć ani nie uruchamiamy LLM.",
        "- Kategorie wynikają z etykiet źródłowych. Cechy: `input_name` + `input_description`; "
        "`gender`: pola `input_gender` i `input_department`; materiały: `input_composition`. "
        "Nie dopisujemy wzmianki o cesze na podstawie samej nazwy podkategorii źródłowej.",
        "- Każdą wartość liczymy niezależnie. Trafienia mogą się nakładać, również w cechach single choice; "
        "sumy procentów mogą przekroczyć 100%. Nie stosujemy limitu dwóch kolorów ani priorytetów klasyfikacji.",
        "- **Brak trafienia nie oznacza `Other`, `Solid`, `Regular`, `Without Hood` ani braku cechy.** "
        "Wiersz „bez trafienia” jest osobną miarą pokrycia tekstu. "
        "`Other` ma wyłącznie dodatnie wskazówki dla części konstrukcji poza nazwanymi klasami; nie mierzy całej pozostałej grupy.",
        "- `0,00%` = reguła istnieje, ale niczego nie znalazła; **n/d** = brak sensownej reguły dodatniej. "
        "Oba wyniki nie dowodzą, że dana konstrukcja nie występuje. "
        "Szczególnie ostrożnie czytaj neutralne i domyślne wartości: `Regular`, `Standard`, `Clean`, "
        "`Solid`, `Full-Length`, `Open Hem`, `Pullover`, `Without Hood`.",
        "- **Materiały:** szeroka kolumna bazuje na obecnych grupowaniach w `materials_mapping.md`. "
        "Kolumna „konkretna nazwa” ogranicza się do nazw danego surowca i jego bliskich synonimów. "
        "Różnica pokazuje skutki grupowań, np. przypisania `polyurethane` do `Polyester`. "
        "Obie kolumny liczą wzmianki w całym składzie, także podszewce i wykończeniach; "
        "**nie ustalają głównej części ani procentowego udziału włókna**.",
        "- Szeroki słownik może łapać kolor guzika, nazwę wzoru, detale lub części produktu. "
        "Sama niska częstość w tekście nie wystarcza do usunięcia wartości. "
        "Najpierw porównaj pokrycie cechy, przykłady i użyteczność filtra.",
        "- Kolory są liczone bez rozstrzygania kontekstu: np. `khaki` trafia do `Green` i `Beige`, "
        "`navy blue` do `Navy` i `Blue`. `Multicolor` to jawne określenia wielobarwności i szeroki sygnał `tie-dye`; "
        "nie wyliczamy go z trzech trafień innych kolorów.",
        "- Pełne reguły, uwagi dla poszczególnych wartości i przykładowe trafienia z ID znajdują się w JSON-ie. "
        "Przyjęte grupowania składów obejmują szersze rodziny surowców w `Polyester`, `Viscose` i `Wool`, "
        "`hemp/ramie` w `Linen`, pióra w `Down`, imitacje skóry/futra. Kolumna „konkretna nazwa” zawęża te grupy, "
        "ale nadal jest tekstowym przybliżeniem (np. `rayon` bywa nazwą szerszej rodziny).",
        "",
        "[Pierwotny przegląd z perspektywy klienta](taxonomy_customer_review.md) przedstawia stan sprzed ostatnich zmian taksonomii. "
        "Poniższe tabele odpowiadają aktualnemu dokumentowi kategorii.",
        "",
        "## Zakres i liczebności",
        "",
        "| Dział | Kategoria | Train | Validation | Razem |",
        "| :--- | :--- | ---: | ---: | ---: |",
    ]
    for category, cat in cats.items():
        md.append(
            f"| {cat['department']} | [{category}](#{anchor(category)}) | "
            f"{cat['products_by_split'].get('train', 0)} | {cat['products_by_split'].get('validation', 0)} | {cat['products']} |"
        )
    md += [
        "",
        f"Produkty występujące w obu splitach w tym zakresie: **{report['metadata']['selected_ids_in_both_splits']}**. "
        "Przy wielu wariantach tekstu jednego produktu uwzględniamy trafienie w dowolnym wariancie.",
        "",
        "## Pokrycie najważniejszych cech",
        "",
        "Procent produktów z co najmniej jednym trafieniem dowolnej dopuszczalnej wartości. "
        "Niskie pokrycie oznacza, że słowa kluczowe słabo opisują rozkład tej cechy; „—” oznacza brak cechy w schemacie.",
        "",
        "| Kategoria | pattern | fit | length | neckline | sleeve_length | rise |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for category, cat in cats.items():
        coverage = [
            pct(percentage(cat["features"][key]["any_match"], cat["products"])) if key in cat["features"] else "—"
            for key in ("pattern", "fit", "length", "neckline", "sleeve_length", "rise")
        ]
        md.append(f"| {category} | " + " | ".join(coverage) + " |")
    for category, cat in cats.items():
        md += [
            "", f'<a id="{anchor(category)}"></a>', "", f"## {category}", "",
            f"**Dział:** {cat['department']}. **Mianownik każdej tabeli: {cat['products']} produktów.**",
            "",
            "Źródło: " + "; ".join(
                f"`{s['category']} / {s['subcategory']}` ({s['products']})" for s in cat["source_pairs"]
            ) + ".",
        ]
        for feature, stats in cat["features"].items():
            materials = feature == "main_composition"
            md += ["", f"### `{feature}`", ""]
            if materials:
                md += [
                    "| Wartość | Szeroko: liczba | Szeroko: % | Konkretna nazwa: liczba / % | Słowa i wskazówki (szeroko) |",
                    "| :--- | ---: | ---: | ---: | :--- |",
                ]
            else:
                md += [
                    "| Wartość | Produkty z trafieniem | % kategorii | Słowa i wskazówki |",
                    "| :--- | ---: | ---: | :--- |",
                ]
            notes = []
            for value, row in stats["values"].items():
                count = "n/d" if row["count"] is None else str(row["count"])
                columns = [f"`{value}`", count, pct(row["percent"])]
                if materials:
                    columns.append(f"{row.get('strict_count', 'n/d')} / {pct(row.get('strict_percent'))}")
                columns.append(cell(row["keywords"]))
                md.append("| " + " | ".join(columns) + " |")
                if row["note"] and feature not in {"gender", "colors", "main_composition", "pattern"}:
                    notes.append(f"`{value}`: {row['note']}")
            md += [
                "",
                f"**Co najmniej jedno trafienie:** {stats['any_match']} ({pct(percentage(stats['any_match'], cat['products']))}); "
                f"**bez trafienia:** {stats['no_match']} ({pct(percentage(stats['no_match'], cat['products']))}); "
                f"**trafienia ≥2 wartości:** {stats['multiple_matches']} ({pct(percentage(stats['multiple_matches'], cat['products']))}).",
            ]
            if notes:
                md += ["", "Uwagi: " + " ".join(notes)]
    md += [
        "", "## Dodatkowe sygnały do oceny zakresu", "",
        "To pomocnicze zliczenia poza zestawem enumów. Nie dodają cech do taksonomii. "
        "Nazwy tkanin liczymy w opisach niezależnie od składu surowcowego.",
        "",
        "| Kategoria | Rękaw 3/4 | Rękaw do łokcia / half | Denim | Koronka | Satyna | Aksamit / welur | Sztruks | Grafika / logo |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for category in cats:
        cells = []
        for key in ("sleeve_three_quarter", "sleeve_elbow", "denim", "lace", "satin", "velvet", "corduroy", "graphic_logo"):
            row = report["extra_signals"][key]["categories"][category]
            cells.append(f"{row['count']} / {pct(row['percent'])}")
        md.append(f"| {category} | " + " | ".join(cells) + " |")
    md += [
        "",
        "W tej tabeli `lace` może też opisywać sznurowanie, a `graphic/logo` ma celowo szeroki zakres; "
        "to wskazówki do review, nie etykiety docelowe.",
        "",
        "## Odtworzenie i kontrola",
        "",
        "```sh",
        ".venv/bin/python products_new/scripts/audit_taxonomy_keywords.py",
        "```",
        "",
        "- [Skrypt](../scripts/audit_taxonomy_keywords.py)",
        "- [Słownik cech wspólnych](../scripts/taxonomy_audit_common_rules.json)",
        "- [Słownik pozostałych cech i wyjątków kategorii](../scripts/taxonomy_audit_specific_rules.json)",
        "- [Wyniki JSON, regexy i przykładowe trafienia z ID produktów](taxonomy_keyword_audit.json)",
        "",
        f"Wygenerowano (UTC): {report['generated_at']}. "
        "JSON zawiera odciski SHA-256 taksonomii i słowników oraz metadane plików wejściowych.",
        "",
        "Kontrole: pełne pokrycie wszystkich kombinacji kategoria–cecha–wartość z dokumentu; "
        "liczenie raz na ID; brak Jackets & Coats; osobne braki trafień; "
        "każda liczba w przedziale 0…liczba produktów; zgodność liczebności źródeł i kategorii.",
        "",
    ]
    return "\n".join(md)


def validate(report, taxonomy):
    assert set(report["categories"]) == set(taxonomy)
    assert sum(cat["products"] for cat in report["categories"].values()) == report["metadata"]["selected_unique_products"]
    for category, cat in report["categories"].items():
        assert cat["department"] != "Jackets & Coats"
        assert sum(source["products"] for source in cat["source_pairs"]) == cat["products"]
        assert set(cat["features"]) == set(taxonomy[category]["features"])
        for feature, stats in cat["features"].items():
            assert list(stats["values"]) == taxonomy[category]["features"][feature]
            assert stats["any_match"] + stats["no_match"] == cat["products"]
            assert stats["multiple_matches"] <= stats["any_match"]
            for row in stats["values"].values():
                assert row["count"] is None or 0 <= row["count"] <= cat["products"]
                if row["count"] is not None:
                    assert row["percent"] == percentage(row["count"], cat["products"])
                    if report["metadata"]["selected_ids_in_both_splits"] == 0:
                        assert sum(row["count_by_split"].values()) == row["count"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", type=Path, help="Write selected text metadata to a temporary JSON for inspection.")
    args = parser.parse_args()
    taxonomy = parse_taxonomy()
    products, metadata = load_products()
    if args.prepare_only:
        args.prepare_only.write_text(json.dumps({"metadata": metadata, "products": products}, ensure_ascii=False))
        print(json.dumps({key: value for key, value in metadata.items() if key != "all_source_counts"}, ensure_ascii=False, indent=2))
        return
    rules = load_rules(taxonomy)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "All taxonomy categories except Jackets & Coats, train + validation, unique input_productID.",
        "metadata": metadata,
        "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [TAXONOMY] + RULE_FILES},
        "categories": audit(taxonomy, products, rules),
        "extra_signals": extra_signals(products),
    }
    validate(report, taxonomy)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "taxonomy_keyword_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (OUT / "taxonomy_keyword_audit.md").write_text(markdown_report(report))
    print(json.dumps({
        "products": len(products), "categories": len(report["categories"]),
        "feature_tables": sum(len(cat["features"]) for cat in report["categories"].values()),
        "value_rows": sum(len(stats["values"]) for cat in report["categories"].values() for stats in cat["features"].values()),
        "markdown": str(OUT / "taxonomy_keyword_audit.md"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
