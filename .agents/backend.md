# AGENTS.md — backend

> **Single source of truth for `backend/`.** Repo-wide rules live in [`AGENTS.md`](AGENTS.md). Change
> backend rules only here; the pointer files (`backend/AGENTS.md`, `backend/CLAUDE.md`,
> `.clinerules/backend.md`) never carry copies. The task workflow for backend changes is
> [`skills/backend/SKILL.md`](skills/backend/SKILL.md); project documents live in
> [`docs/backend/`](docs/backend/README.md).

## 1. Commands (from `backend/`)

```bash
cp .env.template .env    # then set POSTGRES_*, GEMINI_API_KEY, API_KEY, ALLOWED_ORIGINS
docker compose up -d --build
docker compose logs -f api scraper postgres
docker compose down      # -v also deletes the postgres volume (all data)
```

Local Python — the API image runs Python 3.12, so match it locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt          # API only
pip install -r scraper/requirements.txt      # scraper (then: playwright install chromium)
uvicorn api.main:app --reload --port 8000    # run from backend/
python -m scraper.main                       # run from backend/; module form is required
```

Swagger UI is served at `http://localhost:8000/docs` only when `ENVIRONMENT=development`; `GET /health`
reports database connectivity. There is no backend test suite or lint config — verify with the Docker
stack and real requests. Keep the code clean for Ruff/Pylance (VS Code formats Python with Ruff).

## 2. Module map

| Path | Responsibility |
| --- | --- |
| `api/main.py` | FastAPI app, CORS, security headers, rate-limiter wiring, router registration, startup table creation |
| `api/controllers/` | Routers: `listing_controller`, `curation_controller`, `health_controller` |
| `api/auth.py` | `verify_api_key` (required) and `verify_api_key_optional` |
| `api/dependencies.py` | `get_db` dependency built on the shared `SessionManager` |
| `api/database.py` | Legacy alias exporting `engine`, `AsyncSessionLocal`, `get_db`; prefer `api/dependencies.py` |
| `api/curation_task.py` | Runs a curation batch from the background task triggered by `POST /curation/trigger` |
| `config/settings.py` | `Settings` with one `@property` per env var and the `settings` singleton |
| `models/listing.py` | SQLAlchemy `Base` + the single `Listing` model (shared by API and worker) |
| `schemas/listing_schema.py` | Pydantic v2 response models (`ListingResponse`, `PaginatedListingsResponse`, `StatsResponse`, `HealthCheckResponse`) |
| `services/listing_service.py` | Read queries + statistics |
| `services/scraper_service.py` | Parses scraper output and upserts into `listings` |
| `services/curation_service.py` | Legacy duplicate of `curation/service.py`; runtime paths import `curation.CurationService` |
| `curation/` | `gemini_client.py` (HTTP client), `prompts.py` (JSON contract), `service.py` |
| `scraper/main.py` | Worker daemon: DB retry/init, APScheduler, optional startup run |
| `scraper/scheduler.py` | Cron jobs: OLX 00:00, Rumah123 01:00, curation 03:00 |
| `scraper/scrapers/` | `base.py` contract, `olx_scraper.py`, `rumah123_scraper.py` |
| `scraper/workers/` | Job entry points that own their `SessionManager` |
| `utils/` | `validators.py` (input sanitation/allow-lists), `parsers.py` (`Price`, `Location`), `proxy.py`, `stealth.py` |
| `init.sql` | DDL for a fresh Postgres volume (tables + indexes) |
| `docker-compose.yml`, `deployment/nginx/` | Runtime topology and reverse proxy config |

## 3. Import and run model

- The Docker images copy `backend/` to `/app`, so shared packages are imported as top-level modules
  (`from models import Listing`, `from services import ListingService`, `from config import settings`).
  Every entry point and some modules append `BACKEND_DIR` to `sys.path` before importing them — keep
  that bootstrap when adding modules that are executed as entry points or imported by both apps.
- Inside the `scraper` package use relative imports (`from ..scrapers.olx_scraper import OLXScraper`).
  Follow the surrounding file's existing import style instead of converting it.
- Run from `backend/`: `uvicorn api.main:app --reload --port 8000` and `python -m scraper.main`.
  Never run `python scraper/main.py` or `python scraper/workers/scraper_worker.py` directly — their
  relative imports fail outside module form.

