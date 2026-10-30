"""
Text to Emotion Detection
Uses SamLowe/roberta-base-go_emotions running on the ML Utils Space (Web/ml_space)
Maps 28 GoEmotions to 6 FER categories
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import EMOTIONS, GRADIO_TEXT_EMOTION_API_NAME
from ml_service.emotion_mapping import GOEMOTIONS_TO_FER
from ml_service.ml_utils_client import get_ml_utils_client


def call_hf_api(text: str):
    """Get all 28 GoEmotions scores as [{"label", "score"}] (same shape the HF Inference API returned)"""
    scores = get_ml_utils_client().predict(text, api_name=GRADIO_TEXT_EMOTION_API_NAME)
    return [{"label": label, "score": score} for label, score in scores.items()]


def get_emotion_from_text(text: str) -> dict:
    """
    Detect emotion from text
    Uses SamLowe/roberta-base-go_emotions model (runs on the ML Utils Space)
    Maps 28 GoEmotions to 6 FER categories matching the notebook's approach
    
    Args:
        text: Input text to analyze
        
    Returns:
        dict with emotion, confidence, and scores (6 FER categories)
    """
    try:
        # Call the ML Utils Space
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
