# Deployment Guide - Property Data Scraper System

Complete guide for deploying the Property Data Scraper System to a production VPS.

## 📋 Prerequisites

### VPS Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 1 vCPU | 2 vCPU |
| **RAM** | 1 GB | 2 GB |
| **Storage** | 20 GB SSD | 40 GB SSD |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **Monthly Cost** | $5-6 | $10-12 |

**Recommended VPS Providers:**
- DigitalOcean (Basic Droplet)
- Hetzner (CX11 or CX21)
- Vultr (Regular Performance)
- Linode (Nanode or Shared CPU)

### Required Services

- **Domain name** with DNS access
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com)
- **Residential proxy service** (optional): Webshare, Bright Data, Oxylabs

---

## 🚀 Phase 1: VPS Initial Setup

### 1.1 Create VPS Instance

1. **Create Ubuntu 22.04 LTS server** on your chosen provider
2. **Note the IP address** (e.g., `123.45.67.89`)
3. **Set up SSH key** (recommended) or use password

### 1.2 Initial Server Configuration

**Connect to your VPS:**
```bash
ssh root@123.45.67.89
```

**Update system packages:**
```bash
apt update && apt upgrade -y
```

**Set timezone to Jakarta:**
```bash
timedatectl set-timezone Asia/Jakarta
timedatectl
```

**Create non-root user:**
```bash
adduser scraper
usermod -aG sudo scraper
```

**Set up SSH for new user:**
```bash
rsync --archive --chown=scraper:scraper ~/.ssh /home/scraper
```

**Test new user access:**
```bash
# From your local machine
ssh scraper@123.45.67.89
```

### 1.3 Configure Firewall

**Install and configure UFW:**
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 1.4 Secure SSH (Optional but Recommended)

**Edit SSH config:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Recommended settings:**
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

**Restart SSH:**
```bash
sudo systemctl restart sshd
```

---

## 🐳 Phase 2: Install Docker

### 2.1 Install Docker Engine

**Remove old versions:**
```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

**Install dependencies:**
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```

**Add Docker's official GPG key:**
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

**Set up repository:**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Install Docker:**
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**Verify installation:**
```bash
sudo docker --version
sudo docker compose version
```

### 2.2 Configure Docker for Non-Root User

**Add user to docker group:**
```bash
sudo usermod -aG docker $USER
```

**Apply group changes:**
```bash
newgrp docker
```

**Test Docker without sudo:**
```bash
docker run hello-world
```

---

## 🌐 Phase 3: Domain and DNS Configuration

### 3.1 Configure DNS Records

**Add A record in your DNS provider:**
```
Type: A
Name: @ (or your subdomain, e.g., api)
Value: 123.45.67.89 (your VPS IP)
TTL: 3600
```

**For subdomain deployment:**
```
Type: A
Name: scraper
Value: 123.45.67.89
TTL: 3600
```

**Verify DNS propagation:**
```bash
# From your local machine
nslookup yourdomain.com
dig yourdomain.com
```

Wait 5-30 minutes for DNS propagation.

---

## 📦 Phase 4: Deploy Application

### 4.1 Clone Repository

**Install Git:**
```bash
sudo apt install -y git
```

**Clone your repository:**
```bash
cd ~
git clone <your-repository-url> property-scraper
cd property-scraper/backend
```

### 4.2 Configure Environment

**Copy environment template:**
```bash
cp .env.template .env
```

**Edit environment file:**
```bash
nano .env
```

**Production configuration:**
```bash
# Database - Use strong passwords!
POSTGRES_DB=scraper_db
POSTGRES_USER=scraper_user
POSTGRES_PASSWORD=<generate-strong-password-here>

# Gemini API
GEMINI_API_KEY=<your-gemini-api-key>

# Proxy List (optional but recommended)
PROXY_LIST=http://user:pass@proxy1.webshare.io:10000,http://user:pass@proxy2.webshare.io:10001

# Scraper Configuration
SCRAPE_ON_STARTUP=false
CURATION_BATCH_SIZE=10
CURATION_RATE_LIMIT_DELAY=1
GEMINI_MODEL=gemini-2.5-flash
```

**Generate strong password:**
```bash
openssl rand -base64 32
```

**Secure the .env file:**
```bash
chmod 600 .env
```

### 4.3 Build and Start Services

