@echo off
echo ========================================================
echo   Starting Verified Course Material Studio API Server
echo ========================================================
set PYTHONPATH=%CD%
python apps/api/main.py
pause
