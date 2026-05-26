from pydantic import SecretStr, computed_field
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
    
    @computed_field
    @property
    def BACKEND_URL(self) -> str:
        return (
            "http://127.0.0.1:8000"
            if self.DEVELOPMENT_MODE
            else "https://panzek.onrender.com"
        )

# Global instance
settings = Settings()
