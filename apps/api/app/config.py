from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    enable_gemini: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    next_public_api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