## 4. API conventions

- One router per resource: `APIRouter(prefix="/x", tags=["x"], dependencies=[Depends(verify_api_key)])`,
  registered in `api/main.py`. Add rate limits to trigger/expensive endpoints with `@limiter.limit(...)`
  and keep the `request` parameter in the handler (`slowapi` requires it).
- Always obtain sessions through the `get_db` dependency (`api/dependencies.py`); never create an
  engine or session per request.
- Responses use the Pydantic v2 models in `schemas/listing_schema.py` through `response_model=`
  (`ConfigDict(from_attributes=True)`). Listing payloads are never ad-hoc dicts; small one-off dicts
  (e.g. `/listings/{id}/curation`) are the existing exception.
- Keep the module docstring, `logger = logging.getLogger(__name__)`, and `sys.path` bootstrap that every
  controller already has.

Surface (all routes require `X-API-Key` except `/health`, which uses `verify_api_key_optional` so Docker
healthchecks work):

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/listings` | `page` ≥1, `limit` 1–100, `city`, `property_type`, `min_price`, `max_price`, `source`, `min_quality` 0–100, `tags` (comma-separated) → `{ total, page, limit, listings[] }` |
| GET | `/listings/stats` | aggregate counts and averages |
| GET | `/listings/curated` | same envelope, curated rows only |
| GET | `/listings/{id}` | `404` when missing |
| GET | `/listings/{id}/curation` | curation fields; `400` when the row is not curated yet |
| POST | `/curation/trigger` | queues a Gemini batch in the background, limited to `5/minute` |
| GET | `/health` | `{ status, database }`, never fails on an unhealthy database |

- Validation lives in the controller via `InputValidator`; invalid values raise
  `HTTPException(status_code=400)` — FastAPI type errors are the only `422`s.
- Allow-lists in `utils/validators.py`: `source` ∈ `olx`, `rumah123`; `property_type` ∈ `house`,
  `apartment`, `land`, `commercial`, `warehouse`, `office`, `villa`, `condominium`. Any new platform or
  property type must update this validator and `frontend/constants/index.ts` together (contract #5 in
  `AGENTS.md`).
- `/health` and `/docs` behaviour is controlled by `ENVIRONMENT`; docs are only enabled when it is
  `development`.

## 5. Database conventions

- `Listing` (`models/listing.py`) is the only model, shared by the API and the worker through one `Base`.
- Schema changes touch `models/listing.py` **and** `init.sql` (DDL + indexes). Startup calls
  `Base.metadata.create_all`, which only creates missing tables — it never alters existing ones.
- `SessionManager` (`database/session.py`) owns the async engine and `async_sessionmaker`; `get_db`
  yields one session per request, commits on success, rolls back on exception, then closes. Prefer
  `flush()`/`add()`/`setattr` and let the context manager commit; `CurationService` is the documented
  exception (it commits per listing so one bad row cannot abort the batch).
- `init.sql` only runs on a fresh Postgres volume. After DDL changes run
  `docker compose down -v && docker compose up -d --build` locally; existing deployments need the SQL
  applied manually because there is no migration tool.
- Upserts key on `listings.external_id` **alone**, so scraper IDs must be namespaced (`olx…`, `r123…`);
  an un-namespaced ID silently overwrites another source's row.
- `tags` and `photos` are `ARRAY(Text)`, `raw_data`/`normalized_data` are `JSONB`, prices are `BIGINT`
  rupiah, and timestamps use server-side defaults (`func.now()`).

## 6. Scrapers

- Each platform subclasses `BaseScraper` (`scraper/scrapers/base.py`): set `source`, implement
  `fetch_listings()` (raw dicts with at least `external_id`, `title`, `url`) and `parse_listing(raw)`
  (the normalized fields are listed in the base docstring).
- Namespace `external_id` per platform — it is the upsert key — and always return absolute detail URLs.
- Use one `async with async_playwright()` block per run and always close browser/context; reuse the
  helpers in `utils/stealth.py` and rotate proxies from `settings.proxy_list` via `utils/proxy.py`.
- Parse money and locations with `utils/parsers.py` (`Price`, `Location`) and validate with
  `InputValidator` instead of adding ad-hoc regexes.
- Log through the module logger and never let one bad listing abort a batch — skip it and continue.
- Jobs live in `scraper/workers/` and each owns its `SessionManager`; cron entries are registered once in
  `scraper/scheduler.py` (OLX 00:00, Rumah123 01:00, curation 03:00, host local time). Add new jobs there.
- `scraper/main.py` retries the database connection, initializes the schema, then starts
  `AsyncIOScheduler`; `SCRAPE_ON_STARTUP=true` runs one immediate pass (read with `os.getenv`).

## 7. Curation

- The runtime implementation is `curation/service.py`, imported by `api/curation_task.py` and
  `scraper/workers/curation_worker.py` (`from curation import CurationService`).
  `services/curation_service.py` is a near-duplicate that is only re-exported by `services/__init__.py`;
  edit the runtime file and keep the duplicate in sync (or remove it once nothing imports
  `services.CurationService`).
- `CurationService.curate_batch()` selects uncurated listings newest-first (`scraped_at DESC`), calls the
  model one listing at a time with `CURATION_RATE_LIMIT_DELAY` seconds between calls, up to
  `CURATION_BATCH_SIZE` per run.
- `curation/gemini_client.py` calls `gemini-2.5-flash` with `GEMINI_API_KEY`; `curation/prompts.py`
  demands JSON only: `quality_score` (0–100), `tags` (≤8), `summary` (Indonesian, 2–3 sentences),
  `normalized` (`bedrooms`, `bathrooms`, `land_area_sqm`, `building_area_sqm`, `furnishing`, `condition`),
  and `is_duplicate_candidate`.
- Persist `curated=true`, `quality_score`, `tags`, `summary`, `normalized_data`, `curation_model`, and
  `curated_at=func.now()`. Keep response parsing defensive (strip code fences, tolerate missing keys).
- Triggers are the 03:00 cron job and `POST /curation/trigger` (background task in
  `api/curation_task.py`). Never call Gemini synchronously inside a request handler.

## 8. Environment, security, operations

- Read configuration through `settings` properties (`config/settings.py`), not scattered `os.getenv`.
  `SCRAPE_ON_STARTUP` in `scraper/main.py` is the existing startup-only exception.
- Variables (template in `.env.template`): `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `DATABASE_URL` (optional full override; otherwise composed from the `POSTGRES_*` values against
  `localhost:5432`), `DATABASE_SSL_MODE`, `API_KEY`, `ALLOWED_ORIGINS`, `ENVIRONMENT`, `PROXY_LIST`,
  `GEMINI_API_KEY`, `CURATION_BATCH_SIZE`, `CURATION_RATE_LIMIT_DELAY`. Compose injects `DATABASE_URL`
  for the containers, so the composed fallback only applies to local runs.
