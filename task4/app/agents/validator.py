from typing import Tuple

def validate_sql(sql: str) -> Tuple[bool, str]:
    if not sql or not sql.strip():
        return False, 'Empty SQL generated.'
    up = sql.upper()
    forbidden = ['DROP ', 'DELETE ', 'UPDATE ', 'INSERT ', 'ALTER ', 'TRUNCATE ', 'GRANT ', 'REVOKE ']
    for k in forbidden:
        if k in up:
            return False, f"Forbidden operation detected: {k.strip()}"
    if not (up.strip().startswith('SELECT') or up.strip().startswith('WITH')):
        return False, 'Only read-only SELECT queries are allowed.'
    return True, 'OK'
