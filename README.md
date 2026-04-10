# MERGE: Multimodal Emotion-Driven Rhythmic Lyric Generation Engine

Simple project guide for running NLP experiments and the Web app.

## NLP Pipeline

1. Image/text input is analyzed for emotion.
2. Emotion is mapped to one of 6 classes: Angry, Fear, Happy, Sad, Surprise, Neutral.
3. Emotion-conditioned lyric generation model creates lyrics.
4. Results are shown in the Web app and can be stored in history.

## Web Pipeline

1. User submits text or image in the frontend.
2. Frontend sends request to FastAPI backend.
3. Backend runs emotion detection:
	- Text path: Hugging Face emotion model
	- Image path: face preprocessing + image emotion model
4. Backend runs emotion-to-lyrics generation.
5. Backend returns emotion scores, detected emotion, and generated lyrics.
6. Frontend displays results and stores history.


## 1) Setup (Required First)

Run from project root:

```bash
cd NLP_Project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Important: Always activate `.venv` before running any Python command.

## 2) Run NLP Part Separately

The NLP/vision training workflow is in notebooks under `Models/Notebooks/`.

```bash
cd NLP_Project
source .venv/bin/activate
pip install jupyter
jupyter lab
```

Then open and run notebook(s):
- `Models/Notebooks/nlp-project-notebook.ipynb`
- `Models/Notebooks/lyrics_generator_model_gpt.ipynb`

## 3) Run Web App (Backend + Frontend)

### Backend

```bash
cd NLP_Project
source .venv/bin/activate
cd Web/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at `http://127.0.0.1:8000`.

### Frontend (run in a second terminal)

```bash
cd NLP_Project
source .venv/bin/activate
cd Web/frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

Note: Frontend uses Node.js/npm; still start from the same project root and keep `.venv` active for consistency across project workflows.

## Evaluation matrix 

We evaluate lyric quality using the **REDS** framework:

| Component | What it measures | Typical signal |
|-----------|------------------|----------------|
| **R - Rhythm & Rhyme** | Line-level rhythm consistency and rhyme quality | Better flow and musicality |
| **E - Emotional Alignment** | How well generated lyrics match the detected emotion | Emotion-faithful output |
| **D - Distinctiveness** | Diversity of generated text (lower repetition, richer phrasing) | Higher creativity |
| **S - Semantic Coherence** | Meaningful continuity across lines/verses | Better readability and sense |

### How to read REDS

1. Each component is scored independently.
2. Higher score means better quality for that dimension.
3. Final REDS score is the weighted sum of R, E, D, and S used in the experiment setup.

In short:
- **R** checks musical structure,
- **E** checks emotional correctness,
- **D** checks novelty,
- **S** checks meaning and consistency.
