import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts.templates import DB_SCHEMA, DECOMPOSITION_PROMPT, GENERATION_PROMPT, FIX_PROMPT

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

def clean_sql(sql_str: str) -> str:
    """Removes markdown formatting if present."""
    sql_str = sql_str.strip()
    if sql_str.startswith("```"):
        # Remove first line (e.g. ```sql)
        sql_str = sql_str.split("\n", 1)[-1]
        # Remove last line (e.g. ```)
        if sql_str.rfind("```") != -1:
            sql_str = sql_str[:sql_str.rfind("```")]
    return sql_str.strip()

def decompose_query(nl_query: str) -> dict:
    """LLM Call 1: Decompose natural language query into JSON variables."""
    prompt = DECOMPOSITION_PROMPT.format(query=nl_query, DB_SCHEMA=DB_SCHEMA)
    
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    return json.loads(response.text)

def generate_sql(decomposition: dict) -> str:
    """LLM Call 2: Generate direct raw SQL query string from decomposition."""
    prompt = GENERATION_PROMPT.format(
        schema=DB_SCHEMA, 
        decomposition=json.dumps(decomposition, indent=2)
    )
    
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.1)
    )
    
    return clean_sql(response.text)

def fix_sql(error_msg: str, bad_sql: str) -> str:
    """LLM Call 3: Fix a failed SQL query using the DB error message."""
    prompt = FIX_PROMPT.format(bad_sql=bad_sql, error_msg=error_msg)
    
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.1)
    )
    
    return clean_sql(response.text)
