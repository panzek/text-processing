import streamlit as st
import requests

from config import settings

API_URL = settings.API_URL

# Configure streamlit page
st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

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
                