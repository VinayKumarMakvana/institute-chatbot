@echo off
echo ==============================================
echo   Starting Institute AI Chatbot Application
echo ==============================================

cd /d "%~dp0backend"

echo Starting FastAPI Backend on port 8000...
start "Institute Chatbot - Backend" cmd /k ".\venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

cd /d "%~dp0frontend"
echo Starting Frontend Web Server on port 5500...
start "Institute Chatbot - Frontend" cmd /k "python -m http.server 5500"

timeout /t 2 /nobreak >nul

echo Opening application in browser...
start http://localhost:8000/login.html

echo.
echo ==============================================
echo   Application started successfully!
echo   Unified App : http://localhost:8000
echo   Frontend Dev: http://localhost:5500
echo   API Docs    : http://localhost:8000/docs
echo ==============================================
pause

