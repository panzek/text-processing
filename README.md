# Résumé Reviewer & Cover Letter Generator

## Introduction

**Résumé Reviewer & Cover Letter Generator** is a full-stack AI application that reviews résumé and generates tailored cover letters using Google Gemini. Built with **FastAPI** (backend) and **Streamlit** (frontend). 

### Features
- **Multi-format Support**: Accepts '.pdf', '.docx', and '.txt' résumé files.
- **Intelligent Résumé Review**: Detailed analysis and professional rewrite suggestions
- **Tailored Cover Letter**: Automatically generated a matching, compelling cover letter
- **Fast & Resoponsive UI**: Built with Streamlit for excellent user experience
- **Secure & Production Ready**: File validation, CORS protection, and error handling

### How it Works
1. **Upload** - Users upload their résumés (PDF, DOCX, or TXT) through the Streamlit interface
2. **Processing** - The frontend sends the file to the FastAPI backend.
3. **Text Extraction** - Backend extracts text from the file:
    - Uses 'python-docx' for '.docx'
    - Uses Gemini's native PDF support for '.pdf'
    - Direct coding for '.txt' files 
4. **AI Analysis** - The extracted text is sent to **Google Gemini** with a well-crafted prompt.
5. **Response Generation** - Gemini returns:
    - An improved, professionally rewritten résumé.
    - A compelling, tailored cover letter
6. **Display** - Results are shown beautifully in the Streamlit frontend.

The entire flow is shown asynchronous, responsive, and includes proper error handling and logging.

### Tech Stack
| Category      | Technology                                    |
|---------------|-----------------------------------------------|
| Frontend      | Streamlit                                     |
| Backend       | Python, FastAPI + Uvicorn                     |
| AI & Data     | Google Gemini (3-flash-preview), Pydantic     |
| Payments      | Stripe API (with Webhook)                     |
| Hosting       | Streamlit Cloud (frontend) + Render (Backend) |
| Environment   | UV (Python Package Manager)                   |
|---------------------------------------------------------------|


### Project Structure
```
text-processing/
|-- interface.py        # Streamlit frontend
|-- resume_reviewer.py  # FastAPI Backend
|-- settings.py         # Shared configuration (Pydantic)
|-- pyproject.toml
|-- uv.lock
|-- .env                # Environment Variable
|-- README.md 
```

### Local Setup & Installation

1. Prerequsites
    - Python 3.10+
    - uv package manager
```
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone & Setup
```
git clone https://github.com/panzek/text-processing
cd resume-reviewer
uv sync
```

3. Environment Variables
Create a .env file in the root directory and add credentials:
```
GEMINI_API_KEY=your_gemini_api_key_here
API_URL=http://127.0.0.1:8000/review
STRIPE_API_KEY=sk_test...
STRIPE_WH_SECRET=whsec...

```

### Running Locally
#### Terminal 1 - Backend
```
uv run uvicorn resume_reviewer:app --reload 
```
### Terminal 2 - Frontend
```
uv run -- streamlit run interface.py
```

### Deployment
#### Backend (Render)
- Build Command: uv sync --frozen && uv cache prune --ci
- Start Command: uvicorn resume_reviewer:app --host 0.0.0.0 --port $PORT

#### Frontend (Streamlit Cloud)
- Connect your GitHub repository
- Set the Main file path to interface.py
- Add the API_URL in **Secrets** pointing to your live Render URL

### Security Features
- File Validation: Enforces a 10MB file size limit and specific file extensions to prevent malicious uploads
- CORS Middleware: Configured to only allow requests from authorized Streamlit and Render domains
- Stripe Webhook: Uses cryptographic signature verification to ensure payment events are genuine
- Environment-based configuration
- Input sanitisation and detailed error handling