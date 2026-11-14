# Spending ledger of the ranking task

`BUDGET_USD = 20` for the whole task, all paid APIs together. Amounts in USD. **Spent: 5.32.**

- The judge log (`data/judgments.jsonl`) held $2.7829 from earlier work when the task started; that is not part of
  this budget.
- "Actual" is the difference of a call log before and after a run. The logs of `judge.py` and `ceiling.py` count
  the reserved estimate for a failed call, so these amounts are slightly too high: 14 failed judge calls and 21
  failed reranker calls (HTTP 500 or timeouts, all repeated with success) add about $0.28.
- Embeddings are priced at $0.20 per million tokens, 4 characters per token
  (`feature_extraction/config/extraction.yaml`); the API does not return a cost.

| Date | What | Estimate | Actual | Running total |
| --- | --- | ---: | ---: | ---: |
| 2026-11-13 | Embeddings: rerun of all 26 rankings on dev with the current code (1,226 calls, cached in `data/embeddings.sqlite`) | 0.05 | 0.002 | 0.002 |
| 2026-11-13 | Judge: 1,104 new top-10 pairs of the rerun rankings (196 calls) | ≤ 1.23 | 0.468 | 0.470 |
| 2026-11-13 | Judge: the ungraded products in the top 20 of `hybrid`, for the ceiling (1,146 pairs, 237 calls) | ≤ 1.44 | 0.518 | 0.988 |
| 2026-11-13 | Ceiling: LLM reranker of the top 20 of `hybrid`, 313 queries (`ceiling.py`; 21 failed calls repeated) | ≤ 2.64 | 1.979 | 2.967 |
| 2026-11-13 | Judge: new top-10 products of the first experiments, hybrid weights and soft thresholds (307 pairs, 125 calls) | ≤ 0.70 | 0.174 | 3.141 |
| 2026-11-13 | Embeddings: 30,994 unique names and description sentences of the products, all 3,072 dimensions | 0.06 | 0.060 | 3.201 |
| 2026-11-13 | Judge: new top-10 products of the first sentence variants (1,490 pairs, 206 calls) | ≤ 1.38 | 0.697 | 3.898 |
| 2026-11-13 | Judge: seven later rounds for fitted, lean and whole-query variants (814 pairs, 437 calls) | ≤ 2.39 | 0.525 | 4.423 |
| 2026-11-13 | Embeddings: phrases, plain-format phrases and query spans for the experiments and the offline latency run (3,853 calls) | 0.02 | 0.008 | 4.431 |
| 2026-11-13 | Second judge: `anthropic/claude-haiku-5.5` through OpenRouter, 7,602 pairs of 313 queries (`judge2.py`; 8 answers could not be read and were repeated, 7 of them logged without their cost, about $0.007) | 0.20 | 0.344 | 4.775 |
| 2026-11-14 | Embeddings: live latency run, three rankings, 313 queries each, not cached (about 8,100 calls) | 0.02 | 0.016 | 4.791 |
| 2026-11-14 | Embeddings: 25 sentences that changed when HTML tags were dropped from the descriptions | 0.001 | 0.000 | 4.791 |
| 2026-11-14 | Judge: the last new top-10 products after the refit (7 pairs, 7 calls) | ≤ 0.04 | 0.007 | 4.798 |
| 2026-11-14 | Second judge: 6 new pairs | 0.001 | 0.001 | 4.799 |
| 2026-11-14 | Jev 1.14 through OpenRouter: second stage for 313 queries, two text variants, and 70 queries of the held-out bank (`rerank.py`, 696 calls) | 0.27 | 0.237 | 5.036 |
| 2026-11-14 | Judge: new top-10 products of the two-stage rankings (373 pairs, 188 calls) | ≤ 1.04 | 0.227 | 5.263 |
| 2026-11-14 | Second judge: 650 new pairs of the two-stage rankings (235 calls) | 0.10 | 0.053 | 5.316 |

OpenRouter in total: $0.63 (second judge $0.40, Jev $0.24). The rest is Google Cloud.

By service before the last three rows: Gemini judge $2.39 (4,874 new graded pairs), LLM reranker $1.98, second judge $0.35, embeddings $0.09.
