@echo off
title AI Resume Analyzer
echo ========================================================
echo         AI Resume Analyzer - Starting Web Server
echo ========================================================
echo.

set PYTHON_PATH="C:\Users\eluch\AppData\Local\Programs\Python\Python312\python.exe"

if exist %PYTHON_PATH% (
    %PYTHON_PATH% app.py
) else (
    python app.py
)

pause
