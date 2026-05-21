import streamlit as st
import requests

from config import settings

API_URL = settings.API_URL

# Set to run backend dynamically
if settings.DEVELOPMENT_MODE:
    BACKEND= "http://127.0.0.1:8000"
else:
    BACKEND = "https://panzek.onrender.com"

# initialise application memory
if "payment_satus" not in st.session_state:
    st.session_state.payment_status = "idle"
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
# Configure streamlit page
st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

if st.session_state.payment_status == "idle":
    st.title("💼 Résumé Reviewer")
    st.write("Professional AI-powered review and cover letter generation for €5.00.")
    
    # Dynamic placeholder block
    button_placeholder = st.empty()
    
    if button_placeholder.button("Pay and Get Started", key="pay_init_btn"):
        try:
            response = requests.get(f"{BACKEND}/create-checkout-session")
            data = response.json()
            checkout_url = data.get("url")
            st.session_state.session_id = data.get("id")
            
            button_placeholder.markdown(f'''
                <a href="{checkout_url}" target="_self"
                    style="
                    display:inline-block;
                        text-decoration:none;
                        background-color: #0074d4; 
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-weight:600;
                    ">
                    Click to Go to Secure Payment
                </a>
                <p 
                style="
                color:red; 
                margin: 0px 0px 0.2rem;
                ">
                </p>
                ''', 
                unsafe_allow_html=True
            )
            
        except Exception as e:  # noqa: E722
            button_placeholder.button("Pay and Get Started", key="pay_retry_btn")
            st.error(f"Could not reach the payment server: {e}")
        
st.title("💼 Résumé Reviewer")  
st.write("Upload your resume below for AI-powered review, rewrite with improvements, "
         "and a draft of a compelling, professional cover letter tailored to it."
         )

# Define your footer HTML and CSS
footer = """
<style>
.footer {
    width: 100%;
    border-top: 1px solid #e9ecef;
    color: #6c757d;
    text-align: center;
    padding: 50px 10px 20px 10px;
    font-size: 14px;
}
</style>

<div class="footer">
    <p>&copy;Panzek Solutions 2026 | <a href="https://panzeksolutions.com/" target="_blank">Website</a></p></p>
    
</div>
"""

uploaded_file = st.file_uploader(
    "Choose a file",
    type= ["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    if st.button("Review"):
        # Spinner wrapped code that performs network request
        with st.spinner("Reviewing document... Please wait.", show_time=True):
            
            # Prepare the file to be sent via HTTP
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            try:
                # Send the POST requests to FastAPI
                response = requests.post(settings.API_URL, files=files, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("Done!")
                    st.subheader("AI Review & Cover Letter")
                    st.markdown(result.get("review", "No summary returned"))
            
                else:
                    st.error(f"Server Error: {response.status_code}")
        
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI.")

# Render the footer
st.markdown(footer, unsafe_allow_html=True)
                