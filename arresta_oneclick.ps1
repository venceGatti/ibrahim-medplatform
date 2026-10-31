# MedPlatform One-Click Cleaner
$ErrorActionPreference = "SilentlyContinue"

$ports = @(8765, 5173)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.OwningProcess -gt 0) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}
