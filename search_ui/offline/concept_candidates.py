"""
Candidates for new concepts: occasions, styles and season, weather or comfort needs that shoppers ask for and that
the concept list does not cover yet.

    python search_ui/offline/concept_candidates.py              # plan and cost, no API calls
    python search_ui/offline/concept_candidates.py --execute    # paid calls, then the table
    python search_ui/offline/concept_candidates.py --analyze    # only the table, from the logs

Sources: real Amazon ESCI clothing queries, from which Gemini extracts the soft phrases, and lists of typical needs
that Gemini writes for each of the 22 categories. The queries are those of ranking_data/esci_clothing_queries.csv
(footwear, accessories, underwear and swimwear left out) and the English and Spanish queries of the full ESCI file
(data/raw/amazon_esci, when present) that name one of the 22 categories by the keywords of
dataset_preparation/amazon_esci/export_query_candidates.py; every query of the benchmark test split is left out.
Every query gets the category its keywords name. The phrases are embedded, compared with the
concept names and grouped; search_ui/data/concept_candidates/candidates.csv and candidates.md list the groups with their
counts, examples and nearest existing concept.
"""
import argparse
from collections import Counter, defaultdict
import re
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import benchmark_parser  # noqa: E402
import common  # noqa: E402
import concepts  # noqa: E402
import facets  # noqa: E402
from parser_adapter import normalize_text  # noqa: E402
import vertex  # noqa: E402

ESCI = common.SEARCH_UI / "ranking_data/esci_clothing_queries.csv"
ESCI_FULL = common.REPO / "data/raw/amazon_esci/shopping_queries_dataset_examples.parquet"
sys.path.insert(0, str(common.REPO / "dataset_preparation/amazon_esci"))
from export_query_candidates import KEYWORDS  # noqa: E402

KEYWORDS = {**KEYWORDS,
            "dresses": r"\b(?:dress(?:es)?|sukienk[aięi]|vestidos?)\b(?![ -]?(?:shoes?|shirts?|socks|pants|boots?|sandals?))",
            "skirts": r"\b(?:skirts?|spódnic[aeęy]|faldas?)\b",
            "cardigans": r"\b(?:cardigans?|kardigan|rebecas?|chaquetas? de punto)\b",
            "hoodies-and-zipups": r"\b(?:hoodies?|hooded sweatshirts?|zip[ -]?ups?|bluz[aey] z kapturem|sudaderas? con capucha)\b",
            "knit-sweaters": r"\b(?:sweaters?|jumpers?|pullovers?|knitwear|swetr[ey]?|jerséis?|suéteres?)\b",
            "sweatshirts": r"\b(?:sweat[ -]?shirts?|crewnecks?|bluz[aey]|sudaderas?)\b"}
OUT = common.DATA / "concept_candidates"
EXTRACT_LOG = OUT / "extract.jsonl"
GENERATE_LOG = OUT / "generate.jsonl"
GARMENTS = ("Tops & Shirts", "Pants & Bottoms", "Dresses", "Outerwear", "General Apparel")
BATCH = 100
KINDS = ["occasion", "style", "season"]
COVERED = 0.80
GROUP = 0.82

EXTRACT = """You read shopping queries for clothing. For every query list its soft requirements of three kinds:
- occasion: an event, place or activity, e.g. "for a wedding", "hiking", "for the office", "4th of july";
- style: a look, aesthetic or vibe, e.g. "boho", "y2k", "preppy", "coastal grandmother";
- season: a season, weather or comfort need, e.g. "for summer", "warm", "breathable", "rainy days".
Leave out product types, colours, materials, prints, sizes, brands, fits, lengths, prices and other concrete
attributes. Copy each phrase from the query in lower case. A query without soft requirements gets an empty list.
Return one result per query, in the input order, with its number."""

GENERATE = """List what shoppers ask for when they buy {category} beyond the product's concrete attributes (colour,
material, size, length, fit): 20 occasions or activities, 15 styles or aesthetics and 10 season, weather or comfort
needs. Short phrases in English, the way people type them in a search bar."""


def prompt_version(text):
    return hashlib.sha256((text + vertex.MODEL).encode()).hexdigest()[:12]


# more specific garments first: "t-shirt dress" is a dress, "jean shorts" are shorts, "bomber jacket" a bomber
ORDER = ["dresses", "trench-coats", "bombers", "cargo-pants", "shorts", "hoodies-and-zipups", "cardigans", "polos",
         "tank-tops", "bodysuits", "blouses", "t-shirts", "shirts", "skirts", "sweatshirts", "knit-sweaters", "vests",
         "classic-coats", "jackets", "jeans", "sweatpants-and-lounge-pants", "trousers"]
