"""
Test script to check if the emotion detection model is biased towards Sad
"""

import sys
import os
from pathlib import Path
import io
from PIL import Image, ImageDraw

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_service.image_to_emotion import predict_emotion_from_image


def create_smiling_face():
    """Create a simple smiling face"""
    img = Image.new('RGB', (400, 400), color='lightyellow')
    draw = ImageDraw.Draw(img)
    
    # Face circle
    draw.ellipse([100, 80, 300, 280], fill='peachpuff', outline='black', width=3)
    # Eyes
    draw.ellipse([150, 140, 180, 170], fill='black')
    draw.ellipse([220, 140, 250, 170], fill='black')
    # Smiling mouth
    draw.arc([140, 180, 260, 250], start=0, end=180, fill='black', width=3)
    
    return img


def create_sad_face():
    """Create a simple sad face"""
    img = Image.new('RGB', (400, 400), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Face circle
    draw.ellipse([100, 80, 300, 280], fill='lightgray', outline='black', width=3)
    # Eyes
    draw.ellipse([150, 140, 180, 170], fill='black')
    draw.ellipse([220, 140, 250, 170], fill='black')
    # Frowning mouth
    draw.arc([140, 220, 260, 260], start=180, end=360, fill='black', width=3)
    
    return img


def create_angry_face():
    """Create a simple angry face"""
    img = Image.new('RGB', (400, 400), color='lightcoral')
    draw = ImageDraw.Draw(img)
    
    # Face circle
    draw.ellipse([100, 80, 300, 280], fill='pink', outline='black', width=3)
    # Angry eyes
    draw.ellipse([150, 140, 180, 170], fill='red')
    draw.ellipse([220, 140, 250, 170], fill='red')
    # Angry eyebrows
    draw.line([145, 130, 185, 135], fill='black', width=4)
    draw.line([215, 135, 255, 130], fill='black', width=4)
    # Frowning mouth
    draw.arc([140, 220, 260, 260], start=180, end=360, fill='black', width=3)
    
    return img


def test_image(img, test_name):
    """Test an image and print results"""
    print("\n" + "=" * 70)
    print(f"Testing: {test_name}")
    print("=" * 70)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    try:
        result = predict_emotion_from_image(img_bytes)
        
        if "error" in result:
            print(f"❌ ERROR: {result['error']}")
        else:
            print(f"✓ Detected Emotion: {result['emotion']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Top 3 scores:")
            sorted_scores = sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)
            for emotion, score in sorted_scores[:3]:
                print(f"    - {emotion}: {score:.2%}")
    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    print("=" * 70)
    print("EMOTION DETECTION MODEL BIAS TEST")
    print("=" * 70)
    print("\nTesting if the model always detects 'Sad' or varies by image...")
    print("Note: Simple drawn faces may not be detected by MTCNN face detector")
    print("Check the terminal output for [DEBUG] logs from the model")
    
    # Test different emotions
    test_image(create_smiling_face(), "Smiling Face")
    test_image(create_sad_face(), "Sad Face")
    test_image(create_angry_face(), "Angry Face")
    
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("Check the results above:")
    print("- If all are 'Sad' → MODEL ISSUE (model is biased)")
    print("- If varied → MODEL WORKING (may need real photos not drawings)")
    print("- If all have 'No face detected' error → Drawings don't work, try real photos")
    print("\nTo test with a real photo:")
    print("  1. Take a selfie with different expressions")
    print("  2. Upload via the web interface")
    print("  3. Check the backend logs for [DEBUG] output")


if __name__ == "__main__":
    main()
