@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title MedPlatform Clinical Workstation - OneClick Launcher
cls

echo ======================================================================
echo          MedPlatform Clinical Workstation - System Boot
echo ======================================================================
echo.

:: 1. Assicura che la directory di lavoro sia sempre la cartella dello script
cd /d "%~dp0"
set "ROOT_DIR=%~dp0"

:: Crea directory per i log diagnostici
if not exist "%ROOT_DIR%.system_logs" mkdir "%ROOT_DIR%.system_logs"

:: 2. Arresto preventivo di eventuali processi residui su 8765 e 5173
echo [*] Bonifica porte di rete (8765 e 5173)...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8765 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: 3. Identificazione ambiente Python dedicato
set "PYTHON_EXE="
if exist "%ROOT_DIR%agent_env\Scripts\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%agent_env\Scripts\python.exe"
) else if exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Interprete Python: !PYTHON_EXE!

:: 4. Token IPC di sicurezza effimero
set "MEDCLIENT_IPC_TOKEN=medclient_local_session_secure_token"

:: 5. Avvio demone Backend Sidecar Python (porta 8765)
echo [*] Avvio FastAPI Clinical Sidecar Engine...
start "MedPlatform - Backend" /min cmd /c "cd /d "%ROOT_DIR%medclient\sidecar-python" && set MEDCLIENT_IPC_TOKEN=%MEDCLIENT_IPC_TOKEN% && "!PYTHON_EXE!" -m src.main --port 8765 --host 127.0.0.1 > "%ROOT_DIR%.system_logs\launcher_backend.log" 2>&1"

:: 6. Avvio server Frontend React 19 SDUI Vite (porta 5173)
echo [*] Avvio React 19 SDUI Frontend Server...
start "MedPlatform - Frontend" /min cmd /c "cd /d "%ROOT_DIR%medclient\frontend-react" && npm run dev > "%ROOT_DIR%.system_logs\launcher_frontend.log" 2>&1"

:: 7. Polling di readiness attivo (attesa che entrambi i servizi siano in ascolto)
echo [*] Attesa sincronizzazione dei servizi (max 20s)...
set /a ATTEMPTS=0
:WAIT_LOOP
set /a ATTEMPTS+=1
ping 127.0.0.1 -n 2 >nul

curl.exe -s -f "http://127.0.0.1:8765/agent/health" -H "X-Tauri-IPC-Secret: %MEDCLIENT_IPC_TOKEN%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    curl.exe -s -f "http://127.0.0.1:5173/" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Backend e Frontend operativi e sincronizzati!
        goto LAUNCH_APP
    )
)

if !ATTEMPTS! GEQ 20 (
    echo [!] Timeout durante l'avvio. Consulta i log in .system_logs\
    goto LAUNCH_APP
)

echo [*] Controllo prontezza servizi (!ATTEMPTS!/20)...
goto WAIT_LOOP

:LAUNCH_APP
echo.
echo [*] Apertura interfaccia grafica MedPlatform...
start http://127.0.0.1:5173/

echo [OK] MedPlatform avviato con successo.
ping 127.0.0.1 -n 3 >nul
exit
