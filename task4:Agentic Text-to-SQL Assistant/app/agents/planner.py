from app.agents.llm import chat_complete
from app.prompts import PLANNER_PROMPT, SCHEMA

def generate_plan(query: str) -> str:
    system = "You are a SQL planner. Produce a short plan describing tables, joins, filters, and output columns."
    user = PLANNER_PROMPT.format(schema=SCHEMA, query=query)
    return chat_complete(system, user, max_tokens=400, temperature=0.0)
