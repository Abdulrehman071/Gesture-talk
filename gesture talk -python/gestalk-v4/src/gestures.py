"""
GestaTalk v4.1 — gestures.py
25 gesture definitions:
  - Group A: 14 single-hand gestures
  - Group B: 11 two-hand sentence gestures
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Gesture:
    id: str
    emoji: str
    name: str
    icon: str
    caption: str
    two_hand: bool = False
    h1: Optional[str] = None   # first hand gesture id (two-hand only)
    h2: Optional[str] = None   # second hand gesture id (two-hand only)


# ── Group A: 14 original single-hand gestures ──────────────────────
SINGLE_HAND_GESTURES = [
    Gesture("open_palm",   "✋",  "Open Palm",       "OPEN PALM",   "Hello!"),
    Gesture("stop",        "🖐️", "Stop Hand",       "STOP",        "Stop please."),
    Gesture("fist",        "✊",  "Closed Fist",     "WAIT",        "Please wait."),
    Gesture("thumbs_up",   "👍",  "Thumbs Up",       "YES",         "Yes!"),
    Gesture("thumbs_down", "👎",  "Thumbs Down",     "NO",          "No!"),
    Gesture("pointing",    "☝️", "Index Point",     "LOOK THERE",  "Look at that!"),
    Gesture("peace",       "✌️", "Peace Sign",      "PEACE",       "Peace!"),
    Gesture("ok",          "👌",  "OK Sign",         "OKAY",        "Okay!"),
    Gesture("call_me",     "🤙",  "Call Me",         "CALL ME",     "Call me!"),
    Gesture("rock",        "🤘",  "Rock Sign",       "AWESOME",     "Awesome!"),
    Gesture("three",       "3️⃣", "Three Fingers",  "THREE",       "Three please."),
    Gesture("four",        "4️⃣", "Four Fingers",   "FOUR",        "Four please."),
    Gesture("love",        "🤟",  "ILY Sign",        "I LOVE YOU",  "I love you!"),
    Gesture("help",        "🙏",  "Prayer Hands",    "THANK YOU",   "Thank you!"),
]

# ── Group B: 11 two-hand sentence gestures ─────────────────────────
TWO_HAND_GESTURES = [
    Gesture("salaam",      "🤲",  "Both Open Palms",    "AS-SALAAM",    "As salaam o alaikum.",     True, "open_palm",   "open_palm"),
    Gesture("how_are_you", "🫵",  "Palm + Point",       "HOW ARE YOU",  "How are you?",             True, "open_palm",   "pointing"),
    Gesture("im_fine",     "😊",  "Both Thumbs Up",     "I'M FINE",     "I'm fine.",                True, "thumbs_up",   "thumbs_up"),
    Gesture("your_name",   "✍️", "Palm + Fist",        "YOUR NAME",    "What is your name?",       True, "open_palm",   "fist"),
    Gesture("my_name",     "🫀",  "Both Fists",         "MY NAME",      "My name is Abdul Rehman.", True, "fist",        "fist"),
    Gesture("nice_meet",   "🤝",  "Both Peace Signs",   "NICE TO MEET", "Nice to meet you.",        True, "peace",       "peace"),
    Gesture("im_sick",     "🤒",  "Thumbs Down + Fist", "I'M SICK",     "I'm sick.",                True, "thumbs_down", "fist"),
    Gesture("im_hungry",   "😋",  "Palm + OK",          "I'M HUNGRY",   "I'm hungry.",              True, "open_palm",   "ok"),
    Gesture("what_time",   "⏰",  "Fist + Point",       "WHAT TIME",    "What time is it?",         True, "fist",        "pointing"),
    Gesture("see_u_later", "👋",  "Palm + Call Me",     "SEE YOU LATER","See you later.",            True, "open_palm",   "call_me"),
    Gesture("goodbye",     "🫡",  "Palm + ILY",         "GOODBYE",      "Goodbye.",                 True, "open_palm",   "love"),
]

# Combined lookup dict: id -> Gesture
ALL_GESTURES: dict[str, Gesture] = {
    g.id: g for g in SINGLE_HAND_GESTURES + TWO_HAND_GESTURES
}
