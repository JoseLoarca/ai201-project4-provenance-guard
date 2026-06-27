import math
import re


# Non-standard punctuation marks tracked for entropy calculation.
# Em dash is included as a separate high-weight signal given its documented
# overuse in LLM output from markdown-heavy training data.
_PUNCTUATION_MARKS = frozenset('.,!?;:—–…()"\'-')
_EM_DASH = '—'


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


def _sentence_lengths(sentences: list[str]) -> list[int]:
    return [len(_tokenize(s)) for s in sentences if _tokenize(s)]


def _burstiness_score(lengths: list[int]) -> float:
    """
    Burstiness = σ / μ (standard deviation / mean of sentence lengths).
    Low burstiness → uniform sentence lengths → AI.

    Scoring (linear):
      burstiness <= 0.30 → 1.0 (AI)
      burstiness >= 0.60 → 0.0 (human)
      linear interpolation between 0.30 and 0.60
    """
    if len(lengths) < 3:
        return 0.5

    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.5

    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    burstiness = math.sqrt(variance) / mean

    if burstiness <= 0.30:
        return 1.0
    if burstiness >= 0.60:
        return 0.0
    return round(1.0 - (burstiness - 0.30) / (0.60 - 0.30), 4)


def _punctuation_entropy_score(text: str) -> float:
    """
    Measures how evenly distributed punctuation is across mark types (Shannon entropy).
    Low entropy → narrow, uniform punctuation set → AI.
    High entropy → varied, idiosyncratic punctuation → human.

    Em dash frequency is added as a secondary component: high em dash usage
    pushes the score toward AI independently of entropy.
    """
    marks = [ch for ch in text if ch in _PUNCTUATION_MARKS]

    if not marks:
        return 0.5

    # Shannon entropy over punctuation type distribution
    total = len(marks)
    counts = {}
    for m in marks:
        counts[m] = counts.get(m, 0) + 1

    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())

    # Normalize by max possible entropy (all mark types equally distributed)
    max_entropy = math.log2(len(_PUNCTUATION_MARKS))
    normalized_entropy = entropy / max_entropy  # 0.0 = one mark only, 1.0 = all marks equally

    # Low entropy → high AI score: invert
    entropy_score = 1.0 - normalized_entropy

    # Em dash component: count em dashes per 100 punctuation marks
    # Research threshold: >1.5–2.0 per 100 tokens is a strong AI signal
    words = _tokenize(text)
    em_dash_rate = (counts.get(_EM_DASH, 0) / max(len(words), 1)) * 100
    em_dash_score = min(1.0, em_dash_rate / 2.0)  # caps at 1.0 at rate of 2.0 per 100 words

    # Combine: entropy carries most of the weight, em dash is a secondary push
    score = 0.75 * entropy_score + 0.25 * em_dash_score
    return round(min(1.0, max(0.0, score)), 4)


def analyze(text: str) -> dict:
    """
    Computes a stylometrics_score between 0.0 (likely human) and 1.0 (likely AI)
    using two signals:

      - burstiness (60%): σ / μ of sentence lengths, linear scoring against
        research-backed thresholds (< 0.30 = AI, > 0.60 = human)
      - punctuation entropy (40%): Shannon entropy over punctuation type
        distribution, with em dash frequency as a secondary component
    """
    sentences = _split_sentences(text)
    lengths = _sentence_lengths(sentences)

    burstiness = _burstiness_score(lengths)
    punctuation_entropy = _punctuation_entropy_score(text)

    stylometrics_score = round(
        0.60 * burstiness + 0.40 * punctuation_entropy,
        4,
    )

    return {
        "stylometrics_score": stylometrics_score,
        "burstiness_score": burstiness,
        "punctuation_entropy_score": punctuation_entropy,
    }
