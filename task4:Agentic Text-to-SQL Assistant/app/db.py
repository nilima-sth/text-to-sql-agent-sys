from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL environment variable not set')

_engine: Engine = create_engine(DATABASE_URL, future=True)

def get_engine() -> Engine:
    return _engine
