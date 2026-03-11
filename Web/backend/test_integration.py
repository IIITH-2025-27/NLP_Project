"""
Integration test for image emotion detection
Tests the complete flow from image upload to emotion detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_service import get_emotion_from_image
from PIL import Image
import io
import requests

def test_image_emotion():
    print("="*60)
    print("Testing Image Emotion Detection Integration")
    print("="*60)
    
    try:
        # Download test image
        print("\n1. Downloading test image (bus)...")
        image_url = "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        response = requests.get(image_url, timeout=10)
        image_bytes = response.content
        print(f"   ✓ Downloaded {len(image_bytes)} bytes")
        
        # Test the image emotion detection
        print("\n2. Calling get_emotion_from_image()...")
        result = get_emotion_from_image(image_bytes)
        
        print("\n3. Result:")
        print(f"   Emotion: {result.get('emotion')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Source: {result.get('source')}")
        print(f"   Model: {result.get('model')}")
        
        if 'error' in result:
            print(f"   ⚠  Error: {result['error']}")
        
        print(f"\n   Scores:")
        for emotion, score in result.get('scores', {}).items():
            bar = "█" * int(score * 50)
            print(f"      {emotion:12s}: {score:.3f} {bar}")
        
        print(f"\n   Metadata:")
        meta = result.get('meta', {})
        print(f"      Emoji: {meta.get('emoji', 'N/A')}")
        print(f"      Color: {meta.get('color', 'N/A')}")
        print(f"      Description: {meta.get('description', 'N/A')}")
        
        print("\n" + "="*60)
        if 'error' not in result or result.get('emotion') != 'Neutral':
            print("✓ Integration test PASSED!")
        else:
            print("⚠  Integration test completed with errors")
        print("="*60)
        
        return result
        
    except Exception as e:
        print(f"\n✗ Integration test FAILED:")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_image_emotion()
