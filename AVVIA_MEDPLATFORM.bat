@echo off
chcp 65001 >nul
title MedPlatform - Centro di Controllo Clinico (One-Click Launcher)
cls

echo ======================================================================
echo           MEDPLATFORM - AVVIO AMBIENTE CLINICO INTEGRATO
echo ======================================================================
echo.

:: 1. Rilevamento interprete Python
set PYTHON_EXE=
if exist "agent_env\Scripts\python.exe" (
    set "PYTHON_EXE=agent_env\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Utilizzo interprete Python: %PYTHON_EXE%

:: 2. Configurazione Token IPC Effimero Locale
set "MEDCLIENT_IPC_TOKEN=medclient_local_session_secure_token"

:: 3. Avvio Sidecar Python su 127.0.0.1:8765
echo [*] Avvio Python Clinical Sidecar su http://127.0.0.1:8765 ...
start "MedPlatform - Python Sidecar" /min cmd /c "cd medclient\sidecar-python && set MEDCLIENT_IPC_TOKEN=%MEDCLIENT_IPC_TOKEN% && ..\..\%PYTHON_EXE% -m src.main --port 8765 --host 127.0.0.1"

:: Attesa breve per inizializzazione FastAPI
ping 127.0.0.1 -n 3 >nul

:: 4. Avvio Frontend React Vite su http://127.0.0.1:5173
echo [*] Avvio Frontend React 19 SDUI su http://127.0.0.1:5173 ...
start "MedPlatform - Frontend SDUI" /min cmd /c "cd medclient\frontend-react && npm run dev"

:: Attesa breve per bind porta Vite
ping 127.0.0.1 -n 3 >nul

:: 5. Apertura Browser Predefinito
echo [*] Apertura dell'interfaccia nel browser...
start http://localhost:5173

echo.
echo ======================================================================
echo   PIATTAFORMA MEDICA ATTIVA E FUNZIONANTE!
echo   - URL Web Clinico : http://localhost:5173
echo   - Sidecar API     : http://127.0.0.1:8765/docs
echo ======================================================================
echo.
echo Per arrestare tutti i servizi, premi un tasto qualsiasi in questa finestra.
echo.
pause >nul

echo.
echo [*] Arresto dei servizi MedPlatform in corso...
call ARRESTA_MEDPLATFORM.bat
