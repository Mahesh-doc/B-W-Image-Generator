import streamlit as st
import cv2
import numpy as np
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

# ================= SETTINGS & CONFIG =================
SENDER_EMAIL = "mahesh3500m@gmail.com"
SENDER_PASSWORD = "slqs taon tdau dxxf" 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Page Config
st.set_page_config(page_title="AI Sketch Dark Edition", page_icon="🌙", layout="wide")

# ================= DARK THEME CUSTOM CSS =================
# This forces the page to be dark and adds neon borders to see everything clearly
st.markdown("""
    <style>
    /* Force Dark Background for the whole app */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1A1C24 !important;
        border-right: 1px solid #3d3d3d;
    }

    /* High Contrast Containers for Images */
    .img-box {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 15px;
        background-color: #161b22;
        margin-bottom: 20px;
    }

    /* Custom Neon Green Button for Generate */
    div.stButton > button:first-child {
        background-color: #2ea043;
        color: white;
        border-radius: 8px;
        border: 1px solid #3fb950;
        width: 100%;
        height: 3em;
        font-size: 18px;
        font-weight: bold;
    }

    /* Custom Blue Button for Email */
    .email-section div.stButton > button:first-child {
        background-color: #238636; /* Different shade for email */
        border: 1px solid #2ea043;
    }

    /* Input text color fix */
    input {
        color: white !important;
        background-color: #0d1117 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= STATE MANAGEMENT =================
if 'generated_sketch' not in st.session_state:
    st.session_state.generated_sketch = None
if 'sketch_path' not in st.session_state:
    st.session_state.sketch_path = None

# ================= LOGIC FUNCTIONS =================
def convert_to_sketch(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    sketch = cv2.divide(gray, blur, scale=256)
    edges = cv2.Canny(gray, 80, 180)
    edges = cv2.bitwise_not(edges)
    return cv2.addWeighted(sketch, 0.7, edges, 0.3, 0)

def artistic_sketch(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (25,25), 0)
    sketch = cv2.divide(gray, 255-blur, scale=256)
    sketch_color = cv2.applyColorMap(sketch, cv2.COLORMAP_OCEAN)
    return cv2.cvtColor(sketch_color, cv2.COLOR_BGR2GRAY)

def send_email(receiver_email, image_path):
    try:
        msg = EmailMessage()
        msg['Subject'] = " Your AI Masterpiece"
        msg['From'] = f"Sketch Studio AI <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg.set_content("Hi! Attached is your AI-generated sketch.")
        with open(image_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename="Sketch.jpg")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return True
    except: return False

# ================= UI LAYOUT =================
st.title("B & W  Sketch Generation")
st.markdown("If you couldn't see anything before, this **High-Contrast Dark Theme** will fix it.")

# Sidebar
with st.sidebar:
    st.header(" Settings")
    email_user = st.text_input("Receiver Email", placeholder="email@domain.com")
    style = st.radio("Sketch Style", ["Quick Sketch", "Artistic Sketch"])
    st.divider()
    st.info("The dark background prevents 'white-out' on bright screens.")

# Body
col_in1, col_in2 = st.columns(2)

with col_in1:
    st.subheader("1. Pick Image")
    up_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])
    
with col_in2:
    st.subheader("2. Take Photo")
    cam_file = st.camera_input("Smile!")

source = up_file if up_file else cam_file

if source:
    # Read Image
    raw_bytes = np.frombuffer(source.getvalue(), np.uint8)
    img_bgr = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    if st.button("🚀 CREATE SKETCH"):
        with st.spinner("Processing..."):
            res = convert_to_sketch(img_bgr) if style == "Quick Sketch" else artistic_sketch(img_bgr)
            st.session_state.generated_sketch = res
            path = os.path.join(UPLOAD_FOLDER, "temp_sketch.jpg")
            cv2.imwrite(path, res)
            st.session_state.sketch_path = path

# ================= RESULTS =================
if st.session_state.generated_sketch is not None:
    st.divider()
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.markdown('<div class="img-box">', unsafe_allow_html=True)
        st.image(img_rgb, caption="Original", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with r_col2:
        st.markdown('<div class="img-box">', unsafe_allow_html=True)
        st.image(st.session_state.generated_sketch, caption="Sketch Result", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer Actions
    st.subheader("3. Export Results")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        with open(st.session_state.sketch_path, "rb") as f:
            st.download_button("📥 Download Image", f, "Sketch.jpg", "image/jpeg")

    with f_col2:
        st.markdown('<div class="email-section">', unsafe_allow_html=True)
        if st.button("📧 Send to Email"):
            if email_user:
                if send_email(email_user, st.session_state.sketch_path):
                    st.success("Sent successfully!")
                else:
                    st.error("Failed to send.")
            else:
                st.warning("Enter email in sidebar!")
        st.markdown('</div>', unsafe_allow_html=True)