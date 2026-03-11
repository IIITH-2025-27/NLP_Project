"""
Test script for 6 FER emotion detection using Hugging Face Inference API
No local model download - runs on HF servers!
"""
import sys
sys.path.append('/home/vikash/Desktop/git_folders/NLP_Project/Web/backend')

from ml_service.text_to_emotion import get_emotion_from_text
from constants import EMOTIONS, EMOTION_META

print("=" * 60)
print("Testing 6 FER Emotion Detection (HF Inference API)")
print("=" * 60)
print(f"\nAvailable emotions: {EMOTIONS}")
print()

# Test cases for different emotions
test_cases = [
    ("I'm so excited and happy today! This is amazing!", "Happy"),
    ("I feel terrible and depressed. Everything is going wrong.", "Sad"),
    ("This makes me furious! I can't believe they did this!", "Angry"),
    ("I'm really scared and anxious about what might happen.", "Fear"),
    ("Wow! I never expected this to happen!", "Surprise"),
    ("The weather is okay today. Nothing special.", "Neutral"),
]

print("Testing emotion detection on sample texts:")
print("-" * 60)

for text, expected in test_cases:
    print(f"\n📝 Text: \"{text}\"")
    print(f"   Expected: {expected}")
    
    result = get_emotion_from_text(text)
    
    detected = result['emotion']
    confidence = result['confidence']
    
    print(f"   Detected: {detected} ({confidence:.1%} confidence)")
    
    # Show top 3 emotions
    sorted_scores = sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   Top scores: {', '.join([f'{e}: {s:.1%}' for e, s in sorted_scores])}")
    
    match = "✓" if detected == expected else "✗"
    print(f"   {match} Match: {detected == expected}")

print("\n" + "=" * 60)
print("✓ All tests completed!")
print("=" * 60)
