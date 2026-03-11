"""
Text to Emotion Detection using Hugging Face Router API
Uses SamLowe/roberta-base-go_emotions model (runs on HF servers)
Maps 28 GoEmotions to 6 FER categories
"""
import requests
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import EMOTIONS, HF_EMOTION_MODEL, HF_ROUTER_API_BASE
from config import HF_API_TOKEN
from ml_service.emotion_mapping import GOEMOTIONS_TO_FER

# Hugging Face Router API endpoint (more reliable than inference API)
API_URL = f"{HF_ROUTER_API_BASE}{HF_EMOTION_MODEL}"

# Setup headers for API requests
HEADERS = {}
if HF_API_TOKEN:
    HEADERS["Authorization"] = f"Bearer {HF_API_TOKEN}"


def call_hf_api(text: str, max_retries=5):
    """Call Hugging Face Router API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={"inputs": text},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 503:
                # Model is loading on HF servers, wait and retry
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 20)  # Exponential backoff, max 20s
                    print(f"⏳ Model loading on HF servers, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Model failed to load on HF servers after multiple retries")
            
            # For other errors, raise immediately
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"⏳ Request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            raise Exception("Request timeout after multiple retries")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"HF API Error: {e}")
    
    raise Exception("Max retries reached")


def get_emotion_from_text(text: str) -> dict:
    """
    Detect emotion from text using Hugging Face Router API
    Uses SamLowe/roberta-base-go_emotions model (runs on HF servers)
    Maps 28 GoEmotions to 6 FER categories matching the notebook's approach
    
    Args:
        text: Input text to analyze
        
    Returns:
        dict with emotion, confidence, and scores (6 FER categories)
    """
    try:
        # Call Hugging Face Router API
        results = call_hf_api(text)
        
        # Handle API response format (list of lists)
        if isinstance(results, list) and len(results) > 0 and isinstance(results[0], list):
            results = results[0]
        
        # Aggregate scores by 6 FER emotions
        emotion_scores = {emotion: 0.0 for emotion in EMOTIONS}
        
        for result in results:
            label = result["label"]
            score = result["score"]
            
            # Map GoEmotions label to FER emotion
            mapped_emotion = GOEMOTIONS_TO_FER.get(label, "Neutral")
            emotion_scores[mapped_emotion] += score
        
        # Normalize scores (so they sum to 1.0)
        total = sum(emotion_scores.values())
        if total > 0:
            normalized_scores = {e: round(v / total, 3) for e, v in emotion_scores.items()}
        else:
            # Equal distribution if no scores
            normalized_scores = {e: round(1.0 / len(EMOTIONS), 3) for e in EMOTIONS}
        
        # Get top emotion (dominant)
        top_emotion = max(normalized_scores, key=normalized_scores.get)
        confidence = round(normalized_scores[top_emotion], 3)
        
        return {
            "emotion": top_emotion,
            "confidence": confidence,
            "scores": normalized_scores
        }
        
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        raise


if __name__ == "__main__":
    # Test the function
    test_text = "I can't believe this happened!"
    result = get_emotion_from_text(test_text)
    print(f"Text: {test_text}")
    print(f"Detected Emotion: {result['emotion']}")
    print(f"Confidence: {result['confidence']}")
    print(f"All Scores: {result['scores']}")
