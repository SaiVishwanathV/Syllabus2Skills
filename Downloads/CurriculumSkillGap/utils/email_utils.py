"""
Utility for sending OTP emails using smtplib.
Reads SMTP configuration from st.secrets.
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import streamlit as st


def send_otp_email(recipient_email: str, otp_code: str) -> bool:
    """
    Sends a 6-digit OTP to the recipient email using the SMTP settings in secrets.toml.
    Returns True if successful, False otherwise.
    """
    try:
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = st.secrets["SMTP_PORT"]
        sender_email = st.secrets["SMTP_EMAIL"]
        sender_password = st.secrets["SMTP_PASSWORD"]
    except KeyError as e:
        st.error(f"Missing SMTP configuration in secrets.toml: {e}")
        return False

    if not sender_email or not sender_password:
        st.error("SMTP_EMAIL or SMTP_PASSWORD is not set in secrets.toml.")
        return False

    # Create the root message and fill in headers
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your Verification Code: {otp_code}"
    msg["From"] = f"Syllabus to Skills <{sender_email}>"
    msg["To"] = recipient_email
    msg["Date"] = formatdate(localtime=True)

    # 1. Plain-text version
    text_content = f"""
Hi there,

Thank you for signing up for the Syllabus to Skills App.

Your verification code is: {otp_code}

If you didn't request this, please ignore this email.

Best regards,
The Syllabus to Skills Team
    """.strip()

    # 2. HTML version
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    .container {{
      font-family: 'Segoe UI', Arial, sans-serif;
      max-width: 500px;
      margin: 20px auto;
      padding: 30px;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      color: #1e293b;
      line-height: 1.6;
    }}
    .header {{
      color: #4f46e5;
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 20px;
      text-align: center;
    }}
    .otp-box {{
      text-align: center;
      margin: 30px 0;
      padding: 20px;
      background-color: #f8fafc;
      border-radius: 8px;
    }}
    .otp-code {{
      font-size: 36px;
      font-weight: 800;
      letter-spacing: 6px;
      color: #1e293b;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #64748b;
      text-align: center;
      border-top: 1px solid #f1f5f9;
      padding-top: 20px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">Verify Your Email</div>
    <p>Hi,</p>
    <p>Use the code below to complete your registration for the <strong>Curriculum-Industry Skill Gap Analysis</strong> app.</p>
    
    <div class="otp-box">
      <div class="otp-code">{otp_code}</div>
    </div>
    
    <p>This code will expire shortly. If you did not request this, you can safely ignore this message.</p>
    
    <div class="footer">
      &copy; 2026 Syllabus to Skills App.
    </div>
  </div>
</body>
</html>
    """.strip()

    # Record the MIME types of both parts - text/plain first, then text/html
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False
