from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    TAVILY_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

# Add this line at the bottom of app/config.py:
settings = Settings()