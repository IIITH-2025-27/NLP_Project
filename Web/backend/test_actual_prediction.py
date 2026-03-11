"""
Test actual prediction with the Gradio API
"""

from gradio_client import Client, handle_file
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

def test_prediction():
    try:
        print("Testing actual prediction with Gradio API...")
        print(f"Using HF Token: {'Yes' if HF_API_TOKEN else 'No'}")
        
        # Try to create client and make prediction directly
        # without checking API info first
        print("\n1. Initializing client...")
        
        try:
            if HF_API_TOKEN:
                client = Client("IIITH-25-27/LyricMind_Models", token=HF_API_TOKEN)
            else:
                client = Client("IIITH-25-27/LyricMind_Models")
            print("   ✓ Client initialized")
        except Exception as e:
            print(f"   ✗ Client initialization error (trying anyway): {e}")
            # Try to proceed anyway
            client = Client("IIITH-25-27/LyricMind_Models")
        
        print("\n2. Making prediction with test image...")
        # Use the bus image from the API documentation
        result = client.predict(
            image=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
            api_name="/predict"
        )
        
        print(f"\n✓ Success! Prediction result:")
        print(f"   Type: {type(result)}")
        print(f"   Value: {result}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error during prediction:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_prediction()
    if result:
        print("\n" + "="*60)
        print("API is working correctly!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("API test failed - check the error above")
        print("="*60)
