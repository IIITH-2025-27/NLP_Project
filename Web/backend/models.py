from pydantic import BaseModel, field_validator

class SignupRequest(BaseModel):
    name: str
    email: str
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

class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) > 72:
            raise ValueError('Password cannot exceed 72 characters')
        return v

class AnalyzeRequest(BaseModel):
    text: str

class ImageAnalyzeRequest(BaseModel):
    """Request model for image-based emotion analysis"""
    pass  # Image will be uploaded as multipart/form-data, not JSON
