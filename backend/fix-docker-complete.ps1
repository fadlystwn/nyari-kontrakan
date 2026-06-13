# Complete Docker Desktop Fix Script
# This script stops everything and restarts Docker Desktop cleanly

Write-Host "=== Docker Desktop Complete Fix ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop Docker Desktop
Write-Host "[1/5] Stopping Docker Desktop..." -ForegroundColor Yellow
Get-Process -Name "*Docker Desktop*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "*com.docker*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "      Docker Desktop stopped" -ForegroundColor Green

# Step 2: Shutdown WSL completely
Write-Host "[2/5] Shutting down WSL..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 5
Write-Host "      WSL shutdown complete" -ForegroundColor Green

# Step 3: Start Docker Desktop
Write-Host "[3/5] Starting Docker Desktop..." -ForegroundColor Yellow
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Write-Host "      Docker Desktop launched" -ForegroundColor Green

# Step 4: Wait for Docker to initialize
Write-Host "[4/5] Waiting for Docker engine to start (this takes 1-2 minutes)..." -ForegroundColor Yellow
Write-Host "      Please be patient..." -ForegroundColor Gray

$maxWait = 120  # 2 minutes
$waited = 0
$dockerReady = $false

while ($waited -lt $maxWait -and -not $dockerReady) {
    Start-Sleep -Seconds 5
    $waited += 5
    
    # Show progress
    $dots = "." * ($waited / 10)
    Write-Host "`r      Waiting $waited seconds $dots" -NoNewline -ForegroundColor Gray
    
    try {
        $result = docker version 2>&1 | Out-String
        if ($result -match "Server:") {
            $dockerReady = $true
        }
    } catch {
        # Still waiting
    }
}

Write-Host ""

if ($dockerReady) {
    Write-Host "      Docker engine is ready!" -ForegroundColor Green
    
    # Step 5: Verify with docker ps
    Write-Host "[5/5] Verifying Docker..." -ForegroundColor Yellow
    docker ps 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      Docker is working correctly!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== SUCCESS ===" -ForegroundColor Green
        Write-Host "Docker Desktop is now running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now run:" -ForegroundColor Cyan
        Write-Host "  docker compose up --build" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "      Docker ps failed, but engine is starting..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please wait 30 more seconds and try:" -ForegroundColor Yellow
        Write-Host "  docker compose up --build" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "=== DOCKER FAILED TO START ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "Docker Desktop did not start within 2 minutes." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try these manual steps:" -ForegroundColor Yellow
    Write-Host "1. Open Docker Desktop from Start menu" -ForegroundColor White
    Write-Host "2. Look for error messages in the Docker Desktop window" -ForegroundColor White
    Write-Host "3. Click Settings > Troubleshooting > 'Reset to factory defaults'" -ForegroundColor White
    Write-Host "4. Restart Docker Desktop after reset" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternative: Use Docker in WSL instead" -ForegroundColor Yellow
    Write-Host "Run: wsl" -ForegroundColor White
    Write-Host "Then: bash setup-docker-wsl.sh" -ForegroundColor White
}
