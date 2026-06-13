# Property Data Scraper System
## Product Requirements Document

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Status | Draft — Ready for Implementation |
| Date | June 10, 2026 |
| Target | Code Agent / Developer |
| Deployment | Single VPS with Docker Compose |

---

## 1. Project Overview

This document defines the requirements, architecture, and implementation specifications for a Property Data Scraper System. The system is designed to run entirely on a single VPS using Docker Compose, collecting property listing data from Indonesian real estate platforms (e.g., OLX, Lamudi, Rumah123) on a scheduled, non-real-time batch basis.

This PRD is intended to serve as a direct implementation reference for a code agent or developer.

### 1.1 Goals

- Automatically scrape property listings from one or more target websites on a configurable schedule.
- Persist structured property data (price, location, rooms, land area, photos) in a PostgreSQL database.
- Expose the collected data through a RESTful API built with FastAPI.
- Deploy the full system as three Docker containers managed by Docker Compose on a single $5–$10/month VPS.
- Avoid detection by anti-bot systems using Playwright Stealth and rotating residential proxies.

### 1.2 Non-Goals

- Real-time or streaming data updates.
- Frontend / UI (this PRD covers the backend data pipeline and API only).
- Multi-VPS or cloud-native distributed deployment.

---

## 2. System Architecture

The system is composed of three Docker containers that communicate over a shared Docker bridge network, fronted by Nginx and Certbot running on the host for TLS termination and reverse proxying.

```
[ VPS HOST ]
│
├── Nginx (host) ──────── Reverse proxy + SSL (Let's Encrypt via Certbot)
│       │
│       └── → forwards /api/* → Container 2 (FastAPI :8000)
│
├── Container 1: postgres
│       Image : postgres:16-alpine
│       Purpose : Persistent storage for all property listings
│       Port  : 5432 (internal only)
│
├── Container 2: api
│       Image : python:3.12-slim (custom)
│       Purpose : FastAPI web server — serves data to the frontend
│       Port  : 8000 (exposed to host via Nginx)
│       Deps  : postgres
│
└── Container 3: scraper
        Image : python:3.12-slim (custom, includes Playwright)
        Purpose : Scheduled scraping jobs via APScheduler
        Port  : none (no inbound traffic)
        Deps  : postgres
```

All three containers share one Docker Compose file and communicate via a single internal Docker network named `scraper_net`.

---

## 3. Technology Stack Specification

