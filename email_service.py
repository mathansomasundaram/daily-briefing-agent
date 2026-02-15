"""
Email service module for handling email operations.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(subject, body, receivers):
    """
    Send an HTML email to multiple recipients.

    Args:
        subject (str): Email subject line
        body (str): Email body content (HTML formatted)
        receivers (list): List of recipient email addresses
    """
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)  # Convert list to comma-separated string
    msg["Subject"] = subject

    # Convert newlines to <br> for HTML
    html_body = body.replace('\n', '<br>\n')

    # Wrap in basic HTML structure
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
          a {{ color: #0066cc; text-decoration: none; }}
          a:hover {{ text-decoration: underline; }}
          hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
          b {{ color: #000; }}
        </style>
      </head>
      <body>
        {html_body}
      </body>
    </html>
    """

    # Attach both plain text (fallback) and HTML version
    plain_text = body.replace('<b>', '').replace('</b>', '').replace('<hr>', '---').replace('<a href=', '').replace('</a>', '')
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    print(f"Sending email to: {receivers}...")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("Email sent successfully!")