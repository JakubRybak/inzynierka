"""
Benchmark parser (--parser benchmark_parser:parse): the reviewed parses of the query extraction benchmark
(experiments/query_parsing/benchmark/queries), looked up by query text, for all 22 categories and without API calls. Only
queries of the dev split are answered from the benchmark; a test query or any other query goes to the LLM parser
(llm_parser.py, paid calls).

The split is the one of the ranking evaluation: dev or test by a hash of the query and its category, so test
queries stay unseen while the ranking is tuned.
"""
import csv
import hashlib
import io
import json
import sys

import common
from parser_adapter import normalize_text

BENCHMARK = common.REPO / "experiments/query_parsing/benchmark/queries"
NO_CATEGORY = "No category"


def benchmark_files(folder=BENCHMARK):
    """-> [(path, csv text)] of the benchmark files."""
    return [(p.relative_to(common.REPO).as_posix(), p.read_text(encoding="utf-8")) for p in sorted(folder.rglob("*.csv"))]


def query_id(query, category):
    return hashlib.sha256(f"{query}|{category}".encode()).hexdigest()[:12]


def split(qid):
    return "dev" if int(hashlib.sha256(f"split|{qid}".encode()).hexdigest(), 16) % 2 == 0 else "test"


def load(files):
    """-> [{id, query, split, category, filters, residual}]; a repeated query and category is kept once."""
    rows = {}
    for path, text in files:
        for row in csv.DictReader(io.StringIO(text)):
            parse = json.loads(row["expected_output"])
            qid = query_id(row["query"], parse["category"])
            rows.setdefault(qid, dict(id=qid, query=row["query"], split=split(qid), category=parse["category"],
                                      filters=parse["filters"], residual=parse["residual"]))
    return list(rows.values())


def examples(rows):
    """Dev queries per category in order of preference: those with a residual first, then a fixed pseudo-random
    order. The server shows the first ones that find products."""
    groups = {}
    for r in sorted(rows, key=lambda r: (not r["residual"], r["id"])):
        if r["split"] == "dev":
            groups.setdefault(r["category"] or NO_CATEGORY, []).append(r["query"])
    return {k: groups[k] for k in sorted(groups, key=lambda k: (k == NO_CATEGORY, k))}


class BenchmarkParser:
    def __init__(self, rows, fallback=None):
        self.dev, self.test = {}, set()
        for r in rows:
            if r["split"] == "dev":
                self.dev.setdefault(normalize_text(r["query"]), r)
            else:
                self.test.add(normalize_text(r["query"]))
        self.fallback = fallback

    def __call__(self, query):
        key = normalize_text(query)
        r = self.dev.get(key)
        if r:
            return dict(query=query, category=r["category"], filters=r["filters"], residual=r["residual"],
                        _source="benchmark (dev)")
        if self.fallback is None:
            return dict(query=query, category=None, filters=[], residual=[], _source="not in the benchmark")
        raw = self.fallback(query)
        return raw | {"_source": "LLM parser (benchmark test query)" if key in self.test else "LLM parser"}


def _llm(query):
    import llm_parser
    return llm_parser.parse(query)


def _fallback_categories():
    sys.path.insert(0, str(common.REPO))
    from query_parsing.core.catalog import load_query_catalog
    return list(load_query_catalog())


ROWS = load(benchmark_files())
EXAMPLES = examples(ROWS)
CATEGORIES = _fallback_categories()
parse = BenchmarkParser(ROWS, _llm)
NAME = (f"benchmark ({sum(r['split'] == 'dev' for r in ROWS)} dev queries of {len(ROWS)}), "
        f"other queries: llm_parser.py")
