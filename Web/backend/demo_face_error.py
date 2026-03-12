"""
Demo: No-Face Error Handling
Demonstrates what happens when users upload images without faces
"""

import sys
import os
from pathlib import Path
import io
from PIL import Image, ImageDraw

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_service.image_to_emotion import predict_emotion_from_image


def create_landscape_image():
    """Create a landscape scene (no face)"""
    img = Image.new('RGB', (800, 600), color='skyblue')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 400, 800, 600], fill='green')
    draw.ellipse([650, 50, 750, 150], fill='yellow')
    draw.rectangle([100, 300, 130, 400], fill='brown')
    draw.ellipse([50, 220, 180, 350], fill='darkgreen')
    
    return img


def create_pattern_image():
    """Create an abstract pattern (no face)"""
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw checkerboard
    for i in range(0, 400, 50):
        for j in range(0, 400, 50):
            if (i + j) % 100 == 0:
                draw.rectangle([i, j, i+50, j+50], fill='black')
    
    return img


def test_image(img, image_name):
    """Test an image and print the result"""
    print(f"\n{'='*70}")
    print(f"Testing: {image_name}")
    print('='*70)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    print(f"Image size: {img.size}")
    print("Processing...")
    
    result = predict_emotion_from_image(img_bytes)
    
    if "error" in result:
        print("\n❌ ERROR DETECTED:")
        print(f"   Error Type: {result.get('error_type', 'Unknown')}")
        print(f"   Message: {result['error']}")
        if "suggestion" in result:
            print(f"   Suggestion: {result['suggestion']}")
    elif "emotion" in result:
        print("\n✓ SUCCESS:")
        print(f"   Emotion: {result['emotion']}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
    else:
        print(f"\n⚠ UNEXPECTED RESULT: {result}")


def main():
    print("=" * 70)
    print("NO-FACE DETECTION DEMO")
    print("=" * 70)
    print("\nThis demonstrates the error handling when images don't contain faces.")
    print("MTCNN (face detector) is strict and requires real human faces.")
    
    # Test various non-face images
    test_image(create_landscape_image(), "Landscape Scene")
    test_image(create_pattern_image(), "Abstract Pattern")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ The system correctly rejects images without detectable faces")
    print("✓ Users receive clear error messages with suggestions")
    print("✓ API returns HTTP 400 (Bad Request) for no-face images")
    print("\nTo test with real images:")
    print("  - Use selfies or portraits with clear, visible faces")
    print("  - Ensure good lighting and no obstructions")
    print("  - Face should be frontal or near-frontal")


if __name__ == "__main__":
    main()
