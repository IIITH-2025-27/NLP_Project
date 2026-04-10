"""
API Models (Request/Response Schemas)

This file contains all Pydantic models used for API request validation and response formatting.
These models define the structure and validation rules for data flowing through the API endpoints.

Categories:
- Authentication Models: Signup, Login, OTP verification
- Analysis Models: Text and image analysis requests
- Chat Models: Chat and message creation/updates
"""

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, Literal

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()


class RequestOTPRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        if len(v) != 6:
            raise ValueError('OTP must be 6 digits')
        return v


class ResendOTPRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        if len(v) != 6:
            raise ValueError('OTP must be 6 digits')
        return v


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        if len(v) != 6:
            raise ValueError('OTP must be 6 digits')
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v

class AnalyzeRequest(BaseModel):
    text: str
    chat_id: Optional[str] = None  # Optional: which chat this belongs to

class EmotionRequest(BaseModel):
    """Request model for lyric generation based on emotion"""
    emotion: str
    
    @field_validator('emotion')
    @classmethod
    def validate_emotion(cls, v):
        from constants import EMOTIONS
        valid_emotions = EMOTIONS
        if v not in valid_emotions:
            raise ValueError(f'Emotion must be one of: {valid_emotions}')
        return v

class ImageAnalyzeRequest(BaseModel):
    """Request model for image-based emotion analysis"""
    pass  # Image will be uploaded as multipart/form-data, not JSON

class CreateChatRequest(BaseModel):
    title: str = "New Chat"

class UpdateChatRequest(BaseModel):
    title: Optional[str] = None

class CreateMessageRequest(BaseModel):
    content: str
    message_type: Literal['user', 'assistant']
    input_type: Literal['text', 'image']
    image_preview: Optional[str] = None  # Base64 image preview URL
    emotion: Optional[dict] = None  # For assistant messages
    lyrics: Optional[str] = None  # For assistant messages
    preprocessed_image: Optional[str] = None  # Base64 preprocessed image for face detection


class UpdateMessageRequest(BaseModel):
    content: Optional[str] = None
    input_type: Optional[Literal['text', 'image']] = None
    image_preview: Optional[str] = None
    emotion: Optional[dict] = None
    lyrics: Optional[str] = None
    preprocessed_image: Optional[str] = None
