# Database Service

This package handles all MongoDB database operations including connection management and collection definitions.

## Structure

```
database_service/
├── __init__.py       # Package exports
├── connection.py     # MongoDB client and database connection
├── collections.py    # Collection definitions and indexes
└── README.md         # This file
```

## Files

### 1. `connection.py`
MongoDB client initialization and database connection:
- Establishes connection to MongoDB using config settings
- Exports `client` and `db` objects

### 2. `collections.py`
Database collections (tables) and index management:
- **users_col** - User accounts
- **otp_col** - OTP verification codes
- **chats_col** - Chat sessions
- **messages_col** - Chat messages
- **image_emotion_data_col** - Image + preprocessed image + detected emotion records
- **emotion_lyrics_data_col** - Emotion + generated lyrics records
- **create_indexes()** - Creates all necessary indexes for performance

### 3. `__init__.py`
Package initialization that exports all collections and connection objects

## Usage

### Import collections

```python
from database_service import (
    users_col,
    otp_col,
    chats_col,
    messages_col,
    image_emotion_data_col,
    emotion_lyrics_data_col,
)

# Use collections
user = users_col.find_one({"email": "user@example.com"})
chats = list(chats_col.find({"user_id": user_id}))
```

### Import database connection

```python
from database_service import db, client

# Use database object
all_collections = db.list_collection_names()

# Use client for advanced operations
client.admin.command('ping')
```

## Collections Schema

### Users Collection
```python
{
    "_id": ObjectId,
    "name": str,
    "email": str,
    "password": str,  # hashed
    "created_at": datetime,
    "verified": bool
}
```

### OTP Collection
```python
{
    "_id": ObjectId,
    "email": str,
    "otp": str,
    "name": str,
    "password_hash": str,
    "created_at": datetime,
    "expires_at": datetime,  # TTL index
    "attempts": int
}
```

### Chats Collection
```python
{
    "_id": ObjectId,
    "user_id": str,
    "title": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Messages Collection
```python
{
    "_id": ObjectId,
    "chat_id": str,
    "user_id": str,
    "content": str,
    "message_type": str,  # "user" or "assistant"
    "input_type": str,  # optional
    "image_preview": str,  # optional
    "emotion": dict,  # optional
    "lyrics": dict,  # optional
    "created_at": datetime
}
```

## Indexes

The following indexes are automatically created on module import:

### OTP Collection
- `expires_at` - TTL index (auto-delete after expiration)
- `email` - Fast lookup by email

### Users Collection
- `email` - Unique index
- `created_at` - Sorted queries

### Chats Collection
- `user_id` - Fast user chat lookup
- `updated_at` - Sort by last updated
- `(user_id, updated_at)` - Compound index for sorted user chats

### Messages Collection
- `chat_id` - Fast chat message lookup
- `user_id` - User message lookup
- `created_at` - Sort by time
- `(chat_id, created_at)` - Compound index for chat history

## Configuration

Database connection settings are configured in `config.py`:
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name

## Adding New Collections

1. Add collection definition in `collections.py`:
   ```python
   new_col = db["new_collection"]
   ```

2. Add indexes in `create_indexes()`:
   ```python
   new_col.create_index("field_name")
   ```

3. Export in `__init__.py`:
   ```python
   from .collections import new_col
   __all__ = [..., 'new_col']
   ```

## Testing

Verify database connection:
```python
from database_service import client, db

# Test connection
try:
    client.admin.command('ping')
    print("✓ MongoDB connected successfully")
    print(f"✓ Database: {db.name}")
    print(f"✓ Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
```
