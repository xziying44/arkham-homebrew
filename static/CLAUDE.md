# Static Directory Documentation

## Purpose
- Provide production-ready static resources (versioned JS/CSS bundles, fonts, images) built by the frontend toolchain and served by the backend.
- Act as the single-layer overview aggregating child docs (notably `assets/CLAUDE.md`) and the current directory layout for quick onboarding.
- Ensure consistent guidance on naming, placement, caching, and integration with the web server (Flask per child doc).

## Structure
```
static/
├── assets/                     # Built bundles, fonts, images (versioned)
│   └── CLAUDE.md              # Detailed assets documentation
├── index.html                 # HTML entry (references versioned assets)
└── favicon.ico                # Site favicon
```
- Assets filenames follow `[name]-[contenthash].[ext]` for cache-busting.
- Browser loads from `/static/` with versioned paths under `/static/assets/`.

## Components
- JavaScript bundle(s): `index-[hash].js`
  - Compiled Vue 3 + TypeScript application code and component library code.
  - Built by Vite; intended for production delivery.

- Stylesheets: `index-[hash].css`
  - Global styles including Naive UI and app-specific CSS.

- Images: `encounter-back-[hash].jpg`, `player-back-[hash].jpg`
  - Card-back assets optimized for web display.

- Fonts: `FiraCode-Regular-[hash].woff2`, `LatoLatin-*- [hash].woff2`
  - WOFF2 format for efficient delivery; used for UI and code-like text.

- HTML entry: `index.html`
  - References the versioned assets emitted by the build.

- Favicon: `favicon.ico`
  - Site icon served from the static root.

## Dependencies
- Internal
  - Frontend source (built by Vite) → outputs to `static/assets/`.
  - Build configuration (Vite) controls hashing, output paths, and CSS processing.

- External
  - Vue 3, Naive UI, TypeScript, Vite toolchain.
  - Font assets (WOFF2) from trusted sources.

## Integration
- Serving
  - Served via Flask static file routing; browser requests under `/static/assets/`.
  - Correct MIME types and cache headers must be configured by the server.

- Caching
  - Long-term caching recommended for versioned assets; hashes change on content changes.
  - CDN-compatible; URLs are content-addressed via the hash.

- Load Flow (production)
  1. Flask serves HTML.
  2. HTML references versioned JS/CSS in `/static/assets/`.
  3. Browser downloads assets, executes Vue app, applies styles and fonts.

## Notes
- Naming convention: `[filename]-[contenthash].[ext]` under `static/assets/` only.
- Performance: consider code-splitting for large JS, critical CSS extraction, `font-display` strategies, and modern image formats if appropriate.
- Security: ensure assets originate from trusted build outputs; configure CORS if accessed cross-origin.
- Maintenance: build (Vite) regenerates hashes; no manual renaming required. Rebuild to publish updates.
- For deeper details on asset categories, constraints, and performance/caching rationale, see `assets/CLAUDE.md`.

