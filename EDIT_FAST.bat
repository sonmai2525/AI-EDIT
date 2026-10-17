@echo off
cd /d "%~dp0"
py -3 helpers\one_click_editor.py --mode fast %*
pause
