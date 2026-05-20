import json
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import text
from app.db import get_engine

def _serialize_value(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v

def execute_query(sql: str):
    engine = get_engine()
    with engine.connect() as conn:
        try:
            result = conn.execute(text(sql))
            rows = [dict(row) for row in result.mappings().all()]
            # serialize
            rows = [{k: _serialize_value(v) for k, v in r.items()} for r in rows]
            return rows
        except Exception as e:
            raise
