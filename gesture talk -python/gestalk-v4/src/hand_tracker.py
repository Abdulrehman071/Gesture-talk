"""
GestaTalk v4.1 — hand_tracker.py
Wraps MediaPipe Hands for landmark detection.
Returns normalized landmarks for up to 2 hands.
"""

import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from typing import Optional


mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


@dataclass
class HandResult:
    landmarks: list          # list of (x, y, z) tuples, 21 points
    label: str               # "Left" or "Right"
    score: float             # detection confidence


class HandTracker:
    """
    Detects up to 2 hands per frame using MediaPipe Hands.
    Call `process(bgr_frame)` → list[HandResult]
    """

    def __init__(
        self,
        max_hands: int = 2,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.72,
        min_tracking_confidence: float = 0.60,
    ):
        self._hands = mp_hands.Hands(
            max_num_hands=max_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=False,
        )

    def process(self, bgr_frame) -> list[HandResult]:
        """
        Process a BGR frame and return detected hand results.
        MediaPipe expects RGB; conversion is done internally.
        """
        import cv2
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True

        if not results.multi_hand_landmarks:
            return []

        hands = []
        for lm_list, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):
            pts = [(lm.x, lm.y, lm.z) for lm in lm_list.landmark]
            label = handedness.classification[0].label
            score = handedness.classification[0].score
            hands.append(HandResult(landmarks=pts, label=label, score=score))

        return hands

    def draw(self, frame, hand_results: list[HandResult]):
        """Draw hand skeleton on frame (in-place)."""
        import cv2
        for hand in hand_results:
            # Convert back to MediaPipe landmark format for drawing
            lm_proto = mp_hands.HandLandmark
            h, w = frame.shape[:2]
            for conn in mp_hands.HAND_CONNECTIONS:
                a, b = conn
                ax, ay = int(hand.landmarks[a][0] * w), int(hand.landmarks[a][1] * h)
                bx, by = int(hand.landmarks[b][0] * w), int(hand.landmarks[b][1] * h)
                cv2.line(frame, (ax, ay), (bx, by), (79, 209, 197), 2)

            # Draw landmark dots
            TIP_IDS   = {4, 8, 12, 16, 20}
            KNUCK_IDS = {2, 3, 5, 6, 9, 10, 13, 14, 17, 18}
            for i, (x, y, _) in enumerate(hand.landmarks):
                px, py = int(x * w), int(y * h)
                if i in TIP_IDS:
                    cv2.circle(frame, (px, py), 7, (79, 209, 197), -1)
                    cv2.circle(frame, (px, py), 7, (255, 255, 255), 1)
                elif i == 0:
                    cv2.circle(frame, (px, py), 6, (99, 179, 237), -1)
                else:
                    r = 4 if i in KNUCK_IDS else 3
                    cv2.circle(frame, (px, py), r, (79, 209, 197), -1)

            # Label (Left / Right)
            wx, wy = int(hand.landmarks[0][0] * w), int(hand.landmarks[0][1] * h)
            cv2.putText(
                frame, f"{hand.label.upper()} HAND",
                (wx + 12, wy - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (79, 209, 197), 1, cv2.LINE_AA,
            )

    def close(self):
        self._hands.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
