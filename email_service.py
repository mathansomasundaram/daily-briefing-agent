"""
Email service module for handling email operations.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(subject, body, receivers):
    """
    Send an email to multiple recipients.

    Args:
        subject (str): Email subject line
        body (str): Email body content
        receivers (list): List of recipient email addresses
    """
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)  # Convert list to comma-separated string
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    print(f"Sending email to: {receivers}...")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("Email sent successfully!")