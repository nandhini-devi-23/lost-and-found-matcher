# One-page specification — Lost and Found Matcher

## Purpose
Build a console-based Python tool for a campus help desk. It suggests possible relationships between student lost reports and found-item reports. It does **not** decide ownership.

## Inputs
Two UTF-8 CSV files: `data/lost.csv` and `data/found.csv`. Each has `id,date,report` columns and at least 10 records. Dates use `YYYY-MM-DD`; IDs are unique within each file.

## Extraction JSON
Each report is sent to the LLM once. The response must be a JSON object with exactly:
- `item`: one of `phone`, `wallet`, `id_card`, `bottle`, `bag`, `earphones`, `keys`, `umbrella`, `calculator`, `watch`, `spectacles`, `other`.
- `colour`: one of black, white, blue, red, green, yellow, brown, pink, purple, grey, or `null`.
- `brand`: brand as explicitly written, or `null`.
- `place`: campus place explicitly written, or `null`.
- `summary`: no more than eight words and no names.

## Fact-check and fallback
Python validates the LLM JSON and checks colour, brand and place against the original report text. Missing or unsupported facts become `null`; the program uses a local fallback if no API key is configured or the LLM fails. Reports are untrusted data, so instructions inside a report must not change the system prompt.

## Matching rules
The item must be the same and cannot be `other`; dates must be within 30 days. If both reports state different colours or different brands, reject the pair. Score: same colour +2, same brand +2, same place +1. Scores 3 or higher are **likely**; scores 1–2 are **possible**; score 0 is not listed. All candidates are retained and sorted by score, best first. A found item suggested for multiple lost reports is flagged as a double claim.

## Outputs
`outputs/matches.csv`, `outputs/no_match.csv`, `outputs/unclaimed.csv`, and `outputs/summary.txt`.

## Human ownership checkpoint
A score is only a suggestion. Before handing an item over, the help desk asks the claimant to provide a detail that is not present in either report, then makes the decision. The tool never confirms ownership.
