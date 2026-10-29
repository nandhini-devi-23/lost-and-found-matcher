# Cost and Latency Note

## Number of API calls
The implementation calls the LLM once for each valid report, not once for every possible pair. For `L` lost reports and `F` found reports, a run uses approximately `L + F` calls when the API is available. With the sample files (12 lost + 12 found), that is **24 extraction calls**. Python then compares up to `L × F = 144` pairs locally.

If the API key is absent, the program uses its local fallback and makes **0 API calls**.

## Latency
Planning estimate only: allow roughly 1–5 seconds per extraction call depending on model, network, rate limits, and response size. Calls currently run sequentially, so 24 calls could take approximately 24–120 seconds plus startup and file I/O. Actual latency must be measured during the showcase; it is not guaranteed.

## Cost
The exact cost depends on the chosen model, input/output tokens, and the provider's current pricing. No fixed currency estimate is claimed here because pricing and token usage can change. To estimate a real run:
1. Record the actual input and output tokens from the API response/provider dashboard.
2. Multiply token counts by the model's current published input/output rates.
3. Add the costs for all valid reports in the day.

The offline fallback costs no API usage. If the class requires a numerical cost-per-day figure, record the model, date, observed token counts, and price source used for that estimate before submission.
