@echo off
echo ========================================================
echo   Running Verified Course Material Studio Test Suite
echo ========================================================
set PYTHONPATH=%CD%
python -m pytest apps services -v
pause
