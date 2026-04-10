import numpy as np
import re
from nltk.corpus import cmudict
from g2p_en import G2p
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from collections import Counter
from sentence_transformers import SentenceTransformer
import random
random.seed(42)

# =========================
# INIT RESOURCES
# =========================

cmu = cmudict.dict()
g2p = G2p()

VOWEL_PHONEMES = set([
    'AA','AE','AH','AO','AW','AY',
    'EH','ER','EY','IH','IY',
    'OW','OY','UH','UW'
])

# =========================
# UTILITY FUNCTIONS
# =========================

def tokenize(text):
    return re.findall(r"\b\w+'\w+|\w+\b", text.lower())

def get_lines(lyrics):
    return [
        line.strip()
        for line in lyrics.split("\n")
        if line.strip() and not line.strip().startswith("[")
    ]

def is_vowel_phoneme(p):
    return any(p.startswith(v) for v in VOWEL_PHONEMES)

def extract_stress(p):
    if p[-1].isdigit():
        return int(p[-1])
    return 0

# =========================
# PHONEME EXTRACTION
# =========================

def get_phonemes(word):
    word = word.lower()

    # CMU
    if word in cmu:
        return cmu[word][0]

    # G2P
    try:
        phonemes = g2p(word)
        phonemes = [p for p in phonemes if p != ' ']
        if phonemes:
            return phonemes
    except:
        pass

    # FINAL fallback (NEVER return empty)
    return list(word)

# =========================
# PHONEME FEATURES
# =========================

def phoneme_features(p):
    return {
        "is_vowel": is_vowel_phoneme(p),
        "stress": extract_stress(p)
    }

# =========================
# TRANSITION COST (PPFS CORE)
# =========================

def transition_cost(p1, p2, weights):
    f1, f2 = phoneme_features(p1), phoneme_features(p2)

    vowel_switch = int(f1["is_vowel"] != f2["is_vowel"])
    stress_diff = abs(f1["stress"] - f2["stress"])

    return (
        weights["vowel"] * vowel_switch +
        weights["stress"] * stress_diff
    )

# =========================
# 1. PPFS (PHONETIC FLOW)
# =========================

class phonetic_pattern_flow_score:
    def __init__(self, weights=None):
        self.weights = weights or {
            "vowel": 0.6,
            "stress": 0.4
        }

    def compute(self, lyrics):
        words = tokenize(lyrics)

        phonemes = []
        for w in words:
            phonemes.extend(get_phonemes(w))

        if len(phonemes) < 2:
            return 1.0

        costs = [
            transition_cost(phonemes[i], phonemes[i+1], self.weights)
            for i in range(len(phonemes) - 1)
        ]

        avg_cost = np.mean(costs)

        return float(np.exp(-avg_cost))


# =========================
# 2. RSFS (RHYTHM)
# =========================

class rhythmic_structure_flow_score:
    def __init__(self, w_length=0.7, w_stress=0.3):
        self.w_length = w_length
        self.w_stress = w_stress

    def get_syllables_and_stress(self, phonemes):
        syllables = []
        for p in phonemes:
            if p[-1].isdigit():  # vowel phoneme
                syllables.append(int(p[-1]))  # store stress
        return syllables

    def compute(self, lyrics):
        lines = get_lines(lyrics)

        if len(lines) < 2:
            return 1.0

        lengths = []
        stress_patterns = []

        for line in lines:
            words = tokenize(line)

            phonemes = []
            for w in words:
                phonemes.extend(get_phonemes(w))

            syllables = self.get_syllables_and_stress(phonemes)

            if len(syllables) == 0:
                continue

            lengths.append(len(syllables))
            stress_patterns.append(syllables)

        if len(lengths) < 2:
            return 0.0

        # ----------------------
        # Length consistency
        # ----------------------
        target = max(np.median(lengths), 1e-6)
        deviations = [abs(l - target) / target for l in lengths]
        length_score = 1 - np.mean(deviations)

        # ----------------------
        # Stress consistency
        # ----------------------
        stress_diffs = []

        for i in range(len(stress_patterns) - 1):
            p1, p2 = stress_patterns[i], stress_patterns[i+1]

            min_len = min(len(p1), len(p2))

            diff = sum(abs(p1[j] - p2[j]) for j in range(min_len)) / min_len
            stress_diffs.append(diff)

        stress_score = 1 - np.mean(stress_diffs) if stress_diffs else 1.0

        return (
            self.w_length * length_score +
            self.w_stress * stress_score
        )


