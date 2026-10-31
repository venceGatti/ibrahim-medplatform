# MedPlatform One-Click Silent Launcher
$ErrorActionPreference = "SilentlyContinue"

$projectDir = "C:\Users\vence\Downloads\projects\ibrahim"
$pythonExe = "$projectDir\agent_env\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "$projectDir\.venv\Scripts\python.exe"
}
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python.exe"
}

$sidecarDir = "$projectDir\medclient\sidecar-python"
$frontendDir = "$projectDir\medclient\frontend-react"

# 1. Verifica e avvio Python Sidecar su porta 8765
$conn8765 = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if (-not $conn8765) {
    $env:MEDCLIENT_IPC_TOKEN = "medclient_local_session_secure_token"
    Start-Process -FilePath $pythonExe `
        -ArgumentList "-m src.main --port 8765 --host 127.0.0.1" `
        -WorkingDirectory $sidecarDir `
        -RedirectStandardOutput "$projectDir\sidecar.log" `
        -RedirectStandardError "$projectDir\sidecar_err.log"
}

# 2. Verifica e avvio Frontend React Vite su porta 5173
$conn5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $conn5173) {
    Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c npm run dev" `
        -WorkingDirectory $frontendDir `
        -RedirectStandardOutput "$projectDir\frontend.log" `
        -RedirectStandardError "$projectDir\frontend_err.log"
}

# 3. Attesa rapida disponibilità porta 5173 (max 4s)
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Milliseconds 350
    $check = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if ($check) { break }
}

# 4. Apertura immediata nel browser predefinito
Start-Process "http://localhost:5173"
