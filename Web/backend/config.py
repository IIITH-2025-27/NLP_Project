import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "nlp-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Database Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "lyricmind"

# Email Configuration for OTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # Your email address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Your app password
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "LyricMind")

# OTP Configuration
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))  # OTP valid for 10 minutes
OTP_LENGTH = int(os.getenv("OTP_LENGTH", "6"))  # 6-digit OTP

# Hugging Face Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")  # Optional: For faster inference and higher rate limits

# CORS Configuration
# Allow any origin in development. In production, set ALLOWED_ORIGINS env variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "dev")

if ALLOWED_ORIGINS == "dev":
    # Development: Allow all localhost ports and common dev servers
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    USE_CREDENTIALS = True
elif ALLOWED_ORIGINS == "*":
    CORS_ORIGINS = ["*"]
    USE_CREDENTIALS = False  # Can't use credentials with wildcard
else:
    CORS_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]
    USE_CREDENTIALS = True
