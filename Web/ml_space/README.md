---
title: LyricMind ML Utils
emoji: 🎵
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 6.9.0
app_file: app.py
pinned: false
short_description: Face extraction and PHREM lyric evaluation for LyricMind
---

# LyricMind ML Utils

Hugging Face Space that runs the torch-heavy parts of the LyricMind backend, so
the FastAPI server on Render only needs lightweight dependencies.

| API name           | Input                      | Output                     |
|--------------------|----------------------------|----------------------------|
| `/extract_face`    | image                      | 224x224 PNG face crop      |
| `/evaluate_lyrics` | lyrics, target emotion     | PHREM score (0-1)          |

`evaluation_matric_PHREM.py` is copied from the repo's `Metric/` folder by
`deploy_space.py`; edit it there, not on the Space.

## Deploy

```bash
pip install huggingface_hub
python Web/ml_space/deploy_space.py                       # IIITH-25-27/lyricmind_ml_utils
python Web/ml_space/deploy_space.py <user>/<space-name>   # custom Space
```

If you use a custom Space name, set `GRADIO_ML_UTILS_SPACE` in
`Web/backend/constants.py` to match.
