# Lost and Found Matcher

A console-based Python project for a college campus help desk. It extracts details from lost/found reports, compares every lost report against every found report, and suggests candidates with reasons and a simple score.

**Important:** this tool never decides ownership. The help desk must ask a claimant for a detail that is not written in either report before handing over an item.

## Features

- Reads `data/lost.csv` and `data/found.csv` (12 sample reports in each file).
- Uses an LLM API for one extraction call per report when `OPENAI_API_KEY` is configured.
- Includes a local fallback so the project can run without an API key.
- Checks facts against the report text; never intentionally accepts an unmentioned colour, brand, or place.
- Applies hard mismatch, item, date, and scoring rules in Python.
- Flags found items suggested for more than one lost report.
- Writes `matches.csv`, `no_match.csv`, `unclaimed.csv`, and `summary.txt`.
- Includes an evaluation harness and three red-team cases.

## Project structure

```text
lost-and-found-matcher/
├── app.py
├── README.md
├── SPECIFICATION.md
├── SYSTEM_PROMPT.txt
├── JUDGMENT_FRAMEWORK.md
├── COST_AND_LATENCY.md
├── AI_DECISION_JOURNAL.md
├── REFLECTION.md
├── requirements.txt
├── .gitignore
├── .env.example
├── data/
│   ├── lost.csv
│   └── found.csv
├── tests/
│   ├── eval_harness.py
│   └── red_team_tests.md
└── outputs/
    ├── matches.csv
    ├── no_match.csv
    ├── unclaimed.csv
    └── summary.txt
```

## Requirements

- Python 3.10 or newer
- Optional: an API key for an OpenAI-compatible API. Without a key, the program uses a local rule-based fallback.

## Run on Windows

1. Download and extract this project ZIP.
2. Open the extracted `lost-and-found-matcher` folder.
3. Open Command Prompt or PowerShell in that folder.
4. Optional API setup:
   - Install dependencies: `py -m pip install -r requirements.txt`
   - Set the key only in your terminal session:
     - PowerShell: `$env:OPENAI_API_KEY="your-key-here"`
     - Command Prompt: `set OPENAI_API_KEY=your-key-here`
   - Optional model override: set `OPENAI_MODEL`.
5. Run: `py app.py`
6. Check the four files in `outputs/`.

Do not put a real key in `app.py`, README, CSV files, screenshots, or GitHub. `.gitignore` excludes `.env` files. Do not upload personal data.

## Run the tests

From the project folder:

```bash
py tests/eval_harness.py
```

The harness tests the scoring rules using controlled extracted fields. It does not require an API key and prints PASS/FAIL for five pairs. The three red-team cases are documented in `tests/red_team_tests.md`.

## GitHub upload — manual website method

The accompanying upload-manual PDF says to create a repository on GitHub, leave the README, `.gitignore`, and license options unchecked for the first upload, then use **Add file → Upload files**, drag in the project files, enter a commit message, and click **Commit changes**. Review the repository afterward to verify the files. Follow your class instructions if your faculty specifies a different setup.

### Three meaningful commits

The manual browser upload method can still have three commits. Do this in order, using the same repository:

1. **`Add project specification and sample input data`** — upload `SPECIFICATION.md`, `data/lost.csv`, and `data/found.csv`.
2. **`Add matcher implementation and safety checks`** — upload `app.py`, `requirements.txt`, `.gitignore`, and `.env.example`.
3. **`Add tests, documentation, and sample outputs`** — upload `README.md`, `SYSTEM_PROMPT.txt`, `tests/`, `JUDGMENT_FRAMEWORK.md`, `COST_AND_LATENCY.md`, `AI_DECISION_JOURNAL.md`, `REFLECTION.md`, and `outputs/`.

If your instructor expects the entire project uploaded at once, do that first and then make two additional meaningful commits by editing or adding useful documentation/tests. Do not create empty commits merely to meet the count.

## Output definitions

- `matches.csv`: all suggested pairs, sorted best score first, including the score and reasons.
- `no_match.csv`: lost reports with no suggested pair.
- `unclaimed.csv`: found reports with no suggested pair.
- `summary.txt`: run counts and any found item suggested for more than one lost report.

## Limitations

- The fallback is deliberately simple and recognises only common items, colours, brands, and campus places. It may miss synonyms.
- The extraction prompt and API response are validated, but LLM output can still be imperfect. Review results.
- Sample reports are fictional.
- A match is a lead for a human help desk, never proof of ownership.
