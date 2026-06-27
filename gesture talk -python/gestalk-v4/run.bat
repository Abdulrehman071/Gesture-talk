@echo off
title GestaTalk v4.1
echo ============================================
echo   GestaTalk v4.1 — Gesture to Speech
echo ============================================
echo.
echo Controls:
echo   SPACE  = Pause / Resume
echo   C      = Clear session
echo   S      = Re-speak last caption
echo   Q/ESC  = Quit
echo.
python main.py %*
echo.
echo [GestaTalk] Session ended.
pause
