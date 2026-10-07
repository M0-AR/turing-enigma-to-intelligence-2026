"""Part 6: weighing evidence — Banburismus / decibans / log-odds.

Turing (1941, via Good 1979; MacKay ch.18):
- Bayes factor * prior odds = posterior odds; work in log10 -> addition.
- 1 ban = factor 10; 1 deciban = 0.1 ban (smallest perceptible).
- Same-position Enigma messages preserve plaintext matches (rate m≈0.076 for
  English, ~2/26); different positions match at chance 1/26.

Video numbers to reproduce: match +2.2 dB, miss -0.1 dB; 23 matches/400 letters
=> +7 dB (5:1); 15 matches => -11.5 dB (14:1 against); accuracy 71%/87%/99.5%
at 100/400/1700 letters.
"""
from __future__ import annotations
import math

ENG_FREQ = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
    'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
    'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
    'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974, 'Z': 0.00074,
}

MATCH_RATE_ENGLISH = sum(p * p for p in ENG_FREQ.values())  # ~0.065


def decibans(lr: float) -> float:
    return 10 * math.log10(lr)


def match_miss_scores(m: float | None = None, A: int = 26) -> tuple[float, float]:
    """Per-letter weights: match = 10log10(m*A), miss = 10log10((1-m)*A/(A-1))."""
    m = MATCH_RATE_ENGLISH if m is None else m
    return decibans(m * A), decibans((1 - m) * A / (A - 1))


def score_pair(s1: str, s2: str, m: float | None = None) -> tuple[float, int, int]:
    """Walk two messages, keep running total. Returns (score_db, matches, total)."""
    pm, pmm = match_miss_scores(m)
    s1, s2 = s1.upper(), s2.upper()
    n = min(len(s1), len(s2))
    matches = sum(1 for i in range(n) if s1[i] == s2[i])
    score = matches * pm + (n - matches) * pmm
    return score, matches, n


def odds_from_db(db: float) -> float:
    return 10 ** (db / 10)


def expected_db_per_letter(h_same: bool, m: float | None = None) -> float:
    pm, pmm = match_miss_scores(m)
    m = MATCH_RATE_ENGLISH if m is None else m
    rate = m if h_same else 1 / 26
    return rate * pm + (1 - rate) * pmm
