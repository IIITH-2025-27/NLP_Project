"""
Utility script to upload models to Hugging Face Hub

Usage:
1. Set LOCAL_MODEL_PATH to your model folder path
2. Set HF_REPO_ID to your Hugging Face repo (format: username/repo-name)
3. Run: python upload_model.py
"""

from huggingface_hub import login, upload_folder

# Local path to your model folder
LOCAL_MODEL_PATH = "/home/vikash/Desktop/Lyric_generator_model/model"# Current directory, or use absolute path like "/path/to/model"

# Hugging Face repository ID (format: username/repo-name)
HF_REPO_ID = "IIITH-25-27/Spotify_gpt2_medium"

# Repository type: "model" or "dataset"
REPO_TYPE = "model"

if __name__ == "__main__":
    print(f"Uploading from: {LOCAL_MODEL_PATH}")
    print(f"To Hugging Face: {HF_REPO_ID}")
    print("-" * 50)
    
    # Login with your Hugging Face credentials
    # You'll be prompted to enter your HF token
    login()
    
    # Upload the model folder
    try:
        upload_folder(
            folder_path=LOCAL_MODEL_PATH,
            repo_id=HF_REPO_ID,
            repo_type=REPO_TYPE
        )
        print(f"\n✓ Successfully uploaded to {HF_REPO_ID}")
    except Exception as e:
        print(f"\n✗ Upload failed: {e}")
