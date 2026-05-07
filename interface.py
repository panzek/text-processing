import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    # layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 Résumé Reviewer")  
st.write("Upload your resume below for AI-powered review and suggestions. "
         "We may draft a compelling cover letter to support your resume."
         )


API_URL = "https://panzek.onrender.com/summarise"

# Define your footer HTML and CSS
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    # background-color: #f1f1f1;
    color: black;
    text-align: center;
    padding: 10px;
    font-size: 14px;
}
</style>

<div class="footer">
    <p>&copy;Panzek Solutions 2026</p>
</div>
"""

# Render the footer
st.markdown(footer, unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Choose a file",
    type= ["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    if st.button("Review"):
        with st.spinner("In progress...", show_time=True):
            time.sleep(5)
        st.success("Done!")
        # Prepare the file to be sent via HTTP
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        try:
            # Send the POST requests to FastAPI
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                if "summarise" in result:
                    st.subheader("Results")
                    st.info(result["summarise"])
                    
                else:
                    st.error(f"Backend error: {result.get('error')}")
            
            else:
                st.error(f"Server Error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to FastAPI.")
                