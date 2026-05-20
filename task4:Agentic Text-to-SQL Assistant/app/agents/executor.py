import time
import logging
from app.tools.db_tools import execute_query

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_sql(sql: str):
    start_time = time.time()
    
    try:
        results = execute_query(sql)
    except Exception as e:
        # Catch runtime DB errors to feed back to the LLM
        raise RuntimeError(f"Database execution failed: {str(e)}")
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    logger.info(f"SQL Execution time: {execution_time:.4f} seconds")
    
    return results