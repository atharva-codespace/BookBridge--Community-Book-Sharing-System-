"""
utils/email_sender.py

Sends OTP to user's email using Gmail SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Your Gmail Address
SENDER_EMAIL = "mydemoemail9@gmail.com"

# Gmail App Password (16 characters)
APP_PASSWORD = "qwrhustvqisvspqh"

def send_email_otp(receiver_email, otp):
    """
    Sends OTP to the given email address.
    """

    subject = "BookBridge - Email Verification OTP"

    body = f"""
Hello,

Welcome to BookBridge!

Your One-Time Password (OTP) for Email Verification is:

=================================
             {otp}
=================================

This OTP will expire in 5 minutes.

If you did not request this OTP, please ignore this email.

Thank You,

BookBridge Team
"""

    message = MIMEMultipart()

    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

        server.starttls()

        server.login(
            SENDER_EMAIL,
            APP_PASSWORD
        )

        server.send_message(message)

        server.quit()

    except smtplib.SMTPAuthenticationError:

        print("Authentication Failed.")
        print("Check your Gmail App Password.")

        raise

    except smtplib.SMTPException as e:

        print("SMTP Error :", e)

        raise

    except Exception as e:

        print("Unexpected Error :", e)

        raise