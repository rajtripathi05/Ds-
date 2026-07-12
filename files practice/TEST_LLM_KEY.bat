@echo off
cd /d "%~dp0"
echo Testing your OpenRouter key with ONE cheap call...
python test_llm_key.py
echo.
pause
