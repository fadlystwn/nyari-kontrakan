# Docker Desktop Troubleshooting Guide

## Current Issue
Docker Desktop is installed but the Docker engine service won't start, causing all `docker` commands to fail with:
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.46/containers/json": 
The system cannot find the file specified.
```

## Solution 1: Reset Docker Desktop (Recommended)

### Step 1: Completely Uninstall Docker Desktop
1. **Open Settings** → Apps → Installed apps
2. **Find "Docker Desktop"** and click Uninstall
3. **Delete Docker data folders**:
   - `C:\Program Files\Docker`
   - `C:\ProgramData\Docker`
   - `%LOCALAPPDATA%\Docker`
   - `%APPDATA%\Docker`

### Step 2: Restart Computer
Restart your computer to clear any locked files or services.

### Step 3: Reinstall Docker Desktop
1. **Download Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. **Run the installer** as Administrator
3. **Enable WSL 2** during installation (recommended)
4. **Start Docker Desktop** and wait for initialization
5. **Verify installation**: Open PowerShell and run `docker ps`

## Solution 2: Fix Current Installation

### Option A: Reset Docker Desktop Settings
1. **Open Docker Desktop** from Start menu
2. **Click the gear icon** (Settings)
3. **Go to Troubleshooting** tab
4. **Click "Clean / Purge data"** - This will delete all containers, images, and volumes
5. **Click "Reset to factory defaults"**
6. **Restart Docker Desktop**

### Option B: Restart Docker Service Manually
1. **Open Services** (Win + R, type `services.msc`)
2. **Find "Docker Desktop Service"**
3. **Right-click** → Properties
4. **Set Startup type** to "Automatic"
5. **Click "Start"** to start the service
6. **Restart Docker Desktop**

### Option C: Check WSL Integration
1. **Open PowerShell as Administrator**
2. **Run**: `wsl --update`
3. **Run**: `wsl --set-default-version 2`
4. **Restart Docker Desktop**
5. **In Docker Desktop Settings** → Resources → WSL Integration
6. **Enable integration** with your WSL distributions

## Solution 3: Use Docker via WSL 2 Directly (Alternative)

If Docker Desktop continues to fail, you can install Docker Engine directly in WSL 2:

### Step 1: Install Docker in WSL
```bash
# Open WSL terminal
wsl

# Update packages
sudo apt update
sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

### Step 2: Run Backend in WSL
```bash
# Navigate to project
cd /mnt/c/Users/fadly/Documents/projects/nyari-kontrakan/backend

# Build and start
docker compose up --build
```

## Solution 4: Run Backend Without Docker

If Docker continues to fail, you can run the backend directly with Python:

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 16

### Step 1: Install PostgreSQL
1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for the `postgres` user

### Step 2: Create Database
```sql
-- Open pgAdmin or psql
CREATE DATABASE scraper_db;
CREATE USER scraper_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;
```

### Step 3: Set Up Python Environment
```powershell
# Install Python dependencies for API
cd api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install Python dependencies for scraper
cd ..\scraper
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 4: Update .env File
```bash
DATABASE_URL=postgresql+asyncpg://scraper_user:your_password@localhost:5432/scraper_db
GEMINI_API_KEY=your_api_key_here
```

### Step 5: Run Services
```powershell
# Terminal 1: Run API
cd api
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run Scraper
cd scraper
.\venv\Scripts\Activate.ps1
python main.py
```

## Checking Docker Desktop Status

### Check if Docker is running:
```powershell
docker ps
```

### Check Docker Desktop service:
```powershell
Get-Service -Name "com.docker.service"
```

### Check Docker processes:
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*docker*"}
```

### Check WSL status:
```powershell
wsl --status
wsl --list --verbose
```

## Common Error Messages

### "The system cannot find the file specified"
- Docker engine is not running
- Try restarting Docker Desktop
- Check if WSL is running: `wsl --status`

### "request returned Internal Server Error"
- Docker engine service failed to start
- Try resetting Docker Desktop
- Check Windows Event Viewer for errors

### "Cannot connect to the Docker daemon"
- Docker Desktop is not running
- Start Docker Desktop from Start menu
- Wait 1-2 minutes for initialization

## Getting Help

If none of these solutions work:
1. Check Docker Desktop logs in `%LOCALAPPDATA%\Docker\`
2. Check Windows Event Viewer for Docker-related errors
3. Visit Docker Desktop troubleshooting: https://docs.docker.com/desktop/troubleshoot/overview/
4. Consider using WSL 2 with Docker Engine instead of Docker Desktop
