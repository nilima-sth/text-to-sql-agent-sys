

## Repository Layout

- `task2:Query_Decomposition/`: decomposition script + input/output CSVs
- `task3:Text-to-SQL Pipeline/`: Streamlit pipeline app + Docker setup
- `task4:Agentic Text-to-SQL Assistant/`: agentic app (`app/`) + API + Streamlit + Docker setup
- `sql/seed.sql`: shared ClassicModels PostgreSQL seed file
- `Benchmark/`: benchmark reference files
- `Documents/`: supporting project docs

## Prerequisites

- Python 3.10+ (3.11 recommended for `task4`)
- PostgreSQL (for local non-Docker runs)
- Docker + Docker Compose (recommended for `task3` and `task4`)
- Gemini API key

## Environment Setup

Each component loads environment variables from different files:

- `task2:Query_Decomposition/` reads `GEMINI_API_KEY` from repository root `.env`
- `task3:Text-to-SQL Pipeline/` reads from `task3:Text-to-SQL Pipeline/.env`
- `task4:Agentic Text-to-SQL Assistant/` reads from `task4:Agentic Text-to-SQL Assistant/.env` and optionally `task4:Agentic Text-to-SQL Assistant/app/.env`

Suggested values:

```env
# .env (repo root)
GEMINI_API_KEY=your_gemini_api_key
```

```env
# task3:Text-to-SQL Pipeline/.env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=5433
DB_NAME=classicmodels
DB_USER=postgres
DB_PASSWORD=password
```

```env
# task4:Agentic Text-to-SQL Assistant/.env (or task4:Agentic Text-to-SQL Assistant/app/.env)
GEMINI_API_KEY=your_gemini_api_key
MODEL=gemini-3.1-flash-lite
DATABASE_URL=postgresql://user:password@localhost:5434/text2sql
```

## Run: Query Decomposition (`task2:Query_Decomposition/`)

```bash
python "task2:Query_Decomposition/query_decomposition.py"
```

Input:
- `task2:Query_Decomposition/SQL_QUESTIONS - sql_questions_only.csv`

Output:
- `task2:Query_Decomposition/task2_decomposed_answers.csv`

## Run: Prompt-Chained Pipeline (`task3:Text-to-SQL Pipeline/`)

Docker:

```bash
cd "task3:Text-to-SQL Pipeline"
docker compose up --build
```

Local:

```bash
cd "task3:Text-to-SQL Pipeline"
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Optional benchmark:

```bash
python evaluate.py
```

## Run: Agentic Assistant (`task4:Agentic Text-to-SQL Assistant/`)

Docker:

```bash
cd "task4:Agentic Text-to-SQL Assistant/app"
docker compose up --build
```

Local:

```bash
cd "task4:Agentic Text-to-SQL Assistant"
pip install -r app/requirements.txt
streamlit run app/streamlit_app.py
uvicorn app.main:app --reload
```

API:
- `POST /agent/sql`

Example payload:

```json
{
  "question": "What are the top 5 customers by total payments?"
}
```

## Ports

- `task3:Text-to-SQL Pipeline` Streamlit: `http://localhost:8501`
- `task3:Text-to-SQL Pipeline` Postgres: `localhost:5433`
- `task4:Agentic Text-to-SQL Assistant` Streamlit: `http://localhost:8501`
- `task4:Agentic Text-to-SQL Assistant` Postgres: `localhost:5434`

## Notes

- `task3:Text-to-SQL Pipeline` and `task4:Agentic Text-to-SQL Assistant` both use Streamlit port `8501` by default; run one at a time or remap ports.
- In `task4:Agentic Text-to-SQL Assistant` Docker mode, DB host is `db`; in local mode, use `localhost:5434` in `DATABASE_URL`.
- Keep API keys out of version control and use placeholders in example env files.

## Component Docs

- `task2:Query_Decomposition/README.md`
- `task3:Text-to-SQL Pipeline/README.md`
- `task4:Agentic Text-to-SQL Assistant/README.md`
