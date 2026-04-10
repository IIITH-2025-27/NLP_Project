import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    LYRIC_GEN_MODEL_NAME,
    HF_LYRIC_GEN_SPACE_URL,
    LYRIC_GEN_MAX_WORDS,
    LYRIC_GEN_TEMPERATURE,
    LYRIC_GEN_TOP_K,
    LYRIC_GEN_TOP_P,
)
from config import HF_API_TOKEN

# Gradio client import with error handling
try:
    from gradio_client import Client
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("Warning: gradio_client not installed. Lyrics generation unavailable.")

# Global client instance (lazy loaded)
_gradio_client = None
_client_error = None


def get_gradio_client():
    """Get or create Gradio client for lyrics generation."""
    global _gradio_client, _client_error

    if not GRADIO_AVAILABLE:
        raise Exception("gradio_client module not available")

    if _client_error:
        raise Exception(f"Previous client initialization failed: {_client_error}")

    if _gradio_client is None:
        try:
            if HF_API_TOKEN:
                _gradio_client = Client(HF_LYRIC_GEN_SPACE_URL, token=HF_API_TOKEN)
            else:
                _gradio_client = Client(HF_LYRIC_GEN_SPACE_URL)
        except Exception as e:
            _client_error = str(e)
            raise Exception(f"Failed to initialize lyric Gradio client: {e}")

    return _gradio_client


def generate_lyrics(emotion: str) -> dict:
    """
    Generate lyrics using Hugging Face Space via gradio_client.

    Raises:
        Exception: Propagated directly if the HF Space call fails.
    """
    print(f"[lyrics] emotion received: {emotion!r}")

    client = get_gradio_client()
    print(f"[lyrics] gradio space: {HF_LYRIC_GEN_SPACE_URL}")
    payload = [emotion.lower(), LYRIC_GEN_MAX_WORDS, LYRIC_GEN_TEMPERATURE, LYRIC_GEN_TOP_K, LYRIC_GEN_TOP_P]
    print(f"[lyrics] gradio payload: {{\"data\": {payload}}}")

    result = client.predict(*payload)
    print(f"[lyrics] gradio raw response: {result}")

    # Handle common response shapes from endpoint wrappers.
    lyrics = ""
    if isinstance(result, str):
        lyrics = result.strip()
    elif isinstance(result, dict):
        if result.get("generated_text"):
            lyrics = str(result["generated_text"]).strip()
        elif result.get("lyrics"):
            lyrics = str(result["lyrics"]).strip()
        elif isinstance(result.get("data"), list) and result["data"]:
            lyrics = str(result["data"][0]).strip()
    elif isinstance(result, (list, tuple)) and result:
        lyrics = str(result[0]).strip()

    if not lyrics:
        raise Exception(f"Unexpected lyric Space response: {result}")

    return {
        "lyrics": lyrics,
        "emotion_used": emotion,
        "model": LYRIC_GEN_MODEL_NAME,
        "tokens_generated": len(lyrics.split()),
    }
