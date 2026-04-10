import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import constants from parent directory
from constants import (
    EMOTION_META,
    HF_EMOTION_MODEL,
)

# Import ML service modules
from .text_to_emotion import get_emotion_from_text
from .image_to_emotion import predict_emotion_from_image
from .emotion_to_lyrics import generate_lyrics as _generate_lyrics


def predict_emotion(text: str) -> dict:
    """
    Predict emotion from text using Hugging Face model
    Uses SamLowe/roberta-base-go_emotions model
    
    Raises:
        Exception: If HF API fails, the error is propagated to the caller
    """
    # Use the Hugging Face model for emotion detection
    emotion_result = get_emotion_from_text(text)
    top_emotion = emotion_result["emotion"]
    confidence = emotion_result["confidence"]
    scores = emotion_result["scores"]
    
    return {
        "emotion": top_emotion,
        "confidence": confidence,
        "scores": scores,
        "meta": EMOTION_META[top_emotion],
        "model": HF_EMOTION_MODEL
    }


def get_emotion_from_image(image_bytes: bytes) -> dict:
    """
    Wrapper function to get emotion from image
    Calls the predict_emotion_from_image function from image_to_emotion module
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        dict: Emotion detection result with emotion, confidence, scores, meta, and model info
    """
    result = predict_emotion_from_image(image_bytes)
    return result


def generate_lyrics(emotion: str) -> dict:
    """
    Wrapper function to generate lyrics from emotion
    Calls the generate_lyrics function from emotion_to_lyrics module

    Args:
        emotion: Emotion string (e.g. "Happy", "Sad")

    Returns:
        dict: Generated lyrics result with lyrics, emotion_used, model, and tokens_generated

    Raises:
        Exception: If the HF Space call fails, the error is propagated to the caller
    """
    result = _generate_lyrics(emotion)
    return result
