import importlib
import sys
from pathlib import Path
from threading import Lock


# Make the project root importable so we can use Metric.evaluation_matric_PHREM
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


_model_lock = Lock()
_phrem_model = None
_init_error = None


def _load_phrem_model():
    """Lazy-load PHREM model once for process lifetime."""
    global _phrem_model, _init_error

    if _phrem_model is not None:
        return _phrem_model

    if _init_error is not None:
        raise RuntimeError(_init_error)

    with _model_lock:
        if _phrem_model is not None:
            return _phrem_model

        if _init_error is not None:
            raise RuntimeError(_init_error)

        try:
            nltk = importlib.import_module("nltk")

            try:
                nltk.data.find("corpora/cmudict")
            except LookupError:
                nltk.download("cmudict", quiet=True)

            from Metric.evaluation_matric_PHREM import PHREM  # local import by design

            _phrem_model = PHREM()
            return _phrem_model
        except Exception as exc:
            _init_error = f"PHREM evaluator initialization failed: {exc}"
            raise RuntimeError(_init_error) from exc


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
        model = _load_phrem_model()
        raw_score = float(model.compute(lyrics, emotion_target=target))
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
