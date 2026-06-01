import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parent.parent / ".env"

print(f"--- DEBUG ---")
print(f"Looking for .env at: {env_path}")
print(f"File exists? {env_path.exists()}")
print(f"-------------")

load_dotenv(dotenv_path=env_path, override=True)

class Settings(BaseSettings):

    # ── GET APIs ──────────────────────────────────────────
    PROJECT_GET_API: str
    MEETING_GET_API: str
    DOCUMENT_GET_API: str
    EMAIL_GET_API: str
    CLIENT_GET_API:   str

    # ── POST / AI-Update APIs ─────────────────────────────
    AI_UPDATE_PROJECT_API: str
    AI_UPDATE_WEEKLY_SUMMARY_API: str
    AI_UPDATE_MEETING_API: str
    AI_UPDATE_DOCUMENT_API: str
    AI_UPDATE_EMAIL_API: str
    AI_DETECTION_API: str
    CLIENT_PUSH_API: str

    # ── Auth ──────────────────────────────────────────────
    BACKEND_SERVICE_SECRET: str

    # ── OpenAI ────────────────────────────────────────────
    OPENAI_API_KEY: str

    # ── Pinecone ──────────────────────────────────────────
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_EMAIL_INDEX_NAME: str
    PINECONE_EMAIL_INDEX_NAME_SECONDARY: str
    PINECONE_ENV: str

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore"
    )

try:
    settings = Settings()
    print("✅ Settings loaded successfully.")
except Exception as e:
    print(f"❌ Settings validation failed: {e}")
    raise e