ALIASES = {"tank-tops": "tank-tops-and-camisoles"}


def category_of(query, names):
    """The category whose keywords the query contains, the most specific garment first, or None."""
    for key in ORDER:
        if re.search(KEYWORDS[key], query, flags=re.IGNORECASE):
            return names[ALIASES.get(key, key)]
    return None


def esci_queries():
    """-> {query: dict(locale, category)} without benchmark test queries."""
    names = {facets._schema_name(c): c for c in facets.category_schemas()}
    d = pd.read_csv(ESCI)
    d = d[d["Category"].map(lambda c: any(g in str(c) for g in GARMENTS))]
    found = {q.strip().lower(): "us" for q in d["Query_Text"].astype(str)}
    if ESCI_FULL.exists():
        full = pd.read_parquet(ESCI_FULL, columns=["query", "query_id", "product_locale"]).drop_duplicates("query_id")
        full = full[full["product_locale"].isin(["us", "es"])]
        for q, locale in zip(full["query"].astype(str), full["product_locale"]):
            q = q.strip().lower()
            if q not in found and category_of(q, names):
                found[q] = locale
    test = {normalize_text(r["query"]) for r in benchmark_parser.ROWS if r["split"] == "test"}
    return {q: dict(locale=locale, category=category_of(q, names)) for q, locale in found.items()
            if normalize_text(q) not in test}


def logged(path, version):
    out = []
    if path.exists():
        out = [r for r in map(json.loads, path.open(encoding="utf-8")) if r.get("prompt_version") == version
               and "error" not in r]
    return out


def extract_body(queries):
    item = {"type": "OBJECT", "required": ["phrase", "kind"],
            "properties": {"phrase": {"type": "STRING"}, "kind": {"type": "STRING", "enum": KINDS}}}
    schema = {"type": "OBJECT", "required": ["results"], "properties": {"results": {"type": "ARRAY", "items": {
        "type": "OBJECT", "required": ["n", "phrases"],
        "properties": {"n": {"type": "INTEGER"}, "phrases": {"type": "ARRAY", "items": item}}}}}}
    text = "Queries:\n" + "\n".join(f"{i + 1}. {q}" for i, q in enumerate(queries))
    return {"systemInstruction": {"parts": [{"text": EXTRACT}]}, "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 16384, "responseMimeType": "application/json",
                                 "responseSchema": schema, "thinkingConfig": {"thinkingLevel": "MINIMAL"}}}


