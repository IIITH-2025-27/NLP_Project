"""
Test script to verify no-face detection error handling
"""

import sys
import os
from pathlib import Path
import io
from PIL import Image, ImageDraw

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ml_service.image_processing import preprocess_image, preprocess_and_save_image
    from ml_service.image_to_emotion import predict_emotion_from_image
    print("✓ Successfully imported modules")
except ImportError as e:
    print(f"✗ Failed to import modules: {e}")
    sys.exit(1)


def create_image_with_face():
    """Create a simple test image with a face-like structure"""
    img = Image.new('RGB', (512, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    draw.ellipse([150, 100, 362, 312], fill='peachpuff', outline='black', width=3)
    draw.ellipse([200, 180, 230, 210], fill='black')
    draw.ellipse([282, 180, 312, 210], fill='black')
    draw.line([256, 195, 256, 240], fill='black', width=2)
    draw.arc([220, 240, 292, 280], start=0, end=180, fill='black', width=3)
    
    return img


def create_image_without_face():
    """Create an image without a face (landscape)"""
    img = Image.new('RGB', (800, 600), color='skyblue')
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, 400, 800, 600], fill='green')
    
    # Draw sun
    draw.ellipse([650, 50, 750, 150], fill='yellow')
    
    # Draw tree
    draw.rectangle([100, 300, 130, 400], fill='brown')
    draw.ellipse([50, 220, 180, 350], fill='darkgreen')
    
    return img


def test_with_face():
    """Test with an image that has a face - should succeed"""
    print("\n--- Test 1: Image WITH face (should succeed) ---")
    
    try:
        img = create_image_with_face()
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        result = predict_emotion_from_image(img_bytes)
        
        if "error" in result and result.get("error_type") == "NoFaceDetected":
            print(f"✗ Unexpectedly got no-face error: {result['error']}")
            return False
        elif "emotion" in result:
            print(f"✓ Successfully detected emotion: {result['emotion']}")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
            return True
        else:
            print(f"✗ Unexpected result format: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_without_face():
    """Test with an image that has NO face - should return error"""
    print("\n--- Test 2: Image WITHOUT face (should return error) ---")
    
    try:
        img = create_image_without_face()
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        result = predict_emotion_from_image(img_bytes)
        
        if "error" in result and result.get("error_type") == "NoFaceDetected":
            print(f"✓ Correctly returned no-face error")
            print(f"  Error message: {result['error']}")
            print(f"  Suggestion: {result.get('suggestion', 'N/A')}")
            return True
        elif "emotion" in result:
            print(f"✗ Should have returned error but got emotion: {result['emotion']}")
            return False
        else:
            print(f"✗ Unexpected result format: {result}")
            return False
            
    except ValueError as e:
        # This is also acceptable - error raised directly
        if "No face detected" in str(e):
            print(f"✓ Correctly raised ValueError: {e}")
            return True
        else:
            print(f"✗ Got ValueError but wrong message: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error type: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocess_function_directly():
    """Test the preprocess_image function directly"""
    print("\n--- Test 3: Direct preprocess_image function test ---")
    
    # Test with no face
    try:
        img_no_face = create_image_without_face()
        img_bytes = io.BytesIO()
        img_no_face.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        print("Testing preprocess_image with no-face image...")
        result = preprocess_image(img_bytes)
        print(f"✗ Should have raised ValueError but got result: {result.shape}")
        return False
        
    except ValueError as e:
        if "No face detected" in str(e):
            print(f"✓ Correctly raised ValueError: {e}")
            return True
        else:
            print(f"✗ Got ValueError but wrong message: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        return False


def main():
    print("=" * 70)
    print("NO-FACE DETECTION ERROR HANDLING TEST")
    print("=" * 70)
    
    results = []
    results.append(("Image with face", test_with_face()))
    results.append(("Image without face", test_without_face()))
    results.append(("Direct preprocess function", test_preprocess_function_directly()))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! No-face error handling is working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
