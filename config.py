import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-31b-it")
DB_PATH = os.path.join("data", "stocksense.db")
DEMO_MODE = not bool(GEMINI_API_KEY)
