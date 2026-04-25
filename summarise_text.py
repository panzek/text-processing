import io
from fastapi import FastAPI, File, UploadFile
from google import genai
# from google.genai import types
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pypdf import PdfReader
from docx import Document


# Settings Configuration
class Settings(BaseSettings):
    GEMINI_API_KEY: SecretStr
    
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )
    
settings = Settings()

# Initialize the Gemini Clienyt
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())

# Security Check
print(f"Secret {settings.GEMINI_API_KEY}")

# Instantiate FastAPI
app = FastAPI()

# Define a path operation
@app.post("/summarise")
# path operation function
async def summarise(file: UploadFile = File(...)):
    # Read the file into memory
    content = await file.read()
    text =""
    
    # Open as a PDF
    if file.filename.endswith('.pdf'):
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            page_text = page.extract_text
            if page_text:
                text += page_text + "\n"
    
    # Open as a word document
    elif file.filename.endswith('docx'):
        doc = Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
        
    else:
        # Fallback for plain text
        try:
            text = content.decode("utf=8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
    
    if text.strip():
        return {"error": "Could not extract and readable text from this file"}
    
   
            
    