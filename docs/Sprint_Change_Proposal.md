# Sprint Change Proposal: Unified SvelteKit Application

## 1. Identified Issue Summary
The current project path involves two separate applications: a Cloudflare-based CRUD app (potentially legacy Python/Streamlit or early Next.js attempts) and a Vercel-based Evidence dashboard. This separation causes fragmentation in authentication, deployment, and user experience. A strategic decision has been made to **consolidate both the Dashboard and the CRUD functionality into a single SvelteKit application hosted on Cloudflare Pages**.

This change leverages the "Dashboard Handoff" work (existing SQL queries, Supabase setup) while adopting SvelteKit to handle both the dynamic CRUD operations (replacing the legacy app) and the data visualization (replacing Evidence.dev), all secured by **Cloudflare Access (Microsoft Entra ID)**.

## 2. Epic Impact Summary
*   **Legacy Epics (Python/Taipy/Streamlit):** All existing stories related to the Python/Taipy/Streamlit stack are now obsolete.
*   **Current Epics (Next.js/Cloudflare Worker):** The "Backend API (Cloudflare Worker)" and "Frontend Application (Next.js)" epics defined in the PRD are partially relevant but need to be refactored into a **single SvelteKit Epic** (SvelteKit handles both frontend and backend API routes).
*   **New Epic Needed:** A unified "SvelteKit WNDMNGR Platform" epic is required to cover setup, Cloudflare Access integration, Supabase DB connection, Dashboard implementation, and CRUD features.

## 3. Artifact Adjustment Needs
*   **PRD (`docs/prd.md`):**
    *   **Update:** Replace "Next.js + Cloudflare Worker" architecture with **SvelteKit (SSR)** on **Cloudflare Pages**.
    *   **Update:** Consolidate Frontend and Backend requirements (SvelteKit handles both).
    *   **Add:** Specific requirements for the Dashboard (porting existing Evidence queries).
    *   **Update:** Authentication to focus on **Cloudflare Access / Microsoft Entra ID integration** (via App Registration) to restrict access (ideally to `@wpd.fr` domains) at the network level.
*   **Architecture (`docs/architecture/*`):**
    *   **Create/Update `architecture.md`:** Define the SvelteKit + Supabase + Cloudflare Pages architecture, secured by Cloudflare Access.
    *   **Update `tech-stack.md`:** Remove Python/Taipy. Add SvelteKit, TypeScript, Supabase (DB only), Cloudflare Pages, Cloudflare Access (Entra ID).
    *   **Update `coding-standards.md`:** Replace Python standards with TypeScript/SvelteKit standards.
*   **Stories (`docs/stories/*`):**
    *   **Action:** Archive all existing `1.x` and `2.x` stories as they target the old stack.
    *   **Action:** Create new stories for the SvelteKit implementation plan.

## 4. Recommended Path Forward
**Option: Full Pivot to Unified SvelteKit App**
We will abandon the split architecture and the Python legacy code. We will start a fresh SvelteKit project that serves as both the API and the UI.
*   **Rationale:**
    *   **Security:** Fixes the "static file exposure" issue of Evidence.dev by using server-side fetching in SvelteKit.
    *   **Auth:** Cloudflare Access provides enterprise-grade security with Entra ID integration, perfectly matching the "ideally @wpd.fr" requirement.
    *   **Simplicity:** One codebase, one deployment (Cloudflare Pages), one auth layer.
    *   **Cost:** Cloudflare Pages/Access has generous free tiers for small teams.

## 5. PRD MVP Impact
*   **Scope:** The MVP now explicitly includes the **Dashboard** (previously a separate Evidence app).
*   **Goals:** The primary goal shifts from "API Certification" (though still relevant) to "delivering a functional Unified Platform".
*   **Timeline:** Short-term delay to set up the SvelteKit scaffolding, but long-term gain in velocity due to unified codebase.

## 6. High-Level Action Plan
1.  **Refine Artifacts:** Update PRD, Tech Stack, and create a new Architecture doc.
2.  **Archive Legacy:** Move old stories to an archive folder to clear the workspace.
3.  **Scaffold Project:** Initialize a new SvelteKit app with `adapter-cloudflare`.
4.  **Create New Epics/Stories:**
    *   **Setup:** Init SvelteKit, Tailwind, Supabase Client.
    *   **Auth:** Configure Cloudflare Access with Entra ID.
    *   **Dashboard:** Port SQL queries from `dashboard-handoff.md` to SvelteKit loaders and build UI.
    *   **CRUD:** Implement the Farm Management features (Read/Create/Update).
5.  **Agent Handoff:**
    *   **PM:** Finalize PRD/Stories.
    *   **Architect:** Define the SvelteKit folder structure and data fetching pattern.
    *   **Dev:** Execute implementation.

## 7. Approval Request
Do you approve this proposal to:
1.  **Update the PRD and Architecture** to reflect the SvelteKit + Supabase + Cloudflare stack?
2.  **Archive existing stories** and generate a new backlog for the unified app?
3.  **Proceed with the SvelteKit implementation**?