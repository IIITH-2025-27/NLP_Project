"""
API Package
Contains API endpoints documentation and helper functions
"""

from .endpoints import (
    BASE_URL,
    HEALTH_CHECK,
    AUTH_BASE,
    AUTH_REQUEST_OTP,
    AUTH_VERIFY_OTP,
    AUTH_RESEND_OTP,
    AUTH_SIGNUP,
    AUTH_LOGIN,
    GET_EMOTION_FROM_TEXT,
    GET_EMOTION_FROM_IMAGE,
    GET_LYRICS_FOR_EMOTION,
    CHATS_BASE,
    GET_CHATS,
    CREATE_CHAT,
    GET_CHAT,
    UPDATE_CHAT,
    DELETE_CHAT,
    GET_MESSAGES,
    CREATE_MESSAGE,
    DELETE_MESSAGE
)

from .schemas import ENDPOINTS

from .helpers import (
    get_full_url,
    list_all_endpoints,
    get_endpoint_info,
    get_endpoints_by_method,
    get_public_endpoints,
    get_protected_endpoints,
    format_endpoint_path
)

# Import models (Pydantic request/response schemas)
from . import models

# Import routers submodule
from . import routers

__all__ = [
    # Constants
    'BASE_URL',
    'HEALTH_CHECK',
    'AUTH_BASE',
    'AUTH_REQUEST_OTP',
    'AUTH_VERIFY_OTP',
    'AUTH_RESEND_OTP',
    'AUTH_SIGNUP',
    'AUTH_LOGIN',
    'GET_EMOTION_FROM_TEXT',
    'GET_EMOTION_FROM_IMAGE',
    'GET_LYRICS_FOR_EMOTION',
    'CHATS_BASE',
    'GET_CHATS',
    'CREATE_CHAT',
    'GET_CHAT',
    'UPDATE_CHAT',
    'DELETE_CHAT',
    'GET_MESSAGES',
    'CREATE_MESSAGE',
    'DELETE_MESSAGE',
    # Schemas
    'ENDPOINTS',
    # Helper functions
    'get_full_url',
    'list_all_endpoints',
    'get_endpoint_info',
    'get_endpoints_by_method',
    'get_public_endpoints',
    'get_protected_endpoints',
    'format_endpoint_path',
    # Models and Routers
    'models',
    'routers'
]
