"""
API Schemas
Request/Response schemas and detailed information for all API endpoints
"""

from .endpoints import (
    HEALTH_CHECK,
    AUTH_REQUEST_OTP,
    AUTH_VERIFY_OTP,
    AUTH_RESEND_OTP,
    AUTH_SIGNUP,
    AUTH_LOGIN,
    GET_EMOTION_FROM_TEXT,
    GET_EMOTION_FROM_IMAGE,
    GET_LYRICS_FOR_EMOTION,
    GET_CHATS,
    CREATE_CHAT
)

# ============================================================================
# ENDPOINT SCHEMAS WITH REQUEST/RESPONSE DETAILS
# ============================================================================

ENDPOINTS = {
    "health": {
        "path": HEALTH_CHECK,
        "method": "GET",
        "auth_required": False,
        "description": "Health check endpoint",
        "response": {"message": "LyricMind API is running 🎵"}
    },
    
    # Authentication
    "auth_request_otp": {
        "path": AUTH_REQUEST_OTP,
        "method": "POST",
        "auth_required": False,
        "description": "Request OTP for signup",
        "request_body": {
            "name": "string",
            "email": "string",
            "password": "string"
        },
        "response": {
            "message": "string",
            "email": "string"
        }
    },
    
    "auth_verify_otp": {
        "path": AUTH_VERIFY_OTP,
        "method": "POST",
        "auth_required": False,
        "description": "Verify OTP and complete signup",
        "request_body": {
            "email": "string",
            "otp": "string"
        },
        "response": {
            "message": "string",
            "token": "string",
            "user": {
                "id": "string",
                "name": "string",
                "email": "string"
            }
        }
    },
    
    "auth_resend_otp": {
        "path": AUTH_RESEND_OTP,
        "method": "POST",
        "auth_required": False,
        "description": "Resend OTP to email",
        "request_body": {
            "email": "string"
        },
        "response": {
            "message": "string",
            "email": "string"
        }
    },
    
    "auth_signup": {
        "path": AUTH_SIGNUP,
        "method": "POST",
        "auth_required": False,
        "description": "Legacy signup endpoint (no OTP)",
        "request_body": {
            "name": "string",
            "email": "string",
            "password": "string"
        },
        "response": {
            "token": "string",
            "user": {
                "id": "string",
                "name": "string",
                "email": "string"
            }
        }
    },
    
    "auth_login": {
        "path": AUTH_LOGIN,
        "method": "POST",
        "auth_required": False,
        "description": "Login with credentials",
        "request_body": {
            "email": "string",
            "password": "string"
        },
        "response": {
            "token": "string",
            "user": {
                "id": "string",
                "name": "string",
                "email": "string"
            }
        }
    },
    
    # ML/AI Endpoints
    "get_emotion_from_text": {
        "path": GET_EMOTION_FROM_TEXT,
        "method": "POST",
        "auth_required": True,
        "description": "Get emotion from text using HF API",
        "request_body": {
            "text": "string"
        },
        "response": {
            "input_text": "string",
            "input_type": "text",
            "emotion_detection": {
                "emotion": "string",
                "confidence": "float",
                "scores": "dict",
                "meta": "dict"
            }
        }
    },
    
    "get_emotion_from_image": {
        "path": GET_EMOTION_FROM_IMAGE,
        "method": "POST",
        "auth_required": True,
        "description": "Get emotion from image using Gradio API",
        "request_body": "multipart/form-data (image file)",
        "response": {
            "input_type": "image",
            "input_filename": "string",
            "emotion_detection": {
                "emotion": "string",
                "confidence": "float",
                "scores": "dict",
                "meta": "dict"
            }
        }
    },
    
    "get_lyrics_for_emotion": {
        "path": GET_LYRICS_FOR_EMOTION,
        "method": "POST",
        "auth_required": True,
        "description": "Generate lyrics based on detected emotion",
        "request_body": {
            "emotion": "string (one of: Happy, Sad, Angry, Fear, Surprise, Neutral)"
        },
        "response": {
            "emotion": "string",
            "lyric_generation": {
                "lyrics": "string",
                "emotion_used": "string",
                "model": "string",
                "tokens_generated": "int",
                "lyrics_evaluation": {
                    "score": "float|null",
                    "metric": "string",
                    "status": "string",
                    "emotion_target": "string"
                }
            }
        }
    },
    
    # Chats
    "get_chats": {
        "path": GET_CHATS,
        "method": "GET",
        "auth_required": True,
        "description": "Get all chats for current user",
        "response": {
            "chats": [{
                "id": "string",
                "user_id": "string",
                "title": "string",
                "created_at": "datetime",
                "updated_at": "datetime"
            }]
        }
    },
    
    "create_chat": {
        "path": CREATE_CHAT,
        "method": "POST",
        "auth_required": True,
        "description": "Create a new chat",
        "request_body": {
            "title": "string"
        },
        "response": {
            "id": "string",
            "user_id": "string",
            "title": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    },
    
    "get_chat": {
        "path": "/chats/{chat_id}",
        "method": "GET",
        "auth_required": True,
        "description": "Get a specific chat",
        "path_params": {
            "chat_id": "string"
        },
        "response": {
            "id": "string",
            "user_id": "string",
            "title": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    },
    
    "update_chat": {
        "path": "/chats/{chat_id}",
        "method": "PUT",
        "auth_required": True,
        "description": "Update chat title",
        "path_params": {
            "chat_id": "string"
        },
        "request_body": {
            "title": "string (optional)"
        },
        "response": {
            "id": "string",
            "user_id": "string",
            "title": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    },
    
    "delete_chat": {
        "path": "/chats/{chat_id}",
        "method": "DELETE",
        "auth_required": True,
        "description": "Delete chat and all messages",
        "path_params": {
            "chat_id": "string"
        },
        "response": {
            "message": "Chat and all messages deleted"
        }
    },
    
    # Messages
    "get_messages": {
        "path": "/chats/{chat_id}/messages",
        "method": "GET",
        "auth_required": True,
        "description": "Get all messages for a chat",
        "path_params": {
            "chat_id": "string"
        },
        "response": {
            "messages": [{
                "id": "string",
                "chat_id": "string",
                "user_id": "string",
                "content": "string",
                "message_type": "string",
                "created_at": "datetime"
            }]
        }
    },
    
    "create_message": {
        "path": "/chats/{chat_id}/messages",
        "method": "POST",
        "auth_required": True,
        "description": "Create a new message in a chat",
        "path_params": {
            "chat_id": "string"
        },
        "request_body": {
            "content": "string",
            "message_type": "string (user|assistant)",
            "input_type": "string (optional)",
            "image_preview": "string (optional)",
            "emotion": "dict (optional)",
            "lyrics": "dict (optional)"
        },
        "response": {
            "id": "string",
            "chat_id": "string",
            "user_id": "string",
            "content": "string",
            "message_type": "string",
            "created_at": "datetime"
        }
    },
    
    "delete_message": {
        "path": "/messages/{message_id}",
        "method": "DELETE",
        "auth_required": True,
        "description": "Delete a specific message",
        "path_params": {
            "message_id": "string"
        },
        "response": {
            "message": "Message deleted"
        }
    }
}
