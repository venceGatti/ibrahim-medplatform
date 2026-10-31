@echo off
chcp 65001 >nul
title MedPlatform - Arresto Servizi

echo [*] Arresto dei processi sulle porte 8765 (Python Sidecar) e 5173 (React Frontend)...

:: Cerca e termina i processi in ascolto sulla porta 8765
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    echo [*] Terminazione processo PID %%a su porta 8765...
    taskkill /F /PID %%a >nul 2>&1
)

:: Cerca e termina i processi in ascolto sulla porta 5173
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo [*] Terminazione processo PID %%a su porta 5173...
    taskkill /F /PID %%a >nul 2>&1
)

echo [OK] Tutti i servizi MedPlatform sono stati arrestati con successo.
ping 127.0.0.1 -n 3 >nul
