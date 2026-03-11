"""
API Endpoints
Path constants for all API endpoints in the LyricMind backend
"""

# ============================================================================
# BASE URL
# ============================================================================
BASE_URL = "http://localhost:8000"  # Update with your production URL

# ============================================================================
# HEALTH CHECK
# ============================================================================

# GET / - Health check endpoint
HEALTH_CHECK = "/"

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

# Authentication base path
AUTH_BASE = "/auth"

# POST /auth/request-otp - Request OTP for signup (sends email)
AUTH_REQUEST_OTP = f"{AUTH_BASE}/request-otp"

# POST /auth/verify-otp - Verify OTP and complete signup
AUTH_VERIFY_OTP = f"{AUTH_BASE}/verify-otp"

# POST /auth/resend-otp - Resend OTP to email
AUTH_RESEND_OTP = f"{AUTH_BASE}/resend-otp"

# POST /auth/signup - Legacy signup endpoint (no OTP)
AUTH_SIGNUP = f"{AUTH_BASE}/signup"

# POST /auth/login - Login with email and password
AUTH_LOGIN = f"{AUTH_BASE}/login"

# ============================================================================
# ANALYSIS ENDPOINTS (ML/AI)
# ============================================================================

# POST /getEmotionFromText - Get emotion from text using HF API
GET_EMOTION_FROM_TEXT = "/getEmotionFromText"

# POST /getEmotionFromImage - Get emotion from image using Gradio API
GET_EMOTION_FROM_IMAGE = "/getEmotionFromImage"

# POST /getLyricsForEmotion - Generate lyrics for a given emotion
GET_LYRICS_FOR_EMOTION = "/getLyricsForEmotion"

# ============================================================================
# CHAT MANAGEMENT ENDPOINTS
# ============================================================================

# Chats base path
CHATS_BASE = "/chats"

# GET /chats - Get all chats for current user
GET_CHATS = CHATS_BASE

# POST /chats - Create a new chat
CREATE_CHAT = CHATS_BASE

# GET /chats/{chat_id} - Get a specific chat by ID
GET_CHAT = lambda chat_id: f"{CHATS_BASE}/{chat_id}"

# PUT /chats/{chat_id} - Update chat (title)
UPDATE_CHAT = lambda chat_id: f"{CHATS_BASE}/{chat_id}"

# DELETE /chats/{chat_id} - Delete chat and all its messages
DELETE_CHAT = lambda chat_id: f"{CHATS_BASE}/{chat_id}"

# ============================================================================
# MESSAGE MANAGEMENT ENDPOINTS
# ============================================================================

# GET /chats/{chat_id}/messages - Get all messages for a chat
GET_MESSAGES = lambda chat_id: f"{CHATS_BASE}/{chat_id}/messages"

# POST /chats/{chat_id}/messages - Create a new message in a chat
CREATE_MESSAGE = lambda chat_id: f"{CHATS_BASE}/{chat_id}/messages"

# DELETE /messages/{message_id} - Delete a specific message
DELETE_MESSAGE = lambda message_id: f"/messages/{message_id}"
