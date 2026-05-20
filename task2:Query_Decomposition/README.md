# Query Decomposition Pipeline

This module decomposes natural-language SQL questions into a strict 5-part structure:

1. `Intent`
2. `Tables`
3. `Columns`
4. `Filters`
5. `Joins`

It uses Gemini (`gemini-2.5-flash`) with schema context, retry logic, and rate-limit throttling.

## What This Script Does

`query_decomposition.py`:
- loads `GEMINI_API_KEY` from the repository root `.env`,
- reads questions from `SQL_QUESTIONS - sql_questions_only.csv` (first column),
- calls Gemini for each question,
- normalizes output into exactly five labeled lines,
- writes results to `task2_decomposed_answers.csv`,
- captures API errors into output rows instead of crashing.

## Files

- `query_decomposition.py`: main decomposition script
- `SQL_QUESTIONS - sql_questions_only.csv`: input questions
- `decomposed.csv`: sample/reference decomposition output

## Prerequisites

- Python 3.10+
- Gemini API key
- Required packages:
  - `google-genai`
  - `python-dotenv`

Install dependencies (from repository root or your active environment):

```bash
pip install google-genai python-dotenv
```

## Environment Setup

The script explicitly loads environment variables from:

- `../.env` (repository root)

Add your key in root `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

## Run

From repository root:

```bash
python "task2:Query_Decomposition/query_decomposition.py"
```

Or from inside `task2:Query_Decomposition/`:

```bash
python query_decomposition.py
```

## Input and Output

Input CSV:
- `SQL_QUESTIONS - sql_questions_only.csv` (header + question text in first column)

Fallback input (used only if primary file is missing):
- `question_only.csv`

Output CSV:
- `task2_decomposed_answers.csv`

Output columns:
- `question_no`
- `question`
- `decomposition`
- `raw_json_response`

## Reliability Features

- Exponential backoff retries (up to 5 attempts) for transient API failures.
- Fixed 6-second delay between requests to reduce free-tier rate-limit errors.
- Best-effort normalization if model output is noisy.
- Per-row error capture in CSV when a question fails after retries.

## Notes

- The script is decomposition-only; it does not generate or execute SQL.
- Schema context is embedded directly in `query_decomposition.py` (`SCHEMA_CONTEXT`).
