"""
GestaTalk v4.1 — Main Entry Point
Run: python main.py
"""

import sys
import argparse
from src.app import GestaTalkApp


def parse_args():
    parser = argparse.ArgumentParser(
        description="GestaTalk v4.1 — Real-time Hand Gesture to Speech",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--camera", type=int, default=0,
        help="Camera device index (default: 0)"
    )
    parser.add_argument(
        "--width", type=int, default=1280,
        help="Camera capture width (default: 1280)"
    )
    parser.add_argument(
        "--height", type=int, default=720,
        help="Camera capture height (default: 720)"
    )
    parser.add_argument(
        "--no-tts", action="store_true",
        help="Disable text-to-speech output"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Show landmark debug overlay"
    )
    return parser.parse_args()


def main():
    print("=" * 55)
    print("  GestaTalk v4.1 — Gesture to Subtitle & Speech")
    print("  25 gestures | 2-hand support | male TTS voice")
    print("=" * 55)
    print("  [SPACE]  Pause / Resume")
    print("  [C]      Clear session history")
    print("  [S]      Re-speak last caption")
    print("  [Q/ESC]  Quit")
    print("=" * 55)

    args = parse_args()

    try:
        app = GestaTalkApp(
            camera_index=args.camera,
            width=args.width,
            height=args.height,
            tts_enabled=not args.no_tts,
            debug=args.debug,
        )
        app.run()
    except KeyboardInterrupt:
        print("\n[GestaTalk] Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[GestaTalk] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
