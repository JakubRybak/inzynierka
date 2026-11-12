"""
Builds the phrase bank (ranking_data/phrase_bank.jsonl): residual phrases with their kind, negation, English version and
concepts, labelled offline by Gemini.

    python search_ui/offline/phrase_bank.py              # plan and cost, no API calls
    python search_ui/offline/phrase_bank.py --execute    # paid calls, then the bank

Phrases: the current bank, the soft phrases of real ESCI clothing queries and of the category lists
(concept_candidates.py), and Polish and Spanish versions of the most frequent ones. A phrase found in a residual of a
benchmark test query is left out, so the test split stays unseen. Calls are logged in search_ui/data/phrase_bank/; a rerun
labels only what is missing for the current prompt and concept list.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import bank  # noqa: E402
import benchmark_parser  # noqa: E402
import common  # noqa: E402
import concept_candidates  # noqa: E402
import concepts  # noqa: E402
import product_colors  # noqa: E402
import vertex  # noqa: E402

OUT = common.DATA / "phrase_bank"
OLD_BANK = OUT / "phrase_bank_v1.jsonl"
LABELS = OUT / "labels.jsonl"
VARIANTS = OUT / "variants.jsonl"
SHADES = OUT / "shades.jsonl"
KINDS = ["detail", "shade", "occasion", "style", "season", "size_or_audience", "other"]
BATCH = 50
TOP_FOR_VARIANTS = 150

LABEL = """You label phrases that shoppers add to clothing searches in an online store selling designer clothing. Each
phrase is the part of a search query that no product filter covers. For every phrase return:

- kind: detail (a garment detail, trim, material, texture, print, motif, graphic, slogan or construction), shade
  (a specific colour shade), occasion (an event, place or activity), style (a look, aesthetic or vibe), season (a
  season, weather or comfort need, such as warm, breathable or rainy days), size_or_audience (sizes, fit groups,
  body types, children or other audiences), other (anything else, such as themes, characters, bands, licences,
  brands, prices, quantities or gifts);
- negated: true when the phrase says what the product must not have;
- english: the phrase in English without any negation word; translate it literally when it is in another language,
  otherwise keep its words;
- concepts: the ids of at most two concepts from the list below that the phrase asks for, or an empty list. Choose
  a concept only when ranking the products by how well they fit it would put first what the shopper wants:
  - a phrase that names a concrete print, motif, graphic, character, band, slogan or brand gets no concept, even
    when it hints at a style or an era (for example "80s lip print", "harry potter", "skull graphic");
  - an activity, event or place that no concept fits gets none (for example "golf", "fishing trip"); do not
    stretch a concept to cover it;
  - a synonym or a paraphrase of a concept gets that concept (for example "breathable" or "lightweight" -> hot
    weather, "thermal" or "extra warm" -> winter, "comfy" -> cozy, "waterproof" or "for rainy days" -> rainy
    weather);
  - a negated phrase keeps the concept it negates (for example "not too revealing" -> sexy, negated).

Concepts:
{concepts}

