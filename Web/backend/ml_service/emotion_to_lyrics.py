import sys
import os
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    LYRIC_GEN_MODEL_NAME,
    HF_LYRIC_GEN_SPACE_URL,
    LYRIC_GEN_MAX_TOKENS,
    LYRIC_GEN_TEMPERATURE,
    LYRIC_GEN_TOP_P,
)
from config import HF_API_TOKEN


def generate_lyrics(emotion: str) -> dict:
    """
    Generate lyrics using the private Hugging Face Space
    (https://iiith-25-27-lyrics-generator-for-emotion.hf.space/generate)

    Raises:
        Exception: Propagated directly if the HF Space call fails.
    """
    headers = {}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"

    response = requests.post(
        HF_LYRIC_GEN_SPACE_URL,
        json={
            "text": emotion,
            "max_tokens": LYRIC_GEN_MAX_TOKENS,
            "temperature": LYRIC_GEN_TEMPERATURE,
            "top_p": LYRIC_GEN_TOP_P,
        },
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    # The Space returns {"generated_text": "..."}  (adjust key if needed)
    lyrics = data.get("generated_text") or data.get("lyrics") or str(data)

    return {
        "lyrics": lyrics,
        "emotion_used": emotion,
        "model": LYRIC_GEN_MODEL_NAME,
        "tokens_generated": len(lyrics.split()),
    }
