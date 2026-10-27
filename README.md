# NyariKontrakan

NyariKontrakan is an Indonesian **kontrakan** (rental house) listing site. Listings are scraped from
OLX and Rumah123, curated with Google Gemini, stored in PostgreSQL, served by a FastAPI read API, and
rendered by a statically exported Next.js site.

- **Automated scraping** — Playwright + BeautifulSoup workers for OLX and Rumah123 on a daily cron,
  with optional residential proxies and stealth helpers.
- **LLM curation** — `gemini-2.5-flash` assigns a quality score, tags, an Indonesian summary, and
  normalized attributes (bedrooms, bathrooms, areas, furnishing, condition).
- **REST API** — FastAPI listing endpoints plus a curation trigger, with API-key auth, a CORS
  allow-list, rate limiting, and security headers.
- **SEO-ready frontend** — Next.js App Router static export, MUI 9 theme, sitemap/robots/manifest, and
  a mock-data fallback when the API is unreachable.

> This README is the human entry point. Canonical rules live in `.agents/` and project documents in
> `.agents/docs/` — see [Documentation](#documentation) for the full index.

## Architecture

```
┌─ Docker Compose network ──────────────────────────────────────────────────────┐
│                                                                               │
│  scraper   Playwright workers for OLX and Rumah123, APScheduler cron,         │
│            Gemini curation batch                                              │
│                                                                               │
│            │  upsert via ScraperService.save_listings()                       │
│            ▼                                                                  │
│  postgres  PostgreSQL 16, single `listings` table, 8 indexes                  │
│                                                                               │
│            │  asyncpg via SQLAlchemy 2 async sessions                         │
│            ▼                                                                  │
│  api       FastAPI on :8000, listing reads plus curation trigger,             │
│            CORS allow-list, rate limiting, security headers                   │
│                                                                               │
└────────────┬──────────────────────────────────────────────────────────────────┘
             │
             │  JSON over HTTP
             ▼
             frontend  Next.js 16 static export on Netlify
                       services/api.ts → app/page.tsx
                       mock listings when the API fails or is empty
```

Data flow: `scraper/scheduler.py` cron → `ScraperService.save_listings()` upsert → `listings` table →
`GET /listings` → `frontend/services/api.ts` → `frontend/app/page.tsx` (falls back to
`frontend/data/properties.ts` when the API errors or returns nothing).

## Tech stack

| Layer | Stack |
| --- | --- |
| API | Python 3.12, FastAPI, SQLAlchemy 2 (async), asyncpg, slowapi |
| Scraper | Playwright + Chromium, BeautifulSoup, APScheduler, httpx |
| Curation | Google Gemini `gemini-2.5-flash` |
| Database | PostgreSQL 16, one `listings` table |
| Frontend | Next.js 16 (App Router, static export), React 19, MUI 9 + Emotion, TypeScript strict |
| Deployment | Docker Compose + Nginx on the backend, Netlify for the frontend |

## Repository layout

```
nyari-kontrakan/
├── backend/                 FastAPI API, scraper worker, curation, shared models
│   ├── api/                 app wiring, routers, auth, background curation task
│   ├── scraper/             scheduler, platform scrapers, job workers
│   ├── curation/            Gemini client, prompts, curation service
│   ├── config/ models/      settings singleton, SQLAlchemy model
│   ├── schemas/ services/   Pydantic response models, read/scrape services
│   ├── utils/               validators, price/location parsers, proxy, stealth
│   ├── database/            async session manager
│   ├── deployment/nginx/    reverse proxy config
│   ├── init.sql             DDL for a fresh Postgres volume
│   └── docker-compose.yml   postgres + api + scraper
├── frontend/                Next.js static-export site
│   ├── app/                 layout, home page, sitemap, robots, manifest
│   ├── components/          Navbar, FilterBar, PropertyCard, dialogs, Footer
│   ├── services/api.ts      backend fetch + `BackendListing` → `Property` mapping
│   ├── data/properties.ts   `Property` type + mock fallback listings
│   ├── constants/ theme/    filter vocabulary, API defaults, MUI theme
│   └── utils/format.ts      `formatPrice()` (IDR)
├── .agents/                 agent guides, skills, and project documents
├── netlify.toml             frontend build (base = frontend, publish = out)
└── nyari-kontrakan.code-workspace
```

## Prerequisites

- **Docker** 20.10+ with **Docker Compose** v2 — for the full backend stack.
- **Python 3.12** — only for running the backend outside Docker (match the API image).
- **Node.js 20.9+** — required by Next.js 16.
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com) for curation.
- Optional: a residential **proxy service** (Webshare, Bright Data, Oxylabs) to reduce scraping bans.
- Optional: a domain pointed at your VPS for the production reverse proxy and SSL.

