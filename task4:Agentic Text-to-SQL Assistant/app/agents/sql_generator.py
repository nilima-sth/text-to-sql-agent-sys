from app.agents.llm import chat_complete
from app.prompts import SQL_GENERATOR_PROMPT, SCHEMA

def generate_sql(query: str, plan: str) -> str:
    system = "You are a PostgreSQL expert. Generate only a single read-only SQL statement matching the plan."
    user = SQL_GENERATOR_PROMPT.format(schema=SCHEMA, query=query, plan=plan)
    sql = chat_complete(system, user, max_tokens=700, temperature=0.0)
    # strip code fences if present
    if sql.startswith('```'):
        sql = sql.split('```')[-1]
    return sql.strip()
