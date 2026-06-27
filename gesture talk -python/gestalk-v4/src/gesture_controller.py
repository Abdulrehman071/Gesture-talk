"""
GestaTalk v4.1 — gesture_controller.py
Classifies hand landmarks into gesture IDs.
Supports single-hand (14 gestures) and two-hand (11 gestures).
"""

import math
from typing import Optional
from src.gestures import ALL_GESTURES, TWO_HAND_GESTURES


# ── Helpers ─────────────────────────────────────────────────────────

def _dist(a, b) -> float:
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def _finger_states(lm: list[tuple]) -> tuple[bool, bool, bool, bool, bool]:
    """
    Returns (thumb, index, middle, ring, pinky) extended booleans.
    lm: list of 21 (x, y, z) tuples.
    """
    THRESH = 0.04
    thumb = (
        abs(lm[4][0] - lm[2][0]) > 0.04 or
        abs(lm[4][1] - lm[3][1]) > 0.04
    )
    index  = lm[8][1]  < lm[6][1]  - THRESH
    middle = lm[12][1] < lm[10][1] - THRESH
    ring   = lm[16][1] < lm[14][1] - THRESH
    pinky  = lm[20][1] < lm[18][1] - THRESH
    return thumb, index, middle, ring, pinky


def _is_ok(lm: list[tuple]) -> bool:
    pinch = _dist(lm[4], lm[8])
    return (
        pinch < 0.065 and
        lm[12][1] < lm[10][1] - 0.03 and
        lm[16][1] < lm[14][1] - 0.03 and
        lm[20][1] < lm[18][1] - 0.03
    )


# ── Single-hand classifier ───────────────────────────────────────────

def classify_single(lm: list[tuple]) -> tuple[Optional[str], int]:
    """
    Returns (gesture_id, confidence) for a single hand's 21 landmarks.
    Returns (None, 0) if no match.
    """
    if not lm:
        return None, 0

    if _is_ok(lm):
        return "ok", 91

    thumb, idx, mid, ring, pinky = _finger_states(lm)
    count = sum([thumb, idx, mid, ring, pinky])

    # Special combos
    if thumb and idx and not mid and not ring and pinky:
        return "love", 92
    if thumb and not idx and not mid and not ring and pinky:
        return "call_me", 91
    if not thumb and idx and not mid and not ring and pinky:
        return "rock", 90

    # Thumb alone
    if thumb and not idx and not mid and not ring and not pinky:
        if lm[4][1] < lm[2][1] - 0.05:
            return "thumbs_up", 96
        if lm[4][1] > lm[2][1] + 0.05:
            return "thumbs_down", 94
        return None, 0

    if not thumb and idx and not mid and not ring and not pinky:
        return "pointing", 96
    if not thumb and idx and mid and not ring and not pinky:
        return "peace", 94
    if not thumb and idx and mid and ring and not pinky:
        return "three", 88
    if not thumb and idx and mid and ring and pinky:
        return "four", 87

    # All 5 fingers
    if thumb and idx and mid and ring and pinky:
        spread = _dist(lm[8], lm[20])
        if spread > 0.10:
            return "open_palm", 97
        return "stop", 89

    if count == 0:
        return "fist", 94

    # Prayer / Thank you
    if thumb and not idx and not mid and ring and pinky:
        return "help", 80

    return None, 0


# ── Two-hand classifier ──────────────────────────────────────────────

def classify_two(lm0: list[tuple], lm1: list[tuple]) -> tuple[Optional[str], int]:
    """
    Classify a two-hand combo. Order-independent matching.
    Returns (gesture_id, confidence) or (None, 0).
    """
    id0, c0 = classify_single(lm0)
    id1, c1 = classify_single(lm1)
    if not id0 or not id1:
        return None, 0

    avg_conf = round((c0 + c1) / 2)

    for g in TWO_HAND_GESTURES:
        if (id0 == g.h1 and id1 == g.h2) or (id0 == g.h2 and id1 == g.h1):
            return g.id, avg_conf

    return None, 0


# ── Public interface ─────────────────────────────────────────────────

def classify(all_landmarks: list[list[tuple]]) -> tuple[Optional[str], int]:
    """
    Main classifier. Pass a list of per-hand landmark lists.
    Returns (gesture_id, confidence).
    """
    if not all_landmarks:
        return None, 0
    if len(all_landmarks) >= 2:
        gid, conf = classify_two(all_landmarks[0], all_landmarks[1])
        if gid:
            return gid, conf
    return classify_single(all_landmarks[0])
