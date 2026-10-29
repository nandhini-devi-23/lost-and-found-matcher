# Judgment Framework

| Tool part | What the system does | What can go wrong? | Human judgment / checkpoint |
|---|---|---|---|
| Input reports | Reads the ID, date and report text from CSV | Typo, wrong date, duplicate or incomplete report | Help desk checks invalid or unclear submissions |
| LLM extraction | Extracts item, colour, brand, place and short summary | May omit a fact or hallucinate a brand/place | Python fact-checks each field against report text |
| JSON validation | Checks allowed item/colour values and required fields | Invalid JSON or unexpected values | Fallback is used; staff review ambiguous reports |
| Match rules | Rejects different items, >30-day gaps, and explicit colour/brand clashes | Missing facts may make a match less distinctive | Staff reviews the reason and the original reports |
| Scoring and sorting | Adds colour +2, brand +2, place +1; shows all scores above zero | Score can look more certain than it is | Scores are leads only; no automatic ownership decision |
| Double-claim flag | Lists found IDs suggested for multiple lost IDs | Two people may describe similar items | Help desk investigates all candidate claims fairly |
| Output files | Writes candidates, no-match, unclaimed, and summary files | Staff may overlook a candidate or misread a CSV | Staff reviews all candidates, not only the top result |
| **Handing over an item** | **The software does not hand over an item** | A wrong claimant could collect an item | **Mandatory human checkpoint: help desk asks the claimant for a detail that is not in either report, then decides whether to release the item.** |

## Three questions for judgment

1. **What is automated?** Repetitive extraction, validation, pairwise comparison, scoring, sorting, and report generation.
2. **What must be reviewed?** Ambiguous extraction, all suggested pairs, double claims, and possible false positives.
3. **Who makes the final decision?** The campus help desk, after checking a new detail not contained in either report. The model must never be treated as proof of ownership.
