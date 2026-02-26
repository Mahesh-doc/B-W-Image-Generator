import cv2
import numpy as np
import os
import webbrowser
from flask import Flask, request, render_template_string
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# ================== EMAIL CONFIG ==================
SENDER_EMAIL = "mahesh3500m@gmail.com"
SENDER_PASSWORD = "slqs taon tdau dxxf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# ==================================================

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def convert_to_sketch(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    invert = cv2.bitwise_not(blur)
    sketch = cv2.divide(gray, invert, scale=256.0)

    sketch_path = os.path.join(UPLOAD_FOLDER, "sketch.jpg")
    cv2.imwrite(sketch_path, sketch)

    return sketch_path


def send_email(receiver_email, image_path):
    try:
        msg = EmailMessage()
        msg['Subject'] = "Your AI Sketch Image"
        msg['From'] = f"Mahesh - NMC <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg.set_content(
            "Hello,\n\nYour AI generated sketch image is attached.\n\nThank you!"
        )

        with open(image_path, 'rb') as f:
            file_data = f.read()

        msg.add_attachment(file_data,
                           maintype='image',
                           subtype='jpeg',
                           filename="AI_Sketch.jpg")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()  # Secure connection
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        return "✅ Email sent successfully!"

    except Exception as e:
        return f"❌ Email failed: {str(e)}"


HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Sketch Generator - Mahesh</title>
</head>
<body style="text-align:center; font-family:Arial;">

    <h1>🎨 AI Sketch Black & White Generator</h1>
    <h3>By Mahesh - NMC</h3>

    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required><br><br>
        <input type="email" name="email" placeholder="Enter Audience Email" required><br><br>
        <button type="submit">Generate & Send</button>
    </form>

    {% if sketch %}
        <h2>Sketch Preview:</h2>
        <img src="{{ sketch }}" width="300"><br><br>
    {% endif %}

    {% if message %}
        <script>
            alert("{{ message }}");
        </script>
    {% endif %}

</body>
</html>
'''


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            file = request.files["image"]
            email = request.form["email"]

            original_path = os.path.join(UPLOAD_FOLDER, "original.jpg")
            file.save(original_path)

            sketch_path = convert_to_sketch(original_path)

            if sketch_path is None:
                return render_template_string(
                    HTML_PAGE,
                    sketch=None,
                    message="Image processing failed."
                )

            email_status = send_email(email, sketch_path)

            return render_template_string(
                HTML_PAGE,
                sketch=sketch_path,
                message=email_status
            )

        except Exception as e:
            return f"Application Error: {str(e)}"

    return render_template_string(HTML_PAGE, sketch=None)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
