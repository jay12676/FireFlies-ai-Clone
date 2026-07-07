# Starts both the FastAPI backend and the Next.js frontend, each in its own
# PowerShell window, then opens the app in the default browser once both are up.
# Safe to re-run any time: it first kills anything already using ports
# 8000/3000/3001, so leftover processes from a previous run never conflict.
#
# Usage:  powershell -ExecutionPolicy Bypass -File run.ps1
#     or, from an existing PowerShell prompt:  .\run.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Stop-ProcessOnPort($port) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        try {
            Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "  Closed a leftover process on port $port (PID $($c.OwningProcess))" -ForegroundColor DarkYellow
        } catch {}
    }
}

Write-Host "Making sure ports 8000/3000/3001 are free..." -ForegroundColor Yellow
Stop-ProcessOnPort 8000
Stop-ProcessOnPort 3000
Stop-ProcessOnPort 3001
Start-Sleep -Seconds 1

Write-Host "Starting backend (FastAPI) on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 127.0.0.1 --port 8000"
)

Write-Host "Starting frontend (Next.js) on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$root\frontend'; `$env:NEXT_PUBLIC_API_URL='http://localhost:8000'; npm run dev"
)

Write-Host "Waiting for both servers to come up..." -ForegroundColor Yellow
$backendUp = $false
$frontendUp = $false
for ($i = 0; $i -lt 40; $i++) {
    if (-not $backendUp) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $backendUp = $true }
        } catch {}
    }
    if (-not $frontendUp) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $frontendUp = $true }
        } catch {}
    }
    if ($backendUp -and $frontendUp) { break }
    Start-Sleep -Seconds 1.5
}

if ($backendUp -and $frontendUp) {
    Write-Host "Both servers are up!" -ForegroundColor Green
    Write-Host "  Backend:  http://localhost:8000  (docs at /docs)"
    Write-Host "  Frontend: http://localhost:3000"
    Start-Process "http://localhost:3000"
} else {
    Write-Host "Timed out waiting for servers. Check the two opened windows for errors." -ForegroundColor Red
    Write-Host "  Backend up:  $backendUp"
    Write-Host "  Frontend up: $frontendUp"
}
