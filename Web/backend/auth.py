from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
import string
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, OTP_LENGTH, OTP_EXPIRE_MINUTES
from database_service import users_col, otp_col

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Don't auto-raise 403, handle manually

def hash_password(password: str) -> str:
    """Hash a plain password (bcrypt has 72-byte limit)"""
    # Ensure password is within bcrypt's 72-byte limit
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password too long")
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Truncate if needed for verification (shouldn't happen with validation)
    if len(plain.encode('utf-8')) > 72:
        plain = plain[:72]
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get the current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="Invalid token - missing user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = users_col.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user
    except JWTError as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ─── OTP Functions ─────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Generate a random OTP of specified length"""
    return ''.join(secrets.choice(string.digits) for _ in range(OTP_LENGTH))


def store_otp(email: str, otp: str, name: str, password_hash: str):
    """Store OTP in database with expiration time"""
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    
    # Delete any existing OTP for this email
    otp_col.delete_many({"email": email})
    
    # Insert new OTP record
    otp_col.insert_one({
        "email": email,
        "otp": otp,
        "name": name,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "attempts": 0
    })


def verify_otp(email: str, otp: str, delete_after: bool = True) -> dict:
    """Verify OTP and return stored data if valid"""
    otp_record = otp_col.find_one({"email": email})
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="No OTP request found. Please request a new OTP.")
    
    # Check if OTP has expired
    if datetime.utcnow() > otp_record["expires_at"]:
        otp_col.delete_one({"_id": otp_record["_id"]})
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
    
    # Check attempt limit (max 5 attempts)
    if otp_record["attempts"] >= 5:
        otp_col.delete_one({"_id": otp_record["_id"]})
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. Please request a new OTP.")
    
    # Verify OTP
    if otp_record["otp"] != otp:
        # Increment attempts
        otp_col.update_one(
            {"_id": otp_record["_id"]},
            {"$inc": {"attempts": 1}}
        )
        remaining_attempts = 5 - (otp_record["attempts"] + 1)
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
        )
    
    # OTP is valid - prepare return data based on purpose
    purpose = otp_record.get("purpose", "signup")
    
    if purpose == "password_reset":
        # Password reset OTP
        result_data = {
            "email": otp_record["email"],
            "name": otp_record["name"],
            "purpose": "password_reset"
        }
    else:
        # Signup OTP
        result_data = {
            "name": otp_record["name"],
            "email": otp_record["email"],
            "password_hash": otp_record["password_hash"],
            "purpose": "signup"
        }
    
    # Delete OTP record if requested (default True)
    if delete_after:
        otp_col.delete_one({"_id": otp_record["_id"]})
    
    return result_data
