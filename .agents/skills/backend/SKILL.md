---
name: backend
description: Use when editing anything under backend/ — FastAPI routes or response models, SQLAlchemy models and init.sql, OLX/Rumah23 scrapers, Gemini curation, Docker Compose, or backend env/security. Sequences the change, names the files it must touch, and defers all rules to .agents/backend.md.
---

# Backend skill

`.agents/backend.md` is the single source of truth for backend rules, and `.agents/AGENTS.md` §4
owns the cross-app contracts. Read both before writing code. This skill only orders the work, names
the files a change must touch, and points at the verification steps.

## Before you start

- Read `.agents/backend.md` end to end.
- `git status` — the working tree often holds unrelated edits; leave them alone.
- Work from `backend/`; run entry points in module form (see `.agents/backend.md` §3).

## Workflow: add or change an endpoint

1. Router in `backend/api/controllers/<resource>_controller.py`, registered in `backend/api/main.py`
   (`include_router`). The router carries `dependencies=[Depends(verify_api_key)]` unless it is a
   probe like `/health`.
2. Queries in `backend/services/listing_service.py`; keep the controller to
   validate → call → return.
3. Response model from `backend/schemas/listing_schema.py` via `response_model=`; the list envelope
   stays `{ total, page, limit, listings }`.
4. Validation through `InputValidator` (`backend/utils/validators.py`); invalid input → `400`.
5. Costly or trigger endpoints also get a `@limiter.limit(...)` (see `.agents/backend.md` §4).
6. If a field or filter becomes visible to the UI, update `.agents/AGENTS.md` contracts #2/#5 plus
   `frontend/services/api.ts` and `frontend/constants/index.ts` in the same change.
7. Verify with `.agents/backend.md` §9 steps 1–3.

## Workflow: schema change

1. Edit `backend/models/listing.py` **and** `backend/init.sql` (column plus any index).
2. Update `backend/schemas/listing_schema.py`; update the mapping in `frontend/services/api.ts` too
   if the field reaches the UI.
3. Grep the writers: `backend/services/scraper_service.py` (upsert) and
   `backend/curation/service.py`.
4. Verify with `.agents/backend.md` §9 step 4 — an existing volume never picks the DDL up.

## Workflow: new scraper source

1. New class in `backend/scraper/scrapers/` subclassing `BaseScraper`: set `source`, implement
   `fetch_listings()` and `parse_listing(raw)`.
2. Namespace `external_id` with a platform prefix — it is the upsert key (`.agents/backend.md` §5).
3. Add a job entry point in `backend/scraper/workers/` (it owns its `SessionManager`), a cron entry
   in `backend/scraper/scheduler.py`, and the platform to the `source` allow-list in
   `backend/utils/validators.py` plus `frontend/constants/index.ts`.
4. Verify with `.agents/backend.md` §9 step 5.

## Workflow: curation

1. Runtime code is `backend/curation/service.py`, `backend/curation/gemini_client.py`, and
   `backend/curation/prompts.py`. `backend/services/curation_service.py` is a legacy duplicate —
   keep it in sync or remove it deliberately (`.agents/backend.md` §7).
2. Changing the prompt means changing the defensive parser in the service in the same edit.
3. Keep curation out of the request path; the triggers are the cron job and
   `POST /curation/trigger`.
4. Verify with `.agents/backend.md` §9 step 6.

## Debugging the stack

- State: `docker compose ps`, then `docker compose logs --tail=100 api scraper postgres`.
- Import or startup failures are usually module-form misuse or a missing `sys.path` bootstrap
  (`.agents/backend.md` §3).
- `401`/`403` means `API_KEY` is set and the request lacks or misstates `X-API-Key`; an empty
  `ALLOWED_ORIGINS` blocks every browser origin (`.agents/backend.md` §8).
- Playwright code fails inside the API image by design — only the scraper image ships it.

## Definition of done

- [ ] Change follows `.agents/backend.md`; no rules copied into the pointer files.
- [ ] Verification steps for the touched area executed, with their output reported.
- [ ] The matching document under `.agents/docs/backend/` (README, PRD, SECURITY) or
      `backend/.env.template` updated if behavior or configuration changed.