## Quick start

### 1. Backend with Docker (recommended)

```bash
cd backend
cp .env.template .env          # then set POSTGRES_*, GEMINI_API_KEY, API_KEY, ALLOWED_ORIGINS
docker compose up -d --build
docker compose logs -f api scraper postgres

curl localhost:8000/health     # {"status":"ok","database":"healthy"}
```

| Service | Container | Port | Role |
| --- | --- | --- | --- |
| `postgres` | `scraper_postgres` | 5432 (internal) | PostgreSQL 16, seeded from `init.sql` |
| `api` | `scraper_api` | 8000 | FastAPI read API |
| `scraper` | `scraper_worker` | – | APScheduler worker (scrape + curation) |

- Swagger UI is at <http://localhost:8000/docs> and ReDoc at `/redoc` **only** when
  `ENVIRONMENT=development`.
- `SCRAPE_ON_STARTUP=true` makes the worker run one immediate scraping pass instead of waiting for cron.
- `docker compose down` stops the stack; `docker compose down -v` also deletes the Postgres volume and
  all data (the next start re-runs `init.sql`).
- Windows/WSL helpers ship in `backend/`: `setup-docker-wsl.sh` installs Docker Engine in WSL 2 and
  `restart-docker.ps1` restarts Docker Desktop and waits until it is ready.

### 2. Backend with local Python (optional)

Run from `backend/` so the shared packages resolve:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt          # API only
pip install -r scraper/requirements.txt      # scraper, then: playwright install chromium
uvicorn api.main:app --reload --port 8000
python -m scraper.main                       # module form is required for relative imports
```

Start Postgres separately (`docker compose up -d postgres`) or point `DATABASE_URL` at an existing
database.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run lint     # ESLint 9 + eslint-config-next
npm run build    # static export to frontend/out/
```

Create `frontend/.env.local` when you need to override the defaults:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=https://nyarikontrakan.com
```

Both values are inlined at build time, so changing them requires a rebuild. The client sends **no**
`X-API-Key` header: when the backend runs with a non-empty `API_KEY`, requests are rejected and the
page silently falls back to the mock listings. Clear `API_KEY` in `backend/.env` for local UI work
against real data.

## API

All routes require the `X-API-Key` header when `API_KEY` is set, except `/health`, which accepts an
optional key so Docker healthchecks keep working. A missing header returns `401`, a wrong one `403`.

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/listings` | `page` ≥ 1, `limit` 1–100, `city`, `property_type`, `min_price`, `max_price`, `source`, `min_quality` 0–100, `tags` (comma-separated) → `{ total, page, limit, listings[] }` |
| `GET` | `/listings/stats` | Aggregate counts and averages |
| `GET` | `/listings/curated` | Same envelope as `/listings`, curated rows only |
| `GET` | `/listings/{id}` | `404` when the listing is missing |
| `GET` | `/listings/{id}/curation` | Curation fields; `400` when the row is not curated yet |
| `POST` | `/curation/trigger` | Queues a Gemini batch in the background, limited to `5/minute` |
| `GET` | `/health` | `{ status, database }`; never fails on an unhealthy database |

