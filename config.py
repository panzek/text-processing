from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings Configuration
class Settings(BaseSettings):
    # API Config   
    STRIPE_SECRET_KEY: SecretStr
    STRIPE_WH_SECRET: str
    GEMINI_API_KEY: SecretStr
    
    DEVELOPMENT_MODE: bool = False
    API_URL: str = "https://panzek.onrender.com"
    STRIPE_PUBLIC_KEY: str = ""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf=8",
        case_sensitive=True,
        extra='ignore'
    )
    
# Global instance
settings = Settings()
