from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
# Load .env from project root (one level up) if present, then app/.env to allow
# overriding values. This covers running locally and inside Docker where
# docker-compose may set env vars from the compose directory.
parent_env = BASE_DIR.parent / '.env'
app_env = BASE_DIR / '.env'
if parent_env.exists():
	load_dotenv(parent_env)
if app_env.exists():
	load_dotenv(app_env)

DATABASE_URL = os.getenv('DATABASE_URL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL = os.getenv('MODEL', 'gemini-3.1-flash-lite')
