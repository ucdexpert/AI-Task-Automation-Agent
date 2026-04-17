import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "AI Task Automation Agent")
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agent.db")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-this")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # Google Calendar
    GOOGLE_CALENDAR_CREDENTIALS: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "")
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "")
    
    # WhatsApp (Meta API)
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_WABA_ID: str = os.getenv("WHATSAPP_WABA_ID", "")
    WHATSAPP_RECIPIENT_NUMBER: str = os.getenv("WHATSAPP_RECIPIENT_NUMBER", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

    # CORS
    BACKEND_CORS_ORIGINS: list = [
        origin.strip() 
        for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    ]

settings = Settings()