Return one result per input phrase, in the input order, with the phrase copied exactly."""

VARIANT = """For every English phrase below, which shoppers add to clothing searches, write how Polish shoppers would
type it in a search bar (up to two versions) and how Spanish shoppers would (one version). Lower case, the way people
really type, with or without diacritics. Return one result per input phrase, in the input order."""


def version(text):
    return hashlib.sha256((text + vertex.MODEL).encode()).hexdigest()[:12]


def logged(path, v):
    return [r for r in map(json.loads, path.open(encoding="utf-8")) if r.get("prompt_version") == v
            and "error" not in r] if path.exists() else []


def test_phrases():
    return {bank.normalize_phrase(p) for r in benchmark_parser.ROWS if r["split"] == "test" for p in r["residual"]}


def sources():
    """-> Counter of phrase -> number of queries (or lists) it comes from. A phrase of a benchmark test query is kept
    only when ESCI queries or the category lists have it too: the older bank mixed benchmark phrases in."""
    old = Counter({r["phrase"]: r["queries"] for r in bank.load_rows(OLD_BANK if OLD_BANK.exists() else bank.BANK)})
    new = Counter()
    for r in concept_candidates.logged(concept_candidates.EXTRACT_LOG, concept_candidates.prompt_version(
            concept_candidates.EXTRACT)):
        for item in r["items"]:
            new.update({bank.normalize_phrase(x["phrase"]) for x in item["phrases"]})
    for r in concept_candidates.logged(concept_candidates.GENERATE_LOG, concept_candidates.prompt_version(
            concept_candidates.GENERATE)):
        new.update(bank.normalize_phrase(v) for values in r["lists"].values() for v in values)
    test = test_phrases()
    counts = Counter({p: n for p, n in old.items() if p not in test}) + new
    counts.pop("", None)
    return counts


def concept_lines():
    return "\n".join(f"- {c['id']}: {c['name']} ({c['type']})" + (f" – {c['description']}" if c.get("description") else "")
                     for c in yaml.safe_load(concepts.CONCEPTS_YAML.read_text(encoding="utf-8")))


def label_body(phrases, system, ids):
    item = {"type": "OBJECT", "required": ["phrase", "kind", "negated", "english", "concepts"],
            "properties": {"phrase": {"type": "STRING"}, "kind": {"type": "STRING", "enum": KINDS},
                           "negated": {"type": "BOOLEAN"}, "english": {"type": "STRING"},
                           "concepts": {"type": "ARRAY", "items": {"type": "STRING", "enum": ids}}}}
    text = "Phrases:\n" + "\n".join(f"{i + 1}. {p}" for i, p in enumerate(phrases))
    return {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 16384, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "required": ["results"],
                                                    "properties": {"results": {"type": "ARRAY", "items": item}}},
                                 "thinkingConfig": {"thinkingLevel": "MEDIUM"}}}


def variant_body(phrases):
    item = {"type": "OBJECT", "required": ["phrase", "polish", "spanish"],
            "properties": {"phrase": {"type": "STRING"}, "polish": {"type": "ARRAY", "items": {"type": "STRING"}},
                           "spanish": {"type": "ARRAY", "items": {"type": "STRING"}}}}
    text = "Phrases:\n" + "\n".join(f"{i + 1}. {p}" for i, p in enumerate(phrases))
    return {"systemInstruction": {"parts": [{"text": VARIANT}]}, "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 16384, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "required": ["results"],
                                                    "properties": {"results": {"type": "ARRAY", "items": item}}},
                                 "thinkingConfig": {"thinkingLevel": "MINIMAL"}}}


SHADE = """You give the colour that each phrase of a shopping query names. The phrases are colours and shades in English,
Polish or Spanish, for example "dusty rose", "brudny róż", "azul claro", "emerald green", "light", "ciemny".
- hex: the colour as it would look on a garment, as #RRGGBB; null when the phrase names no hue, only a lightness
  ("light", "dark", "jasny").
- family: the basic colour family of that colour, one of: {families}; null when hex is null.
- lightness: "light" when the phrase asks for a lighter shade than the plain colour ("light blue", "pale", "pastel",
  "jasny"), "dark" when it asks for a darker one ("dark green", "deep purple", "ciemny"), otherwise "none".