- Auth: `verify_api_key` compares `X-API-Key` against `API_KEY` — `401` when the header is missing, `403`
  when it is wrong, and no auth at all when `API_KEY` is empty.
- CORS: `ALLOWED_ORIGINS` is a comma-separated list; unset means empty, so no browser origin is allowed.
  Configure origins in `.env`, never in code.
- Never log secrets, API keys, proxy credentials, or full Gemini responses.
- Scraping and curation need outbound network access and a valid `GEMINI_API_KEY`; the scraper image ships
  Playwright + Chromium, the API image does not (so Playwright code cannot run there).

## 9. Verify

1. `docker compose up -d --build`, then `curl localhost:8000/health` → `"database": "healthy"`.
2. `curl -H "X-API-Key: $API_KEY" "localhost:8000/listings?limit=1"` (drop the header when `API_KEY` is
   empty) and confirm the `{ total, page, limit, listings }` envelope.
3. Endpoint change → exercise filters and pagination bounds (`400`), unknown IDs (`404`), and the auth
   codes (`401`/`403`).
4. Schema change → `docker compose down -v && docker compose up -d --build`, then confirm the new
   columns/indexes and that `/listings` still returns rows.
5. Scraper change → `SCRAPE_ON_STARTUP=true docker compose up -d --build scraper`, then
   `docker compose logs -f scraper` for per-listing errors and row counts.
6. Curation change → `curl -X POST -H "X-API-Key: $API_KEY" localhost:8000/curation/trigger`, watch the
   logs, and confirm rows flip to `curated=true` with `quality_score`/`tags` populated.
