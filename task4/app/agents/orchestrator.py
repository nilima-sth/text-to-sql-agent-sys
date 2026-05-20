from app.agents.llm import chat_complete
from app.agents.validator import validate_sql
from app.tools.db_tools import execute_query
from app.prompts import SQL_GENERATOR_PROMPT, SQL_REPAIR_PROMPT, SUMMARIZER_PROMPT, SCHEMA
import json


def run_workflow(user_query: str) -> dict:
    generated_sql = ""
    is_valid_sql = False
    execution_results = None
    error_msg = ""

    # Step 1: Generate Initial SQL
    sys_prompt = SQL_GENERATOR_PROMPT.format(schema=SCHEMA, query=user_query)
    generated_sql = chat_complete(sys_prompt, user_query)

    # Step 2: The Self-Correction Loop (Max 3 Attempts)
    for attempt in range(3):
        # Validate for read-only safety
        is_valid_sql, val_msg = validate_sql(generated_sql)

        if not is_valid_sql:
            error_msg = f"Validation Failed: {val_msg}"
        else:
            try:
                # Execute against PostgreSQL
                execution_results = execute_query(generated_sql)
                error_msg = ""
                break  # Success! Break out of the retry loop.
            except Exception as e:
                # Catch runtime errors (e.g., column does not exist)
                error_msg = f"Database Execution Error: {str(e)}"
                is_valid_sql = False

        # If it failed and we still have retries left, ask the LLM to fix it
        if attempt < 2:
            repair_sys = SQL_REPAIR_PROMPT.format(schema=SCHEMA, bad_sql=generated_sql, error_msg=error_msg)
            generated_sql = chat_complete(repair_sys, "Fix the SQL query based on the error.")

    # Step 3: Summarize the Final Output
    if is_valid_sql and execution_results is not None:
        try:
            results_json = json.dumps(execution_results, default=str)
        except Exception:
            results_json = str(execution_results)

        summary_sys = SUMMARIZER_PROMPT.format(query=user_query, results=results_json, sql=generated_sql)
        final_answer = chat_complete(summary_sys, "Summarize the results.")
    else:
        final_answer = f"Failed to answer the query after 3 attempts. Last error: {error_msg}"

    return {
        "sql": generated_sql,
        "result": execution_results,
        "summary": final_answer,
        "status": "success" if is_valid_sql else "error",
        "is_valid_sql": is_valid_sql,
        "execution_results": execution_results,
        "generated_sql": generated_sql,
        "validation_error": error_msg if not is_valid_sql else None,
    }
