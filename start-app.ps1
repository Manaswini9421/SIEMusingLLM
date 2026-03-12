# SIEM LLM Application Startup Script
# This script ensures all services are running before starting the application

Write-Host "===== SIEM LLM Application Startup =====" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "  Docker not running. Starting Docker Desktop..." -ForegroundColor Red
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "  Waiting 15 seconds for Docker to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
}
else {
    Write-Host "  ✓ Docker is running" -ForegroundColor Green
}

# Step 2: Check Wazuh containers
Write-Host "[2/4] Checking Wazuh containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" 2>$null
if ($containers -notcontains "single-node-wazuh.indexer-1") {
    Write-Host "  Wazuh not running. Starting Wazuh containers..." -ForegroundColor Red
    Set-Location "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM\wazuh-deployment\single-node"
    docker-compose up -d 2>&1 | Out-Null
    Write-Host "  Waiting 30 seconds for Wazuh to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    Set-Location "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM"
}
else {
    Write-Host "  ✓ Wazuh containers are running" -ForegroundColor Green
}

# Step 3: Check Backend server
Write-Host "[3/4] Checking Backend server..." -ForegroundColor Yellow
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $backendRunning) {
    Write-Host "  Backend not running. Starting backend server..." -ForegroundColor Red
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM'; Write-Host 'Starting Backend Server...' -ForegroundColor Cyan; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
    Start-Sleep -Seconds 5
}
else {
    Write-Host "  ✓ Backend server is running on port 8000" -ForegroundColor Green
}

# Step 4: Check Frontend server
Write-Host "[4/4] Checking Frontend server..." -ForegroundColor Yellow
$frontendRunning = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if (-not $frontendRunning) {
    Write-Host "  Frontend not running. Starting frontend server..." -ForegroundColor Red
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM\frontend'; Write-Host 'Starting Frontend Server...' -ForegroundColor Cyan; npm run dev"
    Start-Sleep -Seconds 5
}
else {
    Write-Host "  ✓ Frontend server is running on port 5173" -ForegroundColor Green
}

# Final check and open browser
Write-Host ""
Write-Host "===== Status Check =====" -ForegroundColor Cyan
$backendOk = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$frontendOk = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if ($backendOk -and $frontendOk) {
    Write-Host "✓ All services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
    Write-Host ""
    Write-Host "Opening application in browser..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:5173"
}
else {
    Write-Host "⚠ Some services failed to start. Check the opened terminal windows for errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
