"""
Modules/mail.py
Sends the generated PDF report as an email attachment.
"""

import smtplib
import os
from email.message import EmailMessage

from utils.email_sender import SENDER_EMAIL, APP_PASSWORD


def send_report_email(receiver, pdf_path, report_title):
    # NOTE: previously read GMAIL_USER / GMAIL_APP_PASSWORD from the
    # environment, but those variables are never set anywhere in this
    # project, so sender/password were always None and login always failed.
    # Reuse the same Gmail credentials already used (and working) for OTP
    # emails in utils/email_sender.py instead.
    sender = SENDER_EMAIL
    password = APP_PASSWORD

    msg = EmailMessage()
    msg["Subject"] = f"BookBridge {report_title} Report"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(f"Hello,\n\nYour BookBridge {report_title} Report (with graph) is attached.")

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    msg.add_attachment(file_data, maintype="application", subtype="pdf",
                        filename=os.path.basename(pdf_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("Report Sent Successfully to", receiver)