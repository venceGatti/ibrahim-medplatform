@echo off
chcp 65001 >nul
title MedPlatform Workstation
cls

:: 1. Arresto preventivo di eventuali processi residui su 8765 e 5173
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8765 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: 2. Identificazione ambiente Python
set PYTHON_EXE=
if exist "agent_env\Scripts\python.exe" (
    set "PYTHON_EXE=agent_env\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

:: 3. Token IPC di sicurezza
set "MEDCLIENT_IPC_TOKEN=medclient_local_session_secure_token"

:: 4. Avvio Backend Sidecar e Frontend SDUI
start "MedPlatform - Backend" /min cmd /c "cd medclient\sidecar-python && set MEDCLIENT_IPC_TOKEN=%MEDCLIENT_IPC_TOKEN% && ..\..\%PYTHON_EXE% -m src.main --port 8765 --host 127.0.0.1"
ping 127.0.0.1 -n 2 >nul
start "MedPlatform - Frontend" /min cmd /c "cd medclient\frontend-react && npm run dev"
ping 127.0.0.1 -n 2 >nul

:: 5. Apertura istantanea dell'applicazione
start http://localhost:5173

:: 6. Chiusura pulita della finestra del launcher
exit
