"""
PHREM lyric quality evaluation.

The PHREM model (roberta + sentence-transformers) runs on the ML Utils Space
(Web/ml_space); this module only calls it.
"""
from constants import GRADIO_EVAL_API_NAME
from .ml_utils_client import get_ml_utils_client


def evaluate_generated_lyrics(lyrics: str, emotion_target: str) -> dict:
    """
    Evaluate generated lyrics quality with PHREM.

    Returns a stable payload shape even when evaluation fails.
    """
    if not isinstance(lyrics, str) or not lyrics.strip():
        return {
            "score": None,
            "metric": "PHREM",
            "status": "skipped",
            "reason": "empty_lyrics",
        }

    target = emotion_target if isinstance(emotion_target, str) and emotion_target else "Happy"

    try:
        raw_score = float(get_ml_utils_client().predict(
            lyrics, target, api_name=GRADIO_EVAL_API_NAME
        ))
        score = max(0.0, min(1.0, raw_score))
        return {
            "score": score,
            "metric": "PHREM",
            "status": "ok",
            "emotion_target": target,
        }
    except Exception as exc:
        return {
            "score": None,
            "metric": "PHREM",
            "status": "failed",
            "emotion_target": target,
            "reason": str(exc),
        }
