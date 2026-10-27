# AGENTS.md — repository-wide

Guidance for AI coding agents (Cline, Claude Code, Codex, Copilot, Cursor). Every authoritative agent
document lives in `.agents/`.

## 1. Single source of truth

| Scope | Authoritative file | Owns |
| --- | --- | --- |
| Whole repo | `.agents/AGENTS.md` (this file) | Project map, data flow, cross-app contracts, shared rules |
| Backend | `.agents/backend.md` | Everything under `backend/` — commands, API, schema, scrapers, curation, env, security |
| Frontend | `.agents/frontend.md` | Everything under `frontend/` — commands, UI conventions, theme, SEO, env |

Rules live in exactly one place. Do not copy content between these files, into the pointer files
(`AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`, any `CLAUDE.md`), or into `.clinerules/` —
link to the owning file instead. Those files exist only for tool discovery; `frontend/AGENTS.md` also
hosts the Next.js-managed block.

Task workflows live in `.agents/skills/<area>/SKILL.md` (Agent Skills format: `name` + `description`
frontmatter, body = procedure). A skill sequences the work, names the files a change must touch, and
links back here for every rule, so skills never become a second source of truth.

### Documents

Project documentation lives in `.agents/docs/`; outside `.agents/` and `.clinerules/` the tree holds
code, config, and the discovery pointers only. The root [`README.md`](../README.md) is the human entry
point: it summarizes setup and links into these documents without owning any rules.

| Document | Covers |
| --- | --- |
| [`docs/backend/README.md`](docs/backend/README.md) | Backend setup, architecture diagram, usage, troubleshooting |
| [`docs/backend/property-scraper-prd.md`](docs/backend/property-scraper-prd.md) | Product requirements and data model |
| [`docs/backend/ARCHITECTURE_PLAN.md`](docs/backend/ARCHITECTURE_PLAN.md) | Layered architecture and migration plan |
| [`docs/backend/SECURITY.md`](docs/backend/SECURITY.md) | Security hardening |
| [`docs/backend/SECURITY_IMPLEMENTATION_SUMMARY.md`](docs/backend/SECURITY_IMPLEMENTATION_SUMMARY.md) | Security change log |
| [`docs/backend/IMPLEMENTATION_SUMMARY.md`](docs/backend/IMPLEMENTATION_SUMMARY.md) | Implementation notes |
| [`docs/frontend/README.md`](docs/frontend/README.md) | Next.js app structure and usage |
| [`docs/frontend/seo.md`](docs/frontend/seo.md) | SEO and metadata strategy |

## 2. Project

NyariKontrakan is an Indonesian "kontrakan" (rental) listing site. Scraped listings are stored and
curated in PostgreSQL, served by a FastAPI read API, and rendered by a statically exported Next.js site.

| Path | Stack |
| --- | --- |
| `backend/api/` | FastAPI, SQLAlchemy 2 (async), asyncpg, slowapi |
| `backend/scraper/` | Playwright, BeautifulSoup, APScheduler |
| `backend/curation/` | Google Gemini (`gemini-2.5-flash`) |
| `backend/` (shared) | `config/`, `models/`, `schemas/`, `services/`, `utils/` |
| `frontend/` | Next.js 16 App Router, React 19, MUI 9 + Emotion, TypeScript strict (static export) |
| Database | PostgreSQL 16, single `listings` table |

Data flow: `scraper/scheduler.py` cron → `ScraperService.save_listings()` upsert → `listings` table →
`GET /listings` → `frontend/services/api.ts` → `frontend/app/page.tsx` (falls back to mock data in
`frontend/data/properties.ts` when the API errors or returns nothing).

## 3. Route your task

| If you are changing… | Rules | Workflow |
| --- | --- | --- |
| API endpoints, database schema, auth, scrapers, curation, Docker or backend env | [`backend.md`](backend.md) | [`skills/backend/SKILL.md`](skills/backend/SKILL.md) |
| Pages, components, MUI theme, SEO/metadata, Netlify build | [`frontend.md`](frontend.md) | [`skills/frontend/SKILL.md`](skills/frontend/SKILL.md) |
| Commands or verification steps | the "Commands" and "Verify" sections of the owning area file | the skill's definition of done |

## 4. Cross-app contracts (owned by this section)

1. **Listing shape** — `backend/init.sql`, `backend/models/listing.py`, and
   `backend/schemas/listing_schema.py` must change together. Details and commands: `backend.md`.
2. **API → client** — `frontend/services/api.ts` consumes `{ listings: [...] }`, where each item has
   `id`, `title`, `location`, `city`, `price`, `tags`, `photos`, and maps it to `Property`.
   Renaming those fields breaks the UI silently because the page falls back to mock data. The full
   endpoint list lives in `backend.md`.
3. **Auth boundary** — when `API_KEY` is set, backend routes require `X-API-Key`; the frontend sends
   no such header. Both sides document the consequence; do not "fix" one without the other.
4. **Environment** — backend variables are documented in `backend.md` and `backend/.env.template`;
   frontend variables in `frontend.md`. A new variable is added to its owner's section (and
   `.env.template` for backend) in the same change.
5. **Filter vocabulary** — backend allow-lists (`source`, `property_type`) are owned by
   `backend/utils/validators.py`; UI filter options by `frontend/constants/index.ts`. Keep them aligned
   when adding a platform or a filter.

## 5. Shared rules (apply everywhere)

- Never commit `.env`, API keys, or proxy credentials; update `backend/.env.template` instead.
- Keep diffs scoped: no drive-by reformatting or refactors, and no new dependencies when the existing
  stack already covers the need.
- Update documentation in the same change as the behavior: `.agents/docs/backend/README.md`,
  `.agents/docs/backend/property-scraper-prd.md`, `.agents/docs/backend/SECURITY.md`,
  `.agents/docs/frontend/seo.md`.
- Verify in the area you touched (see that area's "Verify" section) before reporting done.
- If a rule applies to only one side of the repo, put it in that side's guide (`.agents/backend.md` or
  `.agents/frontend.md`) — not here.
