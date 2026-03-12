import aiosmtplib
from email.message import EmailMessage
from config import (
    SMTP_HOST, 
    SMTP_PORT, 
    SMTP_USER, 
    SMTP_PASSWORD, 
    SMTP_FROM_EMAIL, 
    SMTP_FROM_NAME
)

async def send_email(to_email: str, subject: str, body: str, html_body: str = None):
    """Send an email using SMTP"""
    if not SMTP_USER or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD in .env file")
    
    message = EmailMessage()
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    # Set plain text body
    message.set_content(body)
    
    # Set HTML body if provided
    if html_body:
        message.add_alternative(html_body, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,
        )
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


async def send_otp_email(to_email: str, otp: str, name: str, is_password_reset: bool = False):
    """Send OTP verification email"""
    if is_password_reset:
        subject = "Reset Your Password - LyricMind"
        greeting = "Password Reset Request"
        message = "We received a request to reset your password."
        instruction = "Enter this code to reset your password"
    else:
        subject = "Verify Your Email - LyricMind"
        greeting = "Welcome to LyricMind! 🎵"
        message = "We're excited to have you on board."
        instruction = "Enter this code to complete your registration"
    
    # Plain text version
    body = f"""Hello {name},

{message}

Your verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
The LyricMind Team
"""
    
    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 30px;
            color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .title {{
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        .otp-box {{
            background: white;
            color: #667eea;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 30px 0;
        }}
        .otp-code {{
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            margin: 10px 0;
        }}
        .message {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">𝄞</div>
            <h1 class="title">LyricMind</h1>
        </div>
        
        <p>Hello <strong>{name}</strong>,</p>
        
        <p>{message}</p>
        
        <div class="otp-box">
            <p style="margin: 0; font-size: 14px; color: #666;">Your verification code is:</p>
            <div class="otp-code">{otp}</div>
            <p style="margin: 0; font-size: 12px; color: #999;">{instruction}</p>
        </div>
        
        <div class="message">
            <p style="margin: 0;"><strong>⏱️ This code will expire in 10 minutes</strong></p>
        </div>
        
        <p>If you didn't request this code, please ignore this email.</p>
        
        <div class="footer">
            <p>© 2026 LyricMind - Your emotions. Your verse.</p>
        </div>
    </div>
</body>
</html>
"""
    
    await send_email(to_email, subject, body, html_body)
