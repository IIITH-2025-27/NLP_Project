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
    "Angry",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral",
]

# Class index order must match model training exactly.
CLASS_NAMES = EMOTIONS

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
GRADIO_IMAGE_EMOTION_SPACE = "IIITH-25-27/image_to_emotion"  # Gradio Space on Hugging Face
GRADIO_IMAGE_EMOTION_API_NAME = "/predict"  # API endpoint name
GRADIO_IMAGE_EMOTION_SPACE_URL = "https://iiith-25-27-image-to-emotion.hf.space"  # Direct URL

# HF Space Configuration for Lyrics Generation
# Gradio Space ID for lyric generation (used by gradio_client).
HF_LYRIC_GEN_SPACE_URL = "IIITH-25-27/lyrics_Generator_for_emotion"
LYRIC_GEN_MODEL_NAME = "LyricGen-v2"
LYRIC_GEN_MAX_WORDS = 120
LYRIC_GEN_TEMPERATURE = 0.9
LYRIC_GEN_TOP_K = 50
LYRIC_GEN_TOP_P = 0.95
