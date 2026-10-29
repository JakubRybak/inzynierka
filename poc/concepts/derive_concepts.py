"""
Step A: concept candidates from the residuals of real and synthetic queries.

    select      ESCI queries for the indexed categories      -> data/queries_esci.csv
    synthesize  queries with a soft part, written by Gemini  -> data/queries_synthetic.csv
    parse       both files through poc/scripts/query_parser.py -> data/parsed.jsonl
    report      residual phrases and clusters                -> data/residuals_report.md

synthesize, parse and the clusters in report call Vertex AI only with --execute. The report only suggests
candidates; concepts.yaml is written by hand.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import threading
import time

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "data"
sys.path.insert(0, str(REPO / "poc/scripts"))
from query_parser import (QueryParser, SUPPORTED_CATEGORIES, PROMPTS_DIR, SCHEMAS_DIR,  # noqa: E402
                          INPUT_RATE, OUTPUT_RATE)

ESCI = REPO / "poc/query_parsing/amazon_clothing_queries.csv"
ESCI_QUERIES = DATA / "queries_esci.csv"
SYNTHETIC_QUERIES = DATA / "queries_synthetic.csv"
PARSED = DATA / "parsed.jsonl"
REPORT = DATA / "residuals_report.md"
SYNTHETIC_PROMPT = HERE / "prompts/synthetic_queries.txt"

IN_SCOPE = re.compile(r"\bdress(es)?\b|\bt[- ]?shirts?\b|\btees?\b|\btanks?\b|\bcamis?\b|\bcamisoles?\b"
                      r"|\bhalters?\b|\b(crop|tube) tops?\b")
NOT_GARMENT = re.compile(r"\bdress (shoes?|shirts?|socks?|sox|pants?|boots?|watch(es)?|gloves?|belts?|suits?"
                         r"|slacks|up|sweaters?|clothes)\b")
GARMENT = re.compile(r"\b(t[- ]?shirts?|tee shirts?|tees?|tank tops?|tanks?|(crop |tube )?tops?|camisoles?|camis?"
                     r"|dress(es)?)\b", re.IGNORECASE)
THEMES = ("occasion", "style", "season")
STOPWORDS = set("a an the for with and or in on of to my me i that is it at from by as but be very so some "
                "any like can will this these not no without".split())
EMBEDDING_MODEL, EMBEDDING_DIM = "gemini-embedding-2", 3072


def key(q):
    return " ".join(str(q).casefold().split())


def call_cost(usage):
    return (usage.get("promptTokenCount", 0) * INPUT_RATE
            + (usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)) * OUTPUT_RATE)


def retry(f, attempts=4):
    for attempt in range(attempts):
        try:
            return f()
        except Exception as e:
            if attempt == attempts - 1 or not any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
                raise
            time.sleep(2 ** attempt + random.random())


def select(args):
    d = pd.read_csv(ESCI, dtype={"Query_ID": str})
    keep = d["Query_Text"].map(lambda q: bool(IN_SCOPE.search(q.lower())) and not NOT_GARMENT.search(q.lower()))
    out = pd.DataFrame({"query": d.loc[keep, "Query_Text"], "source": "esci", "query_id": d.loc[keep, "Query_ID"]})
    DATA.mkdir(exist_ok=True)
    out.to_csv(ESCI_QUERIES, index=False)
    print(f"{len(out)} of {len(d)} ESCI queries -> {ESCI_QUERIES.relative_to(REPO)}")


def synthesize(args):
    system = SYNTHETIC_PROMPT.read_text(encoding="utf-8")
    tasks = [(c, t) for c in SUPPORTED_CATEGORIES for t in THEMES]
    message = "Category: {}\nTheme: {}\nNumber of queries: {}"
    if not args.execute:
        print(system, message.format(*tasks[0], args.per_call), sep="\n")
        print(f"\n{len(tasks)} calls x {args.per_call} queries; add --execute to run them")
        return
    if SYNTHETIC_QUERIES.exists():
        raise SystemExit(f"{SYNTHETIC_QUERIES.relative_to(REPO)} exists; remove it to generate the queries again")
    parser = QueryParser()
    schema = {"type": "OBJECT", "required": ["queries"], "properties": {"queries": {
        "type": "ARRAY", "items": {"type": "STRING"}, "minItems": args.per_call, "maxItems": args.per_call}}}
    rows, seen, cost = [], set(), 0.0
    for category, theme in tasks:
        out, usage, _ = retry(lambda: parser._call_api(system, message.format(category, theme, args.per_call), schema))
        cost += call_cost(usage)
        for q in out["queries"]:
            if key(q) and key(q) not in seen:
                seen.add(key(q))
                rows.append(dict(query=q.strip(), source="synthetic", category=category, theme=theme))
        print(f"{category} / {theme}: {len(out['queries'])}", flush=True)
    DATA.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(SYNTHETIC_QUERIES, index=False)
    print(f"{len(rows)} queries -> {SYNTHETIC_QUERIES.relative_to(REPO)}, ${cost:.4f}")


def load_queries():
    frames = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in (ESCI_QUERIES, SYNTHETIC_QUERIES) if p.exists()]
    if not frames:
        raise SystemExit("no queries, run select (and synthesize) first")
    d = pd.concat(frames, ignore_index=True)
    d["key"] = d["query"].map(key)
    sources = d.groupby("key")["source"].agg(lambda s: sorted(set(s)))
    first = d.drop_duplicates("key")
    return [dict(query=q, sources=sources[k]) for q, k in zip(first["query"], first["key"])]


def read_parsed():
    if not PARSED.exists():
        return []
    return [json.loads(line) for line in PARSED.read_text(encoding="utf-8").splitlines() if line.strip()]


def latest(records):
    by_key = {}
    for r in records:
        if "error" not in r:
            by_key[key(r["query"])] = r
    return list(by_key.values())


def parser_fingerprint(parser):
    h = hashlib.sha256(f"{parser.model}|{parser.thinking}".encode())
    for p in sorted([*PROMPTS_DIR.glob("*.md"), *SCHEMAS_DIR.glob("*.json"), REPO / "poc/scripts/query_parser.py"]):
        h.update(p.name.encode() + p.read_bytes())
    return h.hexdigest()[:16]


def estimated_cost(parser):
    """Upper estimate for one query, 4 characters per token."""
    step2 = max(len(p) + len(json.dumps(s)) for p, s in zip(parser.feature_prompts.values(),
                                                            parser.feature_schemas.values()))
    chars = len(parser.category_system_instruction) + len(json.dumps(parser.category_schema)) + step2
    return chars / 4 * INPUT_RATE + 500 * OUTPUT_RATE


def parse(args):
    queries, done = load_queries(), read_parsed()
    parser = QueryParser()
    fingerprint = parser_fingerprint(parser)
    if any(r["parser_fingerprint"] != fingerprint for r in done):
        raise SystemExit(f"{PARSED.relative_to(REPO)} comes from another parser version; move it away first")
    parsed = {key(r["query"]) for r in latest(done)}
    todo = [q for q in queries if key(q["query"]) not in parsed]
    random.Random(0).shuffle(todo)
    todo = todo[:args.limit] if args.limit else todo
    spent, per_query = sum(r["cost_usd"] for r in done), estimated_cost(parser)
    print(f"{len(queries)} queries, {len(parsed)} parsed, {len(todo)} to parse now "
          f"(up to ${len(todo) * per_query:.2f}); spent so far ${spent:.4f}, budget ${args.budget_usd:.2f}")
    if not args.execute or not todo:
        if todo:
            print("add --execute to parse them")
        return
    parser.session
    lock, state = threading.Lock(), dict(spent=spent, reserved=0.0, done=0, skipped=0)

    def work(item, out):
        with lock:
            if state["spent"] + state["reserved"] + per_query > args.budget_usd:
                state["skipped"] += 1
                return
            state["reserved"] += per_query
        record = dict(query=item["query"], sources=item["sources"], parser_fingerprint=fingerprint,
                      parsed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        try:
            r = retry(lambda: parser.parse(item["query"]).to_dict())
            record.update(category=r["category"], filters=r["filters"], residual=r["residual"],
                          cost_usd=r["metadata"]["estimated_cost_usd"])
        except Exception as e:
            record.update(error=f"{type(e).__name__}: {str(e)[:300]}", cost_usd=per_query)
        with lock:
            state["reserved"] -= per_query
            state["spent"] += record["cost_usd"]
            state["done"] += 1
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            if "error" in record:
                print(f"error: {item['query']!r}: {record['error']}", flush=True)
            if state["done"] % 50 == 0:
                print(f"{state['done']}/{len(todo)}  ${state['spent']:.4f}", flush=True)

    pool = ThreadPoolExecutor(args.workers)
    try:
        with PARSED.open("a", encoding="utf-8") as out:
            for f in as_completed([pool.submit(work, q, out) for q in todo]):
                f.result()
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    pool.shutdown()
    errors = sum("error" in r for r in read_parsed()[len(done):])
    print(f"parsed {state['done'] - errors}, errors {errors}, skipped by the budget {state['skipped']}; "
          f"spent ${state['spent']:.4f}")


def words(text):
    return re.findall(r"[a-z0-9]+(?:['’-][a-z0-9]+)*", text.casefold())


def phrases(text, longest=3):
    w = words(text)
    return {" ".join(w[i:i + n]) for n in range(1, longest + 1) for i in range(len(w) - n + 1)
            if w[i] not in STOPWORDS and w[i + n - 1] not in STOPWORDS}


def source_label(r):
    return "+".join(r["sources"])


def core(residual):
    """Residual without the garment noun the parser sometimes leaves in it and without stopwords at the ends."""
    w = GARMENT.sub(" ", residual).split()
    while w and w[0].casefold() in STOPWORDS:
        w.pop(0)
    while w and w[-1].casefold() in STOPWORDS:
        w.pop()
    return " ".join(w)


def embed(texts, workers):
    sys.path.insert(0, str(REPO / "poc/search_ui"))
    from common import QueryEmbedder, normalize
    embedder = QueryEmbedder(EMBEDDING_MODEL, EMBEDDING_DIM)
    with ThreadPoolExecutor(workers) as pool:
        return normalize(np.stack(list(pool.map(embedder, texts))))


def clusters(residuals, vectors, distance):
    from sklearn.cluster import AgglomerativeClustering
    if len(residuals) < 2:
        return [list(range(len(residuals)))]
    labels = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                     distance_threshold=distance).fit_predict(vectors)
    groups = defaultdict(list)
    for i, label in enumerate(labels):
        groups[label].append(i)
    return list(groups.values())


def report(args):
    records = latest(read_parsed())
    if not records:
        raise SystemExit("nothing parsed yet, run parse first")
    in_scope = [r for r in records if r["category"]]
    with_residual = [r for r in in_scope if core(r["residual"])]
    garment_left = sum(bool(GARMENT.search(r["residual"])) for r in in_scope)
    by_residual = defaultdict(list)
    for r in with_residual:
        by_residual[key(core(r["residual"]))].append(r)
    sources = sorted({source_label(r) for r in records})
    lines = [
        "# Residuals → concept candidates", "",
        f"`derive_concepts.py report`, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, parser fingerprint "
        f"`{records[0]['parser_fingerprint']}`.", "",
        "Candidates only: `concepts.yaml` is written by hand. Leave out anything a hard filter covers and anything "
        "that cannot be judged from the product photos and description (e.g. “trendy this season”, "
        "“flattering for my body”).", "",
        f"In {garment_left} of {len(in_scope)} in-catalog queries the parser left the garment noun in the residual "
        "(rule 10 says it should not). Before counting and clustering the noun is removed, as are stopwords at the "
        "start and end (“for a wedding” → “wedding”); a residual with nothing else is counted as empty.", "",
        "## Queries", "",
        "| source | parsed | outside the catalog | empty residual | with residual |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for s in sources + ["all"]:
        rs = [r for r in records if s == "all" or source_label(r) == s]
        scoped = [r for r in rs if r["category"]]
        filled = sum(bool(core(r["residual"])) for r in scoped)
        lines.append(f"| {s} | {len(rs)} | {len(rs) - len(scoped)} | {len(scoped) - filled} | {filled} |")
    lines += ["", "| category | with residual |", "| --- | ---: |"]
    lines += [f"| {c} | {n} |" for c, n in Counter(r["category"] for r in with_residual).most_common()]

    counts = {s: Counter() for s in sources}
    for r in with_residual:
        counts[source_label(r)].update(phrases(core(r["residual"])))
    total = sum(counts.values(), Counter())
    lines += ["", f"## Phrases ({args.top_phrases} most frequent)", "",
              "Number of residuals containing the phrase (1–3 words, not starting or ending with a stopword).", "",
              "| phrase | all | " + " | ".join(sources) + " |", "| --- | ---: |" + " ---: |" * len(sources)]
    for p, n in total.most_common(args.top_phrases):
        lines.append(f"| {p} | {n} | " + " | ".join(str(counts[s][p]) for s in sources) + " |")

    lines += ["", "## Clusters", ""]
    if not args.execute:
        lines.append(f"Not computed: run `report --execute` (embeddings of {len(by_residual)} distinct residuals).")
    else:
        texts = list(by_residual)
        vectors = embed(texts, args.workers)
        groups = clusters(texts, vectors, args.distance)
        groups.sort(key=lambda g: -sum(len(by_residual[texts[i]]) for i in g))
        lines += [f"{EMBEDDING_MODEL} ({EMBEDDING_DIM} dims) on the residual text, agglomerative clustering, "
                  f"average linkage, cosine distance ≤ {args.distance}. Name = the most frequent residual, ties "
                  f"go to the one closest to the others. Clusters with fewer than {args.min_size} queries are listed at the end.", ""]
        small, number = [], 0
        for g in groups:
            rs = [r for i in g for r in by_residual[texts[i]]]
            if len(rs) < args.min_size:
                small.append(rs)
                continue
            centrality = dict(zip((texts[i] for i in g), (vectors[g] @ vectors[g].T).mean(axis=1)))
            name = max(centrality, key=lambda t: (len(by_residual[t]), centrality[t]))
            number += 1
            distinct = Counter(key(core(r["residual"])) for r in rs)
            more = len(distinct) - 10
            examples = sorted(rs, key=lambda r: (source_label(r), r["query"]))
            examples = [examples[i] for i in sorted(random.Random(0).sample(range(len(rs)), min(6, len(rs))))]
            lines += [f"### {number}. {name}", "",
                      f"{len(rs)} queries: " + ", ".join(f"{s} {n}" for s, n in Counter(map(source_label, rs)).most_common())
                      + "; " + ", ".join(f"{c} {n}" for c, n in Counter(r["category"] for r in rs).most_common()), "",
                      "Residuals: " + " · ".join(f"{v} ({n})" if n > 1 else v for v, n in distinct.most_common(10))
                      + (f" · … +{more}" if more > 0 else ""), ""]
            lines += [f"- {r['query']} → `{r['residual']}` ({source_label(r)})" for r in examples]
            lines.append("")
        if small:
            lines += ["### Outside the clusters", ""]
            lines += [f"- `{r['residual']}` – {r['query']} ({source_label(r)})"
                      for r in sorted((r for rs in small for r in rs), key=lambda r: key(core(r["residual"])))]
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"{len(records)} parsed, {len(with_residual)} with residual, {len(by_residual)} distinct "
          f"-> {REPORT.relative_to(REPO)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("select")
    s = sub.add_parser("synthesize")
    s.add_argument("--per-call", type=int, default=30, help="queries per (category, theme) call")
    s.add_argument("--execute", action="store_true")
    p = sub.add_parser("parse")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--budget-usd", type=float, default=1.0, help="total for data/parsed.jsonl, including earlier runs")
    p.add_argument("--limit", type=int, help="parse at most this many queries now")
    p.add_argument("--workers", type=int, default=8)
    r = sub.add_parser("report")
    r.add_argument("--execute", action="store_true", help="embed the residuals and cluster them")
    r.add_argument("--distance", type=float, default=0.25)
    r.add_argument("--min-size", type=int, default=3)
    r.add_argument("--top-phrases", type=int, default=60)
    r.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    dict(select=select, synthesize=synthesize, parse=parse, report=report)[args.command](args)


if __name__ == "__main__":
    main()
