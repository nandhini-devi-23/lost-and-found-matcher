# AI Decision Journal

| Decision | Choice made | Reason | Risk / check |
|---|---|---|---|
| Use an LLM for | Extracting item, colour, brand, place and summary once per report | Natural-language reports vary in wording | Validate every extracted fact against source text |
| Use Python for | Comparing all lost/found pairs and scoring them | Rules should be transparent and repeatable | Unit tests check hard mismatches and score levels |
| Prompt structure | Authority, Exemplar, Constraint, Rubric, Metadata | Matches the required five-role framework | Examples and allowed values are explicit |
| Handle missing facts | Store colour, brand or place as null | Avoid inventing evidence | Fallback also checks only written facts |
| Handle LLM/API failure | Use local extraction fallback | One bad reply should not crash the full run | Fallback is simple and may miss uncommon wording |
| Resolve double claims | Flag them, do not pick an owner | Similar reports can describe the same item | Help desk reviews all candidates |
| Release an item | Never automate ownership decision | A score cannot prove ownership | Ask for a detail absent from both reports |
| Protect credentials | Read key from environment; ignore `.env` | Prevent accidental public exposure | Review staged files before every commit |

## What I would check next
- Test additional synonyms and spelling mistakes.
- Measure actual latency and token costs for the selected model.
- Ask a faculty member to review the prompt, scoring, and human checkpoint.
- Check whether the help desk needs an audit log before using real reports.
