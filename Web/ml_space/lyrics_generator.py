"""
Emotion -> lyrics generation (IIITH-25-27/Emotion_to_lyrics_model).
Copied unchanged from the original lyrics_Generator_for_emotion Space app.py;
the UI now lives in app.py.
"""
import gradio as gr
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

REPO_ID = "IIITH-25-27/Emotion_to_lyrics_model"

# =========================
# LOAD MODEL
# =========================
tokenizer = GPT2Tokenizer.from_pretrained(REPO_ID)
tokenizer.pad_token = tokenizer.eos_token

model = GPT2LMHeadModel.from_pretrained(REPO_ID)
model.resize_token_embeddings(len(tokenizer))  # ✅ important for special tokens
model.eval()

# =========================
# VALID EMOTIONS
# =========================
VALID_EMOTIONS = ["happy", "sad", "angry", "surprise", "fear", "neutral"]

# =========================
# FUNCTION
# =========================
def generate_lyrics(emotion, max_words, temperature, top_k, top_p):
    # Normalize + validate emotion
    emotion = emotion.lower().strip()
    if emotion not in VALID_EMOTIONS:
        return f"❌ Invalid emotion. Choose from: {', '.join(VALID_EMOTIONS)}"

    # Safety limits
    max_words = int(min(max_words, 300))
    max_tokens = int(max_words * 1.5)

    # ✅ MATCH TRAINING FORMAT
    prompt = f"<{emotion}>"

    inputs = tokenizer.encode(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=max_tokens,
            temperature=float(temperature),
            top_k=int(top_k),
            top_p=float(top_p),
            repetition_penalty=1.25,
            no_repeat_ngram_size=2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove prompt token
    result = text.replace(prompt, "").strip()

    return result if result else "⚠️ Try adjusting parameters for better output."
