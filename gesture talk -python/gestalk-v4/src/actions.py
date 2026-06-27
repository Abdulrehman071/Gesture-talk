"""
GestaTalk v4.1 — actions.py
TTS using Windows SAPI (win32com) directly — no pyttsx3.
Falls back to PowerShell if win32com not installed.
"""

import platform
import threading
import subprocess
import queue


class TTSEngine:
    """
    Windows: uses win32com SAPI directly (most reliable).
    Fallback: PowerShell SpeechSynthesizer (always available on Windows).
    macOS: say command. Linux: espeak.
    All speech runs on a single dedicated worker thread.
    """

    def __init__(self, enabled: bool = True, rate: int = 1, volume: float = 100):
        self.enabled = enabled
        self._q: queue.Queue = queue.Queue()
        self._system = platform.system()

        if not enabled:
            return

        self._worker = threading.Thread(
            target=self._loop,
            args=(rate, volume),
            daemon=True,
            name="TTS-Worker",
        )
        self._worker.start()

    def speak(self, text: str):
        """Queue text — drops old pending items so only latest is spoken."""
        if not self.enabled or not text:
            return
        # Clear queue first (don't pile up)
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except queue.Empty:
                break
        self._q.put(text)

    def stop(self):
        self._q.put(None)

    # ── Worker ────────────────────────────────────────────────────────

    def _loop(self, rate, volume):
        """Single thread owns all TTS for the entire session."""
        speaker = None

        if self._system == "Windows":
            speaker = self._init_sapi(rate, volume)

        print(f"[TTS] Ready  (method: {'SAPI/win32com' if speaker else 'PowerShell'})")

        while True:
            text = self._q.get()
            if text is None:
                break
            print(f"[TTS] Speaking: {text}")
            try:
                if speaker:
                    speaker.Speak(text)
                else:
                    self._ps_speak(text)
            except Exception as e:
                print(f"[TTS] Error: {e} — retrying via PowerShell")
                try:
                    self._ps_speak(text)
                except Exception as e2:
                    print(f"[TTS] PowerShell also failed: {e2}")

        if speaker:
            try:
                del speaker
            except Exception:
                pass

    def _init_sapi(self, rate, volume):
        """Init Windows SAPI via win32com on the worker thread."""
        try:
            import win32com.client
            sp = win32com.client.Dispatch("SAPI.SpVoice")
            sp.Rate = rate      # -10 to 10, 1 = slightly faster than default
            sp.Volume = int(volume)  # 0-100

            # Try to pick a male voice
            voices = sp.GetVoices()
            male_kw   = ["david", "mark", "daniel", "james", "male", "zac", "richard"]
            female_kw = ["zira", "hazel", "susan", "catherine", "female"]
            chosen = None
            for i in range(voices.Count):
                v = voices.Item(i)
                vname = v.GetDescription().lower()
                if any(m in vname for m in male_kw) and not any(f in vname for f in female_kw):
                    chosen = v
                    break
            if chosen:
                sp.Voice = chosen
                print(f"[TTS] Voice: {chosen.GetDescription()}")
            else:
                print(f"[TTS] Voice: {voices.Item(0).GetDescription()} (default)")
            return sp
        except ImportError:
            print("[TTS] win32com not found — using PowerShell TTS")
            print("[TTS] For better performance: pip install pywin32")
            return None
        except Exception as e:
            print(f"[TTS] SAPI init error: {e} — using PowerShell TTS")
            return None

    @staticmethod
    def _ps_speak(text: str):
        """PowerShell SAPI — always available on Windows 7+."""
        safe = text.replace('"', "'").replace("'", " ")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f'$s.Speak("{safe}"); '
            "$s.Dispose()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
        )


class SessionLogger:
    """Logs gesture triggers to console."""

    def log(self, gesture_id: str, caption: str, confidence: int, timestamp: str):
        print(f"[{timestamp}] {gesture_id:<15} | {caption:<35} | conf={confidence}%")

    def close(self):
        pass
