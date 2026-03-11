"""
Database Service Package
Handles MongoDB connection and collections management
"""

from .connection import client, db
from .collections import users_col, otp_col, chats_col, messages_col

__all__ = [
    'client',
    'db',
    'users_col',
    'otp_col',
    'chats_col',
    'messages_col'
]
