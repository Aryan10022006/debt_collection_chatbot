from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/debtbot"
    REDIS_URL: str = "redis://localhost:6379"
    
    # WhatsApp Business API
    WHATSAPP_ACCESS_TOKEN: str = "EAAIrYgZBTkUsBO4Fi5uTUP2FEhpLKor9wQo6TyplVqZCVBNo8gkzydLq7JDlWGENZAfcG4u6vKTzyJBhMhmSsV9WSubrW6gAsSxZAhsZB5hKzGk4ToWVIJFazEzlYAYLJlSC8sKxsAAXKAFf9JYPMGUhxNCZAO5BobVsrfTDLelvvkk7O5545Mg2AZBiVD8TsOz7ezZC6TZAC7TCiMisnmam4qu196DPut1CYW5ikiZC4wqrusWMsZD"
    WHATSAPP_PHONE_NUMBER_ID: str = "674138942450620"
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = "1821321785109097"
    WHATSAPP_APP_ID: str = "561175716819868"
    WHATSAPP_NUMBER: str = "917439330282"
    WHATSAPP_VERIFY_TOKEN: str = "debt_collection_webhook_verify_2024"
    WHATSAPP_WEBHOOK_URL: str = "https://your-domain.com/api/v1/whatsapp/webhook"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "DebtBot AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Compliance
    RBI_COMPLIANCE_MODE: bool = True
    MAX_MESSAGES_PER_DAY: int = 3
    BUSINESS_HOURS_START: str = "09:00"
    BUSINESS_HOURS_END: str = "18:00"
    TIMEZONE: str = "Asia/Kolkata"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: list = ["hi", "mr", "ta", "te", "en", "en-IN"]
    
    class Config:
        env_file = ".env"

settings = Settings()
