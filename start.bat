@echo off
chcp 65001 >nul
echo ========================================
echo 魔兽世界角色管理系统
echo ========================================
echo.

echo [1/2] Starting Backend Service...
cd backend
call venv\Scripts\activate
echo Backend dependencies are already installed.
echo Starting backend server...
start /B python run_server.py
cd ..
echo Backend service started successfully! http://localhost:8000
echo.

echo [2/2] Starting Frontend Service...
cd frontend
echo Frontend dependencies are already installed.
echo Starting frontend server...
start /B npm run dev
cd ..
echo Frontend service started successfully! http://localhost:5173
echo.

echo ========================================
echo System Startup Complete!
echo Backend API Docs: http://localhost:8000/docs
echo Frontend Interface: http://localhost:5173
echo ========================================
echo.
echo Press any key to exit this window (services will continue running)
pause >nul