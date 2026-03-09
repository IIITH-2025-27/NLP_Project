# MERGE: Multimodal Emotion-Driven Rhythmic Lyric Generation Engine

A multimodal NLP system that generates rhythm-aware song lyrics conditioned on emotions inferred from facial expressions.

## Overview

MERGE addresses three core challenges:
1. **Emotion-conditioned language modeling** – Generating lyrics aligned with detected emotions
2. **Constrained decoding** – Enforcing rhythmic and rhyming structure during generation
3. **Task-specific evaluation** – A custom metric (REDS) for assessing creative lyric generation

## Pipeline

- **Facial Emotion Recognition**: CNN-based (ResNet-18/MobileNet) classifier trained on FER2013/RAF-DB
- **Emotion-Conditioned LM**: GPT-2 fine-tuned on lyrics with emotion control tokens
- **Rhythm Constraints**: Syllable and rhyme enforcement using CMU Pronouncing Dictionary

## Evaluation Metric: REDS

| Component | Description |
|-----------|-------------|
| **R** | Rhythm & Rhyme Consistency |
| **E** | Emotional Alignment |
| **D** | Distinctiveness (n-gram diversity) |
| **S** | Semantic Coherence |

## Team

Abhay Sharma | Ankit Kumar | Hritik Ranjan | Vikash Kumar  