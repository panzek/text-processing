import streamlit as st
import requests

from setting import settings

API_URL = settings.API_URL

# Set to run backend dynamically
BACKEND_URL=settings.BACKEND_URL
# if settings.DEVELOPMENT_MODE:
#     BACKEND_URL= "http://127.0.0.1:8000"
# else:
#     BACKEND_URL = "https://panzek.onrender.com"

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

.footer p {
    margin: 0;
}
</style>

<div class="footer">
    <p>&copy;Xclusive Mag 2026 | registered number ...</p> 
    <p>Résumé Reviewer is Powered by Panzek Solutions | <a href="https://panzeksolutions.com/" target="_blank">Website</a></p></p> 
</div>
"""

# Configure streamlit page
st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# initialise application memory
if "payment_status" not in st.session_state:
    st.session_state.payment_status = "idle"
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Global verification layer - Handle redirect from Stripe
query_params = st.query_params
if "payment" in query_params and "session_id" in query_params:
    sid = query_params["session_id"] 
    if st.session_state.payment_status != "paid":
        # verify payment status with the FastAPI backend
        with st.spinner("Verifying payment...", show_time=True):
            try:
                res = requests.get(f"{BACKEND_URL}/verify-payment/{sid}")
                if res.status_code == 200 and res.json().get("status") == "paid":
                    st.session_state.payment_status = "paid"
                    st.session_state.session_id = "idle"
                    st.rerun()
            except Exception as e:
                st.error(f"Connection error: {e}")
            
# The idle layout block   
if st.session_state.payment_status == "idle":
    st.title("💼 Résumé Reviewer")
    st.write("Professional AI-powered review and cover letter generation for €5.00.")
    
    # Dynamic placeholder block
    button_placeholder = st.empty()
    
    if button_placeholder.button("Pay and Get Started", key="pay_init_btn"):
        try:
            response = requests.get(f"{BACKEND_URL}/create-checkout-session")
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
            
        except Exception as e:  
            button_placeholder.button("Pay and Get Started", key="pay_retry_btn")
            st.error(f"Could not reach the payment server: {e}")

# The paid layout block          
elif st.session_state.payment_status == "paid":     
    st.title("Upload Your Résumé")  
    st.success("Payment confirmed! You may now upload your résumé")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type= ["pdf", "docx", "txt"]
    )
    
    if uploaded_file and st.button("Review Your Résumé"):
        # Spinner wrapped code that performs network request
        with st.spinner("AI is reviewing Résumé... Please wait.", show_time=True):
            
            # Prepare the file to be sent via HTTP
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            try:
                # Send the POST requests to FastAPI
                response = requests.post(settings.API_URL, files=files, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    st.balloons()
                    st.success("Review Complete!")
                    st.markdown("### Optimised Review & Cover Letter")
                    st.markdown(result.get("review", "No summary returned"))
            
                else:
                    st.error(f"Server Error: {response.status_code}")
        
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI.")

# Render the footer
st.markdown(footer, unsafe_allow_html=True)
                