# WNDMNGR Modernization PRD

## 1. Intro Project Analysis and Context

### Analysis Source
*   **Source**: Analysis of existing codebase (`app.py`, `auth.py`, `database.py`) and user interaction.

### Current Project State
The project is a Wind Farm Management application ("WNDMNGR") built with Streamlit. It uses a Facade pattern for database access, switching between SQLite (Local/Dev) and Supabase (Prod). Authentication is similarly split (Mock vs. Supabase). It is well-structured but requires modernization to Taipy and enhancements for enterprise readiness.

### Enhancement Scope
*   **Type**: Tech Stack Upgrade (Streamlit -> Taipy), Infrastructure (-> HF Spaces), Auth (-> Entra ID), and New Features.
*   **Impact**: Major Impact. Requires rebuilding the UI layer and significantly refactoring the Auth/Config layers.

### Goals
*   Migrate fully to Taipy framework.
*   Implement Microsoft Entra ID authentication (with Supabase Auth as fallback/legacy).
*   Deploy to Hugging Face Spaces.
*   Add "Add Farm" Wizard and Cascading Delete.
*   Display Database Documentation in-app.

---

## 2. Requirements

### Functional Requirements
*   **FR1**: The application must run on **Taipy** with a responsive layout.
*   **FR2**: Production Authentication must support **Microsoft Entra ID**.
*   **FR3**: Production Authentication must retain **Supabase Auth** as a fallback or for legacy users.
*   **FR4**: Local Development must continue to use **SQLite** and simple/mock authentication.
*   **FR5**: "Add Farm" feature must be a multi-step **Wizard** preventing incomplete data entry.
*   **FR6**: Users must be able to **View and Edit** all farm data categories (General, Contacts, etc.).
*   **FR7**: A "Hidden" or Admin-only **Cascading Delete** must allow removal of a farm and all dependencies.
*   **FR8**: Contact cards must feature a **"Send Email"** button.
*   **FR9**: A **Documentation Tab** must display the database schema and metadata.

### Non-Functional Requirements
*   **NFR1**: Deployable to **Hugging Face Spaces** (Dockerized).
*   **NFR2**: Configuration managed via **Dynaconf**.
*   **NFR3**: UI response time for edits should be immediate (<200ms) where possible.

### Compatibility Requirements
*   **CR1**: Must not break existing SQLite data structure for local dev.
*   **CR2**: Must respect existing Supabase RLS policies (if any).

---

## 3. Technical Constraints

### Integration Approach
*   **Auth**: A strategy pattern for Auth: `EntraIDProvider`, `SupabaseProvider`, `LocalProvider`.
*   **Config**: `settings.toml` for base, `.secrets.toml` for local secrets, Environment Variables for HF Spaces.
*   **DB**: Reuse `database.py` logic but wrap it to handle Taipy's state management.

### Deployment
*   **Container**: Dockerfile required for HF Spaces.
*   **Ports**: Taipy runs on 5000 (default) or variable.

---

## 4. Epic Details: WNDMNGR Modernization

**Epic Goal**: Transform WNDMNGR into an enterprise-ready, Taipy-based application deployed on HF Spaces.

### Story Sequence

#### Story 1: Foundation & Config (Dynaconf + Taipy Init)
**As a** Developer, **I want** to initialize the Taipy project and set up Dynaconf, **so that** I have a clean environment that distinguishes between Local and Prod.
*   **AC1**: Dynaconf is installed and configured.
*   **AC2**: Taipy "Hello World" runs.
*   **AC3**: `settings.toml` defines the environment.

#### Story 2: Universal Authentication Strategy
**As a** User, **I want** to log in using Entra ID (or Supabase as backup), **so that** my access is secure and managed.
*   **AC1**: Abstract Auth class created.
*   **AC2**: `LocalProvider` implements SQLite auth.
*   **AC3**: `EntraIDProvider` implemented (using `msal`).
*   **AC4**: `SupabaseProvider` ported from legacy code.
*   **AC5**: Configuration determines which provider is active.

#### Story 3: Data Layer Adaptation
**As a** Developer, **I want** to adapt `database.py` for Taipy, **so that** the UI can interact with data efficiently.
*   **AC1**: `database.py` functions verified against Taipy callbacks.
*   **AC2**: Global state management (Current Farm, Current User) implemented in Taipy.

#### Story 4: Dashboard & Read Views
**As a** User, **I want** to browse Farms and their details, **so that** I can access information.
*   **AC1**: Sidebar lists all farms.
*   **AC2**: Tabs for General, Referents, Services, Technical implemented.
*   **AC3**: Data is read-only in this phase.
*   **AC4**: "Send Email" button implemented on Contact cards.

#### Story 5: Edit & Live Updates
**As a** User, **I want** to edit farm details, **so that** the database is kept up-to-date.
*   **AC1**: Fields are editable.
*   **AC2**: Changes trigger DB updates immediately (or on "Save").
*   **AC3**: Success/Error notifications shown.

#### Story 6: The Creation Wizard
**As a** User, **I want** to add a new farm via a step-by-step wizard, **so that** I don't miss critical info.
*   **AC1**: Wizard UI implemented (Steps: ID, Loc, Tech, etc.).
*   **AC2**: Data is held in temporary state until "Finish".
*   **AC3**: "Finish" triggers atomic DB transaction.

#### Story 7: Admin Features (Delete & Docs)
**As an** Admin, **I want** to delete farms and view schema docs, **so that** I can manage the system health.
*   **AC1**: Cascading Delete function implemented and exposed safely.
*   **AC2**: Documentation tab renders schema info.

#### Story 8: HF Spaces Deployment
**As a** DevOps, **I want** to deploy the app to Hugging Face, **so that** users can access it.
*   **AC1**: `Dockerfile` created.
*   **AC2**: HF Space created and connected.
*   **AC3**: Environment variables configured in HF.
