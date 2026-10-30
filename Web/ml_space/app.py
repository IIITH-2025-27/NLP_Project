"""
LyricMind models Space (deployed to the existing IIITH-25-27/lyrics_Generator_for_emotion
Space, since new Gradio Spaces need a paid plan).

Hosts the torch-heavy pieces so the backend fits on Render's free tier:
  - /generate_lyrics  : original lyrics generator, unchanged (lyrics_generator.py)
  - /extract_face    : MTCNN face detection + 224x224 crop (input for image_to_emotion Space)
  - /text_emotion     : SamLowe/roberta-base-go_emotions scores (replaces the paid HF Inference API)
  - /evaluate_lyrics  : PHREM lyric quality score (Metric/evaluation_matric_PHREM.py)

Deploy with: python3 deploy_space.py
"""
import sys
from pathlib import Path

import gradio as gr
import nltk
import torch
from facenet_pytorch import MTCNN

# PHREM needs these at import time (cmudict) and inside g2p_en's pos_tag (taggers).
for pkg in ["cmudict", "averaged_perceptron_tagger", "averaged_perceptron_tagger_eng"]:
    nltk.download(pkg, quiet=True)

# On the Space, evaluation_matric_PHREM.py sits next to app.py (uploaded by deploy_space.py).
# Locally, fall back to the repo's Metric/ folder.
# (.parent rather than .parents[2]: the Space runs from /app, which has no grandparent.)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "Metric"))
from lyrics_generator import generate_lyrics, VALID_EMOTIONS  # noqa: E402
import evaluation_matric_PHREM as phrem_module  # noqa: E402
from evaluation_matric_PHREM import PHREM, FER_LABELS  # noqa: E402

torch.set_grad_enabled(False)
device = "cuda" if torch.cuda.is_available() else "cpu"

# keep_all=False ensures we only keep a single face crop per image.
mtcnn = MTCNN(image_size=224, margin=20, keep_all=False, device=device, post_process=True)
phrem = PHREM()


def extract_face(image):
    """Detect one face and return a stable 224x224 RGB crop from original pixels."""
    if image is None:
        raise gr.Error("No image provided.")
    img = image.convert("RGB")

    boxes, probs = mtcnn.detect(img)
    if boxes is None or len(boxes) == 0:
        raise gr.Error("No face detected.")

    # Pick the highest-confidence face, then crop from the original image.
    best_idx = int(probs.argmax()) if probs is not None else 0
    x1, y1, x2, y2 = boxes[best_idx]

    # Add a small context margin around detected face for robustness.
    w = x2 - x1
    h = y2 - y1
    margin = 0.10
    x1 -= w * margin
    y1 -= h * margin
    x2 += w * margin
    y2 += h * margin

    # Clamp to image bounds.
    img_w, img_h = img.size
    x1 = max(0, int(round(x1)))
    y1 = max(0, int(round(y1)))
    x2 = min(img_w, int(round(x2)))
    y2 = min(img_h, int(round(y2)))

    if x2 <= x1 or y2 <= y1:
        raise gr.Error("No face detected.")

    return img.crop((x1, y1, x2, y2)).resize((224, 224), resample=2)  # 2 = BILINEAR


def text_emotion(text):
    """
    Return {go_emotion_label: score} for all 28 GoEmotions.
    Reuses PHREM's SamLowe/roberta-base-go_emotions model. Sigmoid scores, matching
    what the HF Inference API returned for this multi-label model.
    """
    if not text or not text.strip():
        raise gr.Error("Text is empty.")
    tokenizer = phrem_module.emotion_tokenizer
    model = phrem_module.emotion_model
    inputs = tokenizer(text, truncation=True, return_tensors="pt").to(device)
    probs = torch.sigmoid(model(**inputs).logits)[0].cpu().tolist()
    return {model.config.id2label[i]: p for i, p in enumerate(probs)}


def evaluate_lyrics(lyrics, emotion_target):
    """Return the PHREM score clamped to [0, 1]."""
    if not lyrics or not lyrics.strip():
        raise gr.Error("Lyrics are empty.")
    if emotion_target not in FER_LABELS:
        raise gr.Error(f"emotion_target must be one of {FER_LABELS}")
    score = float(phrem.compute(lyrics, emotion_target=emotion_target))
    return max(0.0, min(1.0, score))


with gr.Blocks(title="LyricMind Models") as demo:
    gr.Markdown("# LyricMind Models\nLyrics generation, face extraction, text emotion and PHREM evaluation used by the LyricMind API.")

    # Same inputs and api_name as the original Space, so existing callers keep working.
    with gr.Tab("Generate lyrics"):
        lyric_inputs = [
            gr.Dropdown(VALID_EMOTIONS, value="happy", label="Select Emotion"),
            gr.Slider(minimum=20, maximum=300, value=100, step=10, label="Max Words"),
            gr.Slider(minimum=0.5, maximum=1.5, value=0.9, step=0.1, label="Temperature (Creativity)"),
            gr.Slider(minimum=10, maximum=100, value=50, step=5, label="Top-K (Word Choices)"),
            gr.Slider(minimum=0.5, maximum=1.0, value=0.95, step=0.05, label="Top-P (Probability Mass)"),
        ]
        lyric_out = gr.Textbox(label="Generated Lyrics")
        gr.Button("Generate").click(generate_lyrics, lyric_inputs, lyric_out, api_name="generate_lyrics")

    with gr.Tab("Extract face"):
        face_in = gr.Image(type="pil", label="Image")
        face_out = gr.Image(type="pil", format="png", label="Face (224x224)")
        gr.Button("Extract").click(extract_face, face_in, face_out, api_name="extract_face")

    with gr.Tab("Text emotion"):
        text_in = gr.Textbox(lines=3, label="Text")
        text_out = gr.JSON(label="GoEmotions scores")
        gr.Button("Analyze").click(text_emotion, text_in, text_out, api_name="text_emotion")

    with gr.Tab("Evaluate lyrics"):
        lyrics_in = gr.Textbox(lines=10, label="Lyrics")
        emotion_in = gr.Dropdown(FER_LABELS, value="Happy", label="Target emotion")
        score_out = gr.Number(label="PHREM score")
        gr.Button("Evaluate").click(
            evaluate_lyrics, [lyrics_in, emotion_in], score_out, api_name="evaluate_lyrics"
        )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
