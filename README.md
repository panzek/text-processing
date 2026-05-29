# Résumé Reviewer & Cover Letter Generator

## Introduction

An automated full-stack application built using **FastAPI** (backend), **Streamlit** frontend, and **PydanticAI** (utilising Google's Gemini 3 Flash Preview). The system securely processes payments via **Stripe**, extracts data from multi-format resumes, and generates structural, type-safe rewritten résumés, tailored cover letters, and career coach tips.

### System Architecture
The application handles data extraction, asynchronous validation, and secure payment processing across three major layers:
- **Frontend (Streamlit):** Cordinates multi-part file uploads and forces parent window top-level redirections to bypass Stripe iframe sandbox restrictions.
- **Backend (FastAPI):** Controls webhooks, manages mock database persistence, parses document content structures, and servers as the API gateway.
- **AI Layer (PydanticAI):** Enforces rigid structureal type-safety constraints directly over Gemini's multimodal output layer, eliminating unstructured raw string parsing failures.

### Core Modules Breakdown
**Type-Safe AI Schema Validation**
The system relies on PydanticAI's structured output_type pipeline configuration. This guarantees that your frontend always receives consistent JSON dictionary fields without risk of random formatting drift:

```
class ResumeFeedback(BaseModel):
    rewritten_resume: str = Field(
        ...,
        description =(
            "Review this resume carefully and rewrite it with modern enhancements. "
            "Structured cleanly in Markdown format."
        )
    )
    suggested_cover_letter: str = Field(
        ...,
        description="A tailored, compelling professional cover "
        "letter matching the candidate's background."
    )
    
    career_coach_tips: str = Field(
        ...,
        description="Actionable career coach tips and strategy "
        "recommendations based on the reviewed resume."
        "Career Coach Tips:\n\n"
    )

```

### Advanced Multi-Modal Document Parsing
- **.docx and .txt files:** Extracted as pure text strings instantly inside the endpoint and cleanly wrapped into the analysis runtime text payload.
- **.pdf files:** Leverages Gemini's native vision capability. The raw file bytes stream directly to the model wrapped inside a PydanticAI:

```
    BinaryContent(
        data=content,
        media_type="application/pdf"
    )
```
node, maintaining all underlying layout structural formatting.

### Features
- **Multi-format Support**: Accepts '.pdf', '.docx', and '.txt' résumé files.
- **Intelligent Résumé Review**: Detailed analysis and executive-level professional rewrite structural suggestions.
- **Tailored Cover Letter**: Automatically generated a matching, highly compelling cover letter.
- **Fast & Resoponsive UI**: Built with Streamlit for a seamless, instantaneous user experience.
- **Secure & Production Ready**: Enforces explicit file size limits, robust CORS protection, and cryptographic signature validations.

### How it Works
1. **Upload:** Users upload their résumés (PDF, DOCX, or TXT) through the Streamlit interface
2. **Payment:** The fuser pays a flat €5.00 checkout fee using a secure top-level window redirect powered by Stripe.
3. **Processing:** Streamlit sends the file and verified session_id securely to the FastAPI backend.
4. **Text Extraction:** FastAPI extracts contents adaptively based on file types using 'python-docx' or native binary streaming. 
5. **AI Analysis & Response:** PydanticAI passes the text/bytes to Google Gemini, validates the schema output fields, and returns a perfectly structured JSON payload containing the rewritten resume, letter, and tips.
6. **Display** - Results render instantly in clean Markdown tabs on the frontend.

The entire flow is shown asynchronous, responsive, and includes proper error handling and logging.

### Tech Stack
| Category      | Technology                                                |
|---------------|-----------------------------------------------------------|
| Frontend      | Streamlit                                                 |
| Backend       | Python, FastAPI + Uvicorn                                 |
| AI & Data     | Google Gemini (3-flash-preview), PydanticAI, Pydantic     |
| Payments      | Stripe API (with Webhook Cryptographic Verification)      |
| Hosting       | Streamlit Cloud (frontend) + Render (Backend)             |
| Environment   | UV (Astral Python Package Manager)                        |
|---------------------------------------------------------------------------|


### Project Structure
```
text-processing/
|-- interface.py        # Streamlit frontend application layer
|-- resume_reviewer.py  # FastAPI Backend logic and endpoints
|-- config.py         # Shared settings environment definition (Pydantic)
|-- pyproject.toml
|-- uv.lock
|-- .env                # Environment Variable
|-- README.md 
```

### Local Setup & Installation

### Prerequsites
    - Python 3.10+
    - uv package manager
```
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone & Setup
```
git clone https://github.com/panzek/text-processing
cd resume-reviewer
uv sync
```

### Configure Environment Variables
Create a .env file in the root directory and add credentials, (or add these key-value configurations inside your Render web service dashboard):
```
# AI Modal Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Stripe Secrets
STRIPE_API_KEY=sk_test...
STRIPE_WH_SECRET=whsec...

# Dynamic URL Configurations
FRONTEND_URL=http://localhost:8501

```
Note: PydanticAI reads the standard GOOGLE_API_KEY slot. Your backend automatically bridges this gap on runtime boot using:

```
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY.get_secret_value()
```

### Running Locally
To run the complete microservice mesh locally, launch both server terminals simultaneously:

#### Terminal 1 - Spin up the FastAPI Backend
```
uv run uvicorn resume_reviewer:app --reload 
```
### Terminal 2 - Spin up the Streamlit Frontend Client
```
uv run streamlit run interface.py
```

### Production Deployment
#### Backend (Render)
- Build Command: uv sync --frozen && uv cache prune --ci
- Start Command: uvicorn resume_reviewer:app --host 0.0.0.0 --port $PORT

#### Frontend (Streamlit Cloud)
- Connect your GitHub repository to Streamlit Cloud
- Set the Main file path to interface.py
- Add your production environment variable secrets inside the dashboard (BACKEND_URL pointing directly to your live Render URL).

### Security Architectures
- File Validation: Restricts payload body requests to a maximum size of 10MB and checks extensions strictly to block malicious executions.
- CORS Middleware: Explicitly white-lists communication to prevent cross-origin unauthorized scripting from foreign domains.
- Stripe Webhook: Employs end-to-end cryptographic signature validation (stripe.Webhook.construct_event) to block fake payment injection attempts.