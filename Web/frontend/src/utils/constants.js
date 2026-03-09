// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Emotion Colors and Metadata
export const EMOTION_COLORS = {
  joy: "#FFD93D",
  sadness: "#6BA3BE",
  anger: "#FF6B6B",
  fear: "#845EC2",
  love: "#FF9EAA",
  surprise: "#4ECDC4",
  disgust: "#4CAF50",
  anticipation: "#FF9800",
};

export const EMOTION_EMOJIS = {
  joy: "✨",
  sadness: "🌧️",
  anger: "🔥",
  fear: "🌑",
  love: "💖",
  surprise: "⚡",
  disgust: "🌿",
  anticipation: "🌅",
};

export const EMOTION_DESCRIPTIONS = {
  joy: "Radiating happiness",
  sadness: "Melancholic undertones",
  anger: "Burning intensity",
  fear: "Shadowed anxiety",
  love: "Warm affection",
  surprise: "Unexpected wonder",
  disgust: "Rejecting repulsion",
  anticipation: "Eager expectation",
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
