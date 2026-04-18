from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from datetime import datetime
import base64

from api.models import AnalyzeRequest, EmotionRequest
from auth import get_current_user
from ml_service import (
    predict_emotion,
    generate_lyrics,
    predict_emotion_from_image,
    evaluate_generated_lyrics,
)
from database_service import image_emotion_data_col, emotion_lyrics_data_col

router = APIRouter(tags=["ML/AI"])


def _to_data_url(image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"


def _store_image_emotion_record(
    image_bytes: bytes,
    content_type: str,
    input_filename: str,
    emotion_result: dict,
    user_id: str,
):
    try:
        image_emotion_data_col.insert_one({
            "image": _to_data_url(image_bytes, content_type),
            "greyscale_small_image": emotion_result.get("preprocessed_image"),
            "emotion": emotion_result.get("emotion"),
            "user_id": user_id,
            "input_filename": input_filename,
            "created_at": datetime.utcnow(),
        })
    except Exception as db_error:
        print(f"Warning: failed to store image_emotion_data record: {db_error}")


def _store_emotion_lyrics_record(emotion: str, lyric_result: dict, user_id: str):
    try:
        emotion_lyrics_data_col.insert_one({
            "emotion": emotion,
            "lyrics": lyric_result.get("lyrics"),
            "lyrics_evaluation": lyric_result.get("lyrics_evaluation"),
            "user_id": user_id,
            "created_at": datetime.utcnow(),
        })
    except Exception as db_error:
        print(f"Warning: failed to store emotion_lyrics_data record: {db_error}")


# ─── Text Emotion Detection ────────────────────────────────────────────────────

@router.post("/getEmotionFromText")
def get_emotion_from_text_endpoint(body: AnalyzeRequest, current_user=Depends(get_current_user)):
    """Get emotion from text using HF Inference API"""
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        emotion_result = predict_emotion(body.text)
        return {
            "input_text": body.text,
            "input_type": "text",
            "emotion_detection": emotion_result,
        }
    
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Emotion detection failed",
                "message": error_message,
                "service": "Hugging Face API",
                "model": "SamLowe/roberta-base-go_emotions",
                "suggestion": "Please try again in a few moments. The model may be loading on HF servers."
            }
        )


# ─── Image Emotion Detection ───────────────────────────────────────────────────

@router.post("/getEmotionFromImage")
async def get_emotion_from_image_endpoint(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Detect emotion from image using IIITH-25-27/LyricMind_Models Gradio API"""
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 10MB)
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be less than 10MB")
    
    try:
        emotion_result = predict_emotion_from_image(contents)
        
        # Check if result contains an error (e.g., no face detected)
        if "error" in emotion_result and "error_type" in emotion_result:
            if emotion_result["error_type"] == "NoFaceDetected":
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": emotion_result["error"],
                        "error_type": "NoFaceDetected",
                        "suggestion": emotion_result.get("suggestion", "Please upload an image with a visible face.")
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": emotion_result["error"],
                        "error_type": emotion_result.get("error_type", "ValidationError")
                    }
                )

        _store_image_emotion_record(
            image_bytes=contents,
            content_type=image.content_type or "image/jpeg",
            input_filename=image.filename or "uploaded-image",
            emotion_result=emotion_result,
            user_id=str(current_user["_id"]),
        )
        
        return {
            "input_type": "image",
            "input_filename": image.filename,
            "emotion_detection": emotion_result,
        }
    
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Image emotion detection failed",
                "message": error_message,
                "suggestion": "Please try again or use a different image."
            }
        )


# ─── Lyric Generation ──────────────────────────────────────────────────────────

@router.post("/getLyricsForEmotion")
def get_lyrics_for_emotion_endpoint(body: EmotionRequest, current_user=Depends(get_current_user)):
    """Generate lyrics based on detected emotion"""
    try:
        lyric_result = generate_lyrics(body.emotion)

        evaluation = evaluate_generated_lyrics(
            lyric_result.get("lyrics", ""),
            body.emotion,
        )
        lyric_result["lyrics_evaluation"] = evaluation

        _store_emotion_lyrics_record(
            emotion=body.emotion,
            lyric_result=lyric_result,
            user_id=str(current_user["_id"]),
        )

        return {
            "emotion": body.emotion,
            "lyric_generation": lyric_result,
        }
    
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Lyric generation failed",
                "message": error_message,
                "suggestion": "Please try again."
            }
        )
