from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ONGOING_PROJECT_API: str
    COMPLETED_PROJECT_API: str
    CANCELLED_PROJECT_API: str

    ONGOING_LOG_API: str
    COMPLETED_LOG_API: str
    CANCELLED_LOG_API: str

    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()