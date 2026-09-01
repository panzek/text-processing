import os
import streamlit as st
import requests

# Set to run backend dynamically
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_URL = f"{BACKEND_URL}/review"

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

# Inject custom CSS
st.markdown("""
    <style>
        /* Reduce vertical padding between elements */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        /* Tighten spacing between text elements */
        .stMarkdown p {
            margin-bottom: 0.25rem;
        }
        /* Reduce gap after titles and headers */
        h1, h2, h3, h4, h5, h6 {
            margin-bottom: 0.4rem;
        }
    </style>
""", unsafe_allow_html=True)

# Configure streamlit page
st.set_page_config(
    page_title="AI Document Reviewer", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# initialise application memory
if "payment_status" not in st.session_state:
    st.session_state.payment_status = "idle"
    
if "checkout_url" not in st.session_state:
    st.session_state.checkout_url = None
    
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Global verification layer - Handle redirect from Stripe
query_params = st.query_params
if "payment" in query_params and "session_id" in query_params:
    sid = query_params["session_id"] 
    
    # Only verify once
    if st.session_state.payment_status != "paid":
        # verify payment status with the FastAPI backend
        with st.spinner("Verifying payment...", show_time=True):
            try:
                res = requests.get(
                    f"{BACKEND_URL}/verify-payment/{sid}"
                )
                if res.status_code == 200 and res.json().get("status") == "paid":
                    st.session_state.payment_status = "paid"
                    st.session_state.session_id = sid
                    st.rerun()
            except Exception as e:
                st.error(f"Connection error: {e}")
            
# The idle layout block   
if st.session_state.payment_status == "idle":
    st.title("💼 Résumé Reviewer")
    st.write("Professional AI-powered review and cover letter generation for €5.00.")
    
    # Show pay button only if checkout_url doesn't exist
    if st.session_state.checkout_url is None:
    
        if st.button(
            "Pay and Get Started", 
            key="pay_init_btn"
        ):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/create-checkout-session"
                )
                st.write("Resonse status:", response.status_code)
                data = response.json()
                # st.write("Returned data:", data)
                
                checkout_url = data.get("url")
                
                if checkout_url:
                    st.session_state.checkout_url = checkout_url
                    st.session_state.session_id = data.get("id")  
                    st.rerun()
                else:
                    st.error("Stripe checkout URL missing.")
                    
            except Exception as e:
                st.error(f"Could not reach payment server: {e}")
                
    else:
                
        st.success("Secure payment session ready.")
        
        st.link_button(
            "Click to Go to Secure Payment",
            st.session_state.checkout_url,
            use_container_width=True,
        )
                    
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
        with st.spinner("Reviewing Your Résumé... Please wait.", show_time=True):
            
            # Prepare the file to be sent via HTTP
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            data = {
                "session_id": st.session_state.session_id
            }
            
            try:
                # Send the POST requests to FastAPI
                response = requests.post(
                    API_URL,
                    params={"session_id": st.session_state.session_id},  
                    files=files,
                    data=data, 
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()  
                    rewritten_resume = result.get("rewritten_resume")
                    suggested_cover_letter = result.get("suggested_cover_letter")
                    career_coach_tips = result.get("career_coach_tips")
                    if rewritten_resume and suggested_cover_letter and career_coach_tips:
                        
                        st.balloons()
                        st.success("Review Complete!")
                        
                        # Add tabs elements
                        tab1, tab2, tab3 = st.tabs(["**Rewritten Resume**", "**Cover Letter**", "**Career Coach Tips**"])

                        with tab1:
                            st.subheader("Your Professional Rewritten Résumé")
                            st.write(rewritten_resume)
                            
                        with tab2:
                            st.subheader("Your Tailored Cover Letter")
                            st.write(suggested_cover_letter)
                            
                        with tab3:
                            st.subheader("Career Coach Tips")
                            st.write(career_coach_tips)
                        
                    else:   
                        st.warning("The analysis completed, but some fields were missing from the payload.")
            
                else:
                    st.error(f"Error processing your request: {response.text}")
        
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI.")

# Render the footer
st.markdown(footer, unsafe_allow_html=True)
                