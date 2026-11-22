# Lost and Found Matcher

AI-powered campus lost-and-found matching tool.

## Files
- `lost.csv`, `found.csv`: input reports
- `system_prompt.txt`: LLM extraction instructions
- `lost_and_found_matcher.py`: extraction, validation, matching and output generation
- `outputs/`: four generated reports
- `eval_harness.py`: basic scoring-rule checks

## Setup
1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your own Gemini API key.
4. Run: `python lost_and_found_matcher.py`

The project specification requires at least 10 lost and 10 found reports.
The starter CSV files contain the 7 + 7 reports visible in the supplied screenshot.
Add at least 3 more reports to each CSV before final submission.

Never commit `.env` or publish your API key.