def generate_body(category):
    lists = {k: {"type": "ARRAY", "items": {"type": "STRING"}} for k in KINDS}
    return {"contents": [{"role": "user", "parts": [{"text": GENERATE.format(category=category)}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 4096, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "required": KINDS, "properties": lists},
                                 "thinkingConfig": {"thinkingLevel": "MINIMAL"}}}


def call(execute, budget):
    queries = esci_queries()
    categories = sorted(facets.category_schemas())
    ev, gv = prompt_version(EXTRACT), prompt_version(GENERATE)
    done = {item["query"] for r in logged(EXTRACT_LOG, ev) for item in r["items"]}
    done_categories = {r["id"] for r in logged(GENERATE_LOG, gv)}
    todo = [q for q in queries if q not in done]
    first = len(logged(EXTRACT_LOG, ev))
    batches = [dict(id=f"batch-{first + k // BATCH}", queries=todo[k:k + BATCH]) for k in range(0, len(todo), BATCH)]
    cats = [dict(id=c) for c in categories if c not in done_categories]
    costs_e = [vertex.estimate(len(EXTRACT) + 30 * len(b["queries"]), 12 * len(b["queries"]) + 200) for b in batches]
    costs_g = [vertex.estimate(len(GENERATE) + 40, 700) for _ in cats]
    spent = vertex.spent_in(EXTRACT_LOG) + vertex.spent_in(GENERATE_LOG)
    print(f"{len(queries)} ESCI queries, {len(todo)} not extracted yet -> {len(batches)} calls (up to ${sum(costs_e):.2f}); "
          f"{len(cats)} category lists (up to ${sum(costs_g):.2f}); spent so far ${spent:.4f}")
    if not execute:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")

    def extract(task, client):
        response = client(extract_body(task["queries"]))
        results = {r["n"]: r["phrases"] for r in json.loads(vertex.response_text(response))["results"]}
        items = [dict(query=q, phrases=results.get(i + 1, [])) for i, q in enumerate(task["queries"])]
        return dict(id=task["id"], prompt_version=ev, items=items, usage=response.get("usageMetadata", {}), at=stamp())

    def generate(task, client):
        response = client(generate_body(task["id"]))
        return dict(id=task["id"], prompt_version=gv, lists=json.loads(vertex.response_text(response)),
                    usage=response.get("usageMetadata", {}), at=stamp())

    vertex.run(batches, costs_e, extract, EXTRACT_LOG, budget, spent)
    vertex.run(cats, costs_g, generate, GENERATE_LOG, budget, vertex.spent_in(EXTRACT_LOG))


def analyze():
    phrases = defaultdict(lambda: dict(esci=0, kinds=Counter(), queries=[], categories=set()))
    for r in logged(EXTRACT_LOG, prompt_version(EXTRACT)):
        for item in r["items"]:
            for x in item["phrases"]:
                p = phrases[" ".join(x["phrase"].lower().split())]
                p["esci"] += 1
                p["kinds"][x["kind"]] += 1
                p["queries"].append(item["query"])
    for r in logged(GENERATE_LOG, prompt_version(GENERATE)):
        for kind, values in r["lists"].items():
            for v in values:
                p = phrases[" ".join(v.lower().split())]
                p["kinds"][kind] += 1
                p["categories"].add(r["id"])
    phrases.pop("", None)
    names = list(phrases)
    meta = json.loads((common.DATA / common.META).read_text(encoding="utf-8"))
    embedder = common.QueryEmbedder(meta["model"], meta["dim"])
    vectors = common.embed_texts(names, [common.query_text(n) for n in names], embedder, OUT / "phrase_embeddings.npz")
    stored = np.load(OUT / "phrase_embeddings.npz")
    V = stored["vectors"]
    rows = pd.read_parquet(common.DATA / concepts.FILE)
    E = common.normalize(np.stack([np.asarray(e, np.float32) for e in rows["embedding"]]))
    near = V @ E.T
    best, best_sim = near.argmax(axis=1), near.max(axis=1)
    weight = np.array([phrases[n]["esci"] + len(phrases[n]["categories"]) for n in names])
    left, groups = set(np.flatnonzero(best_sim < COVERED)), []
    S = V @ V.T
    for i in np.argsort(-weight):
        if i not in left:
            continue
        members = [j for j in np.argsort(-weight) if j in left and S[i, j] >= GROUP]
        left -= set(members)
        groups.append(members)
    out = []
    for members in groups:
        kinds = sum((phrases[names[j]]["kinds"] for j in members), Counter())
        out.append(dict(phrase=names[members[0]], kind=kinds.most_common(1)[0][0],
                        esci_queries=sum(phrases[names[j]]["esci"] for j in members),
                        categories=len(set().union(*(phrases[names[j]]["categories"] for j in members))),
                        nearest_concept=rows["name"][best[members[0]]], similarity=round(float(best_sim[members[0]]), 2),
                        phrases=" | ".join(names[j] for j in members[:8]),
                        example=next((q for j in members for q in phrases[names[j]]["queries"]), "")))
    table = pd.DataFrame(out).sort_values(["esci_queries", "categories"], ascending=False)
    table.to_csv(OUT / "candidates.csv", index=False)
    covered = Counter(rows["name"][best[i]] for i in range(len(names)) if best_sim[i] >= COVERED)
    lines = ["# Concept candidates", "", f"{len(names)} phrases; {sum(covered.values())} close to an existing concept "
             f"(similarity >= {COVERED}), the rest in {len(table)} groups.", "",
             "Existing concepts by phrases close to them: " + ", ".join(f"{k} {v}" for k, v in covered.most_common()), "",
             "| group | kind | ESCI queries | categories listing it | nearest concept | phrases |",
             "| --- | --- | ---: | ---: | --- | --- |"]
    lines += [f"| {r.phrase} | {r.kind} | {r.esci_queries} | {r.categories} | {r.nearest_concept} {r.similarity} | "
              f"{r.phrases} |" for r in table.head(80).itertuples()]
    (OUT / "candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4]))
    print(f"-> {OUT / 'candidates.md'}, {OUT / 'candidates.csv'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--execute", action="store_true", help="make the paid calls")
    ap.add_argument("--analyze", action="store_true", help="only build the table from the logs")
    ap.add_argument("--budget-usd", type=float, default=0.5, help="total for both logs, earlier runs included")
    args = ap.parse_args()
    if not args.analyze:
        call(args.execute, args.budget_usd)
    if args.execute or args.analyze:
        analyze()


if __name__ == "__main__":
    main()
