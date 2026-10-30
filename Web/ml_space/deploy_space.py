"""
Upload the LyricMind models app to the existing lyrics Space.

New Gradio Spaces need a paid HF plan, but Spaces created before that still run
on free CPU, so everything is deployed into IIITH-25-27/lyrics_Generator_for_emotion.
Its README.md (Space config) is left untouched.

Usage:
    python3 deploy_space.py [repo_id]     (default: IIITH-25-27/lyrics_Generator_for_emotion)

Uses your cached HF login (`hf auth login`) or HF_TOKEN env var;
prompts for a token if neither is set. The token needs write access to the org.
"""
import sys
from pathlib import Path

from huggingface_hub import HfApi, get_token, login

SPACE_DIR = Path(__file__).resolve().parent
PHREM_FILE = SPACE_DIR.parents[1] / "Metric" / "evaluation_matric_PHREM.py"
HF_REPO_ID = sys.argv[1] if len(sys.argv) > 1 else "IIITH-25-27/lyrics_Generator_for_emotion"

if __name__ == "__main__":
    if not get_token():
        login()

    api = HfApi()
    if not api.repo_exists(HF_REPO_ID, repo_type="space"):
        sys.exit(f"Space {HF_REPO_ID} not found.")

    print(f"Uploading {SPACE_DIR} -> spaces/{HF_REPO_ID}")
    api.upload_folder(
        folder_path=SPACE_DIR,
        repo_id=HF_REPO_ID,
        repo_type="space",
        allow_patterns=["app.py", "lyrics_generator.py", "requirements.txt"],
        commit_message="Add face extraction, text emotion and PHREM endpoints",
    )
    api.upload_file(
        path_or_fileobj=PHREM_FILE,
        path_in_repo="evaluation_matric_PHREM.py",
        repo_id=HF_REPO_ID,
        repo_type="space",
    )
    print(f"✓ Done: https://huggingface.co/spaces/{HF_REPO_ID}")
    print(f"Backend env (Render + Web/backend/.env): ML_UTILS_SPACE={HF_REPO_ID}")
