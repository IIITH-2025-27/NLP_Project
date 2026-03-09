import random
from PIL import Image
import io

# Emotion Configuration
EMOTIONS = ["joy", "sadness", "anger", "fear", "love", "surprise", "disgust", "anticipation"]

# Map image emotion labels (from FER2013 dataset) to our emotion system
# FER2013 has: 0=Angry, 1=Disgust, 2=Fear, 3=Happy, 4=Sad, 5=Surprise, 6=Neutral
IMAGE_EMOTION_MAP = {
    0: "anger",
    1: "disgust", 
    2: "fear",
    3: "joy",
    4: "sadness",
    5: "surprise",
    6: "anticipation"  # neutral maps to anticipation
}

EMOTION_META = {
    "joy":         {"emoji": "✨", "color": "#FFD93D", "description": "Radiating happiness"},
    "sadness":     {"emoji": "🌧️", "color": "#6BA3BE", "description": "Melancholic undertones"},
    "anger":       {"emoji": "🔥", "color": "#FF6B6B", "description": "Burning intensity"},
    "fear":        {"emoji": "🌑", "color": "#845EC2", "description": "Shadowed anxiety"},
    "love":        {"emoji": "💖", "color": "#FF9EAA", "description": "Warm affection"},
    "surprise":    {"emoji": "⚡", "color": "#4ECDC4", "description": "Unexpected wonder"},
    "disgust":     {"emoji": "🌿", "color": "#4CAF50", "description": "Rejecting repulsion"},
    "anticipation":{"emoji": "🌅", "color": "#FF9800", "description": "Eager expectation"},
}

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
    Dummy emotion classifier
    In production, replace with actual ML model
    """
    text_lower = text.lower()
    keyword_map = {
        "joy":          ["happy", "joy", "great", "wonderful", "excited", "amazing", "love", "laugh", "smile"],
        "sadness":      ["sad", "cry", "miss", "lost", "alone", "empty", "grief", "heartbreak", "tears"],
        "anger":        ["angry", "hate", "furious", "rage", "frustrated", "annoyed", "mad", "outrage"],
        "fear":         ["scared", "afraid", "fear", "terrified", "anxious", "worried", "dread", "panic"],
        "love":         ["love", "adore", "cherish", "heart", "darling", "beloved", "tender", "warm"],
        "surprise":     ["surprised", "shocked", "unexpected", "wow", "unbelievable", "sudden", "astonished"],
        "disgust":      ["disgust", "gross", "repulsive", "awful", "horrible", "revolting", "nauseating"],
        "anticipation": ["waiting", "expecting", "hope", "soon", "tomorrow", "excited", "looking forward"],
    }
    
    scores = {emotion: 0.0 for emotion in EMOTIONS}
    for emotion, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text_lower:
                scores[emotion] += 1.0
    
    total = sum(scores.values())
    if total == 0:
        detected = random.choice(EMOTIONS)
        scores[detected] = 1.0
        total = 1.0
    
    normalized = {e: round(v / total, 3) for e, v in scores.items()}
    top_emotion = max(normalized, key=normalized.get)
    confidence = round(normalized[top_emotion] + random.uniform(0.05, 0.15), 3)
    confidence = min(confidence, 0.99)
    
    return {
        "emotion": top_emotion,
        "confidence": confidence,
        "scores": normalized,
        "meta": EMOTION_META[top_emotion],
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
        "model": "LyricGen-v2-dummy",
        "tokens_generated": len(lyrics.split()),
    }


def predict_emotion_from_image(image_bytes: bytes) -> dict:
    """
    Predict emotion from image
    In production, replace with actual vision model (ResNet18 + FER2013)
    For now, using dummy prediction
    """
    try:
        # Open and validate image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Dummy prediction - in production, this would use a trained model
        # Simulating ResNet18/FER2013 emotion detection
        simulated_prediction = random.randint(0, 6)
        detected_emotion = IMAGE_EMOTION_MAP[simulated_prediction]
        
        # Generate confidence scores
        scores = {emotion: round(random.uniform(0.01, 0.15), 3) for emotion in EMOTIONS}
        scores[detected_emotion] = round(random.uniform(0.4, 0.7), 3)
        
        # Normalize scores
        total = sum(scores.values())
        normalized = {e: round(v / total, 3) for e, v in scores.items()}
        
        confidence = normalized[detected_emotion]
        
        return {
            "emotion": detected_emotion,
            "confidence": confidence,
            "scores": normalized,
            "meta": EMOTION_META[detected_emotion],
            "source": "image"
        }
        
    except Exception as e:
        # If image processing fails, return a default emotion
        default_emotion = "joy"
        return {
            "emotion": default_emotion,
            "confidence": 0.5,
            "scores": {e: 0.125 for e in EMOTIONS},
            "meta": EMOTION_META[default_emotion],
            "source": "image",
            "error": str(e)
        }