**Build containers:**
```bash
docker compose build
```

**Start services:**
```bash
docker compose up -d
```

**Verify services are running:**
```bash
docker compose ps
```

Expected output:
```
NAME                IMAGE                  STATUS
scraper_api         backend-api            Up
scraper_postgres    postgres:16-alpine     Up (healthy)
scraper_worker      backend-scraper        Up
```

**Check logs:**
```bash
docker compose logs -f
```

**Test API locally:**
```bash
curl http://localhost:8000/health
```

---

## 🔒 Phase 5: Nginx and SSL Setup

### 5.1 Install Nginx

**Install Nginx:**
```bash
sudo apt install -y nginx
```

**Start and enable Nginx:**
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### 5.2 Configure Nginx Reverse Proxy

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/scraper
```

**Add configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain
    
    # Redirect all HTTP to HTTPS (will be configured after SSL)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;  # Replace with your domain
    
    # SSL certificates (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Direct root access to API docs
    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
    
    # Request size limits
    client_max_body_size 10M;
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/scraper /etc/nginx/sites-enabled/
```

**Remove default site:**
```bash
sudo rm /etc/nginx/sites-enabled/default
```

**Test Nginx configuration:**
```bash
sudo nginx -t
```

**Reload Nginx:**
```bash
sudo systemctl reload nginx
```

### 5.3 Install SSL Certificate with Certbot

**Install Certbot:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

**Obtain SSL certificate:**
```bash
sudo certbot --nginx -d yourdomain.com
```

**Follow prompts:**
- Enter email address for renewal notifications
- Agree to Terms of Service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

**Verify certificate:**
```bash
sudo certbot certificates
```

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

**Check renewal timer:**
```bash
sudo systemctl status certbot.timer
```

### 5.4 Verify Deployment

**Test HTTPS access:**
```bash
curl https://yourdomain.com/health
```

**Test API endpoints:**
```bash
# Get listings
curl https://yourdomain.com/api/listings

# Get stats
curl https://yourdomain.com/api/listings/stats

# Access Swagger UI
# Open in browser: https://yourdomain.com/docs
```

---

## ✅ Phase 6: Post-Deployment Verification

### 6.1 Verify All Services

**Check Docker containers:**
```bash
docker compose ps
docker compose logs --tail=50
```

**Check database:**
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "SELECT COUNT(*) FROM listings;"
```

**Check API health:**
```bash
curl https://yourdomain.com/health
```

**Check Nginx status:**
```bash
sudo systemctl status nginx
```

**Check SSL certificate:**
```bash
sudo certbot certificates
```

### 6.2 Test Scraper Jobs

**Trigger manual scrape:**
```bash
docker compose exec scraper python -c "
from scheduler import run_olx_scraper
import asyncio
asyncio.run(run_olx_scraper())
"
```

**Check scraper logs:**
```bash
docker compose logs -f scraper
```

**Verify data in database:**
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "
SELECT source, COUNT(*) as count, MAX(scraped_at) as last_scrape 
FROM listings 
GROUP BY source;
"
```

### 6.3 Test Curation

**Trigger manual curation:**
```bash
curl -X POST https://yourdomain.com/api/curation/trigger
```

**Check curation logs:**
```bash
docker compose logs -f scraper | grep -i curation
```

**Verify curated data:**
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "
SELECT COUNT(*) as curated_count, AVG(quality_score) as avg_quality 
FROM listings 
WHERE curated = true;
"
```

---

## 🔄 Maintenance Procedures

### Update Application

**Pull latest changes:**
```bash
cd ~/property-scraper/backend
git pull origin main
```

**Rebuild and restart:**
```bash
docker compose down
docker compose build
docker compose up -d
```

**Verify update:**
```bash
docker compose logs -f
```

### Backup Database

**Create backup:**
```bash
docker compose exec postgres pg_dump -U scraper_user scraper_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Compress backup:**
```bash
gzip backup_*.sql
```

**Download backup to local machine:**
```bash
# From your local machine
scp scraper@yourdomain.com:~/property-scraper/backend/backup_*.sql.gz ./
```

### Restore Database

**Upload backup to VPS:**
```bash
# From your local machine
scp backup_20260612_120000.sql.gz scraper@yourdomain.com:~/
```

