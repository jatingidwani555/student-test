@echo off
title EduTest Online Examination System Server
echo ===================================================
echo   🎓 STARTING EDUTEST ONLINE EXAMINATION SYSTEM
echo ===================================================
echo.
echo Running server via Python Streamlit module...
python -m streamlit run app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ ERROR: Failed to start the server.
    echo Please make sure Python is installed and added to your system PATH.
    echo.
    pause
)
