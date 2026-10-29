# MULE MATRIX — Reliable Multi-Process Launch Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " MULE MATRIX · Forensic Financial Investigation Platform " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

# 1. Start FastAPI Backend with explicit working directory
Write-Host "`n[1/3] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Process powershell -WorkingDirectory $BackendDir -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting MULE MATRIX Backend...' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru

# 2. Wait and verify backend health
Write-Host "[2/3] Verifying Backend Health..." -ForegroundColor Yellow
$backendReady = $false
for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 1
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/system/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($res.status -eq "HEALTHY") {
            $backendReady = $true
            Write-Host "  Backend is HEALTHY and listening on http://127.0.0.1:8000" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "  Waiting for backend startup (attempt $i/10)..." -ForegroundColor Gray
    }
}

if (-not $backendReady) {
    Write-Host "  WARNING: Backend did not respond within 10s. Check the backend PowerShell window for startup logs." -ForegroundColor Red
}

# 3. Start Vite Frontend
Write-Host "`n[3/3] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
$frontendJob = Start-Process powershell -WorkingDirectory $FrontendDir -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting MULE MATRIX Frontend...' -ForegroundColor Cyan; npm run dev" -PassThru

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " MULE MATRIX Services Launched Successfully!" -ForegroundColor Green
Write-Host "  - Frontend UI:      http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API:      http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  - Interactive Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "`nKeep the opened PowerShell windows running to maintain services." -ForegroundColor Gray
