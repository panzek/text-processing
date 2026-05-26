import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from docx import Document

import stripe
from config import settings

# Initialize the Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
stripe.api_key = settings.STRIPE_SECRET_KEY.get_secret_value()

# Mock database to temporary store session id and payment status 
payment_db = {}

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

# define payment endpoint
@app.get("/create-checkout-session")
async def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': 'Professional Résumé Reviewer',
                    'description': 'A rewritten resume with compelling, professional  cover letter tailored to it' 
                },
                'unit_amount': 500  
            },
            'quantity': 1
        }],
        mode='payment',
        success_url="http://localhost:8501/?payment=success&session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8501/?payment=cancel"
        )
        
        return {"url": session.url, "id": session.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )

# Listen for Stripe webhook notifications, specifically based on our 
# selected event type in stripe account, that confirm that a user has paid
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    
    except Exception as e:  
        raise HTTPException(
            status_code=400, 
            detail=f"Webhook Error: {str(e)}"
        )
    
    if event['type'] == 'chechout.session.completed':
        session = event.data.object
        # record payment in the database
        payment_db[session['id']] = "paid"
        print(f"Payment verified for Sessiion: {session['id']}")
        
    return {"status": "success"}

@app.get("/verify-payment/{session_id}")
async def verify_payment(session_id: str):
    # check the database for session id
    status = payment_db.get(session_id)
    if status == "paid":
        print(f"Verification Request: {session_id} is Confirmed Paid.")
        return {"status": "paid"}
    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)     
        if stripe_session.payment_status == "paid":
            payment_db[session_id] = "paid"
            return {"status": "paid"}
    except Exception as e:
        print(f"Stripe API retrieval failed: {e}")
        
    print(f"Verification Request: {session_id} is still Pending.")
    return {"status": "pending"}
   
# Define a path operation
@app.post("/review")
# path operation function
async def review(session_id: str, file: UploadFile = File(...)):
    # verify payment
    if payment_db.get(session_id) != "paid":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail="Payment not verifed. Please complete checkout first"
            )
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