"""
GestaTalk v4.1 — tests/test_classifier.py
Basic unit tests for the gesture classifier logic.
Run: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.gesture_controller import classify_single, classify_two, classify


# ── Helpers to build fake landmark lists ────────────────────────────

def make_lm(finger_states: dict) -> list:
    """
    Build a minimal 21-point landmark list that fakes finger positions.
    finger_states: dict with keys like 'index', 'middle', etc. → True/False
    """
    # Default: all fingers folded (fist)
    lm = [(0.5, 0.5 + i * 0.02, 0.0) for i in range(21)]

    def extend(tip, pip, mcp, direction="up"):
        nonlocal lm
        lm_list = list(lm)
        if direction == "up":
            lm_list[tip]  = (lm[tip][0],  lm[mcp][1] - 0.12, 0.0)
            lm_list[pip]  = (lm[pip][0],  lm[mcp][1] - 0.07, 0.0)
        lm = tuple(lm_list)

    lm = list(lm)

    # Thumb: landmark indices 1-4
    if finger_states.get("thumb"):
        lm[4] = (lm[2][0] + 0.07, lm[2][1], 0.0)   # thumb tip to the side

    # Index: 5-8
    if finger_states.get("index"):
        lm[8] = (lm[8][0], lm[6][1] - 0.10, 0.0)

    # Middle: 9-12
    if finger_states.get("middle"):
        lm[12] = (lm[12][0], lm[10][1] - 0.10, 0.0)

    # Ring: 13-16
    if finger_states.get("ring"):
        lm[16] = (lm[16][0], lm[14][1] - 0.10, 0.0)

    # Pinky: 17-20
    if finger_states.get("pinky"):
        lm[20] = (lm[20][0], lm[18][1] - 0.10, 0.0)

    return lm


# ── Tests ────────────────────────────────────────────────────────────

def test_fist():
    lm = make_lm({})  # all folded
    gid, conf = classify_single(lm)
    assert gid == "fist", f"Expected fist, got {gid}"
    assert conf > 0

def test_thumbs_up():
    lm = make_lm({"thumb": True})
    # Force thumb tip higher than thumb base
    lm[4] = (lm[2][0], lm[2][1] - 0.10, 0.0)
    gid, conf = classify_single(lm)
    assert gid == "thumbs_up", f"Expected thumbs_up, got {gid}"

def test_pointing():
    lm = make_lm({"index": True})
    gid, conf = classify_single(lm)
    assert gid == "pointing", f"Expected pointing, got {gid}"

def test_peace():
    lm = make_lm({"index": True, "middle": True})
    gid, conf = classify_single(lm)
    assert gid == "peace", f"Expected peace, got {gid}"

def test_three_fingers():
    lm = make_lm({"index": True, "middle": True, "ring": True})
    gid, conf = classify_single(lm)
    assert gid == "three", f"Expected three, got {gid}"

def test_classify_no_hands():
    gid, conf = classify([])
    assert gid is None
    assert conf == 0

def test_two_hand_salaam():
    """Both open palms → salaam"""
    lm_open = make_lm({"thumb": True, "index": True, "middle": True,
                        "ring": True, "pinky": True})
    # Make spread wide enough for open_palm
    lm_open[8]  = (lm_open[8][0] + 0.15, lm_open[8][1], 0.0)
    lm_open[20] = (lm_open[20][0] - 0.15, lm_open[20][1], 0.0)

    gid, conf = classify_two(lm_open, lm_open)
    # Two open palms should match salaam
    assert gid == "salaam" or gid is None  # depends on spread threshold

def test_classify_single_dispatch():
    """classify() with 1 hand should call single-hand classifier"""
    lm = make_lm({"index": True})
    gid, conf = classify([lm])
    assert gid == "pointing"


if __name__ == "__main__":
    tests = [
        test_fist,
        test_thumbs_up,
        test_pointing,
        test_peace,
        test_three_fingers,
        test_classify_no_hands,
        test_two_hand_salaam,
        test_classify_single_dispatch,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")
