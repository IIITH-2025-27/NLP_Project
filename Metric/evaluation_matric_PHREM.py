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
    
def transition_cost(s1, s2):
    """
    Role-based stress transition cost
    Lower = better
    """

    # Perfect alternation (best flow)
    if (s1 == 0 and s2 == 1) or (s1 == 1 and s2 == 0):
        return 0.0

    # Secondary stress involvement (soft transition)
    if s1 == 2 or s2 == 2:
        return 0.3

    # Same stress repeated (boring / flat)
    if s1 == s2:
        return 0.6

    # Harsh / unnatural transitions
    return 1.0

# =========================
# 1. PPFS (PHONETIC FLOW)
# =========================

class phonetic_pattern_flow_score:
    def __init__(self, weights=None):
        # Only stress matters now (vowel penalty removed)
        self.weights = weights or {
            "stress": 1.0
        }

    # =========================
    # Main compute
    # =========================
    def compute(self, lyrics):
        words = tokenize(lyrics)

        phonemes = []
        for w in words:
            phonemes.extend(get_phonemes(w))

        # Extract only vowel phonemes (true rhythm units)
        vowel_phonemes = [p for p in phonemes if is_vowel_phoneme(p)]

        if len(vowel_phonemes) < 2:
            return 1.0

        # Get stress sequence
        stresses = [extract_stress(p) for p in vowel_phonemes]

        # Compute transition costs
        costs = [
            transition_cost(stresses[i], stresses[i+1])
            for i in range(len(stresses) - 1)
        ]

        avg_cost = np.mean(costs)
        return float(np.exp(-avg_cost))


# =========================
# 2. RSFS (RHYTHM)
# =========================

