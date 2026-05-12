import io
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from docx import Document

from config import settings

# Initialize the Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())

# Instantiate FastAPI
app = FastAPI()

# CORS (Cross-Origin Resource Sharing)
origins = [
    "https://panzek.onrender.com", 
    "https://resumepluscover.streamlit.app"
    "http://localhost", 
    "http://localhost:8000", 
    "http://127.0.0.1:8000/review",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a path operation
@app.post("/review")
# path operation function
async def review(file: UploadFile = File(...)):
    # Read the raw file bytes
    content = await file.read()
    
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 10MB."
        )
    
    prompt = (
        "You are an expert career coach. "
        "Review this resume carefully and rewrite it with improvements. "
        "Then draft a compelling, professional  cover letter tailored to it.\n\n"
        "Resume content:\n"
    )  
    
    # DOCX handling
    if file.filename.lower().endswith('.docx'):
        try:
            doc = Document(io.BytesIO(content))
            text_content = "\n".join([para.text for para in doc.paragraphs])
            contents = [f"{prompt}\n\n{text_content}"]
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
                        types.Part.from_text(text=prompt),
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
            contents = [f"{prompt}\n\n{text_content}"]

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
    
        return {"review": response.text.strip()}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate review with Gemini: {str(e)}"
        )
        