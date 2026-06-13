# Property Data Scraper System

A production-ready property listing scraper and API system for Indonesian real estate platforms (OLX, Rumah123), featuring automated data collection, LLM-powered curation, and a RESTful API.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      VPS HOST                            │
│                                                          │
│  ┌────────────┐                                         │
│  │   Nginx    │ ──── Reverse Proxy + SSL (Let's Encrypt)│
│  └─────┬──────┘                                         │
│        │                                                 │
│  ┌─────▼──────────────────────────────────────────┐    │
│  │         Docker Compose Network                  │    │
│  │                                                  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────┐│    │
│  │  │  PostgreSQL  │  │   FastAPI    │  │Scraper││    │
│  │  │   :5432      │◄─┤   API :8000  │◄─┤Worker ││    │
│  │  │              │  │              │  │       ││    │
│  │  │  - Listings  │  │  - REST API  │  │- OLX  ││    │
│  │  │  - Indexes   │  │  - Swagger   │  │- R123 ││    │
│  │  │  - Curation  │  │  - CORS      │  │- LLM  ││    │
│  │  └──────────────┘  └──────────────┘  └───────┘│    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Domain name** pointed to your VPS (for production SSL)
- **Gemini API Key** from [Google AI Studio](https://aistudio.google.com)
- **Proxy service** (optional but recommended): Webshare, Bright Data, or Oxylabs

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd nyari-kontrakan/backend
```

2. **Configure environment variables**
```bash
cp .env.template .env
nano .env  # Edit with your actual values
```

Required variables:
```bash
# Database
POSTGRES_DB=scraper_db
POSTGRES_USER=scraper_user
POSTGRES_PASSWORD=your_strong_password_here

# Gemini API for curation
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Residential proxies (comma-separated)
PROXY_LIST=http://user:pass@proxy1.example.com:10000,http://user:pass@proxy2.example.com:10001

# Optional: Scrape on container startup (true/false)
SCRAPE_ON_STARTUP=false
```

3. **Build and start services**
```bash
docker compose up -d --build
```

4. **Verify services are running**
```bash
docker compose ps
docker compose logs -f
```

5. **Access the API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_DB` | ✅ | `scraper_db` | PostgreSQL database name |
| `POSTGRES_USER` | ✅ | `scraper_user` | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ | - | PostgreSQL password (use strong password!) |
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key for curation |
| `PROXY_LIST` | ❌ | - | Comma-separated proxy URLs |
| `SCRAPE_ON_STARTUP` | ❌ | `false` | Run scraper immediately on startup |
| `CURATION_BATCH_SIZE` | ❌ | `10` | Number of listings to curate per batch |
| `CURATION_RATE_LIMIT_DELAY` | ❌ | `1` | Delay in seconds between Gemini API calls |
| `GEMINI_MODEL` | ❌ | `gemini-2.5-flash` | Gemini model to use for curation |

## 🐳 Docker Compose Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f api
docker compose logs -f scraper
docker compose logs -f postgres

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v

# Rebuild and restart
docker compose up -d --build

# Execute command in running container
docker compose exec api bash
docker compose exec scraper python -c "print('Hello')"

# View resource usage
docker compose stats
```

## 📡 API Endpoints

### Listings

#### Get Paginated Listings
```bash
curl "http://localhost:8000/listings?page=1&limit=20"
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `city` (string): Filter by city
- `property_type` (string): Filter by type (house, apartment, land)
- `min_price` (int): Minimum price in IDR
- `max_price` (int): Maximum price in IDR
- `source` (string): Filter by source (olx, rumah123)
- `min_quality` (int): Minimum quality score (0-100)
- `tags` (string): Comma-separated tags

**Example with filters:**
```bash
curl "http://localhost:8000/listings?city=jakarta&property_type=house&min_price=500000000&max_price=2000000000&min_quality=70"
```

#### Get Single Listing
```bash
curl "http://localhost:8000/listings/123"
```

#### Get Statistics
```bash
curl "http://localhost:8000/listings/stats"
```

Returns:
- Count by city
- Average price by property type

#### Get Curated Listings
```bash
curl "http://localhost:8000/listings/curated?page=1&limit=20"
```

Returns only curated listings sorted by quality score (highest first).

#### Get Curation Details
```bash
curl "http://localhost:8000/listings/123/curation"
```

Returns curation metadata for a specific listing.

### Curation

#### Trigger Manual Curation
```bash
curl -X POST "http://localhost:8000/curation/trigger"
```

Triggers a background curation job for uncurated listings.

### Health

#### Health Check
```bash
curl "http://localhost:8000/health"
```

Returns service status and database connectivity.

## 🕐 Scheduled Jobs

The scraper container runs the following scheduled jobs:

| Job | Schedule | Description |
|-----|----------|-------------|
| OLX Scraper | Daily at 00:00 | Scrapes OLX property listings |
| Rumah123 Scraper | Daily at 01:00 | Scrapes Rumah123 property listings |
| Curation | Daily at 03:00 | Enriches listings using Gemini AI |

Jobs are configured in `scraper/scheduler.py` using APScheduler with cron expressions.

## 🗄️ Database Schema

### `listings` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `source` | VARCHAR(64) | Source platform (olx, rumah123) |
| `external_id` | VARCHAR(255) | Unique ID from source (unique constraint) |
| `title` | TEXT | Listing title |
| `price` | BIGINT | Price in IDR |
| `location` | TEXT | Full location string |
| `city` | VARCHAR(128) | Normalized city name |
| `property_type` | VARCHAR(64) | house, apartment, land, etc. |
| `bedrooms` | INTEGER | Number of bedrooms |
| `bathrooms` | INTEGER | Number of bathrooms |
| `land_area_sqm` | INTEGER | Land area in square meters |
| `building_area_sqm` | INTEGER | Building area in square meters |
| `url` | TEXT | Source URL |
| `photos` | TEXT[] | Array of photo URLs |
| `raw_data` | JSONB | Full raw data from source |
| `scraped_at` | TIMESTAMPTZ | When listing was scraped |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |
| **Curation Fields** | | |
| `curated` | BOOLEAN | Whether listing has been curated |
| `quality_score` | SMALLINT | Quality score 0-100 |
| `tags` | TEXT[] | Auto-generated tags |
| `summary` | TEXT | LLM-generated summary |
| `normalized_data` | JSONB | Cleaned/normalized fields |
| `curation_model` | VARCHAR(64) | Model used for curation |
| `curated_at` | TIMESTAMPTZ | When curation completed |

**Indexes:**
- `idx_listings_city` on `city`
- `idx_listings_price` on `price`
- `idx_listings_type` on `property_type`
- `idx_listings_source` on `source`
- `idx_listings_scraped` on `scraped_at DESC`
- `idx_listings_curated` on `curated`
- `idx_listings_quality` on `quality_score DESC`
- `idx_listings_tags` GIN index on `tags`

## 🔧 Development

### Local Development Setup

1. **Install Python dependencies** (for IDE support)
```bash
cd api
pip install -r requirements.txt

cd ../scraper
pip install -r requirements.txt
```

2. **Access database directly**
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db
```

3. **Run manual scrape**
```bash
docker compose exec scraper python -c "
from scrapers.olx import OlxScraper
import asyncio
scraper = OlxScraper()
asyncio.run(scraper.fetch_listings())
"
```

4. **Trigger manual curation**
```bash
curl -X POST "http://localhost:8000/curation/trigger"
```

### Project Structure

```
backend/
├── api/                      # FastAPI application
│   ├── main.py              # App entry point
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── listings.py      # Listings endpoints
│   │   └── curation.py      # Curation endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── scraper/                  # Scraper worker
│   ├── main.py              # Scheduler entry point
│   ├── scheduler.py         # APScheduler jobs
│   ├── database.py          # DB connection
│   ├── scrapers/
│   │   ├── base.py          # Abstract base class
│   │   ├── olx.py           # OLX scraper
│   │   └── rumah123.py      # Rumah123 scraper
│   ├── curation/
│   │   ├── curator.py       # Curation orchestrator
│   │   ├── gemini_client.py # Gemini API client
│   │   └── prompts.py       # LLM prompts
│   ├── utils/
│   │   ├── stealth.py       # Playwright stealth setup
│   │   └── proxy.py         # Proxy rotation
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml        # Orchestration config
├── init.sql                  # Database initialization
├── .env.template             # Environment template
└── README.md                 # This file
```

## 🐛 Troubleshooting

### Services won't start

**Check logs:**
```bash
docker compose logs -f
```

**Common issues:**
- Port 8000 or 5432 already in use → Change ports in `docker-compose.yml`
- Missing `.env` file → Copy from `.env.template`
- Invalid environment variables → Check `.env` syntax

### Database connection errors

**Verify database is healthy:**
```bash
docker compose exec postgres pg_isready -U scraper_user -d scraper_db
```

**Reset database:**
```bash
docker compose down -v
docker compose up -d
```

### Scraper not collecting data

**Check scraper logs:**
```bash
docker compose logs -f scraper
```

**Common issues:**
- Anti-bot detection → Add residential proxies to `PROXY_LIST`
- Website structure changed → Update selectors in scraper files
- Network issues → Check VPS connectivity

### Curation not working

**Verify Gemini API key:**
```bash
docker compose exec scraper python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Check curation logs:**
```bash
docker compose logs -f scraper | grep -i curation
```

**Manually trigger curation:**
```bash
curl -X POST "http://localhost:8000/curation/trigger"
```

### Playwright browser crashes

**Increase container memory:**
Edit `docker-compose.yml` and add:
```yaml
scraper:
  deploy:
    resources:
      limits:
        memory: 2G
```

## 📊 Monitoring

### View container stats
```bash
docker compose stats
```

### Check database size
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "
SELECT 
    pg_size_pretty(pg_database_size('scraper_db')) as db_size,
    (SELECT count(*) FROM listings) as total_listings,
    (SELECT count(*) FROM listings WHERE curated = true) as curated_listings;
"
```

### View recent listings
```bash
docker compose exec postgres psql -U scraper_user -d scraper_db -c "
SELECT id, source, title, city, price, scraped_at 
FROM listings 
ORDER BY scraped_at DESC 
LIMIT 10;
"
```

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- Use **strong passwords** for PostgreSQL
- Rotate **API keys** regularly
- Use **residential proxies** to avoid IP bans
- Enable **firewall** on VPS (see DEPLOYMENT.md)
- Keep **Docker images updated**

## 📚 Additional Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - VPS deployment guide
- [API.md](API.md) - Detailed API documentation
- [property-scraper-prd.md](property-scraper-prd.md) - Product requirements document

## 🤝 Contributing

1. Follow existing code structure
2. Add new scrapers by extending `BaseScraper`
3. Test locally before deploying
4. Update documentation for new features

## 📝 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Check troubleshooting section above
- Review logs: `docker compose logs -f`
- Consult PRD document for architecture details
