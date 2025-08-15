import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CSV_PATH = os.getenv("CSV_PATH", "data/apolloTyres_combined_cleaned.csv")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "models/embedding-001")
    PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "chroma_db")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_USER = os.getenv("DB_USER", "nirbhay")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Nirbhay@123")
    DB_NAME = os.getenv("DB_NAME", "chatbot_analytics")

settings = Settings()