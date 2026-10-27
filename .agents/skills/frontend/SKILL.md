---
name: frontend
description: Use when editing anything under frontend/ — Next.js App Router pages, MUI components or theme tokens, SEO metadata routes, mock data, or the static-export build. Enforces the export constraints, sequences the work, and defers all rules to .agents/frontend.md.
---

# Frontend skill

`.agents/frontend.md` is the single source of truth for frontend rules, `.agents/AGENTS.md` §4 owns
the cross-app contracts, and the Next.js-managed block in `frontend/AGENTS.md` must be read before
using any Next.js API. This skill only orders the work and names the files a change must touch.

## Before you start

- Read `.agents/frontend.md` and the managed block at the top of `frontend/AGENTS.md`.
- After `npm install`, check `frontend/node_modules/next/dist/docs/` for the API you plan to use —
  this is Next.js 16, not the version in your training data.
- `git status` — leave unrelated working-tree edits untouched.

## Workflow: section, page, or component

1. Component as its own file in `frontend/components/` with a PascalCase default export; compose
   page sections in `frontend/app/page.tsx`.
2. Build with `@mui/material` primitives and tokens from `frontend/theme/theme.ts` (styling rules:
   `.agents/frontend.md` §4).
3. Keep `'use client'` as low as possible; `app/layout.tsx` and the metadata routes stay
   server-side.
4. Components take props: `getProperties()` in `frontend/services/api.ts` is called by the page
   only.
5. Prices go through `formatPrice()` (`frontend/utils/format.ts`); images through `next/image`.
6. Verify with `.agents/frontend.md` §6 steps 1–3.

## Workflow: theme or visual change

1. Change tokens or component overrides in `frontend/theme/theme.ts`, never literals in components.
2. Re-check both `Grid` breakpoints (mobile and desktop) and the dialog states.
3. Verify with `.agents/frontend.md` §6 steps 1–3.

## Workflow: SEO, metadata, or manifest

1. Site metadata in `frontend/app/layout.tsx`; `frontend/app/sitemap.ts`, `robots.ts`, and
   `manifest.ts` are static metadata routes (`dynamic = "force-static"`) — keep them request-free.
2. The canonical host comes from `NEXT_PUBLIC_SITE_URL`; do not hardcode a domain.
3. JSON-LD structured data lives in `frontend/app/page.tsx`; keep it consistent with the visible
   page.
4. Update `.agents/docs/frontend/seo.md` when the strategy changes, then run `.agents/frontend.md` §6
   step 4.

## Workflow: API field or endpoint change

1. Confirm the backend change in `.agents/backend.md`; update `.agents/AGENTS.md` contract #2 if the
   payload shape moves.
2. Touch the `BackendListing` mapping in `frontend/services/api.ts`, the `Property` interface and
   mock rows in `frontend/data/properties.ts`, and every consuming component together.
3. Run with the backend up: `getProperties()` swallows failures into `mockProperties`, so a broken
   mapping looks like stale content rather than an error.
4. Verify with `.agents/frontend.md` §6 steps 1–3.

## Guardrails that bite in this repo

- `output: "export"`: route handlers, server actions, middleware, `cookies()`/`headers()`, and
  request-time fetching break the build, not the dev server.
- `NEXT_PUBLIC_*` values are inlined at build time — changing one requires a rebuild.
- The client never sends `X-API-Key`; a failing request silently degrades to mock data.
- New dependencies need a reason; MUI, Emotion, and `fetch` already cover the stack.

## Definition of done

- [ ] Change follows `.agents/frontend.md`; no rules copied into `frontend/AGENTS.md`.
- [ ] `npm run lint` and `npm run build` both pass; `out/` is produced.
- [ ] `.agents/docs/frontend/seo.md` updated if metadata or SEO behavior changed.
