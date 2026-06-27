"""
GestaTalk v4.1 — app.py
Main application loop using OpenCV window.
Handles: camera feed, gesture detection, hold-confirm, TTS, UI overlay.
"""

import cv2
import time
from collections import deque
from datetime import datetime

from src.hand_tracker import HandTracker
from src.gesture_controller import classify
from src.gestures import ALL_GESTURES
from src.actions import TTSEngine, SessionLogger


# ── Tuning ──────────────────────────────────────────────────────────
HOLD_SEC      = 0.6    # seconds to hold gesture before triggering
COOLDOWN_SEC  = 1.8    # seconds between triggers
SMOOTH_FRAMES = 5      # rolling window for gesture smoothing
MIN_VOTES     = 3      # minimum agreeing frames in window


class GestaTalkApp:

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        tts_enabled: bool = True,
        debug: bool = False,
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.debug = debug

        self.tts = TTSEngine(enabled=tts_enabled)
        self.logger = SessionLogger()

        # State
        self._buf: deque = deque(maxlen=SMOOTH_FRAMES)
        self._last_trigger = 0.0
        self._held_id = None
        self._hold_start = 0.0
        self._paused = False
        self._last_caption = ""
        self._session_count = 0
        self._session_conf_sum = 0
        self._session_start = time.time()
        self._history: list[str] = []

    # ── Smoothing ────────────────────────────────────────────────────

    def _smooth(self, gesture_id):
        self._buf.append(gesture_id)
        freq = {}
        for g in self._buf:
            if g:
                freq[g] = freq.get(g, 0) + 1
        if not freq:
            return None
        best = max(freq, key=lambda k: freq[k])
        return best if freq[best] >= MIN_VOTES else None

    # ── Overlay helpers ──────────────────────────────────────────────

    def _put_text(self, frame, text, pos, scale=0.55, color=(79, 209, 197),
                  thickness=1, bg=True):
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        x, y = pos
        if bg:
            cv2.rectangle(frame, (x - 4, y - th - 4), (x + tw + 4, y + 4),
                          (10, 10, 20), -1)
        cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

    def _draw_hold_arc(self, frame, lm, pct: float):
        """Draw a circular progress arc around the wrist."""
        if pct <= 0:
            return
        h, w = frame.shape[:2]
        cx = int(lm[0][0] * w)
        cy = int(lm[0][1] * h)
        radius = 28
        end_angle = int(360 * pct)
        color = (104, 211, 145)
        cv2.ellipse(frame, (cx, cy), (radius, radius),
                    -90, 0, end_angle, color, 3, cv2.LINE_AA)

    def _draw_hud(self, frame, smooth_id, hand_results, confidence):
        h, w = frame.shape[:2]

        # ── Top bar ──
        cv2.rectangle(frame, (0, 0), (w, 44), (10, 10, 25), -1)

        title = "GestaTalk v4.1"
        self._put_text(frame, title, (12, 28), scale=0.65,
                       color=(79, 209, 197), bg=False)

        n_hands = len(hand_results)
        hands_txt = f"HANDS: {n_hands}"
        self._put_text(frame, hands_txt, (w - 200, 28), scale=0.55,
                       color=(255, 220, 100), bg=False)

        # Session time
        elapsed = int(time.time() - self._session_start)
        m, s = divmod(elapsed, 60)
        time_txt = f"TIME: {m}:{s:02d}"
        self._put_text(frame, time_txt, (w - 340, 28), scale=0.55,
                       color=(200, 200, 200), bg=False)

        # Count
        self._put_text(frame, f"TOTAL: {self._session_count}", (w - 480, 28),
                       scale=0.55, color=(200, 200, 200), bg=False)

        # ── Paused banner ──
        if self._paused:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
            self._put_text(frame, "PAUSED  (press SPACE to resume)",
                           (w // 2 - 170, h // 2),
                           scale=0.75, color=(255, 200, 80), bg=False)

        # ── Active gesture pill ──
        if smooth_id and not self._paused:
            g = ALL_GESTURES.get(smooth_id)
            if g:
                label = ("👐 " if g.two_hand else "") + g.icon
                self._put_text(frame, label, (12, h - 60),
                               scale=0.7, color=(104, 211, 145))

        # ── Last caption strip ──
        if self._last_caption:
            self._put_text(
                frame, f'"{self._last_caption}"',
                (12, h - 30), scale=0.65, color=(255, 255, 255),
            )

        # ── History sidebar ──
        sidebar_x = w - 310
        cv2.rectangle(frame, (sidebar_x - 6, 50),
                      (w, 50 + min(len(self._history), 8) * 24 + 10),
                      (10, 10, 25), -1)
        for i, entry in enumerate(reversed(self._history[-8:])):
            alpha = 1.0 - i * 0.11
            color = (int(79 * alpha), int(209 * alpha), int(197 * alpha))
            self._put_text(frame, entry, (sidebar_x, 70 + i * 24),
                           scale=0.42, color=color, bg=False)

        # ── Debug info ──
        if self.debug:
            for i, hr in enumerate(hand_results):
                lm = hr.landmarks
                info = (f"H{i} {hr.label} | "
                        f"wrist=({lm[0][0]:.2f},{lm[0][1]:.2f}) | "
                        f"conf={hr.score:.2f}")
                self._put_text(frame, info, (10, 60 + i * 22),
                               scale=0.38, color=(180, 180, 255), bg=False)

    # ── Main run loop ────────────────────────────────────────────────

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {self.camera_index}")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, 30)

        print(f"[GestaTalk] Camera {self.camera_index} opened — "
              f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
              f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

        with HandTracker() as tracker:
            cv2.namedWindow("GestaTalk v4.1", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("GestaTalk v4.1", self.width, self.height)

            while True:
                ok, frame = cap.read()
                if not ok:
                    print("[GestaTalk] Frame read failed — retrying…")
                    continue

                frame = cv2.flip(frame, 1)  # mirror for natural feel
                hand_results = tracker.process(frame)

                # Draw hand skeletons
                tracker.draw(frame, hand_results)

                smooth_id = None
                confidence = 0

                if not self._paused and hand_results:
                    all_lm = [hr.landmarks for hr in hand_results]
                    raw_id, confidence = classify(all_lm)
                    smooth_id = self._smooth(raw_id)

                    # Hold-to-confirm logic
                    now = time.time()
                    if smooth_id and (now - self._last_trigger) >= COOLDOWN_SEC:
                        if smooth_id != self._held_id:
                            self._held_id = smooth_id
                            self._hold_start = now
                        else:
                            elapsed = now - self._hold_start
                            pct = min(elapsed / HOLD_SEC, 1.0)
                            self._draw_hold_arc(frame, hand_results[0].landmarks, pct)
                            if elapsed >= HOLD_SEC:
                                self._trigger(smooth_id, confidence)
                                self._held_id = None
                    else:
                        if not smooth_id:
                            self._held_id = None
                elif not hand_results:
                    self._held_id = None
                    self._buf.clear()

                # HUD overlay
                self._draw_hud(frame, smooth_id, hand_results, confidence)

                cv2.imshow("GestaTalk v4.1", frame)

                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), 27):           # Q or ESC → quit
                    break
                elif key == ord(' '):               # SPACE → pause
                    self._paused = not self._paused
                    print(f"[GestaTalk] {'Paused' if self._paused else 'Resumed'}")
                elif key == ord('c'):               # C → clear
                    self._clear()
                elif key == ord('s'):               # S → re-speak
                    if self._last_caption:
                        self.tts.speak(self._last_caption)

        cap.release()
        cv2.destroyAllWindows()
        self.tts.stop()
        self.logger.close()
        print("[GestaTalk] Session ended.")

    def _trigger(self, gesture_id: str, confidence: int):
        g = ALL_GESTURES.get(gesture_id)
        if not g:
            return

        self._last_trigger = time.time()
        self._last_caption = g.caption
        self._session_count += 1
        self._session_conf_sum += confidence

        ts = datetime.now().strftime("%M:%S")
        entry = f"{g.emoji} {g.caption}"
        self._history.append(entry)
        if len(self._history) > 20:
            self._history.pop(0)

        self.logger.log(gesture_id, g.caption, confidence, ts)
        self.tts.speak(g.caption)

    def _clear(self):
        self._history.clear()
        self._last_caption = ""
        self._session_count = 0
        self._session_conf_sum = 0
        self._session_start = time.time()
        self._buf.clear()
        self._held_id = None
        print("[GestaTalk] Session cleared.")
