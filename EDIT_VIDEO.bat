@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title V12 VIRAL ENGINE - SMART
set "PY=python"
where py >nul 2>nul && set "PY=py -3"
where ffmpeg >nul 2>nul || goto :noffmpeg
if "%~1"=="" (%PY% helpers\one_click_editor.py --mode smart) else (%PY% helpers\one_click_editor.py --mode smart %*)
echo.
echo V12 SMART hoan tat. Ket qua trong OUTPUT.
pause
exit /b
:noffmpeg
echo [LOI] Chua co FFmpeg. Hay chay SETUP_ONCE.bat.
pause
