import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Manually find the .env file path
env_path = Path(__file__).resolve().parent.parent / ".env"

# 2. Debugging: This will print in your terminal when you start
print(f"--- DEBUG INFO ---")
print(f"Looking for .env at: {env_path}")
print(f"File exists? {env_path.exists()}")
print(f"------------------")

# 3. Explicitly load it into the system environment
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    ONGOING_PROJECT_API: str
    COMPLETED_PROJECT_API: str
    CANCELLED_PROJECT_API: str
    ONGOING_LOG_API: str
    COMPLETED_LOG_API: str
    CANCELLED_LOG_API: str
    OPENAI_API_KEY: str
    
    ALL_EMAILS_API: str
    ALL_PROJECTS_PUBLIC_API: str

    # Pydantic will now pick them up from the system environment
    model_config = SettingsConfigDict(extra="ignore")

try:
    settings = Settings()
except Exception as e:
    print(f"ERROR: Settings validation failed.")
    raise e