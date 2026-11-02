@echo off
echo Stopping Institute Chatbot processes...
taskkill /FI "WINDOWTITLE eq Institute Chatbot - Backend*" /F /T >nul 2>&1
taskkill /FI "WINDOWTITLE eq Institute Chatbot - Frontend*" /F /T >nul 2>&1
echo Done! Application stopped.
timeout /t 2 >nul
