from fastapi import FastAPI
from google import genai
# from google.genai import types
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
# from pypdf import PdfReader
# from docx import Document


# Settings Configuration
class Settings(BaseSettings):
    GEMINI_API_KEY: SecretStr
    
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )
    
settings = Settings()

# Instantiate FastAPI
app = FastAPI

# Initialize the Gemini Clienyt
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())

# Security Check
print(f"Secret {settings.GEMINI_API_KEY}")