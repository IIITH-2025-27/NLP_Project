"""
Create/update the LyricMind ML Utils Hugging Face Space.

Usage:
    python deploy_space.py [repo_id]     (default: IIITH-25-27/lyricmind_ml_utils)

Uses your cached HF login (`huggingface-cli login`) or HF_TOKEN env var;
prompts for a token if neither is set.
"""
import sys
from pathlib import Path

from huggingface_hub import HfApi, get_token, login

SPACE_DIR = Path(__file__).resolve().parent
PHREM_FILE = SPACE_DIR.parents[1] / "Metric" / "evaluation_matric_PHREM.py"
HF_REPO_ID = sys.argv[1] if len(sys.argv) > 1 else "IIITH-25-27/lyricmind_ml_utils"

if __name__ == "__main__":
    if not get_token():
        login()

    api = HfApi()
    api.create_repo(HF_REPO_ID, repo_type="space", space_sdk="gradio", exist_ok=True)

    print(f"Uploading {SPACE_DIR} -> spaces/{HF_REPO_ID}")
    api.upload_folder(
        folder_path=SPACE_DIR,
        repo_id=HF_REPO_ID,
        repo_type="space",
        allow_patterns=["app.py", "requirements.txt", "README.md"],
    )
    api.upload_file(
        path_or_fileobj=PHREM_FILE,
        path_in_repo="evaluation_matric_PHREM.py",
        repo_id=HF_REPO_ID,
        repo_type="space",
    )
    print(f"✓ Done: https://huggingface.co/spaces/{HF_REPO_ID}")
