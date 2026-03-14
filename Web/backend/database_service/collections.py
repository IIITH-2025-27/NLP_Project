"""
Database Collections (Tables)
MongoDB collection definitions and index management
"""

from .connection import db

# ============================================================================
# COLLECTIONS
# ============================================================================

# User collection
users_col = db["users"]

# OTP verification collection
otp_col = db["otp_verification"]

# Chat collection
chats_col = db["chats"]

# Message collection
messages_col = db["messages"]

# Data collection: image + preprocessed image + emotion
image_emotion_data_col = db["image_emotion_data"]

# Data collection: emotion + lyrics
emotion_lyrics_data_col = db["emotion_lyrics_data"]

# ============================================================================
# INDEX CREATION
# ============================================================================

def create_indexes():
    """
    Create indexes for better performance and data management
    Call this function on application startup
    """
    
    # OTP Collection Indexes
    # Automatically delete expired OTP documents
    otp_col.create_index("expires_at", expireAfterSeconds=0)
    otp_col.create_index("email")
    
    # Users Collection Indexes
    users_col.create_index("email", unique=True)
    users_col.create_index("created_at")
    
    # Chats Collection Indexes
    chats_col.create_index("user_id")
    chats_col.create_index("updated_at")
    chats_col.create_index([("user_id", 1), ("updated_at", -1)])  # Compound for sorted queries
    
    # Messages Collection Indexes
    messages_col.create_index("chat_id")
    messages_col.create_index("user_id")
    messages_col.create_index("created_at")
    messages_col.create_index([("chat_id", 1), ("created_at", 1)])  # Compound for chat history

    # Image-Emotion Data Collection Indexes
    image_emotion_data_col.create_index("created_at")
    image_emotion_data_col.create_index("emotion")

    # Emotion-Lyrics Data Collection Indexes
    emotion_lyrics_data_col.create_index("created_at")
    emotion_lyrics_data_col.create_index("emotion")


# Create indexes on module import
create_indexes()
