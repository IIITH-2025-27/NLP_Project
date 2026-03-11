# Backend Structure

A clean, modular FastAPI backend for the LyricMind NLP project.

## 📁 File Structure

```
backend/
├── main.py          # FastAPI app and API routes
├── config.py        # Configuration settings
├── database.py      # MongoDB connection and collections
├── models.py        # Pydantic request/response models
├── auth.py          # Authentication utilities (JWT, password hashing, OTP)
├── email_service.py # Email sending utilities for OTP
├── ml_service.py    # ML models (emotion detection, lyric generation)
├── requirements.txt # Python dependencies
├── .env            # Environment variables (not in git)
└── .env.example    # Example environment variables
```

## 📋 Module Descriptions

### `config.py`
- Environment configuration
- JWT settings
- Database connection strings
- CORS origins
- SMTP email configuration

### `database.py`
- MongoDB client initialization
- Database and collection references
- OTP collection with TTL index for automatic expiration

### `models.py`
- Pydantic models for request validation
- `SignupRequest`, `LoginRequest`, `AnalyzeRequest`
- `RequestOTPRequest`, `VerifyOTPRequest`, `ResendOTPRequest`

### `auth.py`
- Password hashing and verification
- JWT token creation and validation
- OTP generation and verification
- `get_current_user()` dependency for protected routes

### `email_service.py`
- Email sending functionality using SMTP
- OTP email templates (HTML and plain text)
- Configurable SMTP settings

### `ml_service.py`
- Emotion detection from text
- Lyric generation based on emotion
- Contains dummy models (replace with real ML models in production)

### `main.py`
- FastAPI application setup
- CORS middleware configuration
- API endpoints:
  - `GET /` - Health check
  - **`POST /auth/request-otp`** - Request OTP for signup
  - **`POST /auth/verify-otp`** - Verify OTP and complete signup
  - **`POST /auth/resend-otp`** - Resend OTP to email
  - `POST /auth/signup` - User registration (legacy, without OTP)
  - `POST /auth/login` - User authentication
  - `POST /analyze` - Analyze text and generate lyrics
  - `POST /analyze-image` - Analyze image and generate lyrics
  - `GET /history` - Get user's analysis history
  - `DELETE /history/{record_id}` - Delete history record

## 🚀 Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# CORS Configuration
ALLOWED_ORIGINS=dev

# SMTP Email Configuration (Required for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LyricMind

# OTP Configuration (Optional)
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
```

## 🔐 Authentication Flow

### OTP-Based Signup (Recommended):

1. User fills signup form (name, email, password)
2. Frontend calls `POST /auth/request-otp`
3. Backend generates 6-digit OTP, stores it in database with 10-minute expiration
4. Backend sends OTP to user's email
5. User enters OTP on frontend
6. Frontend calls `POST /auth/verify-otp`
7. Backend verifies OTP and creates user account
8. User is logged in with JWT token

### Features:
- ✅ Email verification ensures valid email addresses
- ✅ OTP expires after 10 minutes
- ✅ Maximum 5 attempts per OTP
- ✅ Resend OTP functionality with 60-second cooldown
- ✅ Beautiful HTML email templates
- ✅ Automatic OTP cleanup using MongoDB TTL indexes

### Traditional Signup (Legacy):

For testing or backwards compatibility, the legacy `POST /auth/signup` endpoint is still available but doesn't verify email addresses.

### 📧 Email Configuration for OTP

The application uses SMTP to send OTP emails for user verification. Here's how to set it up:

#### For Gmail:

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit [App Passwords](https://myaccount.google.com/apppasswords)
   - Select app: "Mail" and device: "Other (Custom name)"
   - Name it "LyricMind" and click Generate
   - Copy the 16-character password

3. **Update .env file**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # The app password from step 2
   ```

#### For Other Email Providers:

- **Outlook/Hotmail**: 
  ```env
  SMTP_HOST=smtp-mail.outlook.com
  SMTP_PORT=587
  ```

- **Yahoo Mail**: 
  ```env
  SMTP_HOST=smtp.mail.yahoo.com
  SMTP_PORT=587
  ```

- **Custom SMTP Server**: Update `SMTP_HOST` and `SMTP_PORT` accordingly

### CORS Configuration

By default, the backend allows connections from **any origin** (useful for development).

To restrict origins in production, set the `ALLOWED_ORIGINS` environment variable:
- Development mode: `ALLOWED_ORIGINS=dev`
- Single origin: `ALLOWED_ORIGINS=https://yourdomain.com`
- Multiple origins: `ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com`

## 📝 Notes

- All ML functions are currently using dummy implementations
- Replace `predict_emotion()` and `generate_lyrics()` in `ml_service.py` with actual ML models
- The structure is kept simple and modular for easy maintenance and testing