Answer for every phrase, in the given order."""


def shade_body(phrases, system):
    item = {"type": "OBJECT", "required": ["phrase", "hex", "family", "lightness"],
            "properties": {"phrase": {"type": "STRING"}, "hex": {"type": "STRING", "nullable": True},
                           "family": {"type": "STRING", "enum": product_colors.FAMILIES, "nullable": True},
                           "lightness": {"type": "STRING", "enum": ["light", "dark", "none"]}}}
    text = "Phrases:\n" + "\n".join(f"{i + 1}. {p}" for i, p in enumerate(phrases))
    return {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 8192, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "required": ["results"],
                                                    "properties": {"results": {"type": "ARRAY", "items": item}}},
                                 "thinkingConfig": {"thinkingLevel": "MINIMAL"}}}


def shades(phrases, execute, budget, spent):
    """Target colour of every shade phrase: hex, family and lightness, for the colour ranking."""
    system = SHADE.format(families=", ".join(product_colors.FAMILIES))
    v = version(system)
    done = {x["phrase"]: x for r in logged(SHADES, v) for x in r["items"]}
    todo = [p for p in phrases if p not in done]
    tasks = [dict(id=f"shades-{k}", phrases=todo[k:k + BATCH]) for k in range(0, len(todo), BATCH)]
    costs = [vertex.estimate(len(system) + 30 * len(t["phrases"]), 40 * len(t["phrases"])) for t in tasks]
    print(f"shades: {len(todo)} phrases in {len(tasks)} calls (up to ${sum(costs):.3f})")
    if execute and tasks:
        def work(task, client):
            response = client(shade_body(task["phrases"], system))
            results = json.loads(vertex.response_text(response))["results"]
            if len(results) != len(task["phrases"]):
                raise ValueError(f"{len(results)} results for {len(task['phrases'])} phrases")
            items = []
            for phrase, r in zip(task["phrases"], results):
                hex_value = r.get("hex") if r.get("hex") and product_colors.HEX.fullmatch(r["hex"]) else None
                items.append(dict(phrase=phrase, hex=hex_value and hex_value.upper(),
                                  family=r.get("family") if hex_value else None, lightness=r["lightness"]))
            return dict(id=task["id"], prompt_version=v, items=items, usage=response.get("usageMetadata", {}), at=stamp())
        vertex.run(tasks, costs, work, SHADES, budget, spent)
        done = {x["phrase"]: x for r in logged(SHADES, v) for x in r["items"]}
    return done


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def variants(counts, execute, budget):
    """Polish and Spanish versions of the most frequent English soft phrases (new phrases only)."""
    v = version(VARIANT)
    soft = [p for p, _ in counts.most_common() if p.isascii()][:TOP_FOR_VARIANTS]
    done = {x["phrase"] for r in logged(VARIANTS, v) for x in r["items"]}
    todo = [p for p in soft if p not in done]
    tasks = [dict(id=f"variants-{k}", phrases=todo[k:k + BATCH]) for k in range(0, len(todo), BATCH)]
    costs = [vertex.estimate(len(VARIANT) + 30 * len(t["phrases"]), 25 * len(t["phrases"])) for t in tasks]
    print(f"variants: {len(todo)} phrases in {len(tasks)} calls (up to ${sum(costs):.3f})")
    if execute and tasks:
        def work(task, client):
            response = client(variant_body(task["phrases"]))
            results = json.loads(vertex.response_text(response))["results"]
            items = [dict(phrase=p, polish=r.get("polish", [])[:2], spanish=r.get("spanish", [])[:1])
                     for p, r in zip(task["phrases"], results)]
            return dict(id=task["id"], prompt_version=v, items=items, usage=response.get("usageMetadata", {}), at=stamp())
        vertex.run(tasks, costs, work, VARIANTS, budget, vertex.spent_in(LABELS) + vertex.spent_in(VARIANTS))
    out = Counter()
    for r in logged(VARIANTS, v):
        for x in r["items"]:
            out.update(bank.normalize_phrase(t) for t in x["polish"] + x["spanish"])
    out.pop("", None)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--budget-usd", type=float, default=0.5, help="total for both logs, earlier runs included")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    counts = sources()
    test = test_phrases()
    counts.update({p: n for p, n in variants(counts, args.execute, args.budget_usd).items()
                   if p not in counts and p not in test})
    system = LABEL.format(concepts=concept_lines())
    ids = [c["id"] for c in concepts.load_list()]
    v = version(system)
    done = {x["phrase"]: x for r in logged(LABELS, v) for x in r["items"]}
    todo = [p for p in sorted(counts) if p not in done]
    tasks = [dict(id=f"labels-{k}", phrases=todo[k:k + BATCH]) for k in range(0, len(todo), BATCH)]
    costs = [vertex.estimate(len(system) + 30 * len(t["phrases"]), 60 * len(t["phrases"]) + 2000) for t in tasks]
    print(f"{len(counts)} phrases, {len(todo)} to label in {len(tasks)} calls (up to ${sum(costs):.2f}); "
          f"prompt version {v}; spent so far ${vertex.spent_in(LABELS) + vertex.spent_in(VARIANTS):.4f}")
    if args.execute and tasks:
        def work(task, client):
            response = client(label_body(task["phrases"], system, ids))
            results = json.loads(vertex.response_text(response))["results"]
            if len(results) != len(task["phrases"]):
                raise ValueError(f"{len(results)} results for {len(task['phrases'])} phrases")
            items = [dict(phrase=p, kind=r["kind"], negated=r["negated"], english=" ".join(r["english"].lower().split()),
                          concepts=list(dict.fromkeys(r["concepts"]))[:2]) for p, r in zip(task["phrases"], results)]
            return dict(id=task["id"], prompt_version=v, items=items, usage=response.get("usageMetadata", {}), at=stamp())
        vertex.run(tasks, costs, work, LABELS, args.budget_usd, vertex.spent_in(LABELS) + vertex.spent_in(VARIANTS))
        done = {x["phrase"]: x for r in logged(LABELS, v) for x in r["items"]}
    spent = vertex.spent_in(LABELS) + vertex.spent_in(VARIANTS) + vertex.spent_in(SHADES)
    colours = shades(sorted(p for p in counts if p in done and done[p]["kind"] == "shade"), args.execute,
                     args.budget_usd, spent)
    if args.execute:
        if not OLD_BANK.exists():
            OLD_BANK.write_bytes(bank.BANK.read_bytes())
        rows = [dict(done[p], queries=n) for p, n in sorted(counts.items()) if p in done]
        with bank.BANK.open("w", encoding="utf-8") as out:
            for r in rows:
                row = {k: r[k] for k in ("phrase", "kind", "negated", "english", "concepts", "queries")}
                if r["kind"] == "shade" and r["phrase"] in colours:
                    row |= {k: colours[r["phrase"]][k] for k in ("hex", "family", "lightness")}
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
        kinds = Counter(r["kind"] for r in rows)
        print(f"{len(rows)} phrases -> {bank.BANK}; kinds {dict(kinds)}; with a concept {sum(bool(r['concepts']) for r in rows)}")


if __name__ == "__main__":
    main()
