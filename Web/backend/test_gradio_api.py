"""
Test script to verify Gradio API for image emotion detection
"""

from gradio_client import Client
import httpx
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

def test_space_status():
    """Check if the Gradio Space is running"""
    try:
        print("Checking Space status...")
        url = "https://iiith-25-27-lyricmind-models.hf.space"
        
        # Add HF token to headers if available
        headers = {}
        if HF_API_TOKEN:
            headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
        
        response = httpx.get(url, timeout=10.0, headers=headers, follow_redirects=True)
        print(f"✓ Space URL is reachable (Status: {response.status_code})")
        
        # Try to check /info endpoint
        info_url = f"{url}/info"
        info_response = httpx.get(info_url, timeout=10.0, headers=headers)
        print(f"Info endpoint status: {info_response.status_code}")
        if info_response.status_code == 200:
            print(f"Response: {info_response.text[:200]}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Space is not reachable: {e}")
        return False

def test_gradio_api():
    # First check if space is running
    if not test_space_status():
        print("\n" + "="*60)
        print("ISSUE: The Gradio Space is not accessible")
        print("="*60)
        print("\nPossible reasons:")
        print("1. The Space 'IIITH-25-27/LyricMind_Models' doesn't exist on Hugging Face")
        print("2. The Space is private but the token doesn't have access")
        print("3. The Space name is incorrect")
        print("\nPlease verify:")
        print("- Visit: https://huggingface.co/spaces/IIITH-25-27/LyricMind_Models")
        print("- Check if the Space exists and is public or you have access")
        print("- Verify the Space name is correct")
        return
    
    print("\n" + "="*60)
    print("Attempting to connect to Gradio Client...")
    print("="*60)
    
    try:
        # Try with timeout
        print("\nConnecting to Gradio API (this may take a moment)...")
        print(f"Using HF Token: {'Yes' if HF_API_TOKEN else 'No'}")
        
        if HF_API_TOKEN:
            client = Client("IIITH-25-27/LyricMind_Models", token=HF_API_TOKEN, verbose=True)
        else:
            client = Client("IIITH-25-27/LyricMind_Models", verbose=True)
        
        print("✓ Connected successfully!")
        print("\nAPI Info:")
        
        # Try to get API endpoints
        try:
            print("\nAvailable API endpoints:")
            if hasattr(client, 'endpoints'):
                for endpoint in client.endpoints:
                    print(f"  - {endpoint}")
            
            print("\nTrying to view API structure...")
            api_info = client.view_api(return_format="dict")
            print(api_info)
            
        except Exception as e:
            print(f"Could not fetch detailed API info: {e}")
        
        print("\n" + "="*60)
        print("✓ API connection successful!")
        print("You can now test with an actual image")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error connecting to Gradio API:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        print("\nPossible solutions:")
        print("1. The Space might be sleeping - visit the URL to wake it up")
        print("2. The Space might not have a valid /predict endpoint")
        print("3. Try waiting 30-60 seconds for the Space to fully load")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_gradio_api()
