# GestaTalk v4.1 🤲

**Real-time Hand Gesture to Speech — Python + MediaPipe + OpenCV**

Detects **25 hand gestures** (14 single-hand + 11 two-hand combos) via webcam,
displays live captions on screen, and speaks them aloud in a male voice.

---

## Project Structure

```
gestalk-v4/
├── main.py                  ← Entry point — run this
├── requirements.txt         ← Python dependencies
├── README.md
│
├── src/                     ← Source package
│   ├── __init__.py
│   ├── app.py               ← Main OpenCV loop + HUD overlay
│   ├── hand_tracker.py      ← MediaPipe Hands wrapper (up to 2 hands)
│   ├── gesture_controller.py← Landmark → gesture classifier
│   ├── gestures.py          ← All 25 gesture definitions
│   └── actions.py           ← TTS engine + session logger
│
├── assets/
│   └── sounds/              ← (optional) sound effects
│
├── tests/                   ← Unit tests
│   └── test_classifier.py
│
└── scripts/
    └── setup.bat            ← One-click Windows setup
```

---

## Quick Start (Windows CMD)

### 1 — Install Python 3.10+
Download from https://www.python.org/downloads/
Make sure to check **"Add Python to PATH"** during install.

### 2 — Install dependencies

```cmd
cd gestalk-v4
pip install -r requirements.txt
```

### 3 — Run

```cmd
python main.py
```

---

## Command-Line Options

```
python main.py --help

  --camera N     Camera device index (default: 0)
  --width  N     Capture width  (default: 1280)
  --height N     Capture height (default: 720)
  --no-tts       Disable text-to-speech
  --debug        Show landmark debug overlay
```

**Examples:**

```cmd
python main.py                      # default webcam
python main.py --camera 1           # second camera
python main.py --no-tts             # silent mode
python main.py --debug              # show landmark coords
```

---

## Keyboard Shortcuts (inside the camera window)

| Key       | Action                    |
|-----------|---------------------------|
| `SPACE`   | Pause / Resume            |
| `C`       | Clear session history     |
| `S`       | Re-speak last caption     |
| `Q / ESC` | Quit                      |

---

## Gesture Reference

### Single-Hand (14 gestures)

| Gesture       | Sign      | Says                     |
|---------------|-----------|--------------------------|
| Open Palm     | ✋        | Hello!                   |
| Stop Hand     | 🖐️       | Stop please.             |
| Closed Fist   | ✊        | Please wait.             |
| Thumbs Up     | 👍        | Yes!                     |
| Thumbs Down   | 👎        | No!                      |
| Index Point   | ☝️       | Look at that!            |
| Peace Sign    | ✌️       | Peace!                   |
| OK Sign       | 👌        | Okay!                    |
| Call Me       | 🤙        | Call me!                 |
| Rock Sign     | 🤘        | Awesome!                 |
| Three Fingers | 3️⃣      | Three please.            |
| Four Fingers  | 4️⃣      | Four please.             |
| ILY Sign      | 🤟        | I love you!              |
| Prayer Hands  | 🙏        | Thank you!               |

### Two-Hand (11 gestures — show both hands together)

| Gesture            | Combo             | Says                      |
|--------------------|-------------------|---------------------------|
| Both Open Palms    | ✋ + ✋           | As salaam o alaikum.      |
| Palm + Point       | ✋ + ☝️          | How are you?              |
| Both Thumbs Up     | 👍 + 👍           | I'm fine.                 |
| Palm + Fist        | ✋ + ✊           | What is your name?        |
| Both Fists         | ✊ + ✊           | My name is Abdul Rehman.  |
| Both Peace Signs   | ✌️ + ✌️         | Nice to meet you.         |
| Thumbs Down + Fist | 👎 + ✊           | I'm sick.                 |
| Palm + OK          | ✋ + 👌           | I'm hungry.               |
| Fist + Point       | ✊ + ☝️          | What time is it?          |
| Palm + Call Me     | ✋ + 🤙           | See you later.            |
| Palm + ILY         | ✋ + 🤟           | Goodbye.                  |

---

## Troubleshooting

**Camera not found:**
```cmd
python main.py --camera 1
python main.py --camera 2
```

**MediaPipe install fails:**
```cmd
pip install mediapipe --upgrade
```

**No TTS voice / pyttsx3 error (Windows):**
```cmd
pip install pywin32
pip install pyttsx3 --upgrade
```

**Slow performance:**
- Lower resolution: `python main.py --width 640 --height 480`
- Ensure good lighting on your hands
- Keep hands within 40–80 cm of camera

---

## Requirements

- Python 3.10 or newer
- Webcam (built-in or USB)
- Windows 10/11 recommended (also works on macOS / Linux)
