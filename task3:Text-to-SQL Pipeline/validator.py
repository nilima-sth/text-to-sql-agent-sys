import re

class ValidationError(Exception):
    pass

def validate_sql(sql_query: str) -> None:
    """
    Validates the generated SQL query to ensure it only performs READ operations.
    Blocks any DML/DDL commands like DELETE, DROP, UPDATE, INSERT, ALTER, TRUNCATE.
    """
    if not sql_query or not sql_query.strip():
        raise ValidationError("Empty SQL query.")

    sql_upper = sql_query.upper()
    
    # Check if the query is a SELECT query
    if not sql_upper.lstrip().startswith("SELECT"):
        raise ValidationError("SQL query must start with SELECT.")
    
    # List of blocked keywords
    blocked_keywords = [
        r'\bDELETE\b', r'\bDROP\b', r'\bUPDATE\b', 
        r'\bINSERT\b', r'\bALTER\b', r'\bTRUNCATE\b'
    ]
    
    for pattern in blocked_keywords:
        if re.search(pattern, sql_upper):
            raise ValidationError(f"Blocked keyword detected in query. DML/DDL operations are not allowed.")
