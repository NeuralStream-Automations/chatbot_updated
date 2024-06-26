import os
from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Load environment variables
EMAIL = "ramanuj@neural-stream.com"
PASSWORD = "mxxu ymmj rmzk vpgb"

# Initialize an empty list to store responses
responses = []

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

        # Update responses list
        response = {
            'name': name,
            'mobile': mobile,
            'email': email,
            'department': department,
            'doctor': doctor,
            'timeslot': timeslot,
            'appointment_date': appointment_date
        }
        responses.append(response)

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

if __name__ == '__main__':
    app.run(debug=True)
