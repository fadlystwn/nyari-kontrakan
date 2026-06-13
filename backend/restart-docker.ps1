# Restart Docker Desktop Script
Write-Host "Stopping Docker Desktop..." -ForegroundColor Yellow

# Stop Docker Desktop processes
Get-Process -Name "*docker*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait for processes to stop
Start-Sleep -Seconds 5

# Stop Docker services
Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue

# Wait a bit
Start-Sleep -Seconds 3

Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow

# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

Write-Host "Waiting for Docker Desktop to initialize (this may take 1-2 minutes)..." -ForegroundColor Yellow

# Wait and check if Docker is ready
$maxAttempts = 30
$attempt = 0
$dockerReady = $false

while ($attempt -lt $maxAttempts -and -not $dockerReady) {
    Start-Sleep -Seconds 4
    $attempt++
    
    try {
        $result = docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dockerReady = $true
            Write-Host "Docker Desktop is ready!" -ForegroundColor Green
        } else {
            Write-Host "Attempt $attempt/$maxAttempts - Docker not ready yet..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "Attempt $attempt/$maxAttempts - Docker not ready yet..." -ForegroundColor Gray
    }
}

if ($dockerReady) {
    Write-Host "`nDocker Desktop is now running successfully!" -ForegroundColor Green
    Write-Host "You can now run: docker compose up --build" -ForegroundColor Cyan
} else {
    Write-Host "`nDocker Desktop failed to start properly." -ForegroundColor Red
    Write-Host "Please try the following:" -ForegroundColor Yellow
    Write-Host "1. Open Docker Desktop manually from Start menu" -ForegroundColor White
    Write-Host "2. Check for error messages in Docker Desktop UI" -ForegroundColor White
    Write-Host "3. Try resetting Docker Desktop: Settings > Troubleshooting > Clean/Purge data" -ForegroundColor White
}