| Category | Technology | Role / Notes |
|---|---|---|
| Scraping Core | Playwright (Python) | Headless browser automation; handles JS-heavy SPAs and infinite scroll |
| Scraping Core | playwright-stealth | Plugin to bypass anti-bot fingerprinting (Cloudflare, etc.) |
| Scraping Core | HTTPX / Requests | Lightweight HTTP calls for sites with accessible internal APIs |
| Scraping Core | BeautifulSoup4 | HTML parsing and data extraction from captured page content |
| API Layer | FastAPI | Async REST API framework; auto-generates OpenAPI / Swagger docs |
| API Layer | Uvicorn | ASGI server to serve the FastAPI application |
| Database | PostgreSQL 16 | Primary relational store; optimized indexes for filtering/searching |
| Scheduling | APScheduler | In-process Python scheduler; configurable cron-style job triggers |
| Infrastructure | Docker & Docker Compose | Container orchestration for all three services on one VPS |
| Infrastructure | Nginx | Reverse proxy; TLS termination; routes traffic to FastAPI |
| Infrastructure | Certbot (Let's Encrypt) | Automated free SSL/TLS certificate provisioning |
| Anti-blocking | Rotating Residential Proxies | External proxy service (Webshare / Bright Data / Oxylabs) |

---

## 4. Component Specifications

### 4.1 Container 1 — PostgreSQL Database

#### 4.1.1 Image
```
postgres:16-alpine
```

#### 4.1.2 Environment Variables

- **`POSTGRES_DB`**: `scraper_db`
- **`POSTGRES_USER`**: `scraper_user`
- **`POSTGRES_PASSWORD`**: Inject via `.env` file; never hardcode

#### 4.1.3 Volumes

- **`postgres_data:/var/lib/postgresql/data`**: Persistent named volume — survives container restarts

#### 4.1.4 Core Schema — `listings` Table

```sql
CREATE TABLE listings (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(64)     NOT NULL,          -- e.g. 'olx', 'rumah123'
    external_id     VARCHAR(255)    UNIQUE NOT NULL,   -- unique ID from source site
    title           TEXT            NOT NULL,
    price           BIGINT,                            -- stored in IDR
    location        TEXT,
    city            VARCHAR(128),
    property_type   VARCHAR(64),                       -- e.g. 'house', 'apartment', 'land'
    bedrooms        INTEGER,
    bathrooms       INTEGER,
    land_area_sqm   INTEGER,
    building_area_sqm INTEGER,
    url             TEXT            NOT NULL,
    photos          TEXT[],                            -- array of image URLs
    raw_data        JSONB,                             -- full raw payload for future use
    scraped_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_listings_city     ON listings(city);
CREATE INDEX idx_listings_price    ON listings(price);
CREATE INDEX idx_listings_type     ON listings(property_type);
CREATE INDEX idx_listings_source   ON listings(source);
CREATE INDEX idx_listings_scraped  ON listings(scraped_at DESC);
```

---

### 4.2 Container 2 — FastAPI Application

#### 4.2.1 Directory Structure

```
api/
├── main.py               # FastAPI app entry point
├── database.py           # SQLAlchemy async engine + session factory
├── models.py             # ORM models matching listings schema
├── schemas.py            # Pydantic request/response schemas
├── routers/
│   └── listings.py       # /listings route handlers
├── requirements.txt
└── Dockerfile
```

#### 4.2.2 Required Dependencies (`requirements.txt`)

```
fastapi==0.111.*
uvicorn[standard]==0.30.*
sqlalchemy[asyncio]==2.0.*
asyncpg==0.29.*
pydantic==2.*
python-dotenv
```

#### 4.2.3 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/listings` | Paginated list; supports filters: `city`, `property_type`, `min_price`, `max_price`, `source` |
| GET | `/listings/{id}` | Single listing detail by internal ID |
| GET | `/listings/stats` | Aggregate stats: count by city, avg price by type |
| GET | `/health` | Health check — returns service status and DB connectivity |

#### 4.2.4 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 4.3 Container 3 — Python Scraper + APScheduler

#### 4.3.1 Directory Structure

```
scraper/
├── main.py               # APScheduler entry point; registers all jobs
├── scheduler.py          # Scheduler configuration and job wiring
├── database.py           # Shared DB connection (sync psycopg2 or asyncpg)
├── scrapers/
│   ├── base.py           # Abstract BaseScraper class
│   ├── olx.py            # OLX-specific scraper implementation
│   └── rumah123.py       # Rumah123-specific scraper implementation
├── utils/
│   ├── proxy.py          # Proxy rotation helper
│   └── stealth.py        # Playwright stealth setup utility
├── curation/
│   ├── __init__.py
│   ├── curator.py        # Main curation orchestrator
│   ├── gemini_client.py  # Gemini API wrapper
│   ├── prompts.py        # All prompt templates
│   └── normalizer.py     # Post-processing of LLM JSON responses
├── requirements.txt
└── Dockerfile
```

#### 4.3.2 Required Dependencies (`requirements.txt`)

```
playwright==1.44.*
playwright-stealth==1.0.*
beautifulsoup4==4.12.*
httpx==0.27.*
psycopg2-binary==2.9.*
apscheduler==3.10.*
python-dotenv
```

#### 4.3.3 Scraper Base Class Contract

```python
# scrapers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    source: str  # must be set in subclass, e.g. "olx"

    @abstractmethod
    async def fetch_listings(self) -> List[Dict[str, Any]]:
        """
        Return a list of raw listing dicts.
        Each dict must include at minimum: external_id, title, url.
        """
        ...

    @abstractmethod
    def parse_listing(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw listing dict into the listings table schema.
        """
        ...
```

#### 4.3.4 APScheduler Job Configuration

```python
# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Run OLX scraper every day at 00:00 (midnight) server time
scheduler.add_job(run_olx_scraper,   "cron", hour=0,  minute=0)

# Run Rumah123 scraper every day at 01:00
scheduler.add_job(run_rumah123_scraper, "cron", hour=1, minute=0)
```

#### 4.3.5 Playwright + Stealth Setup

```python
# utils/stealth.py
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def get_stealth_page(proxy: str = None):
    playwright = await async_playwright().start()
    browser_args = {}
    if proxy:
        browser_args["proxy"] = {"server": proxy}
    browser = await playwright.chromium.launch(headless=True, **browser_args)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="id-ID",
        timezone_id="Asia/Jakarta"
    )
    page = await context.new_page()
    await stealth_async(page)
    return playwright, browser, page
```

#### 4.3.6 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps
COPY . .
CMD ["python", "main.py"]
```

---

## 5. Docker Compose Configuration

```yaml
# docker-compose.yml
version: "3.9"

services:

  postgres:
    image: postgres:16-alpine
    container_name: scraper_postgres
    restart: unless-stopped
    env_file: .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - scraper_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: ./api
    container_name: scraper_api
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    ports:
      - "8000:8000"
    networks:
      - scraper_net
    depends_on:
      postgres:
        condition: service_healthy

  scraper:
    build: ./scraper
    container_name: scraper_worker
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      PROXY_LIST: ${PROXY_LIST}
    networks:
      - scraper_net
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:

networks:
  scraper_net:
    driver: bridge
```

---

## 6. Nginx & SSL Configuration

### 6.1 Nginx Config (`/etc/nginx/sites-available/scraper`)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /api/ {
        proxy_pass         http://127.0.0.1:8000/;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### 6.2 Certbot Certificate Provisioning

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Issue certificate (Nginx plugin handles config automatically)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is handled by the systemd timer installed by Certbot
# Verify: sudo systemctl status certbot.timer
```

---

## 7. Environment Variables (`.env`)

```bash
# .env — never commit this file to version control
POSTGRES_DB=scraper_db
POSTGRES_USER=scraper_user
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# Rotating proxy list (comma-separated)
# Format: http://user:pass@host:port
PROXY_LIST=http://user:pass@proxy1.webshare.io:10000,http://user:pass@proxy2.webshare.io:10001

# LLM Curation
GEMINI_API_KEY=your_google_ai_studio_api_key_here
CURATION_BATCH_SIZE=10
CURATION_RATE_LIMIT_DELAY=1
```

> **Important:** Add `.env` to `.gitignore` immediately. Never hardcode secrets in source files.

---

## 8. Proxy Rotation

Each scrape request must use a different residential IP to avoid IP-level bans.

```python
# utils/proxy.py
import os, random

def get_random_proxy() -> str | None:
    proxy_list_raw = os.getenv("PROXY_LIST", "")
    if not proxy_list_raw:
        return None
    proxies = [p.strip() for p in proxy_list_raw.split(",") if p.strip()]
    return random.choice(proxies) if proxies else None
```

**Recommended proxy providers (residential IP pools):**

- **Webshare** — Cost-effective; free tier available for testing
- **Bright Data** — Premium; large residential pool; best for OLX-scale scraping
- **Oxylabs** — Enterprise-grade; reliable for high-frequency jobs

---

## 9. Implementation Checklist

### Phase 1 — Infrastructure
1. Provision VPS (Ubuntu 22.04 LTS, minimum 1 vCPU / 1 GB RAM)
2. Install Docker Engine and Docker Compose plugin
3. Install Nginx and Certbot on the host
4. Point domain DNS A record to VPS IP
5. Create `.env` from the template in Section 7

### Phase 2 — Database
1. Write `docker-compose.yml` for the postgres service
2. Run migrations to create the `listings` table and indexes
3. Verify connectivity: `psql -h localhost -U scraper_user scraper_db`

### Phase 3 — API Service
1. Scaffold FastAPI project using the directory structure in Section 4.2.1
2. Implement all four endpoints listed in Section 4.2.3
3. Write Dockerfile and add `api` service to `docker-compose.yml`
4. Verify Swagger UI accessible at `http://localhost:8000/docs`

### Phase 4 — Scraper Service
1. Implement `BaseScraper` abstract class (Section 4.3.3)
2. Implement `get_stealth_page()` utility (Section 4.3.5)
3. Implement at least one concrete scraper (e.g. `OlxScraper`)
4. Wire scraper jobs into APScheduler (Section 4.3.4)
5. Write Dockerfile with Playwright Chromium install (Section 4.3.6)
6. Add `scraper` service to `docker-compose.yml`

### Phase 5 — Deployment
1. Run: `docker compose up -d`
2. Configure Nginx reverse proxy (Section 6.1)
3. Issue SSL certificate via Certbot (Section 6.2)
4. Trigger manual scrape run and verify data appears in DB
5. Verify `/api/listings` returns data through HTTPS

---

## 10. Constraints & Non-Functional Requirements

| Constraint | Requirement |
|---|---|
| VPS Cost | $5–$10/month (e.g. DigitalOcean Basic, Hetzner CX11) |
| Min RAM | 1 GB (2 GB recommended for Playwright headless browser) |
| Scraping Frequency | Configurable via APScheduler; default: once daily per source |
| Data Freshness | Non-real-time; batch updates are acceptable |
| API Response Time | < 500ms for paginated listing queries with proper indexes |
| Security | API must be served over HTTPS only; no credentials in source code |
| Portability | Full stack must be reproducible via `docker compose up` on any VPS |
| Extensibility | New scrapers must only require a new class implementing `BaseScraper` |

---

## 11. LLM Curation Module (Gemini Flash Integration)

After raw listings are scraped and stored, the Curation Module enriches each listing using Google Gemini Flash (`gemini-2.5-flash`) via the Google Generative Language API. This module runs as an async post-processing step, either triggered automatically after each scraper job completes or on its own separate cron schedule.

### 11.1 Purpose & Responsibilities

- **Data Cleaning** — Normalize inconsistent field values (e.g. `3 KT` vs `3 kamar tidur` vs `3BR`) into a canonical format.
- **Quality Scoring** — Assign a `quality_score` (0–100) based on listing completeness, photo count, description richness, and price plausibility.
- **Duplicate Detection** — Identify semantically duplicate listings across sources using LLM comparison of title + description + location.
- **Tag Generation** — Auto-generate structured tags (e.g. `['pet-friendly', 'near-toll', 'furnished', 'cluster']`) from unstructured description text.
- **Summary Generation** — Produce a clean 2–3 sentence Indonesian-language summary of each listing for use in frontend cards.

### 11.2 Architecture Integration

The curation module runs inside Container 3 (the scraper container) as a separate APScheduler job, keeping the Docker Compose footprint unchanged. It reads uncurated listings from PostgreSQL, calls the Gemini API, and writes results back to the database.

```
[ Scraper Container — APScheduler Jobs ]
│
├── Job A: run_scraper()     → scrapes raw listings → INSERT into listings
│                                                             │
└── Job B: run_curation()    → reads listings WHERE curated = FALSE
                             → calls Gemini Flash API per batch
                             → UPDATE listings SET curated_data = {...},
                                    quality_score = N,
                                    tags = [...],
                                    summary = '...',
                                    curated = TRUE
```

### 11.3 Database Schema — Curation Fields

```sql
ALTER TABLE listings
  ADD COLUMN curated          BOOLEAN     NOT NULL DEFAULT FALSE,
  ADD COLUMN quality_score    SMALLINT,            -- 0–100
  ADD COLUMN tags             TEXT[],              -- e.g. ['furnished', 'near-toll']
  ADD COLUMN summary          TEXT,                -- LLM-generated 2–3 sentence summary
  ADD COLUMN normalized_data  JSONB,               -- cleaned/canonical field values
  ADD COLUMN curation_model   VARCHAR(64),         -- e.g. 'gemini-2.5-flash'
  ADD COLUMN curated_at       TIMESTAMPTZ;

CREATE INDEX idx_listings_curated ON listings(curated);
CREATE INDEX idx_listings_quality ON listings(quality_score DESC);
CREATE INDEX idx_listings_tags    ON listings USING GIN(tags);
```

### 11.4 Directory Structure

```
scraper/
├── ...
└── curation/
    ├── __init__.py
    ├── curator.py          # Main curation orchestrator
    ├── gemini_client.py    # Gemini API wrapper
    ├── prompts.py          # All prompt templates
    └── normalizer.py       # Post-processing of LLM JSON responses
```

### 11.5 Gemini API Client

```python
# curation/gemini_client.py
import os, httpx, json
from typing import Any

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.5-flash:generateContent"
)

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ["GEMINI_API_KEY"]

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def curate_listing(self, listing: dict) -> dict:
        from .prompts import build_curation_prompt
        prompt = build_curation_prompt(listing)
        raw = await self.generate(prompt)
        return json.loads(raw)
```

### 11.6 Prompt Template

```python
# curation/prompts.py

def build_curation_prompt(listing: dict) -> str:
    return f"""
You are a real estate data curator for an Indonesian property platform.
Analyze the following raw property listing and return a JSON object only.

RAW LISTING:
- Title       : {listing.get('title', '')}
- Price       : {listing.get('price', '')}
- Location    : {listing.get('location', '')}
- Bedrooms    : {listing.get('bedrooms', '')}
- Bathrooms   : {listing.get('bathrooms', '')}
- Land Area   : {listing.get('land_area_sqm', '')} sqm
- Building    : {listing.get('building_area_sqm', '')} sqm
- Description : {listing.get('raw_data', {}).get('description', '')[:800]}
- Photos      : {len(listing.get('photos') or [])} photos
- Source      : {listing.get('source', '')}

Return ONLY a valid JSON object with this exact schema:
{{
  "quality_score": <integer 0-100>,
  "tags": [<list of short English/Indonesian keyword tags, max 8>],
  "summary": "<2-3 sentence Indonesian summary of the listing>",
  "normalized": {{
    "bedrooms": <integer or null>,
    "bathrooms": <integer or null>,
    "land_area_sqm": <integer or null>,
    "building_area_sqm": <integer or null>,
    "furnishing": "<unfurnished|semi-furnished|furnished|unknown>",
    "condition": "<new|good|needs-renovation|unknown>"
  }},
  "is_duplicate_candidate": <true|false>
}}

Quality score guide:
- 80–100 : Complete data, many photos, detailed description, plausible price
- 50–79  : Moderate completeness, some fields missing
- 0–49   : Sparse data, no photos, suspicious price, or very short description
"""
```

### 11.7 Curation Orchestrator

```python
# curation/curator.py
import asyncio, logging, json
from .gemini_client import GeminiClient
from ..database import get_db_connection

BATCH_SIZE = 10           # listings to process per run
RATE_LIMIT_DELAY = 1.0    # seconds between API calls (free tier: 15 RPM)

logger = logging.getLogger(__name__)

async def run_curation():
    """
    Fetch uncurated listings in batches, enrich via Gemini, update DB.
    Safe to run concurrently with scraping jobs.
    """
    client = GeminiClient()
    conn = await get_db_connection()

    try:
        rows = await conn.fetch(
            """SELECT id, title, price, location, bedrooms, bathrooms,
                      land_area_sqm, building_area_sqm, photos,
                      source, raw_data
               FROM listings
               WHERE curated = FALSE
               ORDER BY scraped_at DESC
               LIMIT $1""",
            BATCH_SIZE
        )

        logger.info(f"Curating {len(rows)} listings...")

        for row in rows:
            listing = dict(row)
            try:
                result = await client.curate_listing(listing)
                await conn.execute(
                    """UPDATE listings SET
                         curated         = TRUE,
                         quality_score   = $1,
                         tags            = $2,
                         summary         = $3,
                         normalized_data = $4,
                         curation_model  = 'gemini-2.5-flash',
                         curated_at      = NOW()
                       WHERE id = $5""",
                    result["quality_score"],
                    result["tags"],
                    result["summary"],
                    json.dumps(result["normalized"]),
                    listing["id"]
                )
                logger.info(f"Curated listing id={listing['id']} score={result['quality_score']}")
            except Exception as e:
                logger.error(f"Curation failed for id={listing['id']}: {e}")

            await asyncio.sleep(RATE_LIMIT_DELAY)

    finally:
        await conn.close()
```

### 11.8 APScheduler Wiring

```python
# scheduler.py (updated)
from curation.curator import run_curation

# Curation runs after all scraper jobs finish
scheduler.add_job(run_olx_scraper,      "cron", hour=0, minute=0)
scheduler.add_job(run_rumah123_scraper, "cron", hour=1, minute=0)
scheduler.add_job(run_curation,         "cron", hour=3, minute=0)
```

### 11.9 Updated API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/listings` | Add optional filters: `min_quality=<int>`, `tags=<comma-separated>` |
| GET | `/listings/{id}/curation` | Return full curation result for one listing |
| GET | `/listings/curated` | Return only curated listings, sorted by `quality_score DESC` |
| POST | `/curation/trigger` | Manually trigger a curation batch run (admin use) |

### 11.10 Environment Variables

```bash
# Add to .env
GEMINI_API_KEY=your_google_ai_studio_api_key_here

# Optional tuning
CURATION_BATCH_SIZE=10
CURATION_RATE_LIMIT_DELAY=1
```

Obtain a free API key from Google AI Studio at https://aistudio.google.com. The free tier allows up to 15 requests per minute and 1,500 requests per day — sufficient for batch curation on a daily schedule.

### 11.11 Cost Estimate

| Scenario | Daily Listings | Est. Monthly Cost |
|---|---|---|
| Free tier (AI Studio) | Up to ~1,500/day | $0 (within free quota) |
| Small deployment | ~5,000/day | ~$1–3 |
| Medium deployment | ~20,000/day | ~$5–12 |

### 11.12 Implementation Checklist — Curation Module

1. Add curation columns to `listings` table (Section 11.3 migration)
2. Add `GEMINI_API_KEY` to `.env` and `docker-compose.yml` environment block for the scraper service
3. Add `httpx` to `scraper/requirements.txt`
4. Implement `gemini_client.py`, `prompts.py`, `curator.py` (Sections 11.5–11.7)
5. Wire `run_curation()` into APScheduler (Section 11.8)
6. Add new curation endpoints to FastAPI router (Section 11.9)
7. Test with 10 sample listings; verify JSON response schema from Gemini parses correctly
8. Monitor daily token usage via Google AI Studio dashboard to stay within budget
