"""
Emotion Mapping Configuration
Based on the lyrics_emotion_mapper.ipynb notebook approach

This file defines how 28 GoEmotions from SamLowe/roberta-base-go_emotions model
are mapped to 6 FER (Facial Emotion Recognition) categories.

Reference: /Datasets/lyrics_emotion_mapper.ipynb
"""

# ============================================================================
# 28 GoEmotions from SamLowe/roberta-base-go_emotions model
# ============================================================================

ALL_GOEMOTIONS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 
    'caring', 'confusion', 'curiosity', 'desire', 'disappointment',
    'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear',
    'gratitude', 'grief', 'joy', 'love', 'nervousness',
    'optimism', 'pride', 'realization', 'relief', 'remorse',
    'sadness', 'surprise', 'neutral'
]

# ============================================================================
# FER (Facial Emotion Recognition) Categories
# ============================================================================

FER_EMOTIONS = [
    "Angry",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral",
]

# ============================================================================
# Mapping: 28 GoEmotions → 6 FER Emotions
# ============================================================================
# This mapping matches the notebook's FER_MAPPING exactly
# Each FER category is formed by grouping related GoEmotions

FER_GROUPS = {
    'Angry': [
        'anger',       # Direct anger emotion
        'annoyance',   # Mild anger/irritation
        'disapproval', # Negative judgment
        'disgust'      # Strong aversion
    ],
    
    'Fear': [
        'fear',        # Direct fear emotion
        'nervousness'  # Anxiety/worry
    ],
    
    'Happy': [
        'admiration',  # Respect/appreciation
        'amusement',   # Entertainment/humor
        'approval',    # Agreement/acceptance
        'caring',      # Compassion/concern
        'desire',      # Wanting/longing
        'excitement',  # Anticipation/enthusiasm
        'gratitude',   # Thankfulness
        'joy',         # Happiness/delight
        'love',        # Affection/attachment
        'optimism',    # Positive outlook
        'pride',       # Achievement/satisfaction
        'relief'       # Release from tension
    ],
    
    'Sad': [
        'sadness',     # Direct sadness emotion
        'grief',       # Deep sorrow/loss
        'disappointment', # Unmet expectations
        'remorse',     # Regret/guilt
        'embarrassment' # Shame/awkwardness
    ],
    
    'Surprise': [
        'surprise',    # Unexpected event
        'realization'  # Sudden understanding
    ],
    
    'Neutral': [
        'neutral',     # No strong emotion
        'curiosity',   # Interest/wonder
        'confusion'    # Uncertainty/perplexity
    ]
}

# ============================================================================
# Reverse Mapping: GoEmotions → FER (for efficient lookup)
# ============================================================================
# This is the actual mapping dictionary used in the code

GOEMOTIONS_TO_FER = {}
for fer_emotion, go_emotions_list in FER_GROUPS.items():
    for go_emotion in go_emotions_list:
        GOEMOTIONS_TO_FER[go_emotion] = fer_emotion

# ============================================================================
# Emotion Aggregation Logic (from notebook)
# ============================================================================
"""
How emotions are aggregated:

1. **Input**: Text string
   Example: "I'm so excited and happy today! This is amazing!"

2. **Model Output**: 28 GoEmotions with probabilities (scores that sum to ~1.0)
   Example API response:
   [
     {"label": "joy", "score": 0.65},
     {"label": "excitement", "score": 0.25},
     {"label": "admiration", "score": 0.05},
     {"label": "optimism", "score": 0.03},
     {"label": "neutral", "score": 0.01},
     ... (28 emotions total)
   ]

3. **Map to FER**: Sum probabilities for each FER group
   Happy = joy(0.65) + excitement(0.25) + admiration(0.05) + optimism(0.03) = 0.98
   Neutral = neutral(0.01) = 0.01
   Sad = 0.005
   Angry = 0.003
   Fear = 0.001
   Surprise = 0.001

4. **Normalize**: Ensure FER scores sum to 1.0
   total = 1.0
   Happy = 0.98 / 1.0 = 0.980 (98.0%)
   Neutral = 0.01 / 1.0 = 0.010 (1.0%)
   Sad = 0.005 / 1.0 = 0.005 (0.5%)
   Angry = 0.003 / 1.0 = 0.003 (0.3%)
   Fear = 0.001 / 1.0 = 0.001 (0.1%)
   Surprise = 0.001 / 1.0 = 0.001 (0.1%)

5. **Dominant Emotion**: Take argmax
   Dominant = "Happy" (98.0% confidence)

6. **Final Output**:
   {
     "emotion": "Happy",
     "confidence": 0.980,
     "scores": {
       "Happy": 0.980,
       "Sad": 0.005,
       "Angry": 0.003,
       "Fear": 0.001,
       "Surprise": 0.001,
       "Neutral": 0.010
     }
   }
"""

# ============================================================================
# Statistics about the mapping
# ============================================================================

MAPPING_STATS = {
    "total_goemotions": len(ALL_GOEMOTIONS),
    "total_fer_categories": len(FER_EMOTIONS),
    "fer_group_sizes": {
        fer: len(groups) for fer, groups in FER_GROUPS.items()
    },
    "largest_group": "Happy (12 emotions)",
    "smallest_groups": "Fear, Surprise (2 emotions each)"
}

# ============================================================================
# Validation function
# ============================================================================

def validate_mapping():
    """
    Validate that all 28 GoEmotions are mapped exactly once
    """
    # Check all GoEmotions are covered
    mapped_emotions = set()
    for go_emotions_list in FER_GROUPS.values():
        mapped_emotions.update(go_emotions_list)
    
    all_emotions_set = set(ALL_GOEMOTIONS)
    
    if mapped_emotions != all_emotions_set:
        missing = all_emotions_set - mapped_emotions
        extra = mapped_emotions - all_emotions_set
        
        if missing:
            print(f"❌ Missing GoEmotions in mapping: {missing}")
        if extra:
            print(f"❌ Extra emotions in mapping: {extra}")
        return False
    
    print(f"✓ All {len(ALL_GOEMOTIONS)} GoEmotions are properly mapped to 6 FER categories")
    print(f"\nMapping distribution:")
    for fer, groups in FER_GROUPS.items():
        print(f"  {fer}: {len(groups)} emotions")
    
    return True


def print_mapping_table():
    """
    Print a nicely formatted mapping table
    """
    print("\n" + "="*80)
    print("EMOTION MAPPING: 28 GoEmotions → 6 FER Categories")
    print("="*80 + "\n")
    
    for fer_emotion in FER_EMOTIONS:
        go_emotions = FER_GROUPS[fer_emotion]
        print(f"{fer_emotion} ({len(go_emotions)} emotions):")
        print(f"  └─ {', '.join(go_emotions)}")
        print()
    
    print("="*80)
    print(f"Total: {len(ALL_GOEMOTIONS)} GoEmotions → {len(FER_EMOTIONS)} FER Categories")
    print("="*80 + "\n")


if __name__ == "__main__":
    # When run directly, validate and print the mapping
    print("Validating emotion mapping...")
    validate_mapping()
    print_mapping_table()
