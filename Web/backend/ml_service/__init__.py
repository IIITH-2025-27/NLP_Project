"""
ML Service Package
Contains all machine learning models for emotion detection and lyric generation
"""

from .ml_service import (
	predict_emotion,
	generate_lyrics,
	predict_emotion_from_image,
	get_emotion_from_image,
	evaluate_generated_lyrics,
)

__all__ = [
	'predict_emotion',
	'generate_lyrics',
	'predict_emotion_from_image',
	'get_emotion_from_image',
	'evaluate_generated_lyrics',
]
