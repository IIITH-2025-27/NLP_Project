"""
Quick test to verify preprocessed image base64 is returned correctly
"""

import sys
import os
from pathlib import Path
import io
from PIL import Image, ImageDraw

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_service.image_to_emotion import predict_emotion_from_image


def create_simple_face():
    """Create a simple test image with a face-like pattern"""
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    draw.ellipse([100, 80, 300, 280], fill='peachpuff', outline='black', width=2)
    draw.ellipse([150, 140, 180, 170], fill='black')  # Left eye
    draw.ellipse([220, 140, 250, 170], fill='black')  # Right eye
    draw.line([200, 160, 200, 200], fill='black', width=2)  # Nose
    draw.arc([160, 210, 240, 260], start=0, end=180, fill='black', width=2)  # Smile
    
    return img


def main():
    print("=" * 70)
    print("PREPROCESSED IMAGE BASE64 TEST")
    print("=" * 70)
    
    img = create_simple_face()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    print("\nCalling predict_emotion_from_image...")
    result = predict_emotion_from_image(img_bytes)
    
    print("\n--- Result Keys ---")
    for key in result.keys():
        print(f"  - {key}")
    
    if "preprocessed_image" in result:
        print("\n✓ SUCCESS: preprocessed_image field is present!")
        
        img_data = result["preprocessed_image"]
        if img_data.startswith("data:image"):
            print(f"✓ Format is correct: {img_data[:50]}...")
            print(f"✓ Length: {len(img_data)} characters")
            
            # Try to decode and verify
            import base64
            try:
                base64_data = img_data.split(',')[1]
                decoded = base64.b64decode(base64_data)
                test_img = Image.open(io.BytesIO(decoded))
                print(f"✓ Image can be decoded: {test_img.size}")
                
                if test_img.size == (224, 224):
                    print("✓ Image is correctly sized: 224×224")
                else:
                    print(f"✗ Image size is {test_img.size}, expected (224, 224)")
                    
            except Exception as e:
                print(f"✗ Failed to decode image: {e}")
        else:
            print(f"✗ Format is incorrect: {img_data[:100]}")
    else:
        print("\n✗ FAIL: preprocessed_image field is missing!")
        print(f"Available fields: {list(result.keys())}")
    
    print("\n--- Full Result ---")
    for key, value in result.items():
        if key == "preprocessed_image":
            print(f"{key}: [base64 data - {len(value)} chars]")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
