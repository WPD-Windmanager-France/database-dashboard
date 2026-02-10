# Deployment Guide: Cloudflare Pages + Supabase Auth (Microsoft Entra ID)

## Architecture Overview

```
User  ──>  Cloudflare Pages (SvelteKit SSR)  ──>  Supabase Auth (Microsoft OAuth)
                    │                                        │
              hooks.server.ts                    Supabase Dashboard
              (validates session cookies,         (Azure provider configured
               populates locals.user)              with Entra ID credentials)
                    │
              src/lib/server/supabase.ts
              (data client for PostgreSQL queries)
```

**Auth flow:**
1. User visits `/dashboard` → no session → auto-redirect to Microsoft OAuth
2. User authenticates with Entra ID (transparent if already logged into Microsoft)
3. Supabase receives the OAuth token, creates a session
4. Callback route exchanges code for session cookies
5. `hooks.server.ts` validates session on each request via `@supabase/ssr`

---

## Prerequisites

- A Cloudflare account (free plan works — no Zero Trust needed)
- Access to your organization's Azure portal (Entra ID)
- Supabase project with data already populated
- The GitHub repository connected to Cloudflare Pages

---

## Phase A: Azure - Entra ID App Registration

### A1. Create or update the App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Microsoft Entra ID**
3. Left menu: **App registrations** > find `wm-db-connector` (or create new)

| Field | Value |
|-------|-------|
| Name | `wm-db-connector` |
| Supported account types | **Accounts in this organizational directory only** (single tenant) |

### A2. Note the identifiers

From the App Registration **Overview** page, copy:

| Value | Where to find it |
|-------|--------------------|
| **Application (client) ID** | Overview page |
| **Directory (tenant) ID** | Overview page |

### A3. Create a Client Secret (if not already done)

1. **Certificates & secrets** > **Client secrets** > **+ New client secret**
2. Description: `supabase-auth`
3. Expiry: 12 or 24 months
4. **Copy the Value immediately**

### A4. Add Redirect URI

1. **Authentication** > **Platform configurations** > **Add a platform** > **Web**
2. Add the Supabase callback URL:

```
https://<your-supabase-project-ref>.supabase.co/auth/v1/callback
```

For this project: `https://egmwfzmjkpqjpzlcnqya.supabase.co/auth/v1/callback`

---

## Phase B: Supabase Dashboard - Enable Microsoft Provider

### B1. Navigate to Auth Providers

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. **Authentication** > **Providers** > **Azure (Microsoft)**

### B2. Configure Azure Provider

| Field | Value |
|-------|-------|
| **Enabled** | Toggle ON |
| **Client ID** | Application (client) ID from step A2 |
| **Client Secret** | Client Secret Value from step A3 |
| **Tenant URL** | `https://login.microsoftonline.com/<tenant-id>` |

Replace `<tenant-id>` with the Directory (tenant) ID from step A2.

### B3. Note the Callback URL

Supabase displays the callback URL at the top of the provider config:

```
https://<project-ref>.supabase.co/auth/v1/callback
```

Verify this matches the redirect URI you added in step A4.

### B4. Configure Redirect URLs

Go to **Authentication** > **URL Configuration** and add:

| Field | Value |
|-------|-------|
| **Site URL** | `https://windmanager-fr-dashboard.pages.dev` |
| **Redirect URLs** | `https://windmanager-fr-dashboard.pages.dev/auth/callback` |

If using a custom domain later, add that too.

---

## Phase C: Cloudflare Pages (Deploy the Site)

### C1. Create the Pages project

1. Go to **Cloudflare Dashboard** > **Workers & Pages** > **Create**
2. Select **Pages** > **Connect to Git**
3. Select the repository
4. Configure build settings:

| Setting | Value |
|---------|-------|
| Production branch | `main` |
| Build command | `npm run build` |
| Build output directory | `.svelte-kit/cloudflare` |

### C2. Set environment variables

Go to **Pages project** > **Settings** > **Environment variables**:

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | `https://egmwfzmjkpqjpzlcnqya.supabase.co` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | `eyJ...` | From Supabase > Settings > API |
| `NODE_VERSION` | `20` | Build-time Node version |

> These are read via `$env/dynamic/private` — never exposed to the client.

### C3. Verify the deployment

1. Wait for the build to complete
2. Open the Pages URL
3. You should be **automatically redirected to Microsoft login**
4. Log in with your `@wpd.fr` account
5. You should land on the dashboard with farms loaded

---

## Phase D: Validation

### D1. Test authentication flow

1. Open the Pages URL in **incognito/private browser**
2. You should be redirected to Microsoft login automatically
3. Log in with your `@wpd.fr` account
4. You should land on `/dashboard` with data loaded

### D2. Verify identity

- Your **name** and **email** should appear in the sidebar user card
- A logout button (icon) should be visible next to your name

### D3. Test domain restriction

- If a non-`@wpd.fr` account logs in, they should be signed out and redirected to `/login?error=domain`

### D4. Test logout

- Click the logout icon in the sidebar
- You should be redirected to `/login`
- Navigating to `/dashboard` should trigger a new OAuth redirect

### D5. Test API protection

- In incognito (no session), visit `https://<site>/api/farms/<uuid>`
- You should receive a `401` JSON response

---

## Troubleshooting

### Redirect loop after login
- Check that the Supabase **Site URL** and **Redirect URLs** match your actual deployment URL
- Check that the Azure redirect URI matches `<SUPABASE_URL>/auth/v1/callback`

### "Access restricted to wpd.fr domain" error
- The `hooks.server.ts` enforces `@wpd.fr` domain — verify the logged-in account's email

### Dashboard loads but no farms/data
- Check Cloudflare Pages env vars: `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Check Supabase dashboard to confirm tables have data

### Build fails on Cloudflare
- Verify `NODE_VERSION=20` in environment variables
- Ensure `wrangler.toml` has `compatibility_flags = ["nodejs_compat"]`

### OAuth returns error
- Check Azure App Registration redirect URI matches exactly
- Check Client Secret hasn't expired
- Check Supabase Auth logs: Dashboard > Authentication > Logs

---

## Security Notes

- `SUPABASE_ANON_KEY` is used server-side only via `$env/dynamic/private`
- Session cookies are HTTP-only and managed by `@supabase/ssr`
- Domain restriction (`@wpd.fr`) is enforced server-side in `hooks.server.ts`
- All database queries run server-side via `+page.server.ts` loaders
- Unauthenticated API requests get `401`, no data leakage

---

## Quick Reference

| Service | URL |
|---------|-----|
| Cloudflare Dashboard | https://dash.cloudflare.com |
| Azure Portal | https://portal.azure.com |
| Supabase Dashboard | https://supabase.com/dashboard |

| Code File | Role |
|-----------|------|
| `hooks.server.ts` | Creates Supabase auth server client, validates session, populates user |
| `src/lib/server/supabase.ts` | Data client for PostgreSQL queries |
| `src/routes/login/` | Login page (auto-triggers OAuth, fallback for errors) |
| `src/routes/auth/callback/` | OAuth callback handler |
| `src/routes/api/auth/logout/` | Logout endpoint |
| `wrangler.toml` | Cloudflare Pages build config |
