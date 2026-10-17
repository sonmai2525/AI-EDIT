@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
where ffmpeg >nul 2>nul || (echo [LOI] Chua co FFmpeg. & pause & exit /b 1)
if "%~1"=="" (%PY% helpers\one_click_editor.py --mode full-ai) else (%PY% helpers\one_click_editor.py --mode full-ai %*)
pause
