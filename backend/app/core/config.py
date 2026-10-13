from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Backend folder
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    # -----------------------------------------
    # Application
    # -----------------------------------------
    app_name: str = "AI Voice Assistant API"

    # -----------------------------------------
    # Database
    # -----------------------------------------
    database_url: str = (
        f"sqlite:///{(BACKEND_DIR / 'assistant.db').as_posix()}"
    )

    # -----------------------------------------
    # JWT Authentication
    # -----------------------------------------
    jwt_secret: str = "change-me-in-environment"
    jwt_expire_minutes: int = 1440

    # -----------------------------------------
    # Frontend
    # -----------------------------------------
    frontend_url: str = "http://localhost:5173"

    # -----------------------------------------
    # Gemini AI
    # -----------------------------------------
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # -----------------------------------------
    # Weather
    # -----------------------------------------
    openweather_api_key: str = ""
    weather_default_city: str = "Delhi"

    # -----------------------------------------
    # News
    # -----------------------------------------
    news_api_key: str = ""

    # -----------------------------------------
    # Gmail / SMTP
    # -----------------------------------------
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""

    # -----------------------------------------
    # Environment configuration
    # -----------------------------------------
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        case_sensitive=False,
        extra="ignore"
    )


# Create settings object
settings = Settings()