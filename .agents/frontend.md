# AGENTS.md — frontend

> **Single source of truth for `frontend/`.** Repo-wide rules live in [`AGENTS.md`](AGENTS.md) and the
> API/auth contract in [`backend.md`](backend.md). Change frontend rules only here; the pointer files
> (`frontend/AGENTS.md`, `frontend/CLAUDE.md`, `.clinerules/frontend.md`) never carry copies.
>
> The Next.js-managed block (`<!-- BEGIN:nextjs-agent-rules -->`) has to stay in
> `frontend/AGENTS.md` because the framework generates it there — read it together with this file and
> never edit or delete it. The task workflow for frontend changes is
> [`skills/frontend/SKILL.md`](skills/frontend/SKILL.md); project documents live in
> [`docs/frontend/`](docs/frontend/seo.md).

## 1. Commands (from `frontend/`)

```bash
npm install
npm run dev      # http://localhost:3000
npm run lint     # ESLint 9 + eslint-config-next (core-web-vitals, TypeScript)
npm run build    # static export to frontend/out/
```

There is no test runner. Do not introduce one unless the task asks for it.

## 2. Stack and build model

- Next.js **16.2** App Router + React 19, TypeScript strict, MUI **9** with Emotion.
- `next.config.ts` sets `output: "export"` — the site is a **static export** published to Netlify by the
  root `netlify.toml` (`base = "frontend"`, `publish = "out"`). No API routes, route handlers, server
  actions, middleware, `cookies()`/`headers()`, or request-time rendering. Anything dynamic must run in
  the browser.
- One page today: `app/page.tsx` is a client component that fetches listings in `useEffect` and falls
  back to `mockProperties` when the API fails or is empty.

## 3. Layout

| Path | Responsibility |
| --- | --- |
| `app/layout.tsx` | Root layout, Roboto font, `metadata` (title template, OpenGraph, robots, canonical), `viewport` |
| `app/page.tsx` | Home page: data fetch, filters, dialogs, JSON-LD structured data |
| `app/sitemap.ts`, `robots.ts`, `manifest.ts` | SEO/PWA metadata routes (`dynamic = "force-static"`) |
| `components/` | One component per file, PascalCase default export (`Navbar`, `FilterBar`, `PropertyCard`, `PropertyDetailsDialog`, `PostAdDialog`, `EmptyState`, `Footer`) |
| `data/properties.ts` | `Property` interface + mock listings used as the offline/API-failure fallback |
| `services/api.ts` | `getProperties()`: `fetch` the backend and map `BackendListing` → `Property` |
| `constants/index.ts` | Locations, price ranges, facilities, WhatsApp number, `API_LIMIT`, `DEFAULT_API_URL` |
| `theme/theme.ts` | Material 3 theme tokens and MUI component overrides |
| `theme/ThemeRegistry.tsx` | `'use client'` provider wiring `ThemeProvider` + `CssBaseline` |
| `utils/format.ts` | `formatPrice()` (IDR, `id-ID`) |
| `app/globals.css` | Base reset, page background, fade-in animation class only |

## 4. Conventions

- MUI only for UI: `@mui/material` components, layout with `Box`/`Stack`/`Grid`, spacing and one-off
  styling via `sx`. No Tailwind, styled-components, CSS modules, or plain `<div>` layout where MUI has
  a component. `globals.css` stays minimal.
- All visual values (colors, radii, typography, component overrides) come from `theme/theme.ts`. Do not
  hardcode hex colors or font sizes in components — extend the theme instead.
- `'use client'` only where state, effects, or browser APIs are needed (page, `ThemeRegistry`,
  interactive components). Keep `layout.tsx`, `sitemap.ts`, `robots.ts`, `manifest.ts` server-side.
- Repeated or icon-only controls need accessible labels (`aria-label`); preserve MUI's keyboard/focus
  behavior rather than reimplementing it.
- Images use `next/image` with explicit `width`/`height` or `fill` plus a sized container.
- Data flows page → `services/api.ts` → `Property`; components receive props and never fetch the API
  themselves. No data-fetching or global-state library is installed.
- Prices render through `formatPrice()` (`utils/format.ts`), never manual `"Rp "` concatenation.
- When you change `services/api.ts` or `data/properties.ts`, update the `BackendListing` mapping, the
  `Property` interface, and the mock data together (contract #2 in `AGENTS.md`).

## 5. Environment

- `NEXT_PUBLIC_API_URL` — backend base URL; defaults to `DEFAULT_API_URL` (`http://localhost:8000`) in
  `constants/index.ts` when unset.
- `NEXT_PUBLIC_SITE_URL` — canonical site URL; defaults to `https://nyarikontrakan.com` and feeds
  `layout.tsx` metadata, `sitemap.ts`, and `robots.ts`.
- Both are inlined at build time, so changing them requires a rebuild.
- The client sends no `X-API-Key`. With backend auth enabled the request fails and the page silently
  falls back to mock data — see contract #3 in [`AGENTS.md`](AGENTS.md).

## 6. Verify

1. `npm install` once, then `npm run lint`.
2. `npm run dev`: the page renders listings or the mock fallback, filters and dialogs work, and there
   are no console or hydration errors.
3. `npm run build` must succeed and emit `out/` — the static export fails on server-only code.
4. For SEO/metadata changes, inspect the rendered `<head>` plus `out/sitemap.xml` and `out/robots.txt`.
