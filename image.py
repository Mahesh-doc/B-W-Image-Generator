import streamlit as st
import cv2
import numpy as np
import smtplib
from email.message import EmailMessage
import os
from PIL import Image, ImageDraw, ImageFont

# ================= SETTINGS =================
SENDER_EMAIL = "mahesh3500m@gmail.com"
SENDER_PASSWORD = "slqs taon tdau dxxf"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Artifex Sketch Edtion by Mahesh", layout="wide")

# ================= DARK THEME =================
st.markdown("""
<style>
/* Main app background and text */
.stApp {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Segoe UI', sans-serif;
    letter-spacing: 0.5px;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0A0A0A;
    border-right: 1px solid #333;
}

/* Headings */
h1, h2, h3 {
    color: #FFFFFF;
    text-shadow: 0 0 5px #FFFFFF;
}

/* Image container */
.img-box {
    border: 2px solid #AAAAAA;
    border-radius: 15px;
    padding: 15px;
    background: #111111;
    box-shadow: 0 0 10px #222;
}

/* Buttons */
div.stButton > button:first-child {
    background: #FFFFFF;
    color: #000000;
    border-radius: 8px;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
    box-shadow: 0 0 5px #FFF;
}

/* Input fields and sliders */
input, .stSlider {
    background-color: #111111;
    color: #FFFFFF;
    border: 1px solid #555;
    border-radius: 5px;
}

/* Toggle switches */
.stToggle {
    background-color: #222;
    border: 1px solid #555;
}

/* Film grain effect */
body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: url('https://www.transparenttextures.com/patterns/asfalt-dark.png');
    opacity: 0.05;
    pointer-events: none;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if 'generated_sketch' not in st.session_state:
    st.session_state.generated_sketch = None

if 'sketch_path' not in st.session_state:
    st.session_state.sketch_path = None


# ================= SKETCH FUNCTIONS =================
def convert_to_sketch(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(21,21),0)
    sketch = cv2.divide(gray,blur,scale=256)

    edges = cv2.Canny(gray,80,180)
    edges = cv2.bitwise_not(edges)

    return cv2.addWeighted(sketch,0.7,edges,0.3,0)


def artistic_sketch(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = 255-gray
    blur = cv2.GaussianBlur(inv,(25,25),0)
    sketch = cv2.divide(gray,255-blur,scale=256)

    sketch_color = cv2.applyColorMap(sketch,cv2.COLORMAP_OCEAN)

    return cv2.cvtColor(sketch_color,cv2.COLOR_BGR2GRAY)


# ================= A4 SIZE =================
def convert_to_a4(image):

    h, w = image.shape[:2]

    # Detect orientation
    if h > w:
        # Portrait A4
        A4_WIDTH = 2480
        A4_HEIGHT = 3508
    else:
        # Landscape A4
        A4_WIDTH = 3508
        A4_HEIGHT = 2480

    scale = min(A4_WIDTH / w, A4_HEIGHT / h)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(image, (new_w, new_h))

    canvas = np.ones((A4_HEIGHT, A4_WIDTH), dtype=np.uint8) * 255

    x_offset = (A4_WIDTH - new_w) // 2
    y_offset = (A4_HEIGHT - new_h) // 2

    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    return canvas

# ================= SIGNATURE =================
def add_signature(image):

    pil_img = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/seguisbi.ttf",70)
    except:
        font = ImageFont.load_default()

    text = "Created On ARTIFEX by Mahesh"

    width,height = pil_img.size

    text_width,text_height = draw.textbbox((0,0),text,font=font)[2:]

    x = width - text_width - 60
    y = height - text_height - 60

    draw.text((x,y),text,fill=0,font=font)

    return np.array(pil_img)


# ================= EMAIL =================
def send_email(receiver_email,image_path):

    try:

        msg = EmailMessage()
        msg['Subject'] = "Your AI Sketch by Artifex"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        msg.set_content("Attached is your Artifex generated sketch by Mahesh & Baskar.")

        with open(image_path,'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='image',
                subtype='jpeg',
                filename="Sketch.jpg"
            )

        with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as smtp:

            smtp.starttls()
            smtp.login(SENDER_EMAIL,SENDER_PASSWORD)
            smtp.send_message(msg)

        return True

    except:
        return False


# ================= UI =================
st.title("Artifex B & W Sketch Generation")

with st.sidebar:

    st.header("Settings")

    email_user = st.text_input("Receiver Email")

    style = st.radio("Sketch Style",
                     ["Quick Sketch","Artistic Sketch"])


col1,col2 = st.columns(2)

with col1:

    st.subheader("Upload Image")

    up_file = st.file_uploader("Upload Photo",
                               type=["jpg","png","jpeg"])


with col2:

    st.subheader("Camera")

    cam_file = st.camera_input("Take Photo")


source = up_file if up_file else cam_file


# ================= PROCESS =================
if source:

    raw_bytes = np.frombuffer(source.getvalue(),np.uint8)

    img_bgr = cv2.imdecode(raw_bytes,cv2.IMREAD_COLOR)

    img_rgb = cv2.cvtColor(img_bgr,cv2.COLOR_BGR2RGB)

    if st.button("CREATE SKETCH"):

        with st.spinner("Processing..."):

            if style=="Quick Sketch":
                res = convert_to_sketch(img_bgr)
            else:
                res = artistic_sketch(img_bgr)

            a4_image = convert_to_a4(res)

            a4_image = add_signature(a4_image)

            st.session_state.generated_sketch = a4_image

            path = os.path.join(UPLOAD_FOLDER,"temp_sketch.jpg")

            cv2.imwrite(path,a4_image)

            st.session_state.sketch_path = path


# ================= RESULT =================
if st.session_state.generated_sketch is not None:

    st.divider()

    r1,r2 = st.columns(2)

    with r1:

        st.markdown('<div class="img-box">',unsafe_allow_html=True)

        st.image(img_rgb,caption="Original")

        st.markdown('</div>',unsafe_allow_html=True)

    with r2:

        st.markdown('<div class="img-box">',unsafe_allow_html=True)

        st.image(st.session_state.generated_sketch,
                 caption="Sketch by Artifex")

        st.markdown('</div>',unsafe_allow_html=True)


    st.subheader("Export")

    colA,colB = st.columns(2)

    with colA:

        with open(st.session_state.sketch_path,"rb") as f:

            st.download_button(
                "Download Image",
                f,
                "Sketch_A4.jpg",
                "image/jpeg"
            )


    with colB:

        if st.button("Send Email"):

            if email_user:

                if send_email(email_user,
                              st.session_state.sketch_path):

                    st.success("Email Sent!")

                else:

                    st.error("Email Failed")

            else:

                st.warning("Enter Email")


st.divider()

st.markdown("""
<style>
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #0E1117;
    color: #FFFFFF;
    padding: 10px 20px;
    font-size: 14px;
}
.footer-left {
    text-align: left;
    flex: 1;
}
.footer-center {
    text-align: center;
    flex: 1;
}
.footer-right {
    text-align: right;
    flex: 1;
}
.footer a {
    color: #58a6ff;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    <div class="footer-left">
        Mahesh — Data Science Student, NMC
    </div>
    <div class="footer-center">
        ARTIFEX — The Sketch Generator
    </div>
    <div class="footer-right">
        <a href="mailto:mahesh@example.com">mahesh@example.com</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("© 2026 Artifex — The Sketch Generator by Mahesh & Baskar. All rights reserved. Thank you for using ARTIFEX.")