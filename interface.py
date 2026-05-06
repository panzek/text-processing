import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    # layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 AI Resume Reviewer")  
st.write("Upload a your resume below for review")


API_URL = "http://localhost:8000/summarise"

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
                