**Restore on VPS:**
```bash
gunzip backup_20260612_120000.sql.gz
docker compose exec -T postgres psql -U scraper_user scraper_db < backup_20260612_120000.sql
```

### View Logs

**All services:**
```bash
docker compose logs -f
```

**Specific service:**
```bash
docker compose logs -f api
docker compose logs -f scraper
docker compose logs -f postgres
```

**Last N lines:**
```bash
docker compose logs --tail=100 scraper
```

**Nginx logs:**
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitor Resources

**Container stats:**
```bash
docker compose stats
```

**Disk usage:**
```bash
df -h
docker system df
```

**Database size:**
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "
SELECT pg_size_pretty(pg_database_size('scraper_db')) as size;
"
```

---

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker logs:**
```bash
docker compose logs
```

**Check port conflicts:**
```bash
sudo netstat -tulpn | grep -E ':(8000|5432|80|443)'
```

**Restart services:**
```bash
docker compose restart
```

### Database Connection Issues

**Check database health:**
```bash
docker compose exec postgres pg_isready -U scraper_user -d scraper_db
```

**Reset database (⚠️ deletes all data):**
```bash
docker compose down -v
docker compose up -d
```

### SSL Certificate Issues

**Check certificate status:**
```bash
sudo certbot certificates
```

**Renew certificate manually:**
```bash
sudo certbot renew
```

**Check Nginx configuration:**
```bash
sudo nginx -t
```

### Scraper Not Working

**Check logs:**
```bash
docker compose logs -f scraper
```

**Verify environment variables:**
```bash
docker compose exec scraper env | grep -E '(PROXY|GEMINI)'
```

**Test manually:**
```bash
docker compose exec scraper python -c "
from scrapers.olx import OlxScraper
import asyncio
scraper = OlxScraper()
print(asyncio.run(scraper.fetch_listings()))
"
```

### High Memory Usage

**Check container stats:**
```bash
docker compose stats
```

**Limit container memory:**
Edit `docker-compose.yml`:
```yaml
scraper:
  deploy:
    resources:
      limits:
        memory: 1.5G
```

**Restart services:**
```bash
docker compose up -d
```

---

## 🔒 Security Checklist

- [ ] Firewall configured (UFW enabled)
- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] Strong database password set
- [ ] `.env` file permissions set to 600
- [ ] SSL certificate installed and auto-renewing
- [ ] Security headers configured in Nginx
- [ ] Regular backups scheduled
- [ ] System packages up to date
- [ ] Docker images up to date

---

## 📊 Monitoring Setup (Optional)

### Set Up Basic Monitoring

**Install monitoring tools:**
```bash
sudo apt install -y htop iotop nethogs
```

**Monitor in real-time:**
```bash
htop           # CPU and memory
iotop          # Disk I/O
nethogs        # Network usage
```

### Set Up Automated Backups

**Create backup script:**
```bash
nano ~/backup.sh
```

**Add content:**
```bash
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
cd ~/property-scraper/backend
docker compose exec -T postgres pg_dump -U scraper_user scraper_db | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

**Make executable:**
```bash
chmod +x ~/backup.sh
```

**Add to crontab (daily at 4 AM):**
```bash
crontab -e
```

Add line:
```
0 4 * * * /home/scraper/backup.sh
```

---

## 🎯 Success Criteria

✅ **All services running:** `docker compose ps` shows all containers up  
✅ **API accessible:** `https://yourdomain.com/health` returns 200  
✅ **SSL working:** Browser shows secure connection  
✅ **Scraper jobs scheduled:** Check logs for cron execution  
✅ **Database populated:** Listings table has data  
✅ **Curation working:** Curated listings have quality scores  
✅ **Backups configured:** Automated daily backups running  

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker compose logs -f`
2. Review troubleshooting section above
3. Verify all environment variables are set
4. Check firewall and DNS configuration
5. Consult README.md for development tips

---

## 🔄 Rollback Procedure

If deployment fails:

1. **Stop services:**
```bash
docker compose down
```

2. **Restore previous version:**
```bash
git checkout <previous-commit-hash>
docker compose build
docker compose up -d
```

3. **Restore database backup:**
```bash
docker compose exec -T postgres psql -U scraper_user scraper_db < backup_YYYYMMDD_HHMMSS.sql
```

4. **Verify rollback:**
```bash
curl https://yourdomain.com/health
docker compose logs -f
```