```bash
curl -H "X-API-Key: $API_KEY" "localhost:8000/listings?limit=5&city=Bekasi&min_quality=70"
curl -X POST -H "X-API-Key: $API_KEY" localhost:8000/curation/trigger
```

Bad filter values raise `400` from the controller-level validator; FastAPI type errors are the only
`422`s. Allowed `source` values are `olx` and `rumah123`; allowed `property_type` values are `house`,
`apartment`, `land`, `commercial`, `warehouse`, `office`, `villa`, and `condominium`.

## Environment variables

### Backend (`backend/.env`, template in `backend/.env.template`)

| Variable | Required | Description |
| --- | --- | --- |
| `POSTGRES_DB` | yes | Database name |
| `POSTGRES_USER` | yes | Database user |
| `POSTGRES_PASSWORD` | yes | Database password — use a strong unique value |
| `DATABASE_URL` | no | Full async URL override; otherwise composed from `POSTGRES_*` (compose injects its own) |
| `DATABASE_SSL_MODE` | no | SSL mode passed to asyncpg (template default: `require`) |
| `API_KEY` | no | Enables `X-API-Key` auth when non-empty; leave empty to disable auth |
| `ALLOWED_ORIGINS` | no | Comma-separated CORS origins; empty means no browser origin is allowed |
| `ENVIRONMENT` | no | `development` enables `/docs` and `/redoc` |
| `GEMINI_API_KEY` | yes (curation) | Google Gemini key for the curation service |
| `PROXY_LIST` | no | Comma-separated proxy URLs, validated and rotated by `utils/proxy.py` |
| `CURATION_BATCH_SIZE` | no | Listings curated per run (default `10`) |
| `CURATION_RATE_LIMIT_DELAY` | no | Seconds between Gemini calls (default `1`) |
| `SCRAPE_ON_STARTUP` | no | `true` runs one immediate scrape pass on worker start (default `false`) |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL used by `services/api.ts` |
| `NEXT_PUBLIC_SITE_URL` | `https://nyarikontrakan.com` | Canonical URL for metadata, `sitemap.ts`, and `robots.ts` |

Never commit `.env` or `.env.local`; both are git-ignored. Add new backend variables to
`backend/.env.template` and to `.agents/backend.md` in the same change.

## Data model

A single `listings` table (`init.sql`, mirrored by `models/listing.py`) holds scraped and curated data:

- Scraped: `source`, `external_id`, `title`, `price` (BIGINT rupiah), `location`, `city`,
  `property_type`, `bedrooms`, `bathrooms`, `land_area_sqm`, `building_area_sqm`, `url`,
  `photos` (TEXT[]), `raw_data` (JSONB), `scraped_at`, `updated_at`.
- Curated: `curated`, `quality_score`, `tags` (TEXT[]), `summary`, `normalized_data` (JSONB),
  `curation_model`, `curated_at`.

Upserts key on `external_id` alone, so scraper IDs are namespaced per platform (`olx…`, `r123…`).
There is no migration tool: `init.sql` only runs on a fresh volume, so after DDL changes run
`docker compose down -v && docker compose up -d --build` locally and apply the SQL manually on existing
deployments. Surface changes touch `backend/init.sql`, `backend/models/listing.py`, and
`backend/schemas/listing_schema.py` together.

## Cron schedule

Registered once in `scraper/scheduler.py`, in the host's local time:

| Time | Job |
| --- | --- |
| 00:00 | OLX scrape |
| 01:00 | Rumah123 scrape |
| 03:00 | Gemini curation batch |

## Deployment

- **Frontend** — Netlify builds from the root `netlify.toml`: `base = "frontend"`,
  `command = "npm run build"`, `publish = "out"`. Because the site is a static export there are no API
  routes, route handlers, server actions, or request-time rendering; everything dynamic runs in the
  browser.
