# Price prompt check

Model: `gemini-3.5-flash-lite`, configured thinking `NONE`, global Vertex endpoint, structured output enabled. 15 live requests: 12 feature queries and 3 category queries. No automatic retries.

Raw outputs and token usage: [price_prompts_20261027T121653Z.json](price_prompts_20261027T121653Z.json).

## Results

All 12 feature queries returned the expected hard filters. All 3 category queries returned the expected category. All live responses conformed to the response schemas. The 60 few-shot outputs also passed offline schema checks.

| Query | Returned price conditions |
| --- | --- |
| black cotton tee below 175 dollars | `< 175` |
| black cotton tee below 175 euros | `< 175` |
| black cotton tee below 175 PLN | `< 175` |
| sukienka do 399,99 zl | `<= 399.99` |
| dress costing at least 75 euros | `>= 75` |
| tank top costing more than 40 PLN | `> 40` |
| camisole priced at exactly 89.50 dollars | `= 89.5` |
| dress priced between 110 and 230 euros | `>= 110 AND <= 230` |
| tee above 70 but below 180 PLN | `> 70 AND < 180` |
| 100% cotton T-shirt size 42 | No price filter; Cotton extracted; size retained in residual |
| cheap tank top around 80 euros | No price filter; approximate price retained in residual |
| blue dress below 275 dollars for a wedding | `< 275`; Blue extracted; wedding retained in residual |

One residual defect: the vague-price query returned `cheap tank top around 80 euros`, repeating the selected category. The expected hard filters were correct, but this is not a perfectly correct full response. The automated checks verify required residual content for this case and do not detect this duplication; their 15/15 result must not be interpreted as perfect semantic accuracy.

Estimated cost: **USD 0.023099**, using the existing runner's assumed rates of USD 0.30 per million input tokens and USD 2.50 per million output tokens. This is an estimate from usage, not a billing reconciliation.

## Scope

The checks exercise raw model responses with the prompts and response schemas. Application normalization, search conditions, and UI price filtering are pending. The existing normalizer drops price clauses because it expects `values`, while price uses `value`.

These are small targeted checks, not an accuracy estimate over real user traffic.

Reproduce offline checks with `.venv/bin/python poc/query_parsing/check_price_prompts.py`. Adding `--live` makes 15 paid API requests and writes a timestamped report.
