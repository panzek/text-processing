import io
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from google import genai
from google.genai import types
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
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

# Instantiate FastAPI
app = FastAPI()

# Define a path operation
@app.post("/summarise")
# path operation function
async def summarise(file: UploadFile = File(...)):
    # Read the raw file bytes
    content = await file.read()
    
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 10MB."
        )
        
    
    # DOCX handling
    if file.filename.lower().endswith('.docx'):
        try:
            doc = Document(io.BytesIO(content))
            text_content = "\n".join([para.text for para in doc.paragraphs])
            contents = [
                f"Review this resume and rewrite for improvements:\n{text_content}."
                ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read DOCX: {str(e)}."
            )
    
    # Handle PDFs using Gemini's native vision
    elif file.filename.lower().endswith(".pdf"):
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="Review this resume and rewrite for improvements "
                                             "Draft a compelling cover letter that matches the rewritten resume."),
                        types.Part.from_bytes(data=content, mime_type="application/pdf")
                    ]
                )
            ]     
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF: {str(e)}"
            )
    
    # fallback for plain text
    else:
        try:  
            text_content = content.decode("utf-8", errors="replace")
        except UnicodeDecodeError:
            try:
                text_content = content.decode("latin-1", errors="replace")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not decode text file: {str(e)}"
                )
    
    try:
        # Request - Send the clean text to Gemini API
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents
        )
    
        clean_text = response.text.strip()
    
        return {"summarise": clean_text}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summarywith Gemini: {str(e)}"
        )
        
   
            
    