// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Emotion Colors and Metadata (6 FER emotions)
export const EMOTION_COLORS = {
  Happy: "#FFD93D",
  Sad: "#6BA3BE",
  Angry: "#FF6B6B",
  Fear: "#845EC2",
  Surprise: "#4ECDC4",
  Neutral: "#95A5A6",
};

export const EMOTION_EMOJIS = {
  Happy: "😊",
  Sad: "😢",
  Angry: "😠",
  Fear: "😨",
  Surprise: "😲",
  Neutral: "😐",
};

export const EMOTION_DESCRIPTIONS = {
  Happy: "Joyful and positive",
  Sad: "Melancholic and sorrowful",
  Angry: "Intense frustration",
  Fear: "Anxious and worried",
  Surprise: "Unexpected reaction",
  Neutral: "Calm and balanced",
};

// Local Storage Keys
export const STORAGE_KEYS = {
  TOKEN: "lyricmind_token",
  USER: "lyricmind_user",
};

// App Constants
export const APP_NAME = "LyricMind";
export const APP_TAGLINE = "Your emotions. Your verse.";
export const MAX_TEXT_LENGTH = 500;
export const MAX_HISTORY_ITEMS = 20;
