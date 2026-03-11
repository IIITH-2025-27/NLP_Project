"""
Constants for NLP Project Backend
Contains emotion configurations and model settings used in the backend
"""

# ============================================================================
# EMOTION CONFIGURATION
# ============================================================================

# FER (Facial Emotion Recognition) emotion categories
# These 6 emotions are used consistently across:
# - Text emotion detection (HF API: SamLowe/roberta-base-go_emotions)
# - Image emotion detection (Gradio API: IIITH-25-27/LyricMind_Models)
# - Lyrics dataset mapping
EMOTIONS = [
    "Happy",
    "Sad",
    "Angry",
    "Fear",
    "Surprise",
    "Neutral"
]

# Note: The image emotion model (IIITH-25-27/LyricMind_Models) is trained to directly
# output one of the 6 emotions above, so no mapping is required

# Emotion metadata for UI display
EMOTION_META = {
    "Happy": {
        "emoji": "😊",
        "color": "#FFD93D",
        "description": "Joyful and positive"
    },
    "Sad": {
        "emoji": "😢",
        "color": "#6BA3BE",
        "description": "Melancholic and sorrowful"
    },
    "Angry": {
        "emoji": "😠",
        "color": "#FF6B6B",
        "description": "Intense frustration"
    },
    "Fear": {
        "emoji": "😨",
        "color": "#845EC2",
        "description": "Anxious and worried"
    },
    "Surprise": {
        "emoji": "😲",
        "color": "#4ECDC4",
        "description": "Unexpected reaction"
    },
    "Neutral": {
        "emoji": "😐",
        "color": "#95A5A6",
        "description": "Calm and balanced"
    }
}

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Hugging Face API Configuration
HF_ROUTER_API_BASE = "https://router.huggingface.co/hf-inference/models/"  # HF Router API base URL

# Hugging Face Model URLs
HF_EMOTION_MODEL = "SamLowe/roberta-base-go_emotions"  # Text emotion classification
HF_LYRIC_GEN_MODEL = "gpt2"  # Lyric generation model

# Gradio Space Configuration for Image Emotion Detection
GRADIO_IMAGE_EMOTION_SPACE = "IIITH-25-27/LyricMind_Models"  # Gradio Space on Hugging Face
GRADIO_IMAGE_EMOTION_API_NAME = "/predict"  # API endpoint name
GRADIO_IMAGE_EMOTION_SPACE_URL = "https://iiith-25-27-lyricmind-models.hf.space"  # Direct URL

# Model name for lyric generation
LYRIC_GEN_MODEL_NAME = "LyricGen-v2"
