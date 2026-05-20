import json
import os
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any
from sql_generator import decompose_query, generate_sql, fix_sql
from validator import validate_sql, ValidationError
from database import execute_query

LOG_FILE = "logs/query_logs.json"

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def log_execution(log_entry: Dict[str, Any]):
    """Appends an execution result into the query_logs.json"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
            
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4, cls=CustomEncoder)

def run_pipeline(question: str) -> Dict[str, Any]:
    """Orchestrates the prompt chain and retry logic."""
    log_entry = {
        "question": question,
        "decomposition": None,
        "initial_sql": None,
        "retry_needed": False,
        "retry_sql": None,
        "error_message": None,
        "status": "failed",
        "result": [],
        "columns": []
    }
    
    current_sql = ""
    try:
        # Step 1: Decomposition
        decomposition = decompose_query(question)
        log_entry["decomposition"] = decomposition
        
        # Step 2: Generation
        current_sql = generate_sql(decomposition)
        log_entry["initial_sql"] = current_sql
        
        # Step 3: Validation
        validate_sql(current_sql)
        
        # Step 4: Execution
        results, columns, error = execute_query(current_sql)
        
        # Step 5: Retry / Self-Correction
        if error:
            log_entry["retry_needed"] = True
            log_entry["error_message"] = error
            
            # Sub-step: Fix Call
            current_sql = fix_sql(error_msg=error, bad_sql=current_sql)
            log_entry["retry_sql"] = current_sql
            
            # Validate fixed SQL
            validate_sql(current_sql)
            
            # Execute fixed SQL
            results, columns, error = execute_query(current_sql)
            
            if error:
                # If it still fails, bubble up the error gracefully
                log_entry["error_message"] = f"Retry Failed: {error}"
                log_entry["status"] = "failed"
            else:
                log_entry["result"] = results
                log_entry["columns"] = columns
                log_entry["status"] = "success"
        else:
            log_entry["result"] = results
            log_entry["columns"] = columns
            log_entry["status"] = "success"

    except ValidationError as ve:
        log_entry["error_message"] = f"Validation Error: {str(ve)}"
        log_entry["status"] = "failed"
    except Exception as e:
        log_entry["error_message"] = f"System Error: {str(e)}"
        log_entry["status"] = "failed"
        
    log_execution(log_entry)
    return {
        "question": question,
        "sql": current_sql,
        "result": log_entry["result"],
        "columns": log_entry["columns"],
        "status": log_entry["status"],
        "retry_needed": log_entry["retry_needed"],
        "error_message": log_entry.get("error_message")
    }