- **Backend** — Docker Compose behind the Nginx reverse proxy config in `backend/deployment/nginx/`
  (reverse proxy + SSL termination). Terminate TLS at Nginx and keep `ALLOWED_ORIGINS` set to the real
  frontend origin.
- Set `DATABASE_SSL_MODE`, `API_KEY`, and `ALLOWED_ORIGINS` per environment; never reuse development
  secrets in production.

## Documentation

Canonical project documents live in `.agents/docs/`:

| Document | Covers |
| --- | --- |
| [`.agents/docs/backend/README.md`](.agents/docs/backend/README.md) | Backend setup, architecture, usage, troubleshooting |
| [`.agents/docs/backend/property-scraper-prd.md`](.agents/docs/backend/property-scraper-prd.md) | Product requirements and data model |
| [`.agents/docs/backend/ARCHITECTURE_PLAN.md`](.agents/docs/backend/ARCHITECTURE_PLAN.md) | Layered architecture and migration plan |
| [`.agents/docs/backend/SECURITY.md`](.agents/docs/backend/SECURITY.md) | Security hardening |
| [`.agents/docs/backend/SECURITY_IMPLEMENTATION_SUMMARY.md`](.agents/docs/backend/SECURITY_IMPLEMENTATION_SUMMARY.md) | Security change log |
| [`.agents/docs/backend/IMPLEMENTATION_SUMMARY.md`](.agents/docs/backend/IMPLEMENTATION_SUMMARY.md) | Implementation notes |
| [`.agents/docs/frontend/README.md`](.agents/docs/frontend/README.md) | Next.js app structure and usage |
| [`.agents/docs/frontend/seo.md`](.agents/docs/frontend/seo.md) | SEO and metadata strategy |

Agent-facing guidance (rules, contracts, workflows) lives in `.agents/`:

| File | Scope |
| --- | --- |
| [`.agents/AGENTS.md`](.agents/AGENTS.md) | Repo map, data flow, cross-app contracts, shared rules |
| [`.agents/backend.md`](.agents/backend.md) | Everything under `backend/` |
| [`.agents/frontend.md`](.agents/frontend.md) | Everything under `frontend/` |
| [`.agents/skills/backend/SKILL.md`](.agents/skills/backend/SKILL.md) | Backend task workflow |
| [`.agents/skills/frontend/SKILL.md`](.agents/skills/frontend/SKILL.md) | Frontend task workflow |

## Verification

There are no automated test suites in either app; verify changes as follows.

Backend:

```bash
cd backend && docker compose up -d --build
curl localhost:8000/health                                           # database: healthy
curl -H "X-API-Key: $API_KEY" "localhost:8000/listings?limit=1"      # { total, page, limit, listings }
```

- Endpoint changes: exercise filters, pagination bounds (`400`), unknown IDs (`404`), and auth codes
  (`401`/`403`).
- Schema changes: `docker compose down -v && docker compose up -d --build`, then re-check `/listings`.
- Scraper changes: `SCRAPE_ON_STARTUP=true docker compose up -d --build scraper` and
  `docker compose logs -f scraper`.
- Curation changes: `curl -X POST -H "X-API-Key: $API_KEY" localhost:8000/curation/trigger`, then
  confirm rows flip to `curated=true` with `quality_score` and `tags` populated.

Frontend:

```bash
cd frontend && npm run lint && npm run build    # build must emit out/
```

Also load `npm run dev`, confirm listings or the mock fallback render, filters and dialogs work, and
there are no console or hydration errors.

## Contributing

- Keep diffs scoped: no drive-by reformatting and no new dependencies when the existing stack covers
  the need.
- Read the area guide before editing: `.agents/backend.md` or `.agents/frontend.md`, plus the matching
  skill workflow.
- Update the relevant documents in `.agents/docs/` in the same change as the behavior.
- Never commit `.env` files, API keys, or proxy credentials.

## License

No license file is included yet. Add a `LICENSE` before distributing the code.
