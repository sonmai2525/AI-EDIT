@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title V10.2 Fast Quality - One Click
echo ===== V10.2 FAST QUALITY - ONE CLICK =====
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (where python >nul 2>nul || goto :nopython & set "PY=python")
where ffmpeg >nul 2>nul || goto :noffmpeg
if "%~1"=="" (%PY% helpers\one_click_editor.py) else (%PY% helpers\one_click_editor.py %*)
echo.
echo Ket qua nam trong thu muc OUTPUT.
pause
exit /b
:nopython
echo [LOI] Chua co Python 3.10+. Hay cai Python va chon Add Python to PATH.
pause
exit /b 1
:noffmpeg
echo [LOI] Chua co FFmpeg trong PATH. Hay chay SETUP_ONCE.bat.
pause
exit /b 1
