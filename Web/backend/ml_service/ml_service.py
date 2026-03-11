import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import constants from parent directory
from constants import (
    EMOTION_META,
    LYRIC_GEN_MODEL_NAME,
    HF_EMOTION_MODEL
)

# Import ML service modules
from .text_to_emotion import get_emotion_from_text
from .image_to_emotion import predict_emotion_from_image

# Dummy Lyrics Database
DUMMY_LYRICS = {
    "joy": [
        "Sunlight pours through golden cracks,\nEvery shadow fades and comes back,\nDancing on the edge of tomorrow,\nNo more room for yesterday's sorrow.\n\nChorus:\nI'm alive, I'm alive,\nWatch me rise, watch me thrive,\nEvery heartbeat, every breath,\nThis is living, not just death.",
        "The world is wide and so am I,\nStretching arms beneath the sky,\nLaughing loud at nothing much,\nEverything just feels like such.\n\nBridge:\nHold this moment, let it stay,\nDon't let sunshine slip away,\nWe were made for days like this,\nFull of ordinary bliss.",
    ],
    "sadness": [
        "Empty chairs at empty tables,\nAll the stories, all the fables,\nFading pictures on the wall,\nThe quiet after the last call.\n\nChorus:\nStay with me in the grey,\nIn the words I never say,\nEvery tear's a letter sent,\nTo the one who never went.",
        "Rain writes your name on my window,\nI trace each drop like a memento,\nThe echoes of your leaving voice,\nThe silence now, not my choice.\n\nBridge:\nMaybe time will blur the edge,\nMaybe I'll step off this ledge,\nInto something new, unknown,\nBut tonight I'm still alone.",
    ],
    "anger": [
        "You built your walls with borrowed stone,\nAnd claimed a kingdom all your own,\nBut kingdoms fall and walls crack through,\nI'm done with bowing down to you.\n\nChorus:\nLet it burn, let it burn,\nEvery bridge at every turn,\nI am flame, I am storm,\nDone performing, done conform.",
        "Your words were knives, your smiles were lies,\nI counted all your alibis,\nNo more swallowing the smoke,\nThis is where I finally woke.\n\nBridge:\nRage is honest, rage is clean,\nLouder than the things unseen,\nI am done with being small,\nWatch me rise above it all.",
    ],
    "fear": [
        "There's something in the dark again,\nA shape beneath the curtain's hem,\nMy heartbeat trips on every sound,\nI'm lost without a solid ground.\n\nChorus:\nHold the light, hold the flame,\nNothing here is quite the same,\nIn the space between the breath,\nLive the little fears of death.",
        "The clocks have stopped their counting now,\nI don't remember where or how,\nI got so tangled in the thread,\nOf things I've done and words I've said.\n\nBridge:\nMaybe fear is just the door,\nTo something worth exploring more,\nBut standing here at midnight's edge,\nI'm trembling on the ledge.",
    ],
    "love": [
        "You are the song I didn't write,\nThe warm hand reaching in the night,\nThe grammar of a softer world,\nA flag of tenderness unfurled.\n\nChorus:\nLove is not the grand parade,\nIt's the coffee that you made,\nIt's the way you know my name,\nEvery ordinary flame.",
        "Two satellites in different skies,\nOrbiting in slow disguise,\nGravity we didn't choose,\nA frequency we couldn't lose.\n\nBridge:\nPull me close, then let me go,\nBoth of us afraid to show,\nThat something quiet, something true,\nHappens every time I see you.",
    ],
    "surprise": [
        "I didn't see the morning come,\nI didn't hear the distant drum,\nUntil it was already here,\nThe thing I'd waited for all year.\n\nChorus:\nSurprise is just the universe,\nTurning the expected verse,\nInto something stranger, bright,\nA sudden left turn into light.",
        "The plot twist no one saw arriving,\nStill the story keeps on thriving,\nUnexpected, unannounced,\nLike a cat that just pounced.\n\nBridge:\nMaybe life is just the joke,\nThat only gets you when you woke,\nFrom the dream you thought was true,\nInto something wild and new.",
    ],
    "disgust": [
        "Peeling back the painted face,\nI see the rot beneath the grace,\nAll the gloss, the empty shine,\nNone of this was ever mine.\n\nChorus:\nI want to wash this feeling clean,\nScrub away what I have seen,\nTurn the page to something real,\nNot this staged, performative zeal.",
        "They served it up on silver plates,\nAnd called it love and called it fate,\nBut I can taste the bitter truth,\nLost somewhere between the proof.\n\nBridge:\nI'm done consuming what's not right,\nChoosing hunger over blight,\nEmpty is a cleaner state,\nThan eating lies off golden plates.",
    ],
    "anticipation": [
        "The night before the whole world shifts,\nThe held breath, the suspended gifts,\nStanding on the trembling edge,\nOf every undelivered pledge.\n\nChorus:\nAlmost there, almost arrived,\nAll this time I have survived,\nFor this moment, this threshold,\nThis story waiting to be told.",
        "Tomorrow lives in every clock,\nEvery turn of every lock,\nI can feel it in the air,\nSomething waiting over there.\n\nBridge:\nAnticipation is the song,\nThat keeps us moving all along,\nNot the ending, not the start,\nBut the hoping in the heart.",
    ],
}


def predict_emotion(text: str) -> dict:
    """
    Predict emotion from text using Hugging Face model
    Uses SamLowe/roberta-base-go_emotions model
    
    Raises:
        Exception: If HF API fails, the error is propagated to the caller
    """
    # Use the Hugging Face model for emotion detection
    emotion_result = get_emotion_from_text(text)
    top_emotion = emotion_result["emotion"]
    confidence = emotion_result["confidence"]
    scores = emotion_result["scores"]
    
    return {
        "emotion": top_emotion,
        "confidence": confidence,
        "scores": scores,
        "meta": EMOTION_META[top_emotion],
        "model": HF_EMOTION_MODEL
    }


def generate_lyrics(emotion: str) -> dict:
    """
    Dummy lyrics generator
    In production, replace with actual ML model
    """
    lyrics_list = DUMMY_LYRICS.get(emotion, DUMMY_LYRICS["joy"])
    lyrics = random.choice(lyrics_list)
    
    return {
        "lyrics": lyrics,
        "emotion_used": emotion,
        "model": f"{LYRIC_GEN_MODEL_NAME}-dummy",
        "tokens_generated": len(lyrics.split()),
    }


def get_emotion_from_image(image_bytes: bytes) -> dict:
    """
    Wrapper function to get emotion from image
    Calls the predict_emotion_from_image function from image_to_emotion module
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        dict: Emotion detection result with emotion, confidence, scores, meta, and model info
    """
    result = predict_emotion_from_image(image_bytes)
    return result
