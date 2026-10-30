# LyricMind Models Space

Source for the Hugging Face Space `IIITH-25-27/lyrics_Generator_for_emotion`.
It runs all the torch-heavy parts of LyricMind so the FastAPI backend on Render
only needs lightweight dependencies.

New Gradio Spaces now need a paid HF plan, but Spaces created before that still
run on free CPU, so everything is deployed into this existing Space.

| API name           | Input                      | Output                     |
|--------------------|----------------------------|----------------------------|
| `/generate_lyrics` | emotion, max words, temperature, top-k, top-p | lyrics (unchanged original endpoint) |
| `/extract_face`    | image                      | 224x224 PNG face crop      |
| `/text_emotion`    | text                       | 28 GoEmotions scores       |
| `/evaluate_lyrics` | lyrics, target emotion     | PHREM score (0-1)          |

- `lyrics_generator.py` is the original Space code, unchanged.
- `evaluation_matric_PHREM.py` is uploaded from the repo's `Metric/` folder by
  `deploy_space.py`; edit it there, not on the Space.
- The Space's own `README.md` (its config) is not overwritten.

## Deploy

```bash
pip install huggingface_hub
python3 Web/ml_space/deploy_space.py
```

The backend uses this Space by default (`ML_UTILS_SPACE` in `Web/backend/config.py`).
