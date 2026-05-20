from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings Configuration
class Settings(BaseSettings):
    # API Config
    BACKEND: str
    API_URL: str
    
    GEMINI_API_KEY: SecretStr | None = None
    STRIPE_PUBLIC_KEY: str 
    STRIPE_SECRET_KEY: SecretStr
    STRIPE_WH_SECRET: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf=8",
        extra='ignore'
    )

# Global instance
settings = Settings()
