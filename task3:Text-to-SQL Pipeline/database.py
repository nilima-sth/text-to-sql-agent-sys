import os
import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "classicmodels")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def execute_query(sql_query: str) -> Tuple[List[Dict[str, Any]], List[str], str]:
    """
    Executes a SQL query and returns the results and columns.
    Returns: (results (list of dicts), column_names, error_message)
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql_query)
            
            # Fetch column names
            colnames = [desc[0] for desc in cur.description] if cur.description else []
            
            # Fetch all rows
            rows = cur.fetchall()
            
            # Convert to list of dicts for JSON serialization
            results = [dict(row) for row in rows]
            
            return results, colnames, None
    except Exception as e:
        return [], [], str(e)
    finally:
        if conn is not None:
            conn.close()
