from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Load .env file explicitly
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_use_ssl: bool = False
    session_ttl: int = 86400  # 24 hours in seconds

    # FastAPI Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Security
    secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Debug: Print loaded configuration (without sensitive data)
print(f"🔧 Configuration loaded:")
print(f"   - OpenAI Model: {settings.openai_model}")
print(f"   - Host: {settings.host}")
print(f"   - Port: {settings.port}")
print(f"   - Redis Host: {settings.redis_host}")
print(f"   - Redis Port: {settings.redis_port}")
print(f"   - Session TTL: {settings.session_ttl} seconds")
print(f"   - Debug Mode: {settings.debug}")
print(f"   - .env file loaded: {os.path.exists('.env')}")
