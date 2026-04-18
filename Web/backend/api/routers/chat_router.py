from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId

from database_service import chats_col, messages_col
from api.models import CreateChatRequest, UpdateChatRequest, CreateMessageRequest, UpdateMessageRequest
from auth import get_current_user

router = APIRouter(tags=["Chats & Messages"])


# ─── Chat Management ─────────────────────────────────────────────────────────

@router.get("/chats")
def get_chats(current_user=Depends(get_current_user)):
    """Get all chats for the current user"""
    chats = list(
        chats_col.find({"user_id": str(current_user["_id"])})
        .sort("updated_at", -1)
    )
    
    for chat in chats:
        chat["_id"] = str(chat["_id"])
        chat["id"] = str(chat["_id"])
    
    return {"chats": chats}


@router.post("/chats")
def create_chat(body: CreateChatRequest, current_user=Depends(get_current_user)):
    """Create a new chat"""
    chat = {
        "user_id": str(current_user["_id"]),
        "title": body.title,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = chats_col.insert_one(chat)
    chat["_id"] = str(result.inserted_id)
    chat["id"] = str(result.inserted_id)
    
    return chat


@router.get("/chats/{chat_id}")
def get_chat(chat_id: str, current_user=Depends(get_current_user)):
    """Get a specific chat"""
    chat = chats_col.find_one({
        "_id": ObjectId(chat_id),
        "user_id": str(current_user["_id"])
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat["_id"] = str(chat["_id"])
    chat["id"] = str(chat["_id"])
    
    return chat


@router.put("/chats/{chat_id}")
def update_chat(chat_id: str, body: UpdateChatRequest, current_user=Depends(get_current_user)):
    """Update a chat (title only)"""
    update_data = {"updated_at": datetime.utcnow()}
    
    if body.title is not None:
        update_data["title"] = body.title
    
    result = chats_col.update_one(
        {
            "_id": ObjectId(chat_id),
            "user_id": str(current_user["_id"])
        },
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Return updated chat
    return get_chat(chat_id, current_user)


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, current_user=Depends(get_current_user)):
    """Delete a chat and all its messages"""
    # First, verify the chat belongs to the user
    chat = chats_col.find_one({
        "_id": ObjectId(chat_id),
        "user_id": str(current_user["_id"])
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete all messages in this chat
    messages_col.delete_many({"chat_id": chat_id})
    
    # Delete the chat
    chats_col.delete_one({"_id": ObjectId(chat_id)})
    
    return {"message": "Chat and all messages deleted"}


# ─── Message Management ──────────────────────────────────────────────────────

@router.get("/chats/{chat_id}/messages")
def get_messages(chat_id: str, current_user=Depends(get_current_user)):
    """Get all messages for a specific chat"""
    # Verify chat belongs to user
    chat = chats_col.find_one({
        "_id": ObjectId(chat_id),
        "user_id": str(current_user["_id"])
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get all messages for this chat, sorted by creation time
    messages = list(
        messages_col.find({"chat_id": chat_id})
        .sort("created_at", 1)
    )
    
    for message in messages:
        message["_id"] = str(message["_id"])
        message["id"] = str(message["_id"])
    
    return {"messages": messages}


@router.post("/chats/{chat_id}/messages")
def create_message(chat_id: str, body: CreateMessageRequest, current_user=Depends(get_current_user)):
    """Create a new message in a chat"""
    # Verify chat belongs to user
    chat = chats_col.find_one({
        "_id": ObjectId(chat_id),
        "user_id": str(current_user["_id"])
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create message
    message = {
        "chat_id": chat_id,
        "user_id": str(current_user["_id"]),
        "content": body.content,
        "message_type": body.message_type,
        "created_at": datetime.utcnow()
    }
    
    # Add optional fields
    if body.input_type:
        message["input_type"] = body.input_type
    if body.image_preview:
        message["image_preview"] = body.image_preview
    if body.emotion:
        message["emotion"] = body.emotion
    if body.lyrics:
        message["lyrics"] = body.lyrics
    if body.lyrics_score is not None:
        message["lyrics_score"] = body.lyrics_score
    if body.preprocessed_image:
        message["preprocessed_image"] = body.preprocessed_image
    
    result = messages_col.insert_one(message)
    message["_id"] = str(result.inserted_id)
    message["id"] = str(result.inserted_id)
    
    # Update chat's updated_at timestamp
    chats_col.update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )
    
    return message


@router.delete("/messages/{message_id}")
def delete_message(message_id: str, current_user=Depends(get_current_user)):
    """Delete a specific message"""
    # Verify message belongs to user
    message = messages_col.find_one({
        "_id": ObjectId(message_id),
        "user_id": str(current_user["_id"])
    })
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    messages_col.delete_one({"_id": ObjectId(message_id)})
    
    return {"message": "Message deleted"}


@router.put("/messages/{message_id}")
def update_message(message_id: str, body: UpdateMessageRequest, current_user=Depends(get_current_user)):
    """Update a specific message in-place"""
    message = messages_col.find_one({
        "_id": ObjectId(message_id),
        "user_id": str(current_user["_id"])
    })

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    update_data = {}

    if body.content is not None:
        update_data["content"] = body.content
    if body.input_type is not None:
        update_data["input_type"] = body.input_type
    if body.image_preview is not None:
        update_data["image_preview"] = body.image_preview
    if body.emotion is not None:
        update_data["emotion"] = body.emotion
    if body.lyrics is not None:
        update_data["lyrics"] = body.lyrics
    if body.lyrics_score is not None:
        update_data["lyrics_score"] = body.lyrics_score
    if body.preprocessed_image is not None:
        update_data["preprocessed_image"] = body.preprocessed_image

    if update_data:
        messages_col.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update_data}
        )

        # Refresh parent chat timestamp
        if message.get("chat_id"):
            chats_col.update_one(
                {"_id": ObjectId(message["chat_id"])},
                {"$set": {"updated_at": datetime.utcnow()}}
            )

    updated_message = messages_col.find_one({"_id": ObjectId(message_id)})
    updated_message["_id"] = str(updated_message["_id"])
    updated_message["id"] = str(updated_message["_id"])
    return updated_message
