# Prompt-Chained Text-to-SQL Pipeline

This module implements a Text-to-SQL system that:
- accepts a natural language question,
- generates SQL through a prompt chain,
- validates SQL for read-only safety,
- executes it on PostgreSQL,
- retries once with LLM-based SQL repair if execution fails.

The UI is built with Streamlit and execution logs are persisted to `logs/query_logs.json`.

## Pipeline Flow

1. Decompose question into structured JSON (`decompose_query`)
2. Generate SQL from decomposition (`generate_sql`)
3. Validate SQL safety (`validate_sql`)
4. Execute SQL on PostgreSQL (`execute_query`)
5. If execution fails, repair SQL once (`fix_sql`) and retry

Core orchestration lives in `executor.py` (`run_pipeline`).

## Project Structure

- `streamlit_app.py`: Streamlit interface
- `executor.py`: end-to-end pipeline + retry + logging
- `sql_generator.py`: Gemini calls (decompose/generate/fix)
- `validator.py`: read-only SQL validation
- `database.py`: PostgreSQL connection + execution
- `evaluate.py`: small benchmark/evaluation runner
- `prompts/templates.py`: schema + prompt templates
- `sql/seed.sql`: ClassicModels schema + seed data
- `docker-compose.yml`: app + Postgres services

## Requirements

- Python 3.10+
- PostgreSQL (if running locally)
- Gemini API key (`GEMINI_API_KEY`)

Install Python dependencies:

```bash
cd "task3:Text-to-SQL Pipeline"
pip install -r requirements.txt
```

## Environment Variables

Create `task3:Text-to-SQL Pipeline/.env` with:

```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=5433
DB_NAME=classicmodels
DB_USER=postgres
DB_PASSWORD=password
```

Notes:
- `DB_*` values above match the default Docker setup.
- If you run Postgres locally on a different port/credentials, update these values accordingly.

## Run with Docker Compose (Recommended)

From `task3:Text-to-SQL Pipeline/`:

```bash
docker compose up --build
```

Services:
- `db`: PostgreSQL 16 on `localhost:5433`
- `app`: Streamlit UI on `http://localhost:8501`

Before running, make sure `GEMINI_API_KEY` is available in your environment or `.env`.

## Run Locally (Without Docker)

1. Start PostgreSQL and create/load `classicmodels`.
2. Seed schema + data:

```bash
psql -h localhost -U postgres -d classicmodels -f sql/seed.sql
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start Streamlit:

```bash
streamlit run streamlit_app.py
```

## Evaluation Script

Run a quick pipeline benchmark:

```bash
python evaluate.py
```

It prints per-question status, whether retry was needed, and overall success metrics.

## Logging

Each query execution appends an entry to:

- `logs/query_logs.json`

Stored fields include:
- question
- decomposition
- initial SQL
- retry SQL (if any)
- final status
- error message
- result rows and columns

## Safety and Limitations

- Only `SELECT` queries are allowed by validator rules.
- DML/DDL keywords like `DELETE`, `DROP`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE` are blocked.
- Retry policy is fixed to a single correction attempt.
- Output quality depends on prompt quality, model behavior, and schema coverage.
