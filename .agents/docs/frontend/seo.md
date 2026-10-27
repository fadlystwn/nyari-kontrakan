# NyariKontrakan SEO Configuration & Documentation

This document outlines the SEO implementation, practices, and configurations applied to the NyariKontrakan frontend web application to optimize search engine ranking and crawlability.

## Implemented SEO Features

### 1. Enhanced Global Metadata
Configured in `app/layout.tsx` to handle search engine previews and sharing cards across platforms:
- **Canonical Alternates**: Sets canonical tags (`alternates.canonical`) to `/` to avoid duplicate content penalties.
- **OpenGraph (OG)**: Customized fields for Facebook, LinkedIn, etc., including title, description, URL, and website type.
- **Twitter Cards**: Configured using `summary_large_image` to generate elegant Twitter preview cards.
- **Bot-specific rules**: Explicit rules for `googleBot` (`max-image-preview: "large"`, etc.) ensuring search engines present media rich previews.
- **Theme Color & Viewport**: Configured standard theme color `#6750A4` matching the Material Design 3 theme palette.

### 2. Robots Guidelines (`robots.txt`)
Dynamically generated via [robots.ts](../../../frontend/app/robots.ts):
- Allows all search bots (`*`) to access the home and property pages.
- Disallows search crawlers from entering backend API paths (`/api/`) and build bundles (`/_next/`).
- Points search crawlers directly to the sitemap XML URL.

### 3. XML Sitemap Generation (`sitemap.xml`)
Dynamically generated via [sitemap.ts](../../../frontend/app/sitemap.ts):
- Declares the home route with high priority (`1.0`) and daily update check intervals.
- Includes boilerplate structure and comments for indexing dynamic property listing detail pages when dynamic routes are introduced.

### 4. Web Manifest (`manifest.json`)
Dynamically generated via [manifest.ts](../../../frontend/app/manifest.ts):
- Provides app name, description, stand-alone display configuration, icons, and theme colors to support PWA capabilities and mobile-optimized search engines.

### 5. Semantic HTML & Landmark Roles
Refactored inside [page.tsx](../../../frontend/app/page.tsx):
- Changed primary container wrapping main sections to render as `<main>` landmark tag using MUI container's `component="main"`.
- Transformed main hero section title to use a single `<h1>` tag per page ("Cari Kontrakan Petakan"), aligning with Google's indexing guidelines.
- Changed the navbar brand logo text to a clean styling `<div>` component instead of `<h1>` to avoid dilution of header levels.
- Applied unique ID selectors (`id="main-page-heading"`, `id="btn-pasang-iklan-nav"`, etc.) to enhance testability.

### 6. Structured Schema Markup (JSON-LD)
Embedded directly inside [page.tsx](../../../frontend/app/page.tsx) to supply Google Rich Snippets with machine-readable data:
- **WebSite Schema**: Outlines site details, URL, and name.
- **RealEstateAgent Schema**: Identifies NyariKontrakan as a real estate discovery tool.
- **ItemList Schema**: Dynamically maps available property cards, including property names, locations, cities, and prices, directly into the document so Google understands the data stream before rendering client scripts.

---

## Modifying & Extending SEO

### Changing Global Meta Info
Edit the `metadata` object inside [layout.tsx](../../../frontend/app/layout.tsx):
```typescript
export const metadata: Metadata = {
  title: {
    default: "Your Title here",
    template: "%s | NyariKontrakan"
  },
  description: "Your meta description...",
  // ...
};
```

### Adding New Page Paths to Sitemap
When a new static page (e.g. `/tentang` or `/hubungi`) is added, update the `routes` array in [sitemap.ts](../../../frontend/app/sitemap.ts):
```typescript
const routes = [
  {
    url: siteUrl,
    lastModified: new Date(),
    changeFrequency: "daily" as const,
    priority: 1.0,
  },
  {
    url: `${siteUrl}/tentang`,
    lastModified: new Date(),
    changeFrequency: "monthly" as const,
    priority: 0.5,
  },
];
```

### Validator Tools
Use these tools to inspect and test the correctness of SEO adjustments:
1. **Google Rich Results Test**: Verify the JSON-LD schema validity.
2. **Schema.org Validator**: Ensure standard property semantic mappings match accommodation schemas.
3. **Lighthouse / Web Dev Tools**: Run audits to measure SEO score metrics (should be close to 100).
