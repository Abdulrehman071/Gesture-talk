"""
Run this first to confirm TTS works on your machine:
    python test_tts.py
"""
import time, platform, subprocess

print("Testing TTS...")
print(f"Platform: {platform.system()}")

# Method 1: win32com SAPI
try:
    import win32com.client
    sp = win32com.client.Dispatch("SAPI.SpVoice")
    print("[OK] win32com found — using SAPI")
    sp.Speak("Hello! GestaTalk text to speech is working correctly.")
    time.sleep(0.5)
    sp.Speak("Gesture detected. Hello!")
    time.sleep(0.5)
    sp.Speak("Yes!")
    print("[OK] win32com SAPI works — you are good to go!")
except ImportError:
    print("[WARN] win32com not found — trying PowerShell...")
    # Method 2: PowerShell
    script = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        '$s.Speak("Hello! GestaTalk text to speech is working via PowerShell."); '
        '$s.Dispose()'
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        timeout=20
    )
    if result.returncode == 0:
        print("[OK] PowerShell TTS works!")
        print("     Run: pip install pywin32   for better performance")
    else:
        print("[FAIL] PowerShell TTS also failed.")
        print("       Check your Windows audio settings / sound output device.")
except Exception as e:
    print(f"[FAIL] Error: {e}")
