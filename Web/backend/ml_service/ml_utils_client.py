"""
Shared Gradio client for the LyricMind ML Utils Space (face extraction + PHREM).
Source of the Space lives in Web/ml_space/.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gradio_client import Client

from config import HF_API_TOKEN, ML_UTILS_SPACE

_client = None


def get_ml_utils_client():
    """Get or create the client. Failures are not cached, so a sleeping Space is retried."""
    global _client
    if _client is None:
        _client = Client(ML_UTILS_SPACE, token=HF_API_TOKEN or None)
    return _client
