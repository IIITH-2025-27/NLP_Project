from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from database_service import users_col, otp_col
from api.models import SignupRequest, LoginRequest, RequestOTPRequest, VerifyOTPRequest, ResendOTPRequest
from auth import hash_password, verify_password, create_access_token, generate_otp, store_otp, verify_otp
from email_service import send_otp_email
from config import OTP_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── OTP-Based Authentication ──────────────────────────────────────────────────

@router.post("/request-otp")
async def request_otp(body: RequestOTPRequest):
    """Request OTP for signup - sends email with verification code"""
    # Check if email is already registered
    if users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate OTP
    otp = generate_otp()
    
    # Hash password and store OTP with user data
    password_hash = hash_password(body.password)
    store_otp(body.email, otp, body.name, password_hash)
    
    # Send OTP via email
    try:
        await send_otp_email(body.email, otp, body.name)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to send OTP email. Please check SMTP configuration: {str(e)}"
        )
    
    return {
        "message": "OTP sent successfully to your email",
        "email": body.email
    }


@router.post("/verify-otp")
def verify_otp_and_signup(body: VerifyOTPRequest):
    """Verify OTP and complete user signup"""
    # Verify OTP and get stored user data
    user_data = verify_otp(body.email, body.otp)
    
    # Check again if email was registered during OTP verification period
    if users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = {
        "name": user_data["name"],
        "email": user_data["email"],
        "password": user_data["password_hash"],
        "created_at": datetime.utcnow(),
        "verified": True
    }
    result = users_col.insert_one(user)
    token = create_access_token({"sub": str(result.inserted_id)})
    
    return {
        "message": "Signup successful",
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "name": user_data["name"],
            "email": user_data["email"]
        }
    }


@router.post("/resend-otp")
async def resend_otp(body: ResendOTPRequest):
    """Resend OTP to user's email"""
    # Check if there's a pending OTP request
    otp_record = otp_col.find_one({"email": body.email})
    if not otp_record:
        raise HTTPException(status_code=400, detail="No OTP request found. Please start signup again.")
    
    # Generate new OTP
    new_otp = generate_otp()
    
    # Update OTP record
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    
    otp_col.update_one(
        {"email": body.email},
        {
            "$set": {
                "otp": new_otp,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "attempts": 0
            }
        }
    )
    
    # Send new OTP
    try:
        await send_otp_email(body.email, new_otp, otp_record["name"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send OTP email: {str(e)}"
        )
    
    return {
        "message": "OTP resent successfully",
        "email": body.email
    }


@router.post("/signup")
def signup(body: SignupRequest):
    """Register a new user (legacy endpoint - use OTP-based signup instead)"""
    if users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "created_at": datetime.utcnow(),
        "verified": False
    }
    result = users_col.insert_one(user)
    token = create_access_token({"sub": str(result.inserted_id)})
    
    return {
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "name": body.name,
            "email": body.email
        }
    }


@router.post("/login")
def login(body: LoginRequest):
    """Authenticate user and return token"""
    user = users_col.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user["_id"])})
    
    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }
