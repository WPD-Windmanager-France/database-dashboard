# Technology Stack

## Core Frameworks
*   **Language**: Python 3.10+
*   **Frontend**: Taipy (latest stable)
*   **Backend Logic**: Python (Standard Lib + Custom Modules)
*   **Configuration**: Dynaconf (Environment management)

## Authentication
*   **Production**: Microsoft Entra ID (via `msal` library)
*   **Legacy/Fallback**: Supabase Auth (via `supabase` library)
*   **Local/Dev**: SQLite-based Mock Authentication

## Database & Data
*   **Production**: Supabase (PostgreSQL)
*   **Development**: SQLite (`DATA/windmanager.db`)
*   **ORM/Access**: Custom Facade Pattern (wrapping `supabase-py` and `sqlalchemy`)

## Infrastructure & Deployment
*   **Hosting**: Oracle Cloud (OCI)
*   **Containerization**: Docker
*   **CI/CD**: GitHub Actions (planned)

## Key Libraries
*   `taipy`: UI and Core state management
*   `dynaconf`: Configuration management
*   `msal`: Microsoft Authentication Library
*   `supabase`: Supabase client
*   `sqlalchemy`: SQL toolkit for SQLite interactions
*   `pandas`: Data manipulation
