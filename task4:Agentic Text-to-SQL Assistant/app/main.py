from fastapi import FastAPI
from pydantic import BaseModel
from app.agents.orchestrator import run_workflow  # Updated import

app = FastAPI(title="Agentic Text-to-SQL API")


class QueryRequest(BaseModel):
    question: str


@app.post("/agent/sql")
def query_db(req: QueryRequest):
    result = run_workflow(req.question)

    is_success = result.get("is_valid_sql") and not result.get("validation_error")

    return {
        "sql": result.get("generated_sql"),
        "result": result.get("execution_results"),
        "summary": result.get("summary"),
        "status": "success" if is_success else "error",
    }
