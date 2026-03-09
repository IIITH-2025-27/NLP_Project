from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId

from config import CORS_ORIGINS, USE_CREDENTIALS
from database import users_col, history_col
from models import SignupRequest, LoginRequest, AnalyzeRequest
from auth import hash_password, verify_password, create_access_token, get_current_user
from ml_service import predict_emotion, generate_lyrics, predict_emotion_from_image

# Initialize FastAPI app
app = FastAPI(title="LyricMind NLP API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=USE_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "LyricMind API is running 🎵"}


@app.post("/auth/signup")
def signup(body: SignupRequest):
    """Register a new user"""
    if users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "created_at": datetime.utcnow(),
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


@app.post("/auth/login")
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


@app.post("/analyze")
def analyze(body: AnalyzeRequest, current_user=Depends(get_current_user)):
    """Analyze text and generate lyrics based on detected emotion"""
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Model 1: Emotion Detection
    emotion_result = predict_emotion(body.text)

    # Model 2: Lyric Generation
    lyric_result = generate_lyrics(emotion_result["emotion"])

    # Save to history
    record = {
        "user_id": str(current_user["_id"]),
        "input_text": body.text,
        "emotion": emotion_result["emotion"],
        "emotion_confidence": emotion_result["confidence"],
        "emotion_scores": emotion_result["scores"],
        "lyrics": lyric_result["lyrics"],
        "created_at": datetime.utcnow(),
    }
    history_col.insert_one(record)

    return {
        "input_text": body.text,
        "emotion_detection": emotion_result,
        "lyric_generation": lyric_result,
    }


@app.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Analyze image, detect emotion, and generate lyrics based on detected emotion"""
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 10MB)
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be less than 10MB")
    
    # Model 1: Emotion Detection from Image
    emotion_result = predict_emotion_from_image(contents)
    
    # Model 2: Lyric Generation based on detected emotion
    lyric_result = generate_lyrics(emotion_result["emotion"])
    
    # Save to history
    record = {
        "user_id": str(current_user["_id"]),
        "input_type": "image",
        "input_filename": image.filename,
        "emotion": emotion_result["emotion"],
        "emotion_confidence": emotion_result["confidence"],
        "emotion_scores": emotion_result["scores"],
        "lyrics": lyric_result["lyrics"],
        "created_at": datetime.utcnow(),
    }
    history_col.insert_one(record)
    
    return {
        "input_type": "image",
        "input_filename": image.filename,
        "emotion_detection": emotion_result,
        "lyric_generation": lyric_result,
    }


@app.get("/history")
def get_history(current_user=Depends(get_current_user)):
    """Get user's analysis history"""
    records = list(
        history_col.find({"user_id": str(current_user["_id"])})
        .sort("created_at", -1)
        .limit(20)
    )
    for r in records:
        r["_id"] = str(r["_id"])
    
    return {"history": records}


@app.delete("/history/{record_id}")
def delete_history(record_id: str, current_user=Depends(get_current_user)):
    """Delete a specific history record"""
    result = history_col.delete_one({
        "_id": ObjectId(record_id),
        "user_id": str(current_user["_id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Deleted"}
