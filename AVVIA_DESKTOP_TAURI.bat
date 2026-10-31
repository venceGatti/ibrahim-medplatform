@echo off
chcp 65001 >nul
title MedPlatform - Avvio Desktop Tauri (Client Nativo)
cls

echo ======================================================================
echo           MEDPLATFORM - AVVIO CLIENT DESKTOP NATIVO (TAURI)
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

echo [*] Interprete Python rilevato: %PYTHON_EXE%
echo [*] Avvio dell'applicazione desktop Tauri...
echo.

cd medclient\core-rust
cargo test --quiet
cargo run

pause
