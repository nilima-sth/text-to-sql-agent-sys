# Agentic Text-to-SQL Assistant

## Overview
This repository contains a Text-to-SQL assistant that converts natural language questions into PostgreSQL queries, executes them against a seeded relational database, and returns a concise summary of results.

The project includes:
- A FastAPI endpoint for programmatic access
- A Streamlit UI for interactive querying
- An orchestration workflow that generates, validates, repairs, executes, and summarizes SQL

## Key Capabilities
- Natural language to SQL generation with Gemini models
- Read-only SQL safety validation (`SELECT`/`WITH` only)
- Automatic retry loop to repair failed SQL (up to 3 attempts)
- JSON-serializable query results for API/UI usage
- Built-in sample PostgreSQL schema + seed data (classic models dataset)

## Architecture
Core flow (implemented in `app/agents/orchestrator.py`):
1. Generate SQL from user question and schema context
2. Validate SQL for read-only safety
3. Execute SQL on PostgreSQL
4. If validation or execution fails, ask the model to repair SQL and retry
5. Summarize results in natural language

Main modules:
- `app/main.py`: FastAPI app (`POST /agent/sql`)
- `app/streamlit_app.py`: Streamlit interface
- `app/agents/orchestrator.py`: end-to-end workflow controller
- `app/agents/validator.py`: SQL safety checks
- `app/tools/db_tools.py`: query execution layer
- `app/agents/llm.py`: Gemini integration
- `app/prompts/__init__.py`: schema and prompt templates

## Repository Layout
- `app/`: application code, Docker assets, requirements, and in-app seed SQL
- `sql/seed.sql`: root-level seed SQL (also present at `app/sql/seed.sql`)
- `.env`: runtime configuration (not committed in production)

## Configuration
Set environment values before running:
- `GEMINI_API_KEY`: Gemini API key
- `MODEL`: Gemini model name (default in code: `gemini-3.1-flash-lite`)
- `DATABASE_URL`: SQLAlchemy/PostgreSQL URL

Example format:
```env
DATABASE_URL=postgresql://user:password@localhost:5434/text2sql (For example)
GEMINI_API_KEY=your_api_key
MODEL=gemini-3.1-flash-lite
```

Reference template: `app/.env.example`

## Running with Docker Compose
From the `app/` directory:
```bash
cd app
docker compose up --build
```

What starts:
- `db`: PostgreSQL 16, seeded using `app/sql/seed.sql`, exposed on `localhost:5434`
- `app`: Streamlit app on `localhost:8501`

## Running Locally (without Docker)
1. Install dependencies:
```bash
pip install -r app/requirements.txt
```

2. Ensure PostgreSQL is running and loaded with the seed schema/data (`sql/seed.sql` or `app/sql/seed.sql`).

3. Set environment variables (`DATABASE_URL`, `GEMINI_API_KEY`, optional `MODEL`).

4. Start Streamlit UI:
```bash
streamlit run app/streamlit_app.py
```

5. Start FastAPI server (optional):
```bash
uvicorn app.main:app --reload
```

## API Usage
Endpoint:
- `POST /agent/sql`

Request body:
```json
{
  "question": "What are the top 5 customers by total payments?"
}
```

Response includes:
- generated SQL
- execution result rows
- summary text
- status (`success` or `error`)

## Notes and Limitations
- SQL validation is rule-based and blocks common write operations (`INSERT`, `UPDATE`, `DELETE`, etc.).
- Query quality depends on schema coverage in prompts and the selected model.
- Additional agent files (`planner.py`, `sql_generator.py`, `executor.py`, `summarizer.py`) exist, but the active runtime path is the orchestrator-driven flow.
