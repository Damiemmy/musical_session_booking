import json
import smtplib

from email.mime.text import MIMEText


GMAIL_EMAIL = "damisaemmanuel778@gmail.com"

GMAIL_APP_PASSWORD = "ciuhsoudxdmkzicn"


def send_email(event, context):

    body = json.loads(event["body"])

    trigger = body["trigger"]

    recipient = body["email"]

    username = body.get("username", "User")


    if trigger == "SIGNUP_WELCOME":

        subject = "Welcome to HMS"

        message = f"""
Hello {username},

Welcome to the Hospital Management System.
"""

    elif trigger == "BOOKING_CONFIRMATION":

        subject = "Booking Confirmed"

        message = f"""
Hello {username},

Your appointment booking was successful.
"""

    else:

        subject = "Notification"

        message = "Notification from HMS"


    msg = MIMEText(message)

    msg["Subject"] = subject

    msg["From"] = GMAIL_EMAIL

    msg["To"] = recipient


    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(
        GMAIL_EMAIL,
        GMAIL_APP_PASSWORD
    )

    server.send_message(msg)

    server.quit()


    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Email sent successfully"
        })
    }