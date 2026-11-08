"""
Query parser of the search UI (--parser llm, the default): the reviewed parses of the query extraction benchmark,
looked up by query text, for all 22 categories and without API calls. Only queries of the dev split are answered from the benchmark;
a test query or any other query goes to the LLM parser (llm_parser.py, three categories, paid calls).

The split is the one of the ranking evaluation: dev or test by a hash of the query and its category, so test
queries stay unseen while the ranking is tuned. The benchmark is read from query_extraction/queries in the working
tree, or from BENCHMARK_REF while it is not merged.
"""
import csv
import hashlib
import io
import json
import subprocess
import sys

import common
from parser_adapter import normalize_text

BENCHMARK_DIR = "query_extraction/queries"
BENCHMARK_REF = "origin/user_queries"
NO_CATEGORY = "No category"


def _git(*args):
    return subprocess.run(["git", "-C", str(common.REPO), *args], capture_output=True, text=True, check=True).stdout


def benchmark_files():
    """-> [(path, csv text)] from the working tree, or from BENCHMARK_REF."""
    local = common.REPO / BENCHMARK_DIR
    if local.is_dir():
        return [(p.relative_to(common.REPO).as_posix(), p.read_text(encoding="utf-8")) for p in sorted(local.rglob("*.csv"))]
    paths = _git("ls-tree", "-r", "--name-only", BENCHMARK_REF, "--", BENCHMARK_DIR).splitlines()
    return [(p, _git("show", f"{BENCHMARK_REF}:{p}")) for p in paths if p.endswith(".csv")]


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
    sys.path.insert(0, str(common.REPO / "poc/scripts"))
    from query_parser import SUPPORTED_CATEGORIES
    return list(SUPPORTED_CATEGORIES)


ROWS = load(benchmark_files())
EXAMPLES = examples(ROWS)
CATEGORIES = _fallback_categories()
parse = BenchmarkParser(ROWS, _llm)
NAME = (f"benchmark ({sum(r['split'] == 'dev' for r in ROWS)} dev queries of {len(ROWS)}), "
        f"other queries: query_parser.py")
