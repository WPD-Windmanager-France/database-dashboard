# Technology Stack (Unified SvelteKit)

## Core Framework
*   **Framework**: SvelteKit 2.x
*   **Language**: TypeScript 5.x
*   **Styling**: Tailwind CSS
*   **Runtime**: Cloudflare Pages (Workers runtime)

## Authentication & Security
*   **Identity Provider**: Microsoft Entra ID (via Azure App Registration)
*   **Auth Service**: Supabase Auth with Microsoft OAuth provider
*   **Session Management**: `@supabase/ssr` (cookie-based server-side sessions)
*   **Application Auth**: SvelteKit Hook validating Supabase session + `@wpd.fr` domain restriction

## Database & Data
*   **Database**: Supabase (PostgreSQL)
*   **Client**: `@supabase/supabase-js` (Server-side usage)
*   **SQL Logic**: Ported from Evidence.dev queries

## Infrastructure & Deployment
*   **Hosting**: Cloudflare Pages
*   **Adapter**: `@sveltejs/adapter-cloudflare`
*   **CI/CD**: GitHub Actions

## Key Libraries
*   `@supabase/ssr`: Server-side Supabase Auth for SvelteKit
*   `lucide-svelte`: Icons
*   `chart.js` or `layerchart`: Data visualization
*   `zod`: Schema validation for forms and API routes