# =========================
# GLOBAL CONFIG
# =========================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_NAME = "SamLowe/roberta-base-go_emotions"

FER_LABELS = ["Angry", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# =========================
# TEXT PROCESSING
# =========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\[.*?\]", "", text)  # remove [Chorus], etc.
    text = re.sub(r"[^\w\s']", " ", text)  # remove symbols but keep '
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize_lines(lyrics):
    return [
        clean_text(line)
        for line in lyrics.split("\n")
        if clean_text(line)
    ]

# =========================
# LOAD MODEL
# =========================

emotion_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
emotion_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(DEVICE)
emotion_model.eval()

GOEMOTIONS_LABELS = emotion_model.config.id2label

# =========================
# GOEMOTIONS → FER MAPPING
# =========================

FER_MAPPING = {
    "Angry": ["anger", "annoyance", "disapproval", "disgust"],
    "Fear": ["fear", "nervousness"],
    "Happy": ["admiration", "amusement", "approval", "caring", "desire", "excitement", "gratitude", "joy", "love", "optimism", "pride", "relief"],
    "Sad": ["sadness", "disappointment", "grief", "remorse", "embarrassment"],
    "Surprise": ["surprise", "realization"],
    "Neutral": ["neutral", "curiosity", "confusion"]
}

def map_to_fer(go_probs):
    fer_vectors = []

    for probs in go_probs:
        fer_vec = []

        for fer_label in FER_LABELS:
            indices = [
                i for i, label in GOEMOTIONS_LABELS.items()
                if label in FER_MAPPING[fer_label]
            ]
            score = np.sum([probs[i] for i in indices])
            fer_vec.append(score)

        fer_vectors.append(fer_vec)

    return np.array(fer_vectors)

def normalize_fer(fer_vectors):
    fer_vectors = np.array(fer_vectors)
    sums = fer_vectors.sum(axis=1, keepdims=True) + 1e-8
    return fer_vectors / sums

# =========================
# EMOTION PREDICTION (BATCHED)
# =========================

def predict_emotions_batch(lines, batch_size=8):
    all_probs = []

    for i in range(0, len(lines), batch_size):
        batch = lines[i:i+batch_size]

        inputs = emotion_tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(DEVICE)

        with torch.no_grad():
            outputs = emotion_model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        all_probs.extend(probs.cpu().numpy())

    return np.array(all_probs)

# =========================
# EAS CLASS
# =========================

class emotion_arc_score:
    def __init__(self, use_neutral_weight=True):
        self.use_neutral_weight = use_neutral_weight

    # Jensen-Shannon Divergence
    def js_divergence(self, p, q):
        p = np.clip(p, 1e-8, 1)
        q = np.clip(q, 1e-8, 1)

        m = 0.5 * (p + q)

        return 0.5 * (
            np.sum(p * np.log(p / m)) +
            np.sum(q * np.log(q / m))
        )

    def compute(self, lyrics):
        lines = tokenize_lines(lyrics)

        if len(lines) < 2:
            return 1.0

        # Step 1: Emotion probabilities
        go_probs = predict_emotions_batch(lines)

        # Step 2: Map to FER
        fer_vectors = map_to_fer(go_probs)

        # Step 3: Normalize
        fer_vectors = normalize_fer(fer_vectors)

        # Step 4: Neutral weighting
        if self.use_neutral_weight:
            neutral_idx = FER_LABELS.index("Neutral")
            weights = 1.0 - fer_vectors[:, neutral_idx]
        else:
            weights = np.ones(len(fer_vectors))

        # Step 5: Compute transitions
        distances = []

        for i in range(len(fer_vectors) - 1):
            p = fer_vectors[i]
            q = fer_vectors[i + 1]

            d = self.js_divergence(p, q)

            w = (weights[i] + weights[i + 1]) / 2
            distances.append(w * d)

        if not distances:
            return 1.0

        avg_dist = np.mean(distances)

        # Step 6: Final score
        return float(np.exp(-avg_dist))


class hook_quality_catchiness_score:
    def __init__(self, lambda1=0.4, lambda2=0.3, lambda3=0.3, 
                 n=3, k=3.0, baseline=0.5, temp=1.0):
        self.l1 = lambda1
        self.l2 = lambda2
        self.l3 = lambda3
        self.n = n
        self.k = k
        self.baseline = baseline
        self.temp = temp

    def extract_ngrams(self, words):
        return [" ".join(words[i:i+self.n]) for i in range(len(words)-self.n+1)]

    def softmax(self, x):
        x = x / self.temp
        e = np.exp(x - np.max(x))
        return e / np.sum(e)

    def compute(self, lyrics, ppfs_score=None, rsfs_score=None):
        words = tokenize(lyrics)

        if len(words) < self.n:
            return self.baseline

        ngrams = self.extract_ngrams(words)
        counts = Counter(ngrams)

        repeated = {k: v for k, v in counts.items() if v > 1}

        # ----------------------
        # No hook case
        # ----------------------
        if not repeated:
            if ppfs_score is not None and rsfs_score is not None:
                return (ppfs_score + rsfs_score) / 2
            return self.baseline

        total_ngrams = len(ngrams)

        # Salience
        max_repeat = max(repeated.values())
        salience = max_repeat / total_ngrams

        # Coverage
        total_repeat = sum(repeated.values())
        coverage = total_repeat / total_ngrams

        # Flow
        if ppfs_score is None or rsfs_score is None:
            flow_quality = 0.5
        else:
            flow_quality = (ppfs_score + rsfs_score) / 2

        # Diversity
        unique_ngrams = len(counts)
        diversity = unique_ngrams / total_ngrams
        diversity_penalty = np.exp(-self.k * (1 - diversity))

        # Base score
        base_score = (
            self.l1 * salience +
            self.l2 * coverage +
            self.l3 * flow_quality
        )

        # ----------------------
        # SOFTMAX COMBINATION (YOUR IDEA)
        # ----------------------
        scores = np.array([base_score, diversity_penalty]) * 5
        weights = self.softmax(scores)

        final_score = weights[0] * base_score + weights[1] * diversity_penalty

        return np.clip(final_score, 0.0, 1.0)


class rhyme_consistency_score:
    def __init__(self):
        pass

    def get_last_word(self, line):
        words = tokenize(line)
        return words[-1] if words else ""

    def get_rhyme_part(self, phonemes):
        # Find last stressed vowel
        for i in range(len(phonemes)-1, -1, -1):
            if phonemes[i][-1].isdigit():  # vowel
                return phonemes[i:]
        return phonemes  # fallback

    def rhyme_similarity(self, p1, p2):
        # Compare from end backwards
        i, j = len(p1)-1, len(p2)-1
        match = 0

        while i >= 0 and j >= 0:
            if p1[i] == p2[j]:
                match += 1
            else:
                break
            i -= 1
            j -= 1

        return match / max(len(p1), len(p2))

    def compute(self, lyrics):
        lines = get_lines(lyrics)

        if len(lines) < 2:
            return 0.0

        rhyme_parts = []

        for line in lines:
            word = self.get_last_word(line)

            if not word:
                continue

            phonemes = get_phonemes(word)

            if not phonemes:
                continue

            rhyme = self.get_rhyme_part(phonemes)
            rhyme_parts.append(rhyme)

        if len(rhyme_parts) < 2:
            return 0.0

        scores = []

        for i in range(len(rhyme_parts) - 1):
            sim = self.rhyme_similarity(
                rhyme_parts[i],
                rhyme_parts[i+1]
            )
            scores.append(sim)

        return float(np.mean(scores))


mcs_model = SentenceTransformer('all-MiniLM-L6-v2')

class motif_consistency_score:
    def __init__(self, alpha=0.7, global_sample_ratio=0.3):
        self.alpha = alpha
        self.global_sample_ratio = global_sample_ratio

    def cosine(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

    def compute(self, lyrics):
        lines = get_lines(lyrics)

        if len(lines) < 2:
            return 1.0

        embeddings = mcs_model.encode(lines)

        # Local similarity
        local_sims = [
            self.cosine(embeddings[i], embeddings[i+1])
            for i in range(len(embeddings)-1)
        ]
        local_score = np.mean(local_sims)

        # Global sampled
        all_pairs = [
            (i, j)
            for i in range(len(embeddings))
            for j in range(i+2, len(embeddings))
        ]

        sample_size = int(len(all_pairs) * self.global_sample_ratio)
        sampled_pairs = random.sample(all_pairs, min(sample_size, len(all_pairs)))

        global_sims = [
            self.cosine(embeddings[i], embeddings[j])
            for i, j in sampled_pairs
        ] if sampled_pairs else [local_score]

        global_score = np.mean(global_sims)

        return self.alpha * local_score + (1 - self.alpha) * global_score


class degeneracy_penality_score:
    def __init__(self, strength=3.0):
        self.strength = strength

    def compute(self, lyrics):
        words = tokenize(lyrics)

        if not words:
            return 1.0

        counts = Counter(words)
        max_freq = max(counts.values())

        ratio = max_freq / len(words)

        return float(np.exp(-self.strength * ratio))

class length_penalty_score:
    def __init__(self, min_lines=8, steepness=2.0):
        self.min_lines = min_lines
        self.steepness = steepness

    def compute(self, lyrics):
        lines = get_lines(lyrics)
        n = len(lines)

        if n >= self.min_lines:
            return 1.0  # no penalty

        # Smooth penalty that drops hard for very short lyrics
        ratio = n / self.min_lines
        return float(ratio ** self.steepness)

class PHREM:
    def __init__(self, alpha_ppfs = 0.12, beta_rsfs = 0.13, gamma_eas = 0.22, delta_hqcs = 0.13, eta_rcs = 0.1, theta_mcs = 0.2, pi_dps= 0.1):
        self.alpha = alpha_ppfs
        self.beta = beta_rsfs
        self.gamma = gamma_eas
        self.delta = delta_hqcs
        self.eta = eta_rcs
        self.theta = theta_mcs
        self.pi = pi_dps
        

        self.ppfs = phonetic_pattern_flow_score()
        self.rsfs = rhythmic_structure_flow_score()
        self.eas = emotion_arc_score()
        self.hook = hook_quality_catchiness_score()
        self.rhyme = rhyme_consistency_score()
        self.mcs = motif_consistency_score()
        self.dp = degeneracy_penality_score()
        self.lp = length_penalty_score()

    def compute(self, lyrics):
        ppfs = self.ppfs.compute(lyrics)
        rsfs = self.rsfs.compute(lyrics)
        eas = self.eas.compute(lyrics)
        hook = self.hook.compute(lyrics, ppfs, rsfs)
        rhyme = self.rhyme.compute(lyrics)
        mcs = self.mcs.compute(lyrics)
        dp = self.dp.compute(lyrics)
        lp = self.lp.compute(lyrics)

        final_score = (
            self.alpha * ppfs +
            self.beta * rsfs +
            self.gamma * eas +
            self.delta * hook +
            self.eta * rhyme +
            self.theta * mcs + 
            self.pi*dp
        )
        final_score = final_score * lp 
        return final_score