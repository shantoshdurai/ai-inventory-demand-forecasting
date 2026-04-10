@echo off
echo Starting StockSense AI...
echo.
echo [1/2] Starting API server on http://localhost:8000
start "StockSense API" cmd /k "python -m uvicorn api.main:app --reload --port 8000"
timeout /t 3 /nobreak > nul
echo [2/2] Starting web app on http://localhost:5173
start "StockSense Web" cmd /k "cd web && npm run dev"
timeout /t 4 /nobreak > nul
echo.
echo StockSense is running!
echo   Web app:  http://localhost:5173
echo   API docs: http://localhost:8000/docs
echo.
start http://localhost:5173