class rhythmic_structure_flow_score:
    def __init__(self, w_length=0.5, w_stress=0.3, w_alt=0.2):
        self.w_length = w_length
        self.w_stress = w_stress
        self.w_alt = w_alt

    # -------------------------
    # Extract stress sequence
    # -------------------------
    def get_stress_pattern(self, phonemes):
        return [int(p[-1]) for p in phonemes if p[-1].isdigit()]

    # -------------------------
    # Normalize stress into roles
    # 0 = weak, 1 = strong (1/2 merged)
    # -------------------------
    def normalize_stress(self, s):
        return 0 if s == 0 else 1

    # -------------------------
    # Alternation quality (within a line)
    # -------------------------
    def alternation_score(self, pattern):
        if len(pattern) < 2:
            return 1.0

        norm = [self.normalize_stress(s) for s in pattern]

        good = 0
        for i in range(len(norm) - 1):
            if norm[i] != norm[i+1]:  # alternation
                good += 1

        return good / (len(norm) - 1)

    # -------------------------
    # Flexible pattern similarity
    # -------------------------
    def pattern_similarity(self, p1, p2):
        if len(p1) == 0 or len(p2) == 0:
            return 0.0

        # Normalize stress (0 = weak, 1 = strong)
        norm1 = [self.normalize_stress(s) for s in p1]
        norm2 = [self.normalize_stress(s) for s in p2]

        # -------------------------
        # 1. Positional similarity (STRICT)
        # -------------------------
        min_len = min(len(norm1), len(norm2))
        positional_matches = sum(1 for i in range(min_len) if norm1[i] == norm2[i])
        positional_score = positional_matches / min_len

        # -------------------------
        # 2. LCS similarity (FLEXIBLE)
        # -------------------------
        dp = [[0] * (len(norm2) + 1) for _ in range(len(norm1) + 1)]

        for i in range(1, len(norm1) + 1):
            for j in range(1, len(norm2) + 1):
                if norm1[i - 1] == norm2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs_len = dp[-1][-1]
        lcs_score = lcs_len / max(len(norm1), len(norm2))

        # -------------------------
        # 3. Weighted combination
        # -------------------------
        return 0.3 * positional_score + 0.7 * lcs_score

    # -------------------------
    # Main compute
    # -------------------------
    def compute(self, lyrics):
        lines = get_lines(lyrics)

        if len(lines) < 2:
            return 1.0

        lengths = []
        patterns = []
        alt_scores = []

        for line in lines:
            words = tokenize(line)

            phonemes = []
            for w in words:
                phonemes.extend(get_phonemes(w))

            pattern = self.get_stress_pattern(phonemes)

            if len(pattern) == 0:
                continue

            lengths.append(len(pattern))
            patterns.append(pattern)
            alt_scores.append(self.alternation_score(pattern))

        if len(lengths) < 2:
            return 0.0

        # ----------------------
        # Length consistency (soft)
        # ----------------------
        target = np.median(lengths)
        deviations = [abs(l - target) / (target + 1e-6) for l in lengths]

        # softer penalty than v1
        length_score = np.exp(-np.mean(deviations))

        # ----------------------
        # Pattern similarity (not exact match)
        # ----------------------
        sims = []
        for i in range(len(patterns) - 1):
            sims.append(self.pattern_similarity(patterns[i], patterns[i+1]))

        stress_score = np.mean(sims) if sims else 1.0

        # ----------------------
        # Alternation quality
        # ----------------------
        alt_score = np.mean(alt_scores)

        # ----------------------
        # Final score
        # ----------------------
        return (
            self.w_length * length_score +
            self.w_stress * stress_score +
            self.w_alt * alt_score
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

class emotion_alignment_arc_score:
    def __init__(self, w_align=0.7, w_arc=0.3, use_neutral_weight=True):
        self.w_align = w_align
        self.w_arc = w_arc
        self.use_neutral_weight = use_neutral_weight

    # -------------------------
    # Cosine similarity
    # -------------------------
    def cosine(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

    # -------------------------
    # Jensen-Shannon Divergence
    # -------------------------
    def js_divergence(self, p, q):
        p = np.clip(p, 1e-8, 1)
        q = np.clip(q, 1e-8, 1)

        m = 0.5 * (p + q)

        return 0.5 * (
            np.sum(p * np.log(p / m)) +
            np.sum(q * np.log(q / m))
        )

    # -------------------------
    # Main compute
    # -------------------------
    def compute(self, lyrics, target_emotion):
        lines = tokenize_lines(lyrics)

        if len(lines) == 0:
            return 0.0

        # -------------------------
        # Step 1: Emotion prediction
        # -------------------------
        go_probs = predict_emotions_batch(lines)

        # -------------------------
        # Step 2: Map to FER
        # -------------------------
        fer_vectors = map_to_fer(go_probs)

        # -------------------------
        # Step 3: Normalize
        # -------------------------
        fer_vectors = normalize_fer(fer_vectors)

        # -------------------------
        # Step 4: Target vector
        # -------------------------
        target_idx = FER_LABELS.index(target_emotion)

        target_vec = np.zeros(len(FER_LABELS))
        target_vec[target_idx] = 1.0

        # -------------------------
        # Step 5: ALIGNMENT SCORE
        # -------------------------
        align_sims = [vec[target_idx] for vec in fer_vectors]
        alignment_score = np.mean(align_sims)

        # -------------------------
        # Step 6: ARC SCORE (JSD)
        # -------------------------
        if len(fer_vectors) < 2:
            arc_score = 1.0
        else:
            if self.use_neutral_weight:
                neutral_idx = FER_LABELS.index("Neutral")
                weights = 1.0 - fer_vectors[:, neutral_idx]
            else:
                weights = np.ones(len(fer_vectors))

            distances = []

            for i in range(len(fer_vectors) - 1):
                p = fer_vectors[i]
                q = fer_vectors[i + 1]

                d = self.js_divergence(p, q)

                w = (weights[i] + weights[i + 1]) / 2
                distances.append(w * d)

            avg_dist = np.mean(distances) if distances else 0.0
            arc_score = float(np.exp(-avg_dist))

        # -------------------------
        # Step 7: FINAL COMBINATION
        # -------------------------
        final_score = (
            self.w_align * alignment_score +
            self.w_arc * arc_score
        )

        return float(np.clip(final_score, 0.0, 1.0))

class hook_quality_catchiness_score:
    def __init__(self, lambda1=0.4, lambda2=0.3, lambda3=0.3, 
                 n=3, k=3.0, baseline=0.5, temp=1.0, penality_exponent=0.5):
        self.l1 = lambda1
        self.l2 = lambda2
        self.l3 = lambda3
        self.n = n
        self.k = k
        self.baseline = baseline
        self.temp = temp
        self.penality_exponent = penality_exponent

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

        final_score = base_score * (diversity_penalty ** self.penality_exponent)

        return np.clip(final_score, 0.0, 1.0)



class rhyme_consistency_score:
    def __init__(self, max_syllables=3):
        self.max_syllables = max_syllables

    # -------------------------
    # Get last word of line
    # -------------------------
    def get_last_word(self, line):
        words = tokenize(line)
        return words[-1] if words else ""

    # -------------------------
    # Multisyllabic rhyme extraction
    # -------------------------
    def get_multisyllable_rhyme(self, phonemes):
        vowel_indices = []

        for i, p in enumerate(phonemes):
            if p[-1].isdigit():
                vowel_indices.append(i)

        if not vowel_indices:
            return phonemes

        selected = vowel_indices[-self.max_syllables:]
        start = selected[0]

        return phonemes[start:]

    # -------------------------
    # Phoneme similarity (slant rhyme)
    # -------------------------
    def phoneme_similarity(self, a, b):
        # Exact match
        if a == b:
            return 1.0

        # Same phoneme ignoring stress (AA1 vs AA0)
        if a[:-1] == b[:-1]:
            return 0.8

        return 0.0

    # -------------------------
    # Rhyme similarity (suffix-based)
    # -------------------------
    def rhyme_similarity(self, p1, p2):
        i, j = len(p1) - 1, len(p2) - 1
        score = 0.0
        count = 0

        while i >= 0 and j >= 0:
            sim = self.phoneme_similarity(p1[i], p2[j])

            if sim == 0:
                break

            score += sim
            count += 1

            i -= 1
            j -= 1

        if count == 0:
            return 0.0

        return score / max(len(p1), len(p2))

    # -------------------------
    # Internal rhyme detection
    # -------------------------
    def internal_rhyme_score(self, line):
        words = tokenize(line)

        phoneme_list = []
        for w in words:
            ph = get_phonemes(w)
            if ph:
                phoneme_list.append(ph)

        scores = []

        for i in range(len(phoneme_list)):
            for j in range(i + 1, len(phoneme_list)):
                r1 = self.get_multisyllable_rhyme(phoneme_list[i])
                r2 = self.get_multisyllable_rhyme(phoneme_list[j])

                sim = self.rhyme_similarity(r1, r2)

                if sim > 0.5:
                    scores.append(sim)

        return np.mean(scores) if scores else 0.0

    # -------------------------
    # Main compute
    # -------------------------
    def compute(self, lyrics):
        lines = get_lines(lyrics)

        if len(lines) < 2:
            return 0.0

        rhyme_parts = []
        internal_scores = []

        for line in lines:
            word = self.get_last_word(line)

            if not word:
                continue

            phonemes = get_phonemes(word)

            if not phonemes:
                continue

            rhyme = self.get_multisyllable_rhyme(phonemes)
            rhyme_parts.append(rhyme)

            internal_scores.append(self.internal_rhyme_score(line))

        if len(rhyme_parts) < 2:
            return 0.0

        # -------------------------
        # End rhyme consistency
        # -------------------------
        end_scores = []

        for i in range(len(rhyme_parts) - 1):
            sim = self.rhyme_similarity(
                rhyme_parts[i],
                rhyme_parts[i + 1]
            )
            end_scores.append(sim)

        end_score = np.mean(end_scores) if end_scores else 0.0

        # -------------------------
        # Internal rhyme score
        # -------------------------
        internal_score = np.mean(internal_scores) if internal_scores else 0.0

        # -------------------------
        # Final combination
        # -------------------------
        return 0.7 * end_score + 0.3 * internal_score


mcs_model = SentenceTransformer('all-MiniLM-L6-v2')

class motif_consistency_score:
    def __init__(self, alpha=0.9, global_sample_ratio=0.1):
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

        ratio = (max_freq - 1) / (len(words) - 1 + 1e-8)
        score = np.exp(-self.strength * ratio)
        return score


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
        self.eas = emotion_alignment_arc_score()
        self.hook = hook_quality_catchiness_score()
        self.rhyme = rhyme_consistency_score()
        self.mcs = motif_consistency_score()
        self.dp = degeneracy_penality_score()
        self.lp = length_penalty_score()

    def compute(self, lyrics, emotion_target="Happy"):
        ppfs = self.ppfs.compute(lyrics)
        rsfs = self.rsfs.compute(lyrics)
        eas = self.eas.compute(lyrics, emotion_target)
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