"""
What a ranking adds after the parser returns, and how many embedding calls a query makes. Every dev query goes
through server.SearchEngine.search with its benchmark parse.

    python experiments/ranking/latency.py                    # computation only: embeddings from the disk cache
    python experiments/ranking/latency.py --live             # paid, about $0.01 per ranking: real embedding calls

Without --live the embeddings come from memory, so the time is the computation of the ranking alone, and the calls
are counted, not made (a text missing from the cache is embedded once). With --live every call goes to the
embedding API, as in the search UI, and the parser is replaced by a wait of the length the real parser took on a
query of the parser benchmark (results/benchmark_250_seed42.json, both of its steps), before the benchmark parse is
returned. The time after the parser is the total time of the search minus that wait: filtering, waiting for
embeddings that are not ready yet, the ranking and building the result list.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time
import zlib

import numpy as np

import evaluate as ev
from evaluate import benchmark_parser, common, parser_adapter

PARSER_RUN = common.REPO / "experiments/query_parsing/benchmark/results/benchmark_250_seed42.json"
RANKINGS = ("combined", "hybrid", "sentences")


class Counter:
    """An embedder that counts its calls. memory: {text: vector} to serve repeated texts from, or None."""

    def __init__(self, embedder, memory=None):
        self.embedder, self.memory, self.calls, self.lock = embedder, memory, 0, threading.Lock()

    def __call__(self, text):
        with self.lock:
            self.calls += 1
        if self.memory is None:
            return self.embedder(text)
        if text not in self.memory:
            self.memory[text] = self.embedder(text)
        return self.memory[text]


def parser_waits():
    """Seconds the real parser took on each query of the parser benchmark: the category step plus the filter step."""
    run = json.loads(PARSER_RUN.read_text(encoding="utf-8"))
    return [q["stages"]["category"]["latency_seconds"] + q["stages"]["full_qwen"]["latency_seconds"]
            for q in run["queries"] if "full_qwen" in q["stages"]]


def percentiles(values):
    return " / ".join(f"{np.percentile(values, p):.0f}" for p in (50, 95)) + f" / {max(values):.0f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--live", action="store_true", help="real embedding calls and a simulated parser wait (paid)")
    ap.add_argument("--rankings", nargs="+", default=list(RANKINGS))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=1, help="queries in parallel; more than 1 distorts the times")
    args = ap.parse_args()
    _, meta = common.load_index()
    real = common.QueryEmbedder(meta["model"], meta["dim"])
    counter = Counter(real) if args.live else Counter(ev.CachedEmbedder(real, ev.EMBEDDINGS), {})
    waits = parser_waits()
    rows = benchmark_parser.BenchmarkParser(benchmark_parser.ROWS)

    def parse(q):
        if args.live:
            time.sleep(waits[zlib.crc32(q.encode()) % len(waits)])
        return rows(q)

    engine = ev.engines(counter, parser_adapter.Parser("benchmark parses", parse))["bank"]
    queries = ev.load_queries(engine.products, engine.vocabulary, "dev")[:args.limit]
    if not args.live:
        for q in queries:  # fill the memory, so that the timed pass makes no cache lookups
            for r in args.rankings:
                engine.search(q["query"], r)
    print(f"{len(queries)} dev queries, {'live embedding calls, simulated parser wait' if args.live else 'embeddings from memory'}"
          + (f"; parser wait p50 {np.percentile(waits, 50):.2f} s, p95 {np.percentile(waits, 95):.2f} s" if args.live else ""))
    print("\n| ranking | after the parser, ms: p50 / p95 / max | ranking step, ms: p50 / p95 / max | embedding calls per "
          "query: p50 / p95 / max | queries with a call after the parser |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for r in args.rankings:
        time.sleep(1.0)  # let the unused prefetch calls of earlier queries finish before the count
        after, step, calls, late = [], [], [], []

        def one(q):
            before = counter.calls
            out = engine.search(q["query"], r)
            t = out["timings"]
            return (t["total_ms"] - t["parsing_ms"], t["ranking_ms"], counter.calls - before,
                    t.get("phrase_embeddings_late", 0))

        with ThreadPoolExecutor(args.workers) as pool:
            for a, s, c, n in pool.map(one, queries):
                after.append(a), step.append(s), calls.append(c), late.append(n)
        print(f"| {r} | {percentiles(after)} | {percentiles(step)} | {percentiles(calls)} | "
              f"{sum(n > 0 for n in late)} ({np.mean([n > 0 for n in late]):.0%}) |")


if __name__ == "__main__":
    main()
