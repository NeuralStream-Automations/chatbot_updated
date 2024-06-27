import os
import hmac
import hashlib
import json
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jsonschema
from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# --- Security Configuration ---

# # Basic Authentication
# USERNAME = os.getenv('WEBHOOK_USERNAME')
# PASSWORD = os.getenv('WEBHOOK_PASSWORD')  # Store securely (environment variable or secrets management)

# Signature Verification
SECRET_KEY = os.getenv('WEBHOOK_SECRET')

# JSON Schema Validation
SCHEMA_FILE = 'schema.json'

# Email Credentials
EMAIL = "ramanuj@neural-stream.com"
PASSWORD = "mxxu ymmj rmzk vpgb"

# --- Functions ---

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_password_hash(PASSWORD, auth.password):
            return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
        return func(*args, **kwargs)
    return wrapper

def verify_signature(payload, signature_header):
    """Verifies the webhook signature using HMAC-SHA256."""
    calculated_signature = hmac.new(
        SECRET_KEY.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    return calculated_signature == signature_header

def validate_json_schema(payload):
    """Validates the payload against the JSON schema."""
    with open(SCHEMA_FILE) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(payload, schema)
        return True
    except jsonschema.ValidationError as e:
        return False, str(e)

# --- Webhook Endpoint ---

@app.route('/webhook', methods=['POST'])
@authenticate
def webhook_endpoint():
    payload = request.get_json()
    signature_header = request.headers.get('X-Hook-Signature')

    # 1. Signature Verification
    if not verify_signature(payload, signature_header):
        return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400

    # 2. JSON Schema Validation
    is_valid, error_message = validate_json_schema(payload)
    if not is_valid:
        return jsonify({'status': 'error', 'message': error_message}), 400

    # 3. Payload Verification (Example - Check required fields and data types)
    if not payload.get('name'):
        return jsonify({'status': 'error', 'message': 'Missing name'}), 400
    if not isinstance(payload.get('appointment_date'), str):
        return jsonify({'status': 'error', 'message': 'Invalid date format'}), 400

    # 4. Your Webhook Logic (Process the payload)
    # ...

    return jsonify({'status': 'success'}), 200

# --- Appointment Form (same as your previous code) ---

@app.route('/', methods=['GET', 'POST'])
def questionnaire():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        department = request.form.get('department')
        doctor = request.form.get('doctor')
        timeslot = request.form.get('timeslot')
        appointment_date = request.form.get('appointment_date')

        # Prepare data for webhook payload
        payload = {
            'name': name,
            'mobile': mobile,
            'email': email,
            'department': department,
            'doctor': doctor,
            'timeslot': timeslot,
            'appointment_date': appointment_date
        }

        # Send webhook request
        # (You'll need to implement the logic to send the request from here)
        # ...

        # Send confirmation email
        send_confirmation_email(name, email, department, doctor, timeslot, appointment_date)

        # Prepare confirmation message for response
        confirmation_message = (
            f"Dear {name},\n\n"
            f"Your appointment has been scheduled as follows:\n"
            f"Department: {department}\n"
            f"Doctor: {doctor}\n"
            f"Date: {appointment_date}\n"
            f"Timeslot: {timeslot}\n\n"
            f"Thank you for choosing our hospital.\n"
            f"Best regards,\n"
            f"Neural Hospitals"
        )

        # Return confirmation message as JSON response
        return jsonify({
            'message': 'Appointment scheduled successfully!',
            'confirmation': confirmation_message
        }), 200
    else:
        departments = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General Medicine"]
        doctors = ["Dr. John Doe", "Dr. Jane Smith", "Dr. Alice Brown", "Dr. Bob Johnson", "Dr. Carol White"]
        timeslots = ["11-12", "12-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7"]

        return render_template('form.html', departments=departments, doctors=doctors, timeslots=timeslots)

def send_confirmation_email(name, email, department, doctor, timeslot, appointment_date):
    sender_email = EMAIL
    sender_password = PASSWORD

    receiver_email = email

    subject = "Appointment Confirmation"
    body = (
        f"Dear {name},\n\n"
        f"Your appointment has been scheduled as follows:\n"
        f"Department: {department}\n"
        f"Doctor: {doctor}\n"
        f"Date: {appointment_date}\n"
        f"Timeslot: {timeslot}\n\n"
        f"Thank you for choosing our hospital.\n"
        f"Best regards,\n"
        f"Neural Hospitals"
    )

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Using Gmail's SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- Main Function ---

if __name__ == '__main__':
    app.run(debug